"""Build web-asset files for a single story package.

Reads the package's story.md + manifest.json and writes clean, public-safe
derivatives into data/web-assets/<story_no>/. Exact-eight package files are
never modified.
"""
from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

from .recommended_playback_rates import recommended_playback_rate_for_story
from .reviewed_shlokas import shlokas_payload_for_story
from .reviewed_sources import source_links_for_story
from .story_parser import parse_story_markdown
from .waveform import write_peaks_json

# Files hashed into web_manifest.assets (schema-required set).
_MANIFEST_ASSET_NAMES = (
    "reader.md",
    "reader.txt",
    "source_links.json",
    "reflections.json",
    "shlokas.json",
    "sync.json",
    "waveform.json",
)


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_file(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _asset_meta(path: Path) -> dict[str, int | str]:
    data = path.read_bytes()
    return {"sha256": _sha256_bytes(data), "bytes": len(data)}


def _extract_lessons(reader_md: str) -> list[dict]:
    """Seed reflections from Five Lessons / Devotional Meaning sections."""
    reflections: list[dict] = []
    lines = reader_md.splitlines()
    in_lessons = False
    in_meaning = False
    meaning_text: list[str] = []

    for line in lines:
        stripped = line.strip()

        if re.match(r"^#+\s+Five\s+Lessons", stripped, re.IGNORECASE):
            in_lessons = True
            in_meaning = False
            continue
        if re.match(r"^#+\s+Devotional\s+Meaning", stripped, re.IGNORECASE):
            in_meaning = True
            in_lessons = False
            continue
        if re.match(r"^#+\s+", stripped) and (in_lessons or in_meaning):
            in_lessons = False
            in_meaning = False
            continue

        if in_lessons:
            m = re.match(r"^\d+\.\s+(.+)", stripped)
            if m:
                reflections.append({
                    "text": m.group(1).strip(),
                    "source": "five_lessons",
                    "provenance": "needs_review",
                    "source_type": "package_seed",
                })
        elif in_meaning:
            if stripped:
                meaning_text.append(stripped)

    if meaning_text:
        reflections.insert(0, {
            "text": " ".join(meaning_text),
            "source": "devotional_meaning",
            "provenance": "needs_review",
            "source_type": "package_seed",
        })

    return reflections


def _placeholder_waveform(dest: Path) -> dict:
    """Honest empty waveform when narration.mp3 is absent from the package."""
    payload = {
        "bars": 0,
        "method": "none",
        "confidence": 0,
        "note": "Narration audio not present at build time; waveform peaks unavailable.",
        "peaks": [],
    }
    dest.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload


def build_web_assets_for_package(
    package_path: Path,
    story_no: str,
    output_root: Path,
    recommended_playback_rate: float | None = None,
) -> Path:
    """Build web-asset files for one story package and return the output directory."""
    if recommended_playback_rate is None:
        recommended_playback_rate = recommended_playback_rate_for_story(story_no)
    story_md_path = package_path / "story.md"
    manifest_path = package_path / "manifest.json"
    narration_path = package_path / "narration.mp3"

    raw_md = story_md_path.read_text(encoding="utf-8")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    parsed = parse_story_markdown(raw_md)

    dest = output_root / story_no
    dest.mkdir(parents=True, exist_ok=True)

    (dest / "reader.md").write_text(parsed.reader_md, encoding="utf-8")
    (dest / "reader.txt").write_text(parsed.reader_txt, encoding="utf-8")
    (dest / "narration.txt").write_text(parsed.narration_txt, encoding="utf-8")

    source_links = source_links_for_story(story_no, manifest)
    (dest / "source_links.json").write_text(
        json.dumps(source_links, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    reflections = _extract_lessons(parsed.reader_md)
    (dest / "reflections.json").write_text(
        json.dumps(reflections, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    shlokas = shlokas_payload_for_story(story_no)
    (dest / "shlokas.json").write_text(
        json.dumps(shlokas, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    sync = {
        "method": "none",
        "confidence": 0,
        "cues": [],
        "status": "needs_alignment",
    }
    (dest / "sync.json").write_text(
        json.dumps(sync, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    waveform_path = dest / "waveform.json"
    if narration_path.is_file():
        write_peaks_json(narration_path, waveform_path)
    else:
        _placeholder_waveform(waveform_path)

    assets_meta = {
        name: _asset_meta(dest / name)
        for name in _MANIFEST_ASSET_NAMES
        if (dest / name).is_file()
    }

    shloka_status = str(shlokas.get("status") or "pending")
    web_manifest = {
        "story_no": story_no,
        "package_manifest_sha256": _sha256_file(manifest_path),
        "story_md_sha256": _sha256_file(story_md_path),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "recommended_playback_rate": float(recommended_playback_rate),
        "assets": assets_meta,
        # Operator convenience fields (schema allows additionalProperties).
        "rights": manifest.get("rights") or manifest.get("publication") or {},
        "statuses": {
            "reader": "clean" if not parsed.has_internal_leak_markers else "has_leak_markers",
            "narration": "present" if parsed.narration_txt else "missing",
            "reflections": "seeded" if reflections else "empty",
            "shlokas": shloka_status,
            "sync": "needs_alignment",
            "source_links": "seeded" if source_links else "empty",
            "waveform": "present" if narration_path.is_file() else "missing_audio",
        },
    }
    (dest / "web_manifest.json").write_text(
        json.dumps(web_manifest, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    return dest
