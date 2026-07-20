from pathlib import Path

from krishna_story_factory.csv_store import read_next_pending
from krishna_story_factory.master_plan import load_master_plan, validate_master_plan

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "input" / "krishna_book_master_plan.csv"


def test_master_plan_covers_all_krishna_book_chapters() -> None:
    rows = load_master_plan(MASTER)
    assert len(rows) == 93
    assert {int(row["source_chapter"]) for row in rows} == set(range(1, 91))
    assert validate_master_plan(MASTER) == []


def test_next_active_episode_is_story_004() -> None:
    plan = read_next_pending(ROOT)
    assert plan is not None
    assert (plan.chapter_no, plan.slug) == ("004", "narada-warns-kamsa")

