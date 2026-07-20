from __future__ import annotations

import csv
from pathlib import Path

from krishna_story_factory.config import load_settings
from krishna_story_factory.csv_store import read_next_pending
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


def test_next_pending_story_is_004_after_003_done() -> None:
    plan = read_next_pending(PROJECT_ROOT)
    assert plan is not None
    assert plan.chapter_no == "004"
    assert plan.slug == "narada-warns-kamsa"


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
