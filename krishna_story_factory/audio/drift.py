"""Narration source hashing and stale-audio detection."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


def normalize_narration_source(text: str) -> str:
    cleaned = re.sub(r"<break\b[^>]*/?>", " ", text or "", flags=re.I)
    cleaned = re.sub(r"\[[^\]]+\]", " ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip().lower()
    return cleaned


def narration_source_sha(text: str) -> str:
    return hashlib.sha256(normalize_narration_source(text).encode("utf-8")).hexdigest().upper()


def read_manifest_audio(manifest_path: Path) -> dict:
    if not manifest_path.exists():
        return {}
    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    audio = data.get("audio") or {}
    if not isinstance(audio, dict):
        audio = {}
    return {
        "audio_source": data.get("audio_source") or "",
        "audio": audio,
        "narration_source_sha": data.get("narration_source_sha") or audio.get("narration_source_sha") or "",
        "quality_status": (data.get("quality") or {}).get("status") or "",
    }


def preserved_audio_metadata(
    *,
    narration_path: Path,
    prior_manifest: Path | None = None,
    waveform_status: str = "UNKNOWN",
    duration_seconds: float | None = None,
) -> tuple[str, dict]:
    """Build truthful metadata for a preserved MP3 without inventing provider identity."""
    prior = read_manifest_audio(prior_manifest) if prior_manifest else {}
    prior_audio = prior.get("audio") or {}
    provider = str(prior_audio.get("provider") or "").strip()
    model_id = prior_audio.get("model_id")
    voice = prior_audio.get("voice")
    generation_verified = bool(prior_audio.get("generation_verified"))
    if provider in {"", "preserved"} or not generation_verified:
        provider = "unknown_preserved"
        model_id = None
        voice = None
        generation_verified = False
        audio_source = "unknown_preserved"
    else:
        audio_source = str(prior.get("audio_source") or provider)

    sha = ""
    size = 0
    if narration_path.exists():
        raw = narration_path.read_bytes()
        sha = hashlib.sha256(raw).hexdigest().upper()
        size = len(raw)
    meta = {
        "provider": provider,
        "model_id": model_id,
        "voice": voice,
        "generation_verified": generation_verified,
        "sha256": sha,
        "bytes": size,
        "duration_seconds": duration_seconds,
        "waveform_validation_status": waveform_status,
    }
    return audio_source, meta


def detect_audio_stale(*, audio_script: str, manifest_path: Path) -> tuple[bool, str]:
    """Return (stale, detail). Missing or mismatched narration_source_sha => stale."""
    expected = narration_source_sha(audio_script)
    prior = read_manifest_audio(manifest_path)
    recorded = str(prior.get("narration_source_sha") or "").strip().upper()
    if not recorded:
        return True, "AUDIO_STALE: narration_source_sha missing from manifest"
    if recorded != expected:
        return True, "AUDIO_STALE: narration text changed since last verified audio generation"
    return False, ""


__all__ = [
    "detect_audio_stale",
    "narration_source_sha",
    "normalize_narration_source",
    "preserved_audio_metadata",
    "read_manifest_audio",
]
