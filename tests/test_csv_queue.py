from __future__ import annotations

import csv
import shutil
from pathlib import Path

from krishna_story_factory.config import load_settings
from krishna_story_factory.csv_store import ensure_csv_files, read_next_pending, reset_series_status
from krishna_story_factory.whatsapp.recipients import load_active_recipients

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _read_series_rows() -> list[dict[str, str]]:
    path = PROJECT_ROOT / "input" / "series_plan.csv"
    with path.open("r", newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def _read_recipient_rows() -> list[dict[str, str]]:
    path = PROJECT_ROOT / "input" / "whatsapp_recipients.csv"
    with path.open("r", newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def test_series_plan_parses_complete_static_plan() -> None:
    rows = _read_series_rows()
    assert len(rows) == 93
    assert "status" not in rows[0]


def test_next_pending_story_is_005_after_004_done(tmp_path: Path) -> None:
    shutil.copytree(PROJECT_ROOT / "input", tmp_path / "input")
    ensure_csv_files(tmp_path)
    reset_series_status(tmp_path, ["003", "004"], status="done")
    plan = read_next_pending(tmp_path)
    assert plan is not None
    assert plan.chapter_no == "005"
    assert plan.slug == "prayers-by-the-demigods-for-lord-krishna-in-the-womb"


def test_whatsapp_recipients_parses_two_rows() -> None:
    rows = _read_recipient_rows()
    assert len(rows) == 2
    assert rows[0]["phone_e164"]
    assert rows[1]["phone_e164"]


def test_active_opted_in_recipients_loadable() -> None:
    settings = load_settings(PROJECT_ROOT)
    active = load_active_recipients(settings.whatsapp_recipients_csv)
    assert len(active) >= 1
    assert all(r.opt_in for r in active)
    assert all(r.status == "active" for r in active)
