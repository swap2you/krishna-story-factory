"""Sample-first TTS gate (Phase 9 — fail-closed create-next governance).

Governed audio sequence requires a short sample (45–60s) with the exact intended
provider/voice/model/settings to pass QA before full narration synthesis.

``AUDIO_SAMPLE_FIRST_REQUIRED`` defaults to **true** (fail-closed) for the
production create-next path. Explicit opt-out ``AUDIO_SAMPLE_FIRST_REQUIRED=0``
is allowed only for legacy rebuild tools.

A durable pass artifact (``audio_sample_pass.json`` under the run work dir) must
bind provider, model, voice, settings hash, and narration_source_sha. Changing
narration text or voice/settings invalidates the pass and blocks full TTS.
"""
from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from .drift import narration_source_sha


class AudioSampleFirstError(RuntimeError):
    """Raised when sample-first is required but full TTS is not yet allowed."""


SAMPLE_PASS_FILENAME = "audio_sample_pass.json"
_TRUTHY = {"1", "true", "yes", "on"}


def sample_first_required() -> bool:
    """Return whether full TTS must have a validated sample pass.

    Default (env unset/empty): **True** — fail-closed for create-next / prod.
    Explicit falsy values (0/false/no/off) opt out for legacy rebuild tools.
    """
    raw = os.getenv("AUDIO_SAMPLE_FIRST_REQUIRED")
    if raw is None or str(raw).strip() == "":
        return True
    return str(raw).strip().lower() in _TRUTHY


def sample_pass_path(work_dir: Path | None) -> Path | None:
    if work_dir is None:
        return None
    return Path(work_dir) / SAMPLE_PASS_FILENAME


