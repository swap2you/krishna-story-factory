from pathlib import Path

from krishna_story_factory.master_plan import load_master_plan, validate_master_plan

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "input" / "krishna_book_master_plan.csv"


def test_master_plan_covers_all_krishna_book_chapters() -> None:
    rows = load_master_plan(MASTER)
    assert len(rows) == 93
    assert {int(row["source_chapter"]) for row in rows} == set(range(1, 91))
    assert validate_master_plan(MASTER) == []


def test_story_005_follows_story_004_in_static_plan() -> None:
    rows = load_master_plan(MASTER)
    assert (rows[3]["episode_no"], rows[4]["episode_no"]) == ("004", "005")
