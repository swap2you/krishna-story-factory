"""Non-skipping CI tests against committed pilot release hash evidence.

These always run in CI even when local output/ packages are absent.
"""
from __future__ import annotations

import json
from pathlib import Path

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

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_PATH = ROOT / "docs" / "releases" / "PILOT_001_006_HASHES.json"

DRIVE_FOLDER_IDS = {
    "001": "1_7R1uj_WtW0CfuhfMAz_d3FSF1zsHbo-",
    "002": "1pr9ZMwnzE8bx7mgreAguduQFDzc8XC0V",
    "003": "1wXrCGATPxzDpafBbQ9e_y_A3g4JkwcSn",
    "004": "1ngcf6RZ2gxClVOt8_njKp-dorSEyaAs-",
    "005": "1qqox6hHQzMR3HQU12TQv2xRb2IUlbXU3",
    "006": "10SatVqh_Sf1sgn3wr0xFLKlVYSX6Wa15",
}


def _load_evidence() -> dict:
    assert EVIDENCE_PATH.exists(), f"Missing committed evidence file: {EVIDENCE_PATH}"
    return json.loads(EVIDENCE_PATH.read_text(encoding="utf-8"))


def test_pilot_hash_evidence_six_stories_exact_eight_hashes() -> None:
    data = _load_evidence()
    stories = data.get("stories") or {}
    assert set(stories) == {"001", "002", "003", "004", "005", "006"}
    assert data.get("validation_timestamp"), "validation_timestamp required"
    for chapter, entry in stories.items():
        files = entry.get("files") or {}
        assert set(files) == set(REQUIRED_FILES), chapter
        assert entry.get("exact_file_count") == 8
        for name, digest in files.items():
            assert isinstance(digest, str) and len(digest) == 64 and digest == digest.upper(), (
                f"{chapter}/{name} missing or invalid SHA-256"
            )
        assert entry.get("narration_source_sha"), f"{chapter} narration_source_sha missing"
        assert len(str(entry["narration_source_sha"])) == 64
        audio = entry.get("audio") or {}
        assert audio.get("provider"), f"{chapter} audio.provider missing"
        assert audio.get("model"), f"{chapter} audio.model missing"
        assert audio.get("voice"), f"{chapter} audio.voice missing"
        assert audio.get("duration_seconds"), f"{chapter} audio.duration_seconds missing"
        assert entry.get("drive_folder_id"), f"{chapter} drive_folder_id missing"


def test_pilot_hash_evidence_story_006_locked_unchanged() -> None:
    data = _load_evidence()
    lock = data.get("story_006_lock")
    assert isinstance(lock, dict) and set(lock) == set(REQUIRED_FILES)
    assert data["stories"]["006"]["files"] == lock


def test_pilot_hash_evidence_drive_folder_ids_present() -> None:
    data = _load_evidence()
    for chapter, folder_id in DRIVE_FOLDER_IDS.items():
        assert data["stories"][chapter]["drive_folder_id"] == folder_id


def test_pilot_hash_evidence_narration_and_manifest_populated() -> None:
    data = _load_evidence()
    for chapter, entry in data["stories"].items():
        assert entry["files"]["manifest.json"]
        assert entry["files"]["narration.mp3"]
        assert entry["narration_source_sha"]
        assert entry["audio"]["provider"] not in {"", "preserved", "unknown_preserved"}
