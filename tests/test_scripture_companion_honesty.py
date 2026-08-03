"""Scripture companion honesty: exact vs chapter-framed (SSOT = REVIEWED_SHLOKAS)."""

from __future__ import annotations

import re

from bhava_api.web_assets.reviewed_shlokas import REVIEWED_SHLOKAS

EXACT_RANGE_RE = re.compile(r"\d+\.\d+\.\d+")


def _first_item(story_no: str) -> dict:
    payload = REVIEWED_SHLOKAS[story_no]
    items = payload.get("shlokas") or []
    assert items, story_no
    return items[0]


def test_stories_002_004_have_distinct_non_overlapping_ranges() -> None:
    refs = []
    for story in ("002", "003", "004"):
        item = _first_item(story)
        ref = str(item.get("reference") or "")
        assert "SB 10.1" in ref, story
        assert EXACT_RANGE_RE.search(ref), story
        refs.append(ref)
    assert refs[0] != refs[1] != refs[2]
    assert "27" in refs[0] and "55" in refs[0]
    assert "56" in refs[1] and "61" in refs[1]
    assert "62" in refs[2] and "69" in refs[2]


def test_not_applicable_entries_do_not_claim_exact_verse_range() -> None:
    for story in ("001", "005", "006"):
        item = _first_item(story)
        assert item.get("review_status") == "not_applicable"
        assert item.get("decision") == "no-separate-verse"
        ref = str(item.get("reference") or "")
        assert not EXACT_RANGE_RE.search(ref), f"{story} claimed exact range while N/A"


def test_reviewed_chapter_refs_include_vedabase_url() -> None:
    for story in ("009", "011", "019", "020"):
        item = _first_item(story)
        if item.get("review_status") != "reviewed":
            continue
        ref = str(item.get("reference") or "")
        assert "SB" in ref or "Bhagavatam" in ref or "10." in ref
        url = item.get("url") or ""
        assert "vedabase.io" in str(url)


def test_not_applicable_cannot_display_as_exact_and_reviewed_exact_needs_triplet() -> None:
    for story_no, payload in REVIEWED_SHLOKAS.items():
        for item in payload.get("shlokas") or []:
            status = str(item.get("review_status") or "")
            ref = str(item.get("reference") or "")
            if status == "not_applicable":
                assert not EXACT_RANGE_RE.search(ref), story_no
                assert item.get("decision") == "no-separate-verse"
            if status == "reviewed" and EXACT_RANGE_RE.search(ref):
                # Exact-looking windows must keep distinct story-specific refs when present.
                assert "SB" in ref or "ŚB" in ref or "10." in ref
