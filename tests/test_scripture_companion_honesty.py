"""Tests for scripture companion honesty: exact vs chapter-framed."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / "data" / "web-assets"

EXACT_RANGE_RE = re.compile(r"\d+\.\d+\.\d+")


def _load_shlokas(story_no: str) -> dict:
    path = WEB / story_no / "shlokas.json"
    assert path.is_file(), f"missing {path}"
    return json.loads(path.read_text(encoding="utf-8"))


def test_stories_002_004_have_distinct_non_overlapping_ranges() -> None:
    refs = []
    for story in ("002", "003", "004"):
        payload = _load_shlokas(story)
        items = payload.get("shlokas") or []
        assert items, story
        ref = str(items[0].get("reference") or "")
        assert "SB 10.1" in ref, story
        refs.append(ref)
    assert refs[0] != refs[1] != refs[2]
    assert "27" in refs[0] and "55" in refs[0]
    assert "56" in refs[1] and "61" in refs[1]
    assert "62" in refs[2] and "69" in refs[2]


def test_not_applicable_entries_do_not_claim_exact_verse_range() -> None:
    for story in ("001", "005", "006"):
        payload = _load_shlokas(story)
        items = payload.get("shlokas") or []
        assert items, story
        item = items[0]
        assert item.get("review_status") == "not_applicable"
        assert item.get("decision") == "no-separate-verse"
        ref = str(item.get("reference") or "")
        assert not EXACT_RANGE_RE.search(ref), f"{story} claimed exact range while N/A"


def test_reviewed_chapter_refs_without_verse_triplet_are_chapter_framed() -> None:
    for story in ("009", "011", "019", "020"):
        payload = _load_shlokas(story)
        items = payload.get("shlokas") or []
        assert items, story
        item = items[0]
        if item.get("review_status") != "reviewed":
            continue
        ref = str(item.get("reference") or "")
        # Chapter-framed companions may omit verse triplets; that is honest.
        if not EXACT_RANGE_RE.search(ref):
            assert "SB" in ref or "Bhagavatam" in ref or "10." in ref
        url = item.get("url") or ""
        assert "vedabase.io" in str(url)


def test_exact_range_status_requires_evidence_in_reference() -> None:
    """If a companion claims an exact verse window, the reference must include a verse triplet."""
    for path in WEB.glob("*/shlokas.json"):
        payload = json.loads(path.read_text(encoding="utf-8"))
        for item in payload.get("shlokas") or []:
            claim = str(item.get("exact_range_status") or "").lower()
            ref = str(item.get("reference") or "")
            if claim in {"exact", "verified_exact"}:
                assert EXACT_RANGE_RE.search(ref), path
