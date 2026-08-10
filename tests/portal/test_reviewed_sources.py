"""Regression: Stories 001–020 expose reviewed Vedabase URLs and provenance."""
from __future__ import annotations

from bhava_api.web_assets.reviewed_shlokas import REVIEWED_SHLOKAS, shlokas_payload_for_story
from bhava_api.web_assets.reviewed_sources import REVIEWED_SOURCES, source_links_for_story


def test_reviewed_sources_cover_released_stories():
    assert set(REVIEWED_SOURCES) == {f"{n:03d}" for n in range(1, 26)}


def test_reviewed_shlokas_cover_001_025():
    assert set(REVIEWED_SHLOKAS) == {f"{n:03d}" for n in range(1, 26)}
    for story_no in REVIEWED_SHLOKAS:
        payload = shlokas_payload_for_story(story_no)
        assert payload["status"] == "reviewed"
        assert payload["shlokas"]
        for row in payload["shlokas"]:
            assert row["review_status"] in {"reviewed", "not_applicable"}
            assert row.get("sanskrit") in (None, "")
            assert "translation" not in row or row["translation"] is None
            note = str(row.get("note") or "").lower() + str(row.get("child_explanation") or "").lower()
            assert "used with permission" not in note


def test_reviewed_sources_have_verified_vedabase_urls():
    for story_no, row in REVIEWED_SOURCES.items():
        url = row["vedabase_url"]
        assert isinstance(url, str) and url.startswith("https://vedabase.io/"), story_no
        assert row["review_status"] == "reviewed"
        assert row["permissions_status"] == "excerpt-needs-review"
        note = row["permissions_note"].lower()
        assert "used with permission" not in note


def test_stories_010_020_have_sb_companion_and_aug_review_date():
    for n in range(10, 21):
        story_no = f"{n:03d}"
        row = REVIEWED_SOURCES[story_no]
        assert row["reviewed_date"] == "2026-08-01"
        assert row["reviewer"] == "Svarna Gauranga Das"
        secondary = row["scripture_secondary"]
        assert isinstance(secondary, dict)
        assert secondary["canto"] == 10
        assert secondary["vedabase_url"].startswith("https://vedabase.io/en/library/sb/10/")


def test_stories_001_005_006_have_sb_chapter_companions():
    expected = {
        "001": ("https://vedabase.io/en/library/sb/10/1/", 1),
        "005": ("https://vedabase.io/en/library/sb/10/2/", 2),
        "006": ("https://vedabase.io/en/library/sb/10/3/", 3),
    }
    for story_no, (url, chapter) in expected.items():
        secondary = REVIEWED_SOURCES[story_no]["scripture_secondary"]
        assert isinstance(secondary, dict)
        assert secondary["chapter"] == chapter
        assert secondary["vedabase_url"] == url
        assert secondary.get("verse_start") is None
        assert secondary.get("verse_end") is None


def test_bona_fide_verse_ranges_only_where_series_plan_pins_them():
    """Exact ranges only for Stories 002–004 (series_plan SB 10.1.x pins)."""
    for story_no, start, end in (("002", 27, 55), ("003", 56, 61), ("004", 62, 69)):
        secondary = REVIEWED_SOURCES[story_no]["scripture_secondary"]
        assert secondary["verse_start"] == start
        assert secondary["verse_end"] == end
    for n in list(range(1, 2)) + list(range(5, 26)):
        secondary = REVIEWED_SOURCES[f"{n:03d}"]["scripture_secondary"]
        assert secondary.get("verse_start") is None
        assert secondary.get("verse_end") is None


def test_not_applicable_shlokas_remain_not_applicable():
    for story_no in ("001", "005", "006"):
        rows = shlokas_payload_for_story(story_no)["shlokas"]
        assert rows
        assert all(row["review_status"] == "not_applicable" for row in rows)


def test_source_links_include_openable_vedabase_and_bhava_original():
    links = source_links_for_story("006", {"source_reference": "Krishna Book Chapter 3"})
    assert any(item.get("vedabase_url") for item in links)
    assert any(item.get("provenance") == "bhava-original" for item in links)
    assert any(item.get("provenance") == "bbt-source-derived" for item in links)
    assert sum(1 for item in links if item.get("label") == "Companion scripture") == 1


def test_unreviewed_story_does_not_invent_vedabase_url():
    links = source_links_for_story("099", {"source_reference": "Future chapter"})
    assert links
    assert all(not item.get("vedabase_url") for item in links)
    assert all(item.get("review_status") == "needs_review" for item in links)
