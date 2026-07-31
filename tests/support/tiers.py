"""Availability probes for Bhāva test tiers.

``production_security`` needs no data and always runs. The three data-dependent
tiers below are probed by this module:

``content_release``
    Public Stories 001-009 (exact-eight files each), provisioned in CI by
    downloading and verifying the approved ``bhava-content-001-009-v1`` GitHub
    Release, and present naturally on an operator workstation.

``local_archive``
    Pre-copyright drafts under ``output/_archive/``. These are superseded
    devotional text that was never published and must not be published, so they
    exist only on operator workstations.

``local_runtime``
    Mutable scheduler/queue state under ``tracking/``.

``production_security``
    Needs no data; always runs.

Setting ``BHAVA_REQUIRE_CONTENT=1`` / ``BHAVA_REQUIRE_ARCHIVES=1`` /
``BHAVA_REQUIRE_RUNTIME=1`` turns a missing tier into a hard error. CI jobs that
are responsible for provisioning a tier set the matching flag, so a broken
download can never quietly downgrade the job into a pile of skips.
"""
from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "output"
ARCHIVE = OUTPUT / "_archive" / "pre-copyright"
QUEUE = ROOT / "tracking" / "queue_state.csv"

PUBLIC_STORIES = tuple(f"{n:03d}" for n in range(1, 10))
EXACT_EIGHT = frozenset(
    {
        "story.md",
        "narration.mp3",
        "story_poster.png",
        "coloring_page.png",
        "simple_coloring_page.png",
        "activity_sheet.pdf",
        "whatsapp_caption.txt",
        "manifest.json",
    }
)
ARCHIVE_VERSIONS = ("2.0", "2.1.0-copyright")


def _flag(name: str) -> bool:
    return os.getenv(name, "").strip().lower() in {"1", "true", "yes", "on"}


def public_package(story_no: str) -> Path | None:
    matches = sorted(OUTPUT.glob(f"{story_no}_*"))
    return matches[0] if len(matches) == 1 else None


def missing_public_content() -> list[str]:
    """Report every reason the public content tier is not usable."""
    if not OUTPUT.is_dir():
        return [f"{OUTPUT} does not exist"]
    problems: list[str] = []
    for story_no in PUBLIC_STORIES:
        folder = public_package(story_no)
        if folder is None:
            problems.append(f"Story {story_no}: package directory missing or ambiguous")
            continue
        absent = sorted(name for name in EXACT_EIGHT if not (folder / name).is_file())
        if absent:
            problems.append(f"Story {story_no}: missing {', '.join(absent)}")
    return problems


def missing_local_archives() -> list[str]:
    problems: list[str] = []
    for story_no in PUBLIC_STORIES:
        for version in ARCHIVE_VERSIONS:
            folder = ARCHIVE / story_no / version
            if not folder.is_dir():
                problems.append(f"{folder.relative_to(ROOT).as_posix()} missing")
    return problems


def missing_runtime_state() -> list[str]:
    if not QUEUE.is_file():
        return [f"{QUEUE.relative_to(ROOT).as_posix()} missing"]
    return []


TIERS = {
    "content_release": (
        missing_public_content,
        "BHAVA_REQUIRE_CONTENT",
        "public Stories 001-009 release content",
    ),
    "local_archive": (
        missing_local_archives,
        "BHAVA_REQUIRE_ARCHIVES",
        "private pre-copyright archives",
    ),
    "local_runtime": (
        missing_runtime_state,
        "BHAVA_REQUIRE_RUNTIME",
        "operator runtime queue state",
    ),
}


def tier_status(marker: str) -> tuple[list[str], bool, str]:
    """Return (problems, required, human label) for a tier marker."""
    probe, flag, label = TIERS[marker]
    return probe(), _flag(flag), label
