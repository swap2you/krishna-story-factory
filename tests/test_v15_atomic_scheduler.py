"""Tests for V1.5 atomic/resumable production safety."""
from __future__ import annotations

import json
from pathlib import Path

from krishna_story_factory.csv_store import (
    acquire_pipeline_lock,
    reclaim_stale_processing,
    release_pipeline_lock,
    reset_processing_to_pending,
    update_plan_status,
)
from krishna_story_factory.models import PlanRow
from krishna_story_factory.stage_state import (
    ensure_package_layout,
    find_latest_recovery_run,
    quarantine_incomplete_output_packages,
    seed_state_from_recovery_artifacts,
)


def test_stale_lock_is_reclaimed(tmp_path: Path):
    lock = tmp_path / ".pipeline.lock"
    lock.write_text(json.dumps({"pid": 99999999, "started_at": "2020-01-01T00:00:00"}), encoding="utf-8")
    held = acquire_pipeline_lock(tmp_path, stale_after_sec=1)
    assert held.exists()
    meta = json.loads(held.read_text(encoding="utf-8"))
    assert meta["pid"] > 0
    release_pipeline_lock(held)
    assert not held.exists()


def test_quarantine_incomplete_output(tmp_path: Path):
    output = tmp_path / "output"
    incomplete = output / "008_partial"
    incomplete.mkdir(parents=True)
    (incomplete / "story.md").write_text("x", encoding="utf-8")
    (incomplete / "narration.mp3").write_bytes(b"abc")
    complete = output / "007_ok"
    complete.mkdir()
    for name in (
        "story.md",
        "narration.mp3",
        "story_poster.png",
        "coloring_page.png",
        "simple_coloring_page.png",
        "activity_sheet.pdf",
        "whatsapp_caption.txt",
        "manifest.json",
    ):
        (complete / name).write_bytes(b"ok")
    moved = quarantine_incomplete_output_packages(output, tmp_path / "q")
    assert len(moved) == 1
    assert not incomplete.exists()
    assert complete.exists()


def test_seed_recovery_marks_story_and_narration(tmp_path: Path):
    run = tmp_path / "work" / "stories" / "008" / "run1"
    run.mkdir(parents=True)
    (run / "story.md").write_text("# Story 008", encoding="utf-8")
    (run / "narration.mp3").write_bytes(b"x" * 1000)
    state = seed_state_from_recovery_artifacts(run, "008")
    assert state.is_complete("story")
    assert state.is_complete("narration")
    pkg = ensure_package_layout(run)
    assert (pkg / "story.md").is_file()
    assert (pkg / "narration.mp3").is_file()
    found = find_latest_recovery_run(tmp_path, "008")
    assert found == run
    (run / "COMPLETED").write_text("done", encoding="utf-8")
    assert find_latest_recovery_run(tmp_path, "008") is None


def test_scheduled_runner_does_not_tee_stderr():
    text = Path("scripts/run_daily_story_scheduled.ps1").read_text(encoding="utf-8")
    assert "Start-Process" in text
    assert "RedirectStandardError" in text
    assert "Tee-Object" not in text
    assert '*>&1 | Tee-Object' not in text
