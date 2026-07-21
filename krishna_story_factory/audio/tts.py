from __future__ import annotations

import base64
import logging
import re
from pathlib import Path

import requests

from ..config import Settings
from .pronunciation import (
    LOCKED_MODEL_ID,
    LOCKED_OUTPUT_FORMAT,
    LOCKED_VOICE_ID,
    LOCKED_VOICE_NAME,
    assert_voice_matches_lock,
    normalize_for_tts,
    validate_locked_voice,
)
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
        self.last_pronunciation = None
        self.last_voice_name = ""
        self.last_dictionary_attached = False

    def generate_mp3(self, text: str, output_path) -> str:
        if self.mode == "test" or not self.settings.elevenlabs_enabled:
            normalized = normalize_for_tts(text, project_root=self.settings.project_root)
            self.last_pronunciation = normalized
            sanitized = sanitize_audio_script(normalized.audio_text, model_id=self.settings.elevenlabs_model_id)
            output_path.write_bytes(_TEST_MP3_PLACEHOLDER)
            return "placeholder"

        if not self.settings.elevenlabs_api_key:
            raise AudioGenerationError("ELEVENLABS_API_KEY is required when ELEVENLABS_ENABLED=true.")
        lock_errors = validate_locked_voice(
            voice_id=self.settings.elevenlabs_voice_id,
            voice_name=getattr(self.settings, "elevenlabs_voice_name", ""),
            model_id=self.settings.elevenlabs_model_id,
        )
        if lock_errors:
            raise AudioGenerationError(" | ".join(lock_errors))
        try:
            self.last_voice_name = assert_voice_matches_lock(
                self.settings.elevenlabs_api_key,
                self.settings.elevenlabs_voice_id,
                getattr(self.settings, "elevenlabs_voice_name", "") or LOCKED_VOICE_NAME,
            )
        except Exception as exc:
            raise AudioGenerationError(str(exc)) from exc

        normalized = normalize_for_tts(text, project_root=self.settings.project_root)
        self.last_pronunciation = normalized
        narration_text = sanitize_audio_script(normalized.audio_text, model_id=self.settings.elevenlabs_model_id)
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
        voice_id = self.settings.elevenlabs_voice_id or LOCKED_VOICE_ID
        model_id = self.settings.elevenlabs_model_id or LOCKED_MODEL_ID
        output_format = getattr(self.settings, "elevenlabs_output_format", "") or LOCKED_OUTPUT_FORMAT
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        params = {"output_format": output_format}
        headers = {
            "xi-api-key": self.settings.elevenlabs_api_key,
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
        }
        payload: dict = {
            "text": narration_text,
            "model_id": model_id,
            "voice_settings": self._voice_settings(model_id),
        }
        dictionary_id = self.settings.elevenlabs_pronunciation_dictionary_id
        version_id = getattr(self.settings, "elevenlabs_pronunciation_dictionary_version_id", "") or "latest"
        if dictionary_id:
            payload["pronunciation_dictionary_locators"] = [
                {
                    "pronunciation_dictionary_id": dictionary_id,
                    "version_id": version_id,
                }
            ]

        response = requests.post(url, params=params, headers=headers, json=payload, timeout=120)
        self.last_dictionary_attached = bool(dictionary_id)
        if response.status_code >= 400 and "pronunciation_dictionary" in response.text.lower():
            logger.warning("ElevenLabs pronunciation dictionary not supported; retrying with normalized audio text only.")
            payload.pop("pronunciation_dictionary_locators", None)
            self.last_dictionary_attached = False
            if self.last_pronunciation:
                self.last_pronunciation = type(self.last_pronunciation)(
                    display_text=self.last_pronunciation.display_text,
                    audio_text=self.last_pronunciation.audio_text,
                    aliases_applied=self.last_pronunciation.aliases_applied,
                    dictionary_id=dictionary_id,
                    dictionary_version_id=version_id,
                    dictionary_attached=False,
                    dictionary_fallback_reason="API rejected pronunciation_dictionary_locators",
                )
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

    def _voice_settings(self, model_id: str) -> dict:
        s = self.settings
        settings = {
            "stability": s.elevenlabs_stability if s.elevenlabs_stability is not None else 0.42,
            "similarity_boost": s.elevenlabs_similarity_boost if s.elevenlabs_similarity_boost is not None else 0.78,
            "style": s.elevenlabs_style if s.elevenlabs_style is not None else 0.25,
            "use_speaker_boost": s.elevenlabs_use_speaker_boost if s.elevenlabs_use_speaker_boost is not None else True,
        }
        # eleven_v3 does not support numeric speed controls in this project lock.
        if s.elevenlabs_speed is not None and "v3" not in (model_id or "").lower():
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
    cleaned = re.sub(r"\n{3,}", "\n\n", text.strip())
    words = re.findall(r"\S+", cleaned)
    if len(words) <= target_max:
        return cleaned
    sentences = re.split(r"(?<=[.!?])\s+", cleaned)
    if len(sentences) <= 4:
        return " ".join(words[:target_max])
    keep_head = max(2, len(sentences) // 4)
    keep_tail = max(2, len(sentences) // 5)
    middle = sentences[keep_head:-keep_tail]
    reduced_middle = middle[::2] if len(middle) > 2 else middle
    candidate = " ".join(sentences[:keep_head] + reduced_middle + sentences[-keep_tail:])
    candidate_words = re.findall(r"\S+", candidate)
    if len(candidate_words) > target_max:
        candidate = " ".join(candidate_words[:target_max])
    if len(re.findall(r"\S+", candidate)) < target_min:
        candidate = " ".join(words[: max(target_min, min(target_max, len(words)))])
    return candidate
