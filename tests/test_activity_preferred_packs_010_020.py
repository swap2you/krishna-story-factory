"""Editorial QA matrix for Stories 010–020 preferred activity packs (no paid generation)."""
from __future__ import annotations

from pathlib import Path

import pytest

from krishna_story_factory.activities.preferred_packs_010_020 import PREFERRED_PACKS_010_020
from krishna_story_factory.csv_store import read_plan_by_chapter

ROOT = Path(__file__).resolve().parents[1]

PLACEHOLDERS = (
    "i remember my part",
    "act the story moment calmly",
    "simple cloth",
    "simple prop",
    "act the moment calmly",
)


@pytest.mark.parametrize("chapter", sorted(PREFERRED_PACKS_010_020))
def test_preferred_pack_010_020_editorial_gates(chapter: str) -> None:
    plan = read_plan_by_chapter(ROOT, chapter)
    pack = PREFERRED_PACKS_010_020[chapter](plan)
    pack.validate()
    assert pack.story_connection.strip()
    assert pack.learning_goal.strip()
    assert pack.safety_note.strip()
    assert pack.parent_note.strip()
    assert pack.age_variants
    blob = " ".join(
        [
            pack.activity_title,
            pack.story_connection,
            pack.learning_goal,
            *(page.page_title for page in pack.pages),
            *(
                " ".join(getattr(c, f, "") for f in ("role", "line", "action", "prop", "event", "drawing_prompt", "left", "right") if hasattr(c, f))
                for page in pack.pages
                for c in page.components
            ),
        ]
    ).lower()
    for needle in PLACEHOLDERS:
        assert needle not in blob, f"{chapter} still has placeholder {needle!r}"
    # No hard truncation markers from old generator
    assert "…" not in pack.activity_title
    assert all(len(page.page_title) >= 8 for page in pack.pages)
