"""Display→audio pronunciation normalization for ElevenLabs TTS."""
from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

LOCKED_VOICE_ID = "Itr6exdQTrvjpW1lNztS"
LOCKED_VOICE_NAME = "Renee - Rich, Calm and Smooth"
LOCKED_MODEL_ID = "eleven_v3"
LOCKED_OUTPUT_FORMAT = "mp3_44100_128"


@dataclass(frozen=True, slots=True)
class PronunciationResult:
    display_text: str
    audio_text: str
    aliases_applied: tuple[str, ...]
    dictionary_id: str = ""
    dictionary_version_id: str = ""
    dictionary_attached: bool = False
    dictionary_fallback_reason: str = ""


def load_pronunciation_aliases(project_root: Path | None = None) -> dict[str, str]:
    root = project_root or Path.cwd()
    path = root / "input" / "audio_pronunciations.yaml"
    if not path.exists():
        return {}
    try:
        import yaml
    except ImportError:
        return _parse_simple_yaml_aliases(path.read_text(encoding="utf-8"))
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    aliases = data.get("aliases") or {}
    return {str(k): str(v) for k, v in aliases.items() if str(k).strip() and str(v).strip()}


def _parse_simple_yaml_aliases(text: str) -> dict[str, str]:
    """Minimal fallback parser when PyYAML is unavailable."""
    aliases: dict[str, str] = {}
    in_aliases = False
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("aliases:"):
            in_aliases = True
            continue
        if not in_aliases or not stripped or stripped.startswith("#"):
            continue
        if stripped.endswith(":") and not stripped.startswith('"') and ":" == stripped[-1] and stripped.count(":") == 1:
            break
        match = re.match(r'^"?([^"]+)"?\s*:\s*"?([^"]+)"?\s*$', stripped)
        if match:
            aliases[match.group(1).strip()] = match.group(2).strip()
    return aliases


@lru_cache(maxsize=4)
def _cached_aliases(project_root: str) -> tuple[tuple[str, str], ...]:
    items = load_pronunciation_aliases(Path(project_root))
    # Longest keys first so multi-word phrases win.
    ordered = sorted(items.items(), key=lambda pair: len(pair[0]), reverse=True)
    return tuple(ordered)


def normalize_for_tts(text: str, *, project_root: Path | None = None) -> PronunciationResult:
    """Convert display Unicode names to TTS-friendly aliases without touching story.md."""
    root = str((project_root or Path.cwd()).resolve())
    audio = text or ""
    applied: list[str] = []
    for source, target in _cached_aliases(root):
        # Word/token boundaries so "Rama" does not rewrite "drama".
        pattern = re.compile(rf"(?<!\w){re.escape(source)}(?!\w)", re.IGNORECASE)
        if pattern.search(audio):
            audio = pattern.sub(target, audio)
            applied.append(f"{source}->{target}")
    # Generic diacritic fold for leftover Sanskrit letters in audio path only.
    audio = _fold_remaining_diacritics(audio)
    return PronunciationResult(
        display_text=text or "",
        audio_text=audio,
        aliases_applied=tuple(applied),
    )


def _fold_remaining_diacritics(text: str) -> str:
    mapping = str.maketrans(
        {
            "ā": "a",
            "ī": "i",
            "ū": "u",
            "ṛ": "ri",
            "ṝ": "ri",
            "ṅ": "n",
            "ñ": "n",
            "ṭ": "t",
            "ḍ": "d",
            "ṇ": "n",
            "ś": "sh",
            "ṣ": "sh",
            "ḥ": "h",
            "ṁ": "m",
            "ṃ": "m",
            "Ā": "A",
            "Ī": "I",
            "Ū": "U",
            "Ś": "Sh",
            "Ṣ": "Sh",
        }
    )
    return text.translate(mapping)


def validate_locked_voice(*, voice_id: str, voice_name: str = "", model_id: str = "") -> list[str]:
    errors: list[str] = []
    if (voice_id or "").strip() != LOCKED_VOICE_ID:
        errors.append(
            f"ELEVENLABS_VOICE_ID must be {LOCKED_VOICE_ID} (Renee); got {voice_id!r}."
        )
    if voice_name and voice_name.strip() and "renee" not in voice_name.strip().lower():
        errors.append(
            f"ELEVENLABS_VOICE_NAME should identify Renee; got {voice_name!r}."
        )
    if model_id and "v3" not in model_id.lower():
        errors.append(f"ELEVENLABS_MODEL_ID must be eleven_v3; got {model_id!r}.")
    return errors


def fetch_voice_name(api_key: str, voice_id: str) -> str:
    """Resolve voice name from ElevenLabs API; fail fast on mismatch."""
    import requests

    response = requests.get(
        f"https://api.elevenlabs.io/v1/voices/{voice_id}",
        headers={"xi-api-key": api_key},
        timeout=30,
    )
    if response.status_code >= 400:
        raise RuntimeError(f"ElevenLabs voice lookup failed: {response.status_code} {response.text[:300]}")
    data: dict[str, Any] = response.json()
    return str(data.get("name") or "")


def assert_voice_matches_lock(api_key: str, voice_id: str, expected_name: str = LOCKED_VOICE_NAME) -> str:
    name = fetch_voice_name(api_key, voice_id)
    if voice_id != LOCKED_VOICE_ID:
        raise RuntimeError(f"Configured voice ID {voice_id!r} is not the locked Renee voice.")
    if expected_name.lower() not in name.lower() and "renee" not in name.lower():
        raise RuntimeError(
            f"Voice ID {voice_id} resolved to {name!r}, expected name containing 'Renee'."
        )
    return name


__all__ = [
    "LOCKED_VOICE_ID",
    "LOCKED_VOICE_NAME",
    "LOCKED_MODEL_ID",
    "LOCKED_OUTPUT_FORMAT",
    "PronunciationResult",
    "load_pronunciation_aliases",
    "normalize_for_tts",
    "validate_locked_voice",
    "fetch_voice_name",
    "assert_voice_matches_lock",
]
