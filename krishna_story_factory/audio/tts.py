from __future__ import annotations

import base64
import logging

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


class AudioGenerator:
    def __init__(self, settings: Settings, mode: str) -> None:
        self.settings = settings
        self.mode = mode

    def generate_mp3(self, text: str, output_path) -> str:
        if self.mode == "test" or not self.settings.elevenlabs_enabled:
            output_path.write_bytes(_TEST_MP3_PLACEHOLDER)
            return "placeholder"

        if not self.settings.elevenlabs_api_key:
            raise AudioGenerationError("ELEVENLABS_API_KEY is required when ELEVENLABS_ENABLED=true.")
        if not self.settings.elevenlabs_voice_id:
            raise AudioGenerationError("ELEVENLABS_VOICE_ID is required when ELEVENLABS_ENABLED=true.")

        narration_text = sanitize_audio_script(text, model_id=self.settings.elevenlabs_model_id)

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
                {"pronunciation_dictionary_id": self.settings.elevenlabs_pronunciation_dictionary_id, "version_id": "latest"}
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
        return "elevenlabs"

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
    def is_placeholder_mp3(path) -> bool:
        if not path.exists():
            return True
        return path.stat().st_size <= _PLACEHOLDER_MAX_BYTES
