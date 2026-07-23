"""Build web-asset files for a single story package.

Reads the package's story.md + manifest.json and writes clean, public-safe
derivatives into data/web-assets/<story_no>/.
"""
from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

from .story_parser import parse_story_markdown


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


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
                })
        elif in_meaning:
            if stripped:
                meaning_text.append(stripped)

    if meaning_text:
        reflections.insert(0, {
            "text": " ".join(meaning_text),
            "source": "devotional_meaning",
            "provenance": "needs_review",
        })

    return reflections


def _extract_source_links(manifest: dict) -> list[dict]:
    links: list[dict] = []
    for key in ("source_reference", "scripture_reference"):
        val = manifest.get(key)
        if val:
            links.append({
                "label": key.replace("_", " ").title(),
                "reference": val,
                "permissions_status": "needs-review",
            })
    return links


def build_web_assets_for_package(
    package_path: Path,
    story_no: str,
    output_root: Path,
) -> Path:
    """Build web-asset files for one story package and return the output directory."""
    story_md_path = package_path / "story.md"
    manifest_path = package_path / "manifest.json"

    raw_md = story_md_path.read_text(encoding="utf-8")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    parsed = parse_story_markdown(raw_md)

    dest = output_root / story_no
    dest.mkdir(parents=True, exist_ok=True)

    (dest / "reader.md").write_text(parsed.reader_md, encoding="utf-8")
    (dest / "reader.txt").write_text(parsed.reader_txt, encoding="utf-8")
    (dest / "narration.txt").write_text(parsed.narration_txt, encoding="utf-8")

    source_links = _extract_source_links(manifest)
    (dest / "source_links.json").write_text(
        json.dumps(source_links, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    reflections = _extract_lessons(parsed.reader_md)
    (dest / "reflections.json").write_text(
        json.dumps(reflections, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    shlokas = {"shlokas": [], "status": "pending"}
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

    web_manifest = {
        "story_no": story_no,
        "package_sha": _sha256(manifest_path),
        "built_at": datetime.now(timezone.utc).isoformat(),
        "statuses": {
            "reader": "clean" if not parsed.has_internal_leak_markers else "has_leak_markers",
            "narration": "present" if parsed.narration_txt else "missing",
            "reflections": "seeded" if reflections else "empty",
            "shlokas": "pending",
            "sync": "needs_alignment",
            "source_links": "seeded" if source_links else "empty",
        },
    }
    (dest / "web_manifest.json").write_text(
        json.dumps(web_manifest, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    return dest
