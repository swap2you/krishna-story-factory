from __future__ import annotations

import csv
import shutil
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest
from krishna_story_factory.config import load_settings
from krishna_story_factory.csv_store import already_completed_production_today, ensure_csv_files
from krishna_story_factory.pipeline import run_daily_story

pytestmark = pytest.mark.slow


def _write_story_log(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "date", "chapter_no", "slug", "title", "output_dir", "status", "quality_status",
        "whatsapp_status", "sender_type", "manifest_path", "created_at", "errors",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def test_test_preview_does_not_count_as_production_completion(tmp_path: Path) -> None:
    ensure_csv_files(tmp_path)
    today = datetime.now(ZoneInfo("America/New_York")).date().isoformat()
    _write_story_log(
        tmp_path / "tracking" / "story_log.csv",
        [{
            "date": today,
            "chapter_no": "005",
            "slug": "demo",
            "title": "Demo",
            "output_dir": str(tmp_path / ".work" / "test_preview" / "005_demo"),
            "status": "SUCCESS",
            "quality_status": "TEST_PASS",
            "whatsapp_status": "SKIPPED_DISABLED",
            "sender_type": "cloud",
            "manifest_path": "",
            "created_at": f"{today}T10:00:00",
            "errors": "",
        }],
    )
    assert already_completed_production_today(tmp_path, "America/New_York") is False


def test_normal_prod_skips_second_same_day_run(tmp_path: Path) -> None:
    source = Path(__file__).resolve().parents[1]
    project = tmp_path / "project"
    ignore = shutil.ignore_patterns(
        ".git", ".pytest_cache", ".codex_validation_tmp", ".cursor", ".venv", "output", "__pycache__", ".env"
    )
    shutil.copytree(source, project, ignore=ignore)
    ensure_csv_files(project)
    settings = load_settings(project)
    today = datetime.now(ZoneInfo(settings.app_timezone)).date().isoformat()
    _write_story_log(
        project / "tracking" / "story_log.csv",
        [{
            "date": today,
            "chapter_no": "004",
            "slug": "done-today",
            "title": "Done Today",
            "output_dir": str(project / "output" / "004_done-today"),
            "status": "SUCCESS",
            "quality_status": "PASS",
            "whatsapp_status": "SKIPPED_DISABLED",
            "sender_type": "cloud",
            "manifest_path": "",
            "created_at": f"{today}T10:00:00",
            "errors": "",
        }],
    )
    result = run_daily_story(settings, mode="prod", no_upload=True)
    assert result["status"] == "SKIPPED_ALREADY_COMPLETED_TODAY"


def test_noon_backup_noop_after_morning_success(tmp_path: Path) -> None:
    """Simulate successful 10:00 AM prod, then noon wrapper path (prod, no force, no upload)."""
    source = Path(__file__).resolve().parents[1]
    project = tmp_path / "project"
    ignore = shutil.ignore_patterns(
        ".git", ".pytest_cache", ".codex_validation_tmp", ".cursor", ".venv", "output", "__pycache__", ".env"
    )
    shutil.copytree(source, project, ignore=ignore)
    ensure_csv_files(project)
    settings = load_settings(project)
    today = datetime.now(ZoneInfo(settings.app_timezone)).date().isoformat()
    _write_story_log(
        project / "tracking" / "story_log.csv",
        [{
            "date": today,
            "chapter_no": "008",
            "slug": "morning-success",
            "title": "Morning Success",
            "output_dir": str(project / "output" / "008_morning-success"),
            "status": "SUCCESS",
            "quality_status": "PASS",
            "whatsapp_status": "SKIPPED_DISABLED",
            "sender_type": "cloud",
            "manifest_path": "",
            "created_at": f"{today}T10:00:00",
            "errors": "",
        }],
    )
    assert already_completed_production_today(project, settings.app_timezone) is True
    result = run_daily_story(settings, mode="prod", no_upload=True)
    assert result["status"] == "SKIPPED_ALREADY_COMPLETED_TODAY"
    # Isolated: no queue advancement side-effect beyond the skip path
    queue_path = project / "tracking" / "queue_state.csv"
    before = queue_path.read_text(encoding="utf-8")
    again = run_daily_story(settings, mode="prod", no_upload=True)
    assert again["status"] == "SKIPPED_ALREADY_COMPLETED_TODAY"
    assert queue_path.read_text(encoding="utf-8") == before


def test_noon_eligible_when_morning_did_not_run(tmp_path: Path) -> None:
    """If 10:00 did not complete, noon remains eligible for one production attempt (no APIs called here)."""
    ensure_csv_files(tmp_path)
    today = datetime.now(ZoneInfo("America/New_York")).date().isoformat()
    _write_story_log(
        tmp_path / "tracking" / "story_log.csv",
        [{
            "date": today,
            "chapter_no": "008",
            "slug": "failed-morning",
            "title": "Failed Morning",
            "output_dir": str(tmp_path / ".work" / "008_failed"),
            "status": "FAILED",
            "quality_status": "FAIL",
            "whatsapp_status": "SKIPPED_DISABLED",
            "sender_type": "cloud",
            "manifest_path": "",
            "created_at": f"{today}T10:00:00",
            "errors": "simulated miss",
        }],
    )
    assert already_completed_production_today(tmp_path, "America/New_York") is False


def test_force_overrides_same_day_guard(tmp_path: Path) -> None:
    source = Path(__file__).resolve().parents[1]
    project = tmp_path / "project"
    ignore = shutil.ignore_patterns(
        ".git", ".pytest_cache", ".codex_validation_tmp", ".cursor", ".venv", "output", "__pycache__", ".env"
    )
    shutil.copytree(source, project, ignore=ignore)
    ensure_csv_files(project)
    settings = load_settings(project)
    today = datetime.now(ZoneInfo(settings.app_timezone)).date().isoformat()
    _write_story_log(
        project / "tracking" / "story_log.csv",
        [{
            "date": today,
            "chapter_no": "004",
            "slug": "done-today",
            "title": "Done Today",
            "output_dir": str(project / "output" / "004_done-today"),
            "status": "SUCCESS",
            "quality_status": "PASS",
            "whatsapp_status": "SKIPPED_DISABLED",
            "sender_type": "cloud",
            "manifest_path": "",
            "created_at": f"{today}T10:00:00",
            "errors": "",
        }],
    )
    result = run_daily_story(settings, mode="prod", force=True, chapter="999", no_upload=True)
    assert result["status"] == "NO_PLAN_ROW"
