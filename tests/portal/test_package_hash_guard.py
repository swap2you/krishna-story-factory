"""Detect any package drift after lock hashes are recorded."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
LOCK_FILE = ROOT / "data" / "catalog" / "locked_story_hashes.json"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def test_locked_story_packages_match_recorded_hashes() -> None:
    if not LOCK_FILE.exists():
        pytest.skip("No portal lock hash record has been created.")
    lock_data = json.loads(LOCK_FILE.read_text(encoding="utf-8"))
    stories = lock_data.get("stories")
    assert isinstance(stories, dict) and stories, (
        "Lock record must contain a non-empty 'stories' map "
        "(do not fall back to top-level metadata keys)."
    )
    for story_no, files in stories.items():
        assert isinstance(files, dict), f"Story {story_no} must map filenames to hashes."
        package_dirs = list((ROOT / "output").glob(f"{str(story_no).zfill(3)}_*"))
        assert len(package_dirs) == 1, f"Locked Story {story_no} package is missing or ambiguous."
        for filename, expected_hash in files.items():
            artifact = package_dirs[0] / filename
            assert artifact.is_file(), f"Locked artifact missing: {artifact}"
            assert _sha256(artifact) == expected_hash.upper(), f"Locked artifact changed: {artifact}"
