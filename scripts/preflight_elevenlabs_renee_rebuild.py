"""Preflight ElevenLabs Renee full-audio rebuild for Stories 001–005.

Exits with BLOCKED_ELEVENLABS_QUOTA when available characters are insufficient.
Does not overwrite narration.mp3 files.
"""
from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    from dotenv import load_dotenv
    import os

    from krishna_story_factory.audio.pronunciation import (
        LOCKED_MODEL_ID,
        LOCKED_OUTPUT_FORMAT,
        LOCKED_VOICE_ID,
        LOCKED_VOICE_NAME,
        normalize_for_tts,
    )
    from krishna_story_factory.audio.sanitize import sanitize_audio_script
    from krishna_story_factory.content.story_format_v2 import extract_section, word_count

    load_dotenv(ROOT / ".env")
    api_key = os.getenv("ELEVENLABS_API_KEY", "").strip()
    voice_id = os.getenv("ELEVENLABS_VOICE_ID", "").strip() or LOCKED_VOICE_ID
    voice_name = os.getenv("ELEVENLABS_VOICE_NAME", "").strip() or LOCKED_VOICE_NAME
    model_id = os.getenv("ELEVENLABS_MODEL_ID", "").strip() or LOCKED_MODEL_ID
    output_format = os.getenv("ELEVENLABS_OUTPUT_FORMAT", "").strip() or LOCKED_OUTPUT_FORMAT
    dict_id = os.getenv("ELEVENLABS_PRONUNCIATION_DICTIONARY_ID", "").strip()
    dict_ver = os.getenv("ELEVENLABS_PRONUNCIATION_DICTIONARY_VERSION_ID", "").strip()

    if voice_id != LOCKED_VOICE_ID:
        report = {"status": "BLOCKED_VOICE_MISMATCH", "configured_voice_id": voice_id}
        print(json.dumps(report, indent=2))
        return 2

    headers = {"xi-api-key": api_key}
    voice = requests.get(f"https://api.elevenlabs.io/v1/voices/{voice_id}", headers=headers, timeout=30)
    if voice.status_code >= 400:
        print(json.dumps({"status": "BLOCKED_VOICE_LOOKUP", "detail": voice.text[:300]}, indent=2))
        return 2
    api_name = str(voice.json().get("name") or "")
    if "renee" not in api_name.lower():
        print(json.dumps({"status": "BLOCKED_VOICE_MISMATCH", "api_name": api_name}, indent=2))
        return 2

    sub = requests.get("https://api.elevenlabs.io/v1/user/subscription", headers=headers, timeout=30)
    if sub.status_code >= 400:
        print(json.dumps({"status": "BLOCKED_SUBSCRIPTION_LOOKUP", "detail": sub.text[:300]}, indent=2))
        return 2
    data = sub.json()
    used = int(data.get("character_count") or 0)
    limit = int(data.get("character_limit") or 0)
    available = max(0, limit - used)
    reset_unix = data.get("next_character_count_reset_unix")
    reset_iso = (
        datetime.fromtimestamp(int(reset_unix), tz=timezone.utc).isoformat()
        if reset_unix
        else ""
    )

    required = 0
    per_story = []
    for folder in sorted((ROOT / "output").iterdir()):
        if not folder.is_dir() or not re.match(r"^00[1-5]_", folder.name):
            continue
        text = (folder / "story.md").read_text(encoding="utf-8")
        parts = []
        for heading in (
            "Recap",
            "Series Introduction",
            "Main Story",
            "Devotional Meaning",
            "Five Lessons",
            "Bedtime Prayer",
            "Next Story Preview",
            "Moral",
            "Takeaway",
            "Bedtime Reflection",
        ):
            sec = extract_section(text, heading)
            if sec:
                parts.append(sec)
        raw = "\n\n".join(parts)
        clean = sanitize_audio_script(
            normalize_for_tts(raw, project_root=ROOT).audio_text,
            model_id=model_id,
        )
        chars = len(clean)
        required += chars
        per_story.append({"folder": folder.name, "chars": chars, "words": word_count(clean)})

    required_with_margin = int(required * 1.10)
    shortfall = max(0, required_with_margin - available)
    dict_ok = bool(dict_id)
    status = "READY" if available >= required_with_margin and dict_ok else "BLOCKED_ELEVENLABS_QUOTA"
    if available >= required_with_margin and not dict_ok:
        status = "BLOCKED_PRONUNCIATION_DICTIONARY_MISSING"

    report = {
        "status": status,
        "voice_name": api_name,
        "voice_id": voice_id,
        "configured_voice_name": voice_name,
        "model": model_id,
        "output_format": output_format,
        "available_characters": available,
        "required_characters": required,
        "required_with_10pct_margin": required_with_margin,
        "shortfall": shortfall,
        "next_character_reset": reset_iso,
        "pronunciation_dictionary_id_configured": dict_ok,
        "pronunciation_dictionary_version_id_configured": bool(dict_ver),
        "stories": per_story,
        "note": "Narration files were not modified by this preflight.",
    }
    out = ROOT / "output" / "_audio_validation" / "renee_rebuild_preflight.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if status == "READY" else 3


if __name__ == "__main__":
    raise SystemExit(main())
