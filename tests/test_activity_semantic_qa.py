from __future__ import annotations

from pathlib import Path

from krishna_story_factory.activities.models import (
    ActivityPack,
    ActivityPage,
    SequenceCard,
)
from krishna_story_factory.activities.planner import ActivityPlanner
from krishna_story_factory.activities.qa import GENERIC_PLACEHOLDERS, semantic_activity_errors
from krishna_story_factory.models import PlanRow


def _row(chapter: str = "005", title: str = "Prayers by the Demigods") -> PlanRow:
    return PlanRow(
        chapter, "story", title, "p", "l", "Krishna Book", "SB 10.2",
        "Brahma Shiva Narada pray while Krishna remains unseen", "6-13", "daily", "", "pending",
    )


def test_generic_pack_rejected() -> None:
    pack = ActivityPack(
        activity_title="Generic Worksheet",
        activity_type="STORY_SEQUENCE",
        send_mode="SEND_NOW",
        estimated_minutes=15,
        parent_effort="Low",
        learning_goal="Order events",
        story_connection="",
        pages=[
            ActivityPage(
                page_title="Sequence",
                page_type="STORY_SEQUENCE_CARDS",
                instructions=["Number the cards"],
                components=[
                    SequenceCard("Story begins", "draw", 1),
                    SequenceCard("A problem appears", "draw", 2),
                    SequenceCard("A helpful choice", "draw", 3),
                    SequenceCard("The turning point", "draw", 4),
                ],
                story_connection="",
            ),
            ActivityPage(
                page_title="Mission",
                page_type="FAMILY_MISSION",
                instructions=["Do something"],
                components=["Main character"],
                story_connection="",
            ),
        ],
        answer_key=["Story begins", "A problem appears", "A helpful choice", "The turning point"],
        age_variants={},
    )
    errors = semantic_activity_errors(pack)
    assert errors
    blob = " ".join(errors).lower()
    assert "placeholder" in blob or "story_connection" in blob or "age_variants" in blob
    assert any(label in GENERIC_PLACEHOLDERS for label in ("story begins", "a problem appears"))


def test_story_005_pack_passes_semantic_qa(tmp_path: Path) -> None:
    pack = ActivityPlanner(tmp_path / "history.csv").plan(_row(), "story about demigod prayers")
    errors = semantic_activity_errors(pack)
    assert not errors, errors
    assert pack.activity_title == "The Secret Prayer Gathering"
    assert len(pack.pages) == 3
    assert pack.age_variants.get("ages_6_8")
    assert pack.age_variants.get("ages_9_13")
