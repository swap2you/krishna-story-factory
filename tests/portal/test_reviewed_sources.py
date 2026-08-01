"""Regression: Stories 001–020 expose reviewed Vedabase URLs and provenance."""
from __future__ import annotations

from bhava_api.web_assets.reviewed_shlokas import REVIEWED_SHLOKAS, shlokas_payload_for_story
from bhava_api.web_assets.reviewed_sources import REVIEWED_SOURCES, source_links_for_story


def test_reviewed_sources_cover_released_stories():
    assert set(REVIEWED_SOURCES) == {f"{n:03d}" for n in range(1, 21)}


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


def test_reviewed_shlokas_cover_001_020():
    assert set(REVIEWED_SHLOKAS) == {f"{n:03d}" for n in range(1, 21)}
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
