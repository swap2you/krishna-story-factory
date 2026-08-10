"""Governed private-story lock for Stories 021–022 (does not alter 001–020 release lock)."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "deploy" / "content" / "PRIVATE_STORY_LOCK_021_022.json"
RELEASE_PIN = ROOT / "deploy" / "content" / "RELEASE_CONTENT.json"

EXACT_EIGHT = {
    "story.md",
    "narration.mp3",
    "story_poster.png",
    "coloring_page.png",
    "simple_coloring_page.png",
    "activity_sheet.pdf",
    "whatsapp_caption.txt",
    "manifest.json",
}


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def test_production_release_pin_is_025() -> None:
    pin = json.loads(RELEASE_PIN.read_text(encoding="utf-8"))
    assert int(pin["public_story_max"]) == 25
    assert pin["tag"].startswith("bhava-content-001-025-")


def test_private_lock_ledger_schema() -> None:
    data = json.loads(LEDGER.read_text(encoding="utf-8"))
    assert data["schema"] == "bhava-private-story-lock-v1"
    assert int(data["public_story_max_production"]) == 25
    for story_no in ("021", "022"):
        row = data["stories"][story_no]
        assert row["human_listening_status"] == "USER_LISTENED_AND_ACCEPTED_ON_2026-08-04"
        assert len(row["audio_sha256"]) == 64
        assert set(row["exact_eight"]) == EXACT_EIGHT
        assert row["audio_sha256"] == row["exact_eight"]["narration.mp3"]
        for name in row["immutable_without_approval"]:
            assert name in row["exact_eight"]
            assert len(row["exact_eight"][name]) == 64


@pytest.mark.local_runtime
def test_private_lock_ledger_matches_local_packages_when_present() -> None:
    """Fail on unauthorized drift when local packages exist (operator workstation)."""
    data = json.loads(LEDGER.read_text(encoding="utf-8"))
    checked = 0
    drifts = []
    for story_no, row in data["stories"].items():
        pkg = ROOT / "output" / f"{story_no}_{row['slug']}"
        if not pkg.is_dir():
            continue
        for name, expected in row["exact_eight"].items():
            path = pkg / name
            assert path.is_file(), f"missing {path}"
            actual = _sha(path)
            checked += 1
            if actual != expected.upper():
                drifts.append(f"{story_no}/{name}: expected {expected} got {actual}")
    if checked == 0:
        pytest.skip("Stories 021/022 packages not present in this checkout")
    assert not drifts, "Unauthorized private-story lock drift:\n" + "\n".join(drifts)
