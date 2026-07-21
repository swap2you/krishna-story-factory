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
        self.last_request_id = ""
        self.last_trace_id = ""
        self.last_character_cost = 0
        self.last_model_id = ""
        self.last_output_format = ""
        self.last_voice_id = ""
        self.last_request_metadata: dict = {}
        self.last_provider = ""
        self.last_provider_decision = None
        self.last_chunk_metadata: list = []

    def generate_mp3(
        self,
        text: str,
        output_path,
        *,
        provider_decision=None,
        preferred_provider: str | None = None,
        work_dir: Path | None = None,
    ) -> str:
        normalized = normalize_for_tts(text, project_root=self.settings.project_root)
        self.last_pronunciation = normalized
        narration_text = sanitize_audio_script(normalized.audio_text, model_id=self.settings.elevenlabs_model_id)
        if "<break" in narration_text.lower() or "[pause]" in narration_text.lower():
            raise AudioGenerationError("Narration text still contains forbidden SSML/pause markup.")

        if self.mode == "test":
            output_path.write_bytes(_TEST_MP3_PLACEHOLDER)
            self.last_provider = "placeholder"
            return "placeholder"

        decision = provider_decision
        if decision is None:
            from .provider import get_cached_provider_decision, select_audio_provider

            decision = get_cached_provider_decision()
            if decision is None:
                decision = select_audio_provider(self.settings, estimated_chars=len(narration_text))
        self.last_provider_decision = decision

        provider = (preferred_provider or (decision.provider if decision else "") or "").strip().lower()
        if decision is not None and decision.status != "READY" and not preferred_provider:
            raise AudioGenerationError(f"{decision.status}: {decision.reason}")
        if not provider:
            raise AudioGenerationError("No audio provider selected.")

        if provider == "openai":
            model = (decision.model_id if decision else "") or None
            return self._synthesize_openai(
                narration_text,
                output_path,
                work_dir=work_dir,
                model=model,
                allow_model_fallback=not bool(model),
            )
        if provider == "elevenlabs":
            try:
                return self._synthesize_elevenlabs(narration_text, output_path)
            except AudioGenerationError as exc:
                if not self._is_eligible_elevenlabs_runtime_fallback(str(exc)):
                    raise
                from .provider import invalidate_elevenlabs_cache, preflight_openai
                from .redact import sanitize_error_text

                logger.warning(
                    "ElevenLabs synthesis failed after preflight; attempting OpenAI fallback once (%s).",
                    type(exc).__name__,
                )
                try:
                    Path(output_path).unlink(missing_ok=True)
                except OSError:
                    pass
                invalidate_elevenlabs_cache(reason=sanitize_error_text(str(exc), limit=160))
                openai_pf = preflight_openai(self.settings)
                if not openai_pf.get("ok"):
                    raise AudioGenerationError(
                        f"ElevenLabs synthesis failed and OpenAI fallback unavailable: {exc}"
                    ) from exc
                return self._synthesize_openai(
                    narration_text,
                    output_path,
                    work_dir=work_dir,
                    model=str(openai_pf.get("model_id") or "") or None,
                    allow_model_fallback=False,
                )
        raise AudioGenerationError(f"Unsupported audio provider: {provider!r}")

    def _synthesize_openai(
        self,
        narration_text: str,
        output_path,
        *,
        work_dir: Path | None = None,
        model: str | None = None,
        allow_model_fallback: bool = True,
    ) -> str:
        from .openai_tts import OpenAITtsError, synthesize_openai_tts
        from .redact import sanitize_error_text

        max_chars = int(getattr(self.settings, "openai_tts_max_input_chars", 3600) or 3600)
        # Always sanitize with OpenAI rules — never pass SSML or expressive bracket tags.
        text = sanitize_audio_script(narration_text, model_id="openai")
        if "<break" in text.lower() or re.search(r"\[[^\]]+\]", text):
            text = sanitize_audio_script(text, model_id="openai")
            text = re.sub(r"\[[^\]]+\]", "", text)
            text = re.sub(r"<break\b[^>]*/?>", "", text, flags=re.IGNORECASE)
        selected_model = (model or getattr(self.settings, "openai_tts_model", "gpt-4o-mini-tts-2025-12-15")).strip()
        try:
            result = synthesize_openai_tts(
                api_key=self.settings.openai_api_key,
                text=text,
                output_path=Path(output_path),
                model=selected_model,
                voice=getattr(self.settings, "openai_tts_voice", "marin"),
                speed=float(getattr(self.settings, "openai_tts_speed", 0.92) or 0.92),
                response_format=getattr(self.settings, "openai_tts_response_format", "mp3"),
                max_input_chars=max_chars,
                allow_model_fallback=allow_model_fallback,
                work_dir=work_dir,
            )
        except OpenAITtsError as exc:
            status = exc.blocked_status or f"OpenAI TTS failed ({exc.error_class})"
            raise AudioGenerationError(f"{status}: {sanitize_error_text(str(exc))}") from exc

        self.last_provider = "openai"
        self.last_voice_name = result.voice
        self.last_voice_id = result.voice
        self.last_model_id = result.model_id
        self.last_output_format = result.response_format
        self.last_request_id = result.request_id
        self.last_dictionary_attached = False
        self.last_chunk_metadata = list(result.chunk_metadata)
        self.last_request_metadata = {
            "provider": "openai",
            "model_id": result.model_id,
            "voice": result.voice,
            "speed": result.speed,
            "response_format": result.response_format,
            "request_id": result.request_id,
            "used_instructions": result.used_instructions,
            "chunk_count": result.chunk_count,
            "original_text_sha256": result.chunk_plan.original_sha256 if result.chunk_plan else "",
            "reconstructed_text_sha256": result.chunk_plan.reconstructed_sha256 if result.chunk_plan else "",
            "reconstruction_equal": bool(result.chunk_plan.reconstruction_equal) if result.chunk_plan else False,
            "chunks": result.chunk_metadata,
        }
        self.low_credit_mode = False
        return "openai"

    def _synthesize_elevenlabs(self, narration_text: str, output_path) -> str:
        if not self.settings.elevenlabs_enabled:
            raise AudioGenerationError("ElevenLabs provider selected but ELEVENLABS_ENABLED=false.")
        if not self.settings.elevenlabs_api_key:
            raise AudioGenerationError("ELEVENLABS_API_KEY is required when ElevenLabs is selected.")
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

        # No concise/compressed narration path — quota must be gated by preflight.
        self._synthesize(narration_text, output_path)
        self.low_credit_mode = False
        self.last_provider = "elevenlabs"
        return "elevenlabs"

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

        try:
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
        except (requests.Timeout, requests.ConnectionError, requests.RequestException) as exc:
            from .redact import sanitize_error_text

            raise AudioGenerationError(
                f"ElevenLabs TTS network/timeout failure: {sanitize_error_text(str(exc))}"
            ) from exc
        if response.status_code >= 400:
            from .redact import sanitize_error_text

            raise AudioGenerationError(
                f"ElevenLabs TTS failed: {response.status_code} {sanitize_error_text(response.text[:500])}"
            )
        self.last_voice_id = voice_id
        self.last_model_id = model_id
        self.last_output_format = output_format
        self.last_request_id = response.headers.get("request-id") or response.headers.get("x-request-id") or ""
        self.last_trace_id = response.headers.get("x-trace-id") or response.headers.get("trace-id") or ""
        cost_raw = response.headers.get("character-cost") or response.headers.get("x-character-count") or "0"
        try:
            self.last_character_cost = int(float(cost_raw))
        except ValueError:
            self.last_character_cost = 0
        self.last_request_metadata = {
            "provider": "elevenlabs",
            "voice_id": voice_id,
            "voice_name": self.last_voice_name or LOCKED_VOICE_NAME,
            "model_id": model_id,
            "output_format": output_format,
            "pronunciation_dictionary_attached": self.last_dictionary_attached,
            "request_id": self.last_request_id,
            "trace_id": self.last_trace_id,
            "character_cost": self.last_character_cost,
        }
        if "<break" in narration_text.lower() or "[pause]" in narration_text.lower():
            raise AudioGenerationError("Narration text still contains forbidden SSML/pause markup.")
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
    def _is_eligible_elevenlabs_runtime_fallback(message: str) -> bool:
        lower = (message or "").lower()
        markers = (
            "quota",
            "credit",
            "insufficient",
            "timeout",
            "timed out",
            "connection",
            "network",
            "temporarily unavailable",
            "503",
            "502",
            "429",
            "service unavailable",
        )
        return any(marker in lower for marker in markers)

    @staticmethod
    def _is_quota_error(message: str) -> bool:
        lower = message.lower()
        return any(marker in lower for marker in _QUOTA_MARKERS)

    @staticmethod
    def is_placeholder_mp3(path) -> bool:
        if not path.exists():
            return True
        return path.stat().st_size <= _PLACEHOLDER_MAX_BYTES
