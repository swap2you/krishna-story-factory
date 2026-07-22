"""Unit tests for latest-run summary writer."""
from __future__ import annotations

import json
from pathlib import Path

from krishna_story_factory.run_summary import write_latest_run_summary


def test_write_latest_run_summary(tmp_path: Path) -> None:
    payload = write_latest_run_summary(
        tmp_path,
        started_at="2026-07-22T06:00:00-04:00",
        completed_at="2026-07-22T06:12:00-04:00",
        status="SUCCESS",
        chapter_no="007",
        title="Kamsa Begins His Persecutions",
        package_local_path=str(tmp_path / "output" / "007_x"),
        drive_folder_url="https://drive.google.com/drive/folders/abc",
        provider="openai",
        audio_duration=200.5,
        publishable=True,
        exact_eight_files=True,
        queue_advanced=True,
        next_pending="008",
    )
    data = json.loads((tmp_path / "tracking" / "latest_run_summary.json").read_text(encoding="utf-8"))
    assert data["chapter_no"] == "007"
    assert data["drive_folder_url"].endswith("abc")
    assert data["queue_advanced"] is True
    text = (tmp_path / "logs" / "latest_run_summary.txt").read_text(encoding="utf-8")
    assert "Drive folder:" in text
    assert payload["status"] == "SUCCESS"
