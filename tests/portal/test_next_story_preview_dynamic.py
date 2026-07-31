"""Dynamic Next Story Preview from series_plan (packages stay frozen)."""
from __future__ import annotations

import pytest

from bhava_api.catalog.next_preview import (
    apply_dynamic_next_preview,
    clear_next_preview_caches,
    next_plan_story,
    next_story_preview_markdown,
)


@pytest.fixture(autouse=True)
def _reset_preview_cache():
    clear_next_preview_caches()
    yield
    clear_next_preview_caches()


def test_story_009_next_plan_row_is_cart_breaking() -> None:
    """The static plan still names Story 010; public rendering must not."""
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


def test_public_site_hides_unreleased_next_preview(monkeypatch) -> None:
    monkeypatch.setenv("BHAVA_PUBLIC_SITE", "1")
    monkeypatch.setenv("BHAVA_PUBLIC_STORY_MAX", "10")
    clear_next_preview_caches()

    stale = (
        "# Cart\n\n"
        "Body.\n\n"
        "## Next Story Preview\n"
        "Next time: The Salvation of Trinavarta. Wrong.\n\n"
        "## Parent/Teacher Note\n"
        "Keep gentle.\n"
    )
    out = apply_dynamic_next_preview(stale, "010")
    assert "Trinavarta" not in out
    assert "Tṛṇāvarta" not in out
    assert "Story 011" not in out
    assert "beautiful milestone" in out
    assert "## Parent/Teacher Note" in out


def test_local_mode_may_preview_story_011(monkeypatch) -> None:
    monkeypatch.setenv("BHAVA_PUBLIC_SITE", "0")
    clear_next_preview_caches()

    out = next_story_preview_markdown("010")
    assert "Tṛṇāvarta" in out or "Trinavarta" in out
    assert "Story 011" in out
