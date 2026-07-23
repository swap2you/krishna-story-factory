"""Regression: Stories 001–007 expose reviewed Vedabase URLs and provenance."""
from __future__ import annotations

from bhava_api.web_assets.reviewed_sources import REVIEWED_SOURCES, source_links_for_story


def test_reviewed_sources_cover_released_stories():
    assert set(REVIEWED_SOURCES) == {f"{n:03d}" for n in range(1, 8)}


def test_reviewed_sources_have_verified_vedabase_urls():
    for story_no, row in REVIEWED_SOURCES.items():
        url = row["vedabase_url"]
        assert isinstance(url, str) and url.startswith("https://vedabase.io/"), story_no
        assert row["review_status"] == "reviewed"
        assert row["permissions_status"] == "excerpt-needs-review"
        note = row["permissions_note"].lower()
        assert "used with permission" not in note


def test_source_links_include_openable_vedabase_and_bhava_original():
    links = source_links_for_story("006", {"source_reference": "Krishna Book Chapter 3"})
    assert any(item.get("vedabase_url") for item in links)
    assert any(item.get("provenance") == "bhava-original" for item in links)
    assert any(item.get("provenance") == "bbt-source-derived" for item in links)


def test_unreviewed_story_does_not_invent_vedabase_url():
    links = source_links_for_story("099", {"source_reference": "Future chapter"})
    assert links
    assert all(not item.get("vedabase_url") for item in links)
    assert all(item.get("review_status") == "needs_review" for item in links)
