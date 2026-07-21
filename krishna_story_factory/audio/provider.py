"""Audio provider selection with run-scoped preflight cache."""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

import requests

from ..config import Settings
from .openai_tts import preflight_openai_tts
from .pronunciation import LOCKED_MODEL_ID, LOCKED_OUTPUT_FORMAT, LOCKED_VOICE_ID, LOCKED_VOICE_NAME

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class ProviderDecision:
    status: str
    provider: str
    reason: str
    estimated_chars: int = 0
    elevenlabs_available: int = 0
    openai_ok: bool = False
    detail: dict[str, Any] | None = None
    model_id: str = ""
    voice: str = ""


@dataclass
class _RunPreflightCache:
    elevenlabs: dict[str, Any] | None = None
    openai: dict[str, Any] | None = None
    decision: ProviderDecision | None = None


_CACHE = _RunPreflightCache()


def reset_provider_preflight_cache() -> None:
    """Clear run-scoped cache (tests / new process simulation)."""
    global _CACHE
    _CACHE = _RunPreflightCache()


def get_cached_provider_decision() -> ProviderDecision | None:
    return _CACHE.decision


def estimate_narration_chars(text: str) -> int:
    return len((text or "").strip())


def elevenlabs_available_characters(api_key: str) -> tuple[int, dict[str, Any]]:
    if not api_key:
        return 0, {"error": "missing_api_key"}
    response = requests.get(
        "https://api.elevenlabs.io/v1/user/subscription",
        headers={"xi-api-key": api_key},
        timeout=30,
    )
    if response.status_code >= 400:
        return 0, {"error": f"subscription_lookup_{response.status_code}"}
    data = response.json()
    used = int(data.get("character_count") or 0)
    limit = int(data.get("character_limit") or 0)
    return max(0, limit - used), {
        "character_count": used,
        "character_limit": limit,
        "next_character_count_reset_unix": data.get("next_character_count_reset_unix"),
    }


def elevenlabs_voice_resolves(api_key: str, voice_id: str) -> tuple[bool, str]:
    if not api_key or not voice_id:
        return False, ""
    response = requests.get(
        f"https://api.elevenlabs.io/v1/voices/{voice_id}",
        headers={"xi-api-key": api_key},
        timeout=30,
    )
    if response.status_code >= 400:
        return False, ""
    name = str(response.json().get("name") or "")
    ok = voice_id == LOCKED_VOICE_ID and "renee" in name.lower()
    return ok, name


def preflight_elevenlabs(settings: Settings, *, estimated_chars: int, require_dictionary: bool = True) -> dict[str, Any]:
    if _CACHE.elevenlabs is not None:
        return _CACHE.elevenlabs

    reserve = max(1, int(estimated_chars * 1.15))
    detail: dict[str, Any] = {
        "ok": False,
        "available": 0,
        "required_with_reserve": reserve,
        "voice_ok": False,
        "voice_name": "",
        "model_id": settings.elevenlabs_model_id or LOCKED_MODEL_ID,
        "output_format": getattr(settings, "elevenlabs_output_format", "") or LOCKED_OUTPUT_FORMAT,
        "dictionary_configured": bool(settings.elevenlabs_pronunciation_dictionary_id),
        "dictionary_ok": False,
    }
    if not settings.elevenlabs_enabled or not settings.elevenlabs_api_key:
        detail["error"] = "elevenlabs_disabled_or_missing_key"
        _CACHE.elevenlabs = detail
        return detail

    available, sub = elevenlabs_available_characters(settings.elevenlabs_api_key)
    voice_ok, voice_name = elevenlabs_voice_resolves(settings.elevenlabs_api_key, settings.elevenlabs_voice_id)
    model_ok = (settings.elevenlabs_model_id or "") == LOCKED_MODEL_ID
    format_ok = (getattr(settings, "elevenlabs_output_format", "") or LOCKED_OUTPUT_FORMAT) == LOCKED_OUTPUT_FORMAT
    dict_ok = bool(settings.elevenlabs_pronunciation_dictionary_id) if require_dictionary else True
    ok = (
        voice_ok
        and dict_ok
        and model_ok
        and format_ok
        and available >= reserve
        and settings.elevenlabs_voice_id == LOCKED_VOICE_ID
    )
    detail.update(
        {
            "ok": ok,
            "available": available,
            "subscription": sub,
            "voice_ok": voice_ok,
            "voice_name": voice_name or LOCKED_VOICE_NAME,
            "model_ok": model_ok,
            "format_ok": format_ok,
            "dictionary_ok": dict_ok,
        }
    )
    _CACHE.elevenlabs = detail
    return detail


