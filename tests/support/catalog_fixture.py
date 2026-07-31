"""Deterministic synthetic story packages for portal API contract tests.

The real Stories 001-009 are large devotional media that are never committed, so
tests that only need "a publishable catalog of N stories" build one here instead.
Byte content is fixed, so repeated runs index identically.
"""
from __future__ import annotations

import json
from pathlib import Path

REQUIRED_PACKAGE_FILES = (
    "story.md",
    "narration.mp3",
    "story_poster.png",
    "coloring_page.png",
    "simple_coloring_page.png",
    "activity_sheet.pdf",
    "whatsapp_caption.txt",
    "manifest.json",
)

STORY_BODY = (
    "# Fixture story\n"
    "\n"
    "This deterministic reader body stands in for devotional narrative text so "
    "catalog and reader contracts can be verified without shipping media.\n"
    "\n"
    "## Rights and Credits\n"
    "\n"
    "Bhāva design and publication © Svarna Gauranga Das · Dauji Publication\n"
)


def write_package(
    root: Path,
    story_no: str,
    *,
    publishable: bool = True,
    quality: str = "PASS",
    audio_stale: bool = False,
    generation_verified: bool = True,
    include_all_files: bool = True,
) -> Path:
    folder = root / f"{story_no}_fixture"
    folder.mkdir(parents=True, exist_ok=True)
    names = (
        list(REQUIRED_PACKAGE_FILES)
        if include_all_files
        else ["manifest.json", "story.md"]
    )
    for name in names:
        if name == "manifest.json":
            continue
        if name == "story.md":
            (folder / name).write_text(STORY_BODY, encoding="utf-8")
        else:
            (folder / name).write_bytes(b"fixture")
    manifest = {
        "chapter_no": story_no,
        "slug": f"fixture-{story_no}",
        "title": f"Fixture {story_no}",
        "publishable": publishable,
        "quality": {"status": quality, "errors": [], "warnings": []},
        "audio": {
            "generation_verified": generation_verified,
            "audio_stale": audio_stale,
        },
    }
    (folder / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    return folder


def build_public_catalog(root: Path, *, count: int = 9) -> Path:
    """Materialise Stories 001..count as publishable exact-eight packages."""
    root.mkdir(parents=True, exist_ok=True)
    for number in range(1, count + 1):
        write_package(root, f"{number:03d}")
    return root
