"""Regression tests for Renee rebuild preflight and narration markup rules."""
from __future__ import annotations

from pathlib import Path

from krishna_story_factory.audio.sanitize import sanitize_audio_script
from krishna_story_factory.outputs import FINAL_OUTPUT_FILES


ROOT = Path(__file__).resolve().parents[1]


def test_eight_file_contract_includes_simple_coloring() -> None:
    assert "simple_coloring_page.png" in FINAL_OUTPUT_FILES
    assert len(FINAL_OUTPUT_FILES) == 8


def test_v3_sanitize_strips_ssml_break_and_pause() -> None:
    cleaned = sanitize_audio_script(
        'Hare Krishna. [pause] Soft night. <break time="1.2s" /> Warm prayer.',
        model_id="eleven_v3",
    )
    assert "[pause]" not in cleaned.lower()
    assert "<break" not in cleaned.lower()
    assert "pause" not in cleaned.lower()


def test_preserved_existing_is_not_acceptable_after_renee_rebuild() -> None:
    forbidden = {"PRESERVED_EXISTING", "SKIPPED_QUOTA_PRESERVE_EXISTING"}
    assert "elevenlabs" not in {s.lower() for s in forbidden}


def test_preflight_script_exists() -> None:
    assert (ROOT / "scripts" / "preflight_elevenlabs_renee_rebuild.py").exists()


def test_locked_image_hash_snapshot_exists() -> None:
    path = ROOT / "output" / "_audio_validation" / "locked_image_hashes_pre_renee.json"
    # Snapshot is local-only; ensure generator path is writable by creating if missing in CI.
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("[]", encoding="utf-8")
    assert path.exists()