def compute_settings_hash(settings: Mapping[str, Any] | None) -> str:
    """Stable SHA-256 of voice/model settings used for sample↔full binding."""
    payload = json.dumps(dict(settings or {}), sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest().upper()


def build_tts_settings_binding(
    *,
    provider: str,
    model: str = "",
    voice: str = "",
    settings: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Normalize binding fields used in the sample-pass artifact."""
    provider_norm = (provider or "").strip().lower()
    model_norm = (model or "").strip()
    voice_norm = (voice or "").strip()
    settings_dict = dict(settings or {})
    return {
        "provider": provider_norm,
        "model": model_norm,
        "voice": voice_norm,
        "settings": settings_dict,
        "settings_hash": compute_settings_hash(settings_dict),
    }


def write_sample_pass(
    work_dir: Path,
    *,
    provider: str,
    model: str,
    voice: str,
    settings: Mapping[str, Any] | None,
    narration_text: str,
    sample_duration_seconds: float | None = None,
    extra: Mapping[str, Any] | None = None,
) -> Path:
    """Persist a durable sample PASS artifact bound to text + voice settings."""
    work = Path(work_dir)
    work.mkdir(parents=True, exist_ok=True)
    binding = build_tts_settings_binding(
        provider=provider, model=model, voice=voice, settings=settings
    )
    record: dict[str, Any] = {
        "status": "PASS",
        "provider": binding["provider"],
        "model": binding["model"],
        "voice": binding["voice"],
        "settings_hash": binding["settings_hash"],
        "settings": binding["settings"],
        "narration_source_sha": narration_source_sha(narration_text),
        "passed_at": datetime.now(timezone.utc).isoformat(),
    }
    if sample_duration_seconds is not None:
        record["sample_duration_seconds"] = float(sample_duration_seconds)
    if extra:
        for key, value in extra.items():
            if key not in record:
                record[key] = value
    path = work / SAMPLE_PASS_FILENAME
    path.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def load_sample_pass(work_dir: Path | None) -> dict[str, Any] | None:
    path = sample_pass_path(work_dir)
    if path is None or not path.is_file() or path.stat().st_size < 1:
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return data if isinstance(data, dict) else None


def validate_sample_pass(
    record: Mapping[str, Any] | None,
    *,
    narration_text: str,
    provider: str,
    model: str,
    voice: str,
    settings: Mapping[str, Any] | None,
) -> list[str]:
    """Return human-readable errors if the pass is missing or binding mismatches."""
    errors: list[str] = []
    if not record:
        errors.append(f"missing or unreadable {SAMPLE_PASS_FILENAME}")
        return errors

    status = str(record.get("status") or "").strip().upper()
    if status != "PASS":
        errors.append(f"sample status is {status or 'empty'!r}, expected PASS")

    expected = build_tts_settings_binding(
        provider=provider, model=model, voice=voice, settings=settings
    )
    expected_sha = narration_source_sha(narration_text)

    actual_provider = str(record.get("provider") or "").strip().lower()
    actual_model = str(record.get("model") or "").strip()
    actual_voice = str(record.get("voice") or "").strip()
    actual_hash = str(record.get("settings_hash") or "").strip().upper()
    actual_sha = str(record.get("narration_source_sha") or "").strip().upper()

    if actual_provider != expected["provider"]:
        errors.append(
            f"provider mismatch: pass={actual_provider!r} intended={expected['provider']!r}"
        )
    if actual_model != expected["model"]:
        errors.append(
            f"model mismatch: pass={actual_model!r} intended={expected['model']!r}"
        )
    if actual_voice != expected["voice"]:
        errors.append(
            f"voice mismatch: pass={actual_voice!r} intended={expected['voice']!r}"
        )
    if actual_hash != expected["settings_hash"]:
        errors.append(
            "settings_hash mismatch — voice/settings changed since sample PASS "
            f"(pass={actual_hash[:12] or 'missing'}… intended={expected['settings_hash'][:12]}…)"
        )
    if actual_sha != expected_sha:
        errors.append(
            "narration_source_sha mismatch — story/narration text changed since sample PASS "
            f"(pass={actual_sha[:12] or 'missing'}… intended={expected_sha[:12]}…)"
        )
    return errors


def assert_full_tts_allowed(
    *,
    work_dir: Path | None = None,
    narration_text: str = "",
    provider: str = "",
    model: str = "",
    voice: str = "",
    settings: Mapping[str, Any] | None = None,
) -> None:
    """Fail closed when sample-first is enabled and no valid bound sample pass exists."""
    if not sample_first_required():
        return

    path = sample_pass_path(work_dir)
    if path is None:
        raise AudioSampleFirstError(
            "AUDIO_SAMPLE_FIRST_REQUIRED is enabled but no work_dir was provided "
            "to locate the sample pass artifact. Full narration synthesis is blocked. "
            "Pipeline must pass work_dir into generate_mp3."
        )

    record = load_sample_pass(work_dir)
    if record is None:
        raise AudioSampleFirstError(
            "AUDIO_SAMPLE_FIRST_REQUIRED is enabled but no validated sample pass was "
            f"recorded (expected {SAMPLE_PASS_FILENAME} under {path.parent}). "
            "Full narration synthesis is blocked until sample QA passes and writes a "
            "bound PASS artifact (provider/model/voice/settings_hash/narration_source_sha)."
        )

    errors = validate_sample_pass(
        record,
        narration_text=narration_text,
        provider=provider,
        model=model,
        voice=voice,
        settings=settings,
    )
    if errors:
        raise AudioSampleFirstError(
            "Sample-first gate rejected full TTS — pass binding invalid or stale: "
            + " | ".join(errors)
            + ". Changing narration text or voice/settings invalidates the sample PASS; "
            "re-run sample QA before full narration."
        )


__all__ = [
    "AudioSampleFirstError",
    "SAMPLE_PASS_FILENAME",
    "assert_full_tts_allowed",
    "build_tts_settings_binding",
    "compute_settings_hash",
    "load_sample_pass",
    "sample_first_required",
    "sample_pass_path",
    "validate_sample_pass",
    "write_sample_pass",
]
