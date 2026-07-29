"""Guard: Stories 001–009 remain byte-identical to the launch safety baseline."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
BASELINE = ROOT / "docs" / "releases" / "BHAVA_STORIES_LAUNCH_SAFETY_BASELINE.json"


@pytest.mark.parametrize("chapter", [f"{n:03d}" for n in range(1, 10)])
def test_launch_story_hashes_unchanged(chapter: str) -> None:
    data = json.loads(BASELINE.read_text(encoding="utf-8"))
    entry = data["stories"][chapter]
    folder = ROOT / "output" / entry["folder"]
    assert folder.is_dir(), folder
    for name, expected in entry["file_sha256"].items():
        path = folder / name
        assert path.is_file(), path
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        assert actual == expected, f"{chapter}/{name} changed"


@pytest.mark.parametrize("chapter", [f"{n:03d}" for n in range(1, 10)])
def test_pre_copyright_archive_preserved(chapter: str) -> None:
    data = json.loads(BASELINE.read_text(encoding="utf-8"))
    entry = data["stories"][chapter]
    archive_rel = entry.get("archive_2_0") or entry.get("archive") or f"output/_archive/pre-copyright/{chapter}/2.0"
    archive = ROOT / archive_rel
    assert archive.is_dir(), f"Missing pre-copyright archive: {archive}"
    prior = entry.get("pre_copyright_sha256") or {}
    assert prior, f"Baseline missing pre_copyright_sha256 for {chapter}"
    for name, expected in prior.items():
        path = archive / name
        assert path.is_file(), path
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        assert actual == expected.lower(), f"Archive drift {chapter}/{name}"


@pytest.mark.parametrize("chapter", [f"{n:03d}" for n in range(1, 10)])
def test_prior_2_1_0_archive_preserved(chapter: str) -> None:
    data = json.loads(BASELINE.read_text(encoding="utf-8"))
    entry = data["stories"][chapter]
    archive_rel = entry.get("archive_2_1_0") or f"output/_archive/pre-copyright/{chapter}/2.1.0-copyright"
    archive = ROOT / archive_rel
    assert archive.is_dir(), archive
    prior = entry.get("prior_2_1_0_sha256") or {}
    assert prior, f"Baseline missing prior_2_1_0_sha256 for {chapter}"
    for name, expected in prior.items():
        path = archive / name
        assert path.is_file(), path
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        assert actual == expected.lower(), f"2.1.0 archive drift {chapter}/{name}"


def test_story_010_is_a_complete_exact_eight_package() -> None:
    packages = list((ROOT / "output").glob("010_*"))
    assert len(packages) == 1
    expected = {
        "story.md",
        "narration.mp3",
        "story_poster.png",
        "coloring_page.png",
        "simple_coloring_page.png",
        "activity_sheet.pdf",
        "whatsapp_caption.txt",
        "manifest.json",
    }
    actual = {path.name for path in packages[0].iterdir() if path.is_file()}
    assert actual == expected
