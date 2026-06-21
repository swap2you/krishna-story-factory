from __future__ import annotations

import csv
import shutil
from pathlib import Path

from krishna_story_factory.config import load_settings
from krishna_story_factory.csv_store import ensure_csv_files
from krishna_story_factory.outputs import FINAL_OUTPUT_FILES
from krishna_story_factory.pipeline import run_daily_story


def _mark_first_story_pending(project: Path) -> None:
    path = project / "input" / "series_plan.csv"
    with path.open("r", newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames or [])
        rows = list(reader)
    rows[0]["status"] = "pending"
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def test_pipeline_generates_required_files_in_test_mode(tmp_path: Path) -> None:
    source = Path(__file__).resolve().parents[1]
    project = tmp_path / "project"
    ignore = shutil.ignore_patterns(
        ".git", ".pytest_cache", ".codex_validation_tmp", ".cursor", ".venv", "output", "__pycache__", ".env"
    )
    shutil.copytree(source, project, ignore=ignore)
    ensure_csv_files(project)
    _mark_first_story_pending(project)
    settings = load_settings(project)
    result = run_daily_story(settings, mode="test", no_upload=True)
    assert result["status"] == "SUCCESS"
    output_dir = Path(result["output_dir"])
    for filename in FINAL_OUTPUT_FILES:
        path = output_dir / filename
        assert path.exists(), filename
        assert path.stat().st_size > 0, filename
    extras = [p.name for p in output_dir.iterdir() if p.is_file() and p.name not in FINAL_OUTPUT_FILES]
    assert not extras, extras
