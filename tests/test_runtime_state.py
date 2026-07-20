from __future__ import annotations

import csv
import hashlib
import shutil
from pathlib import Path

from krishna_story_factory.config import load_settings
from krishna_story_factory.csv_store import (
    bootstrap_queue_state, ensure_csv_files, read_queue_state, reset_series_status,
)
from krishna_story_factory.pipeline import run_daily_story


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_legacy_status_migrates_to_runtime_queue(tmp_path: Path) -> None:
    (tmp_path / "input").mkdir()
    plan = tmp_path / "input" / "series_plan.csv"
    plan.write_text(
        "chapter_no,slug,title,source_reference,summary_seed,status\n"
        "001,one,One,Krishna Book Chapter 1,Seed,done\n"
        "002,two,Two,Krishna Book Chapter 1,Seed two,pending\n",
        encoding="utf-8",
    )
    before = _sha256(plan)
    bootstrap_queue_state(tmp_path)
    state = read_queue_state(tmp_path)
    assert [row["status"] for row in state] == ["done", "pending"]
    assert _sha256(plan) == before


def test_normal_test_run_never_mutates_static_plan(tmp_path: Path) -> None:
    source = Path(__file__).resolve().parents[1]
    project = tmp_path / "project"
    shutil.copytree(source, project, ignore=shutil.ignore_patterns(".git", ".venv", ".env", "output", "tracking", ".work", ".codex_validation_tmp", ".pytest_cache", "__pycache__"))
    ensure_csv_files(project)
    reset_series_status(project, ["001"], "pending")
    static = project / "input" / "series_plan.csv"
    master = project / "input" / "krishna_book_master_plan.csv"
    before = (_sha256(static), _sha256(master))
    result = run_daily_story(load_settings(project), mode="test", no_upload=True)
    assert result["status"] == "SUCCESS"
    assert (_sha256(static), _sha256(master)) == before


def test_no_pending_queue_returns_success_state(tmp_path: Path) -> None:
    source = Path(__file__).resolve().parents[1]
    project = tmp_path / "project"
    shutil.copytree(source, project, ignore=shutil.ignore_patterns(".git", ".venv", ".env", "output", "tracking", ".work", ".codex_validation_tmp", ".pytest_cache", "__pycache__"))
    ensure_csv_files(project)
    queue = project / "tracking" / "queue_state.csv"
    with queue.open("r", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle); fields = list(reader.fieldnames or []); rows = list(reader)
    for row in rows:
        row["status"] = "done"
    with queue.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields); writer.writeheader(); writer.writerows(rows)
    result = run_daily_story(load_settings(project), mode="test", no_upload=True)
    assert result["status"] == "NO_PENDING_STORY"
