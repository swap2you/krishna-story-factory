"""Fail if Stories 001–007 packages or queue 008 drift from the V1.1 safety baseline."""
from __future__ import annotations

import csv
import hashlib
import json
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
BASELINE_FILE = ROOT / "docs" / "releases" / "BHAVA_V1_1_SAFETY_BASELINE.json"
QUEUE = ROOT / "tracking" / "queue_state.csv"
ENV_EXAMPLE = ROOT / ".env.example"

REQUIRED_FILES = (
    "story.md",
    "narration.mp3",
    "story_poster.png",
    "coloring_page.png",
    "simple_coloring_page.png",
    "activity_sheet.pdf",
    "whatsapp_caption.txt",
    "manifest.json",
)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().lower()


@pytest.fixture(scope="module")
def baseline() -> dict:
    if not BASELINE_FILE.is_file():
        pytest.skip("BHAVA_V1_1_SAFETY_BASELINE.json not present.")
    data = json.loads(BASELINE_FILE.read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    return data


def test_stories_001_007_file_hashes_match_baseline(baseline: dict) -> None:
    stories = baseline.get("stories")
    assert isinstance(stories, dict) and stories, "Baseline must include stories map."

    for story_no in ("001", "002", "003", "004", "005", "006", "007"):
        meta = stories.get(story_no)
        assert isinstance(meta, dict), f"Baseline missing story {story_no}."
        package_folder = meta.get("package_folder")
        files = meta.get("files")
        assert isinstance(package_folder, str) and package_folder
        assert isinstance(files, dict) and files

        package_dir = ROOT / "output" / package_folder
        assert package_dir.is_dir(), f"Package folder missing: {package_dir}"

        for filename in REQUIRED_FILES:
            expected = files.get(filename)
            assert isinstance(expected, str) and expected, (
                f"Baseline missing hash for {story_no}/{filename}"
            )
            artifact = package_dir / filename
            assert artifact.is_file(), f"Required package file missing: {artifact}"
            actual = _sha256(artifact)
            assert actual == expected.lower(), (
                f"Output package changed for Story {story_no}: {filename} "
                f"(expected {expected.lower()}, got {actual})"
            )


def test_queue_008_still_pending(baseline: dict) -> None:
    assert baseline.get("queue_008_status") == "pending"
    if not QUEUE.is_file():
        pytest.skip("Runtime queue_state.csv not present in this environment.")
    rows = list(csv.DictReader(QUEUE.open(encoding="utf-8")))
    by_chapter = {str(row["chapter_no"]).zfill(3): row["status"] for row in rows}
    assert by_chapter.get("008") == "pending", (
        f"Story 008 must remain pending; found status={by_chapter.get('008')!r}"
    )


def test_factory_actions_not_forced_true_in_env_example() -> None:
    if not ENV_EXAMPLE.is_file():
        pytest.skip(".env.example not present.")
    text = ENV_EXAMPLE.read_text(encoding="utf-8")
    # Fail only when the example forces the flag true (assignment, not a comment alone).
    forced = re.search(
        r"(?im)^\s*BHAVA_FACTORY_ACTIONS_ENABLED\s*=\s*(true|1|yes|on)\s*(?:#.*)?$",
        text,
    )
    assert forced is None, (
        ".env.example must not force BHAVA_FACTORY_ACTIONS_ENABLED=true"
    )
