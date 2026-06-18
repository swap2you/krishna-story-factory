from __future__ import annotations

import base64

import requests

from ..config import Settings


from .sanitize import sanitize_audio_script


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
        payload = {
            "text": narration_text,
            "model_id": self.settings.elevenlabs_model_id,
            "voice_settings": {
                "stability": 0.55,
                "similarity_boost": 0.75,
                "style": 0.15,
                "use_speaker_boost": True,
            },
        }
        response = requests.post(url, params=params, headers=headers, json=payload, timeout=120)
        if response.status_code >= 400:
            raise AudioGenerationError(f"ElevenLabs TTS failed: {response.status_code} {response.text[:500]}")
        output_path.write_bytes(response.content)
        return "elevenlabs"

    @staticmethod
    def is_placeholder_mp3(path) -> bool:
        if not path.exists():
            return True
        return path.stat().st_size <= _PLACEHOLDER_MAX_BYTES
