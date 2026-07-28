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


def test_story_010_absent_from_output() -> None:
    assert not list((ROOT / "output").glob("010_*"))
