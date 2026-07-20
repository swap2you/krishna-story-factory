from __future__ import annotations

import base64
import logging
import re

import requests

from ..config import Settings
from .sanitize import sanitize_audio_script

logger = logging.getLogger(__name__)


class AudioGenerationError(RuntimeError):
    pass


_TEST_MP3_PLACEHOLDER = base64.b64decode(
    "SUQzBAAAAAAAI1RTU0UAAAAPAAADTGF2ZjU4LjIwLjEwMAAAAAAAAAAAAAAA//tQxAADBwAABpAAAACAAADSAAAA"
)

_PLACEHOLDER_MAX_BYTES = 512
_QUOTA_MARKERS = ("quota", "credit", "insufficient", "payment_required", "402")


class AudioGenerator:
    def __init__(self, settings: Settings, mode: str) -> None:
        self.settings = settings
        self.mode = mode
        self.low_credit_mode = False

    def generate_mp3(self, text: str, output_path) -> str:
        if self.mode == "test" or not self.settings.elevenlabs_enabled:
            output_path.write_bytes(_TEST_MP3_PLACEHOLDER)
            return "placeholder"

        if not self.settings.elevenlabs_api_key:
            raise AudioGenerationError("ELEVENLABS_API_KEY is required when ELEVENLABS_ENABLED=true.")
        if not self.settings.elevenlabs_voice_id:
            raise AudioGenerationError("ELEVENLABS_VOICE_ID is required when ELEVENLABS_ENABLED=true.")

        narration_text = sanitize_audio_script(text, model_id=self.settings.elevenlabs_model_id)
        try:
            self._synthesize(narration_text, output_path)
            self.low_credit_mode = False
            return "elevenlabs"
        except AudioGenerationError as exc:
            if not self._is_quota_error(str(exc)):
                raise
            logger.warning("ElevenLabs quota/credits low; retrying with concise narration (420-560 words).")
            concise = _to_concise_narration(narration_text, target_min=420, target_max=560)
            concise = sanitize_audio_script(concise, model_id=self.settings.elevenlabs_model_id)
            self._synthesize(concise, output_path)
            self.low_credit_mode = True
            return "elevenlabs_low_credit"

    def _synthesize(self, narration_text: str, output_path) -> None:
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{self.settings.elevenlabs_voice_id}"
        params = {"output_format": "mp3_44100_128"}
        headers = {
            "xi-api-key": self.settings.elevenlabs_api_key,
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
        }
        payload: dict = {
            "text": narration_text,
            "model_id": self.settings.elevenlabs_model_id,
            "voice_settings": self._voice_settings(),
        }
        if self.settings.elevenlabs_pronunciation_dictionary_id:
            payload["pronunciation_dictionary_locators"] = [
                {
                    "pronunciation_dictionary_id": self.settings.elevenlabs_pronunciation_dictionary_id,
                    "version_id": "latest",
                }
            ]

        response = requests.post(url, params=params, headers=headers, json=payload, timeout=120)
        if response.status_code >= 400 and "pronunciation_dictionary" in response.text.lower():
            logger.warning("ElevenLabs pronunciation dictionary not supported; retrying without it.")
            payload.pop("pronunciation_dictionary_locators", None)
            response = requests.post(url, params=params, headers=headers, json=payload, timeout=120)
        if response.status_code >= 400 and self._has_optional_voice_fields(payload):
            logger.warning("ElevenLabs rejected optional voice settings; retrying with core settings only.")
            payload["voice_settings"] = {
                "stability": payload["voice_settings"].get("stability", 0.42),
                "similarity_boost": payload["voice_settings"].get("similarity_boost", 0.78),
            }
            response = requests.post(url, params=params, headers=headers, json=payload, timeout=120)
        if response.status_code >= 400:
            raise AudioGenerationError(f"ElevenLabs TTS failed: {response.status_code} {response.text[:500]}")
        output_path.write_bytes(response.content)

    def _voice_settings(self) -> dict:
        s = self.settings
        settings = {
            "stability": s.elevenlabs_stability if s.elevenlabs_stability is not None else 0.42,
            "similarity_boost": s.elevenlabs_similarity_boost if s.elevenlabs_similarity_boost is not None else 0.78,
            "style": s.elevenlabs_style if s.elevenlabs_style is not None else 0.35,
            "use_speaker_boost": s.elevenlabs_use_speaker_boost if s.elevenlabs_use_speaker_boost is not None else True,
        }
        if s.elevenlabs_speed is not None:
            settings["speed"] = s.elevenlabs_speed
        return settings

    @staticmethod
    def _has_optional_voice_fields(payload: dict) -> bool:
        voice = payload.get("voice_settings", {})
        return "style" in voice or "speed" in voice or "use_speaker_boost" in voice

    @staticmethod
    def _is_quota_error(message: str) -> bool:
        lower = message.lower()
        return any(marker in lower for marker in _QUOTA_MARKERS)

    @staticmethod
    def is_placeholder_mp3(path) -> bool:
        if not path.exists():
            return True
        return path.stat().st_size <= _PLACEHOLDER_MAX_BYTES


def _to_concise_narration(text: str, *, target_min: int, target_max: int) -> str:
    """Compress narration while preserving expressive tags and story arc; never pads."""
    # Keep performance tags; strip excess whitespace.
    cleaned = re.sub(r"\n{3,}", "\n\n", text.strip())
    words = re.findall(r"\S+", cleaned)
    if len(words) <= target_max:
        return cleaned
    # Prefer sentence-level trim from the middle filler, keep opening and closing.
    sentences = re.split(r"(?<=[.!?])\s+", cleaned)
    if len(sentences) <= 4:
        return " ".join(words[:target_max])
    keep_head = max(2, len(sentences) // 4)
    keep_tail = max(2, len(sentences) // 5)
    middle = sentences[keep_head:-keep_tail]
    # Drop every other middle sentence to shorten without removing arc ends.
    reduced_middle = middle[::2] if len(middle) > 2 else middle
    candidate = " ".join(sentences[:keep_head] + reduced_middle + sentences[-keep_tail:])
    candidate_words = re.findall(r"\S+", candidate)
    if len(candidate_words) > target_max:
        candidate = " ".join(candidate_words[:target_max])
    # Ensure we did not collapse too far; if so, keep more of original head.
    if len(re.findall(r"\S+", candidate)) < target_min:
        candidate = " ".join(words[: max(target_min, min(target_max, len(words)))])
    return candidate