def preflight_openai(settings: Settings) -> dict[str, Any]:
    if _CACHE.openai is not None:
        return _CACHE.openai

    openai_enabled = bool(getattr(settings, "openai_tts_enabled", False))
    if not openai_enabled or not settings.openai_api_key:
        detail = {
            "ok": False,
            "provider": "openai",
            "error_class": "authentication_invalid_key" if not settings.openai_api_key else "disabled",
            "detail": "OpenAI TTS disabled or API key missing.",
        }
        _CACHE.openai = detail
        return detail

    detail = preflight_openai_tts(
        api_key=settings.openai_api_key,
        model=getattr(settings, "openai_tts_model", "gpt-4o-mini-tts-2025-12-15"),
        voice=getattr(settings, "openai_tts_voice", "marin"),
        speed=float(getattr(settings, "openai_tts_speed", 0.92) or 0.92),
    )
    _CACHE.openai = detail
    return detail


def select_audio_provider(
    settings: Settings,
    *,
    estimated_chars: int,
    require_dictionary: bool = True,
    reuse_cached_decision: bool = True,
) -> ProviderDecision:
    """Choose ElevenLabs or OpenAI before expensive generation.

    Run-scoped: ElevenLabs and OpenAI preflights execute at most once each per process.
    """
    if reuse_cached_decision and _CACHE.decision is not None:
        # Recompute only the readiness against a new estimate if ElevenLabs was chosen;
        # still reuse preflight payloads.
        pass

    mode = (getattr(settings, "audio_provider_mode", "auto") or "auto").strip().lower()
    primary = (getattr(settings, "audio_provider_primary", "elevenlabs") or "elevenlabs").strip().lower()
    fallback = (getattr(settings, "audio_provider_fallback", "openai") or "openai").strip().lower()
    audio_required = bool(getattr(settings, "audio_required", True))

    eleven_detail = preflight_elevenlabs(
        settings, estimated_chars=estimated_chars, require_dictionary=require_dictionary
    )
    # Re-evaluate balance against this estimate using cached subscription numbers.
    reserve = max(1, int(estimated_chars * 1.15))
    eleven_available = int(eleven_detail.get("available") or 0)
    eleven_ok = bool(eleven_detail.get("ok")) and eleven_available >= reserve
    if eleven_detail.get("ok") and eleven_available < reserve:
        eleven_ok = False
        eleven_detail = {**eleven_detail, "ok": False, "required_with_reserve": reserve}

    openai_preflight: dict[str, Any] = {"ok": False}
    # Only hit OpenAI preflight when ElevenLabs cannot serve, or mode forces OpenAI.
    need_openai = mode == "openai" or (not eleven_ok and mode != "elevenlabs")
    if need_openai:
        openai_preflight = preflight_openai(settings)
    elif _CACHE.openai is not None:
        openai_preflight = _CACHE.openai

    def prefer(provider: str) -> ProviderDecision | None:
        if provider == "elevenlabs" and eleven_ok:
            return ProviderDecision(
                status="READY",
                provider="elevenlabs",
                reason="ElevenLabs balance/voice/dictionary/model/format preflight passed.",
                estimated_chars=estimated_chars,
                elevenlabs_available=eleven_available,
                openai_ok=bool(openai_preflight.get("ok")),
                detail={"elevenlabs": eleven_detail, "openai": openai_preflight},
                model_id=str(eleven_detail.get("model_id") or LOCKED_MODEL_ID),
                voice=str(eleven_detail.get("voice_name") or LOCKED_VOICE_NAME),
            )
        if provider == "openai" and openai_preflight.get("ok"):
            return ProviderDecision(
                status="READY",
                provider="openai",
                reason="OpenAI TTS preflight passed; ElevenLabs unavailable or insufficient.",
                estimated_chars=estimated_chars,
                elevenlabs_available=eleven_available,
                openai_ok=True,
                detail={"elevenlabs": eleven_detail, "openai": openai_preflight},
                model_id=str(openai_preflight.get("model_id") or getattr(settings, "openai_tts_model", "")),
                voice=str(openai_preflight.get("voice") or getattr(settings, "openai_tts_voice", "marin")),
            )
        return None

    if mode == "elevenlabs":
        decision = prefer("elevenlabs")
    elif mode == "openai":
        decision = prefer("openai")
    else:
        decision = prefer(primary) or prefer(fallback)

    if decision:
        _CACHE.decision = decision
        return decision

    if not audio_required:
        decision = ProviderDecision(
            status="SKIPPED_AUDIO_OPTIONAL",
            provider="",
            reason="No audio provider available and AUDIO_REQUIRED=false.",
            estimated_chars=estimated_chars,
            elevenlabs_available=eleven_available,
            openai_ok=bool(openai_preflight.get("ok")),
            detail={"elevenlabs": eleven_detail, "openai": openai_preflight},
        )
        _CACHE.decision = decision
        return decision

    decision = ProviderDecision(
        status="SKIPPED_AUDIO_PROVIDER_UNAVAILABLE",
        provider="",
        reason="Neither ElevenLabs nor OpenAI TTS preflight succeeded.",
        estimated_chars=estimated_chars,
        elevenlabs_available=eleven_available,
        openai_ok=bool(openai_preflight.get("ok")),
        detail={"elevenlabs": eleven_detail, "openai": openai_preflight},
    )
    _CACHE.decision = decision
    return decision
