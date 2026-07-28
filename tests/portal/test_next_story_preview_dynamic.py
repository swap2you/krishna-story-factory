"""Dynamic Next Story Preview from series_plan (packages stay frozen)."""
from __future__ import annotations

from bhava_api.catalog.next_preview import apply_dynamic_next_preview, next_plan_story


def test_story_009_next_is_cart_breaking() -> None:
    nxt = next_plan_story("009")
    assert nxt is not None
    assert nxt["chapter_no"] == "010"
    assert "cart" in nxt["title"].lower() or "breaks" in nxt["title"].lower()
    assert "trinavarta" not in nxt["title"].lower()
    assert "tṛṇāvarta" not in nxt["title"].lower()


def test_story_010_next_is_trinavarta() -> None:
    nxt = next_plan_story("010")
    assert nxt is not None
    assert nxt["chapter_no"] == "011"
    assert "tṛṇāvarta" in nxt["title"].lower() or "trinavarta" in nxt["title"].lower()


def test_apply_dynamic_next_preview_rewrites_stale_trinavarta() -> None:
    stale = (
        "# Putana\n\n"
        "Body.\n\n"
        "## Next Story Preview\n"
        "Next time: The Salvation of Trinavarta. Wrong.\n\n"
        "## Parent/Teacher Note\n"
        "Keep gentle.\n"
    )
    out = apply_dynamic_next_preview(stale, "009")
    assert "Baby Kṛṣṇa Breaks the Cart" in out or "Breaks the Cart" in out
    assert "Story 010" in out
    assert "Trinavarta" not in out
    assert "Tṛṇāvarta" not in out
    assert "## Parent/Teacher Note" in out
