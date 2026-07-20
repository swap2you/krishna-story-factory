from __future__ import annotations

from pathlib import Path

from krishna_story_factory.activities.planner import ActivityPlanner
from krishna_story_factory.models import PlanRow


def test_story_005_planner_returns_secret_prayer_gathering(tmp_path: Path) -> None:
    plan = PlanRow(
        "005",
        "prayers-by-the-demigods-for-lord-krishna-in-the-womb",
        "Prayers by the Demigods for Lord Krishna in the Womb",
        "p",
        "l",
        "Krishna Book Ch. 2",
        "SB 10.2.25-42",
        "Demigods pray to Krishna within Devaki",
        "6-13",
        "daily",
        "",
        "pending",
    )
    pack = ActivityPlanner(tmp_path / "history.csv").plan(plan, "story")
    assert pack.activity_title == "The Secret Prayer Gathering"
    assert len(pack.pages) == 3
    assert any(page.page_type == "STORY_SEQUENCE_CARDS" for page in pack.pages)
    assert any(page.page_type == "MATCHING_CARDS" for page in pack.pages)
