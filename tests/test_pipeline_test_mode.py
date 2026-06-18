from __future__ import annotations

import csv
import shutil
from pathlib import Path

from krishna_story_factory.config import load_settings
from krishna_story_factory.csv_store import ensure_csv_files
from krishna_story_factory.pipeline import run_daily_story


def _mark_first_story_pending(project: Path) -> None:
    """Keep the test independent of local queue state in series_plan.csv."""
    path = project / "input" / "series_plan.csv"
    with path.open("r", newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames or [])
        rows = list(reader)
    if not rows:
        raise AssertionError("series_plan.csv has no rows for the isolated test copy.")
    rows[0]["status"] = "pending"
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def test_pipeline_generates_required_files_in_test_mode(tmp_path: Path, monkeypatch) -> None:
    source = Path(__file__).resolve().parents[1]
    project = tmp_path / "project"
    ignore = shutil.ignore_patterns(
        ".git",
        ".pytest_cache",
        ".codex_validation_tmp",
        ".cursor",
        ".venv",
        "output",
        "__pycache__",
        ".env",
        "krishna-story-factory-v1-buildpack",
    )
    shutil.copytree(source, project, ignore=ignore)

    ensure_csv_files(project)
    _mark_first_story_pending(project)
    settings = load_settings(project)
    result = run_daily_story(settings, mode="test", force=False)

    assert result["status"] == "SUCCESS"
    output_dir = Path(result["output_dir"])
    for filename in [
        "story.md",
        "audio_script.txt",
        "whatsapp_caption.txt",
        "activity_sheet.pdf",
        "story_card.png",
        "image_prompt.txt",
        "parent_notes.md",
        "manifest.json",
        "narration.mp3",
    ]:
        path = output_dir / filename
        assert path.exists(), filename
        assert path.stat().st_size > 0, filename

    with (project / "tracking" / "story_log.csv").open("r", newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    assert rows[-1]["quality_status"] == "PASS"
