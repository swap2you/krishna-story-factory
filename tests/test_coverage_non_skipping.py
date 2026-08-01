"""Regression tests for Krishna Book non-skipping / coverage gates."""
from __future__ import annotations

import csv
import shutil
from copy import deepcopy
from pathlib import Path

import pytest

from krishna_story_factory.coverage import (
    clear_coverage_cache,
    earliest_pending_major_story,
    evaluate_ledger_integrity,
    evaluate_package_text,
    evaluate_queue_advancement,
    evaluate_story_coverage,
    load_coverage_ledger,
)
from krishna_story_factory.csv_store import bootstrap_queue_state, read_next_pending
from krishna_story_factory.models import PlanRow, StoryContent

ROOT = Path(__file__).resolve().parents[1]


def _plan_009(**overrides) -> PlanRow:
    base = PlanRow(
        chapter_no="009",
        slug="putana-krishnas-astonishing-mercy",
        title="Pūtanā — Kṛṣṇa’s Astonishing Mercy",
        project="krishna_book_bedtime",
        library_id="krishna_book",
        source_reference="Krishna Book Chapter 6",
        scripture_reference="SB 10.6 / Complete Krishna Book Chapter 6 — Putana Killed",
        summary_seed="Putana pastime",
        age_range="6-12",
        package_type="bedtime_story",
        send_date="",
        status="pending",
        must_include="Putana|poison|breast|fragrant",
        must_avoid="universe in Krishna's mouth|Trinavarta|after Putana's defeat",
        start_boundary="Opening",
        end_boundary="Conclusion",
    )
    for key, value in overrides.items():
        setattr(base, key, value)
    return base


def _good_content() -> StoryContent:
    main = (
        "Nanda remembered Vasudeva's warning and took shelter of the Lord. "
        "Kamsa sent Putana, who had been killing infants. She took a beautiful form, "
        "entered Gokula and Nanda's home, and took baby Krishna on her lap. Krishna closed His eyes. "
        "She offered her poison-smeared breast. Krishna sucked the poison and her life air. "
        "She revealed her gigantic form and fell. Krishna played safely on her body. "
        "Yasoda, Rohini, and the gopis lifted Him and remembered Vishnu's names. "
        "Nanda and the cowherd men returned. When her body was burned it gave a fragrant aroma "
        "because Krishna purified her. He granted her a motherly destination — astonishing mercy. "
        "Hearing this pastime brings attachment to Govinda."
    )
    return StoryContent(
        title="Pūtanā — Kṛṣṇa’s Astonishing Mercy",
        recap="After Nanda and Vasudeva met, baby Krishna was safe in Gokula.",
        main_story=main,
        moral="",
        takeaway="",
        five_star_challenge=["1", "2", "3", "4", "5"],
        audio_script=main,
        bedtime_reflection="How does Krishna show mercy?",
        parent_note="Discuss mercy.",
        next_story_preview="Next time: The Salvation of Trinavarta.",
        five_lessons=["a", "b", "c", "d", "e"],
        think_about_it=["1?", "2?", "3?", "4?", "5?"],
        bedtime_prayer="Hare Krishna",
        greeting="Hare Krishna",
        source_reference="Krishna Book Chapter 6",
        scripture_reference="SB 10.6",
        age_range="6-12",
        devotional_meaning="Krishna magnifies even the appearance of motherly service.",
    )


def test_coverage_ledger_loads_chapters_1_to_10() -> None:
    ledger = load_coverage_ledger()
    chapters = {int(c["chapter"]) for c in ledger["chapters"]}
    assert set(range(1, 11)).issubset(chapters)
    ch6 = next(c for c in ledger["chapters"] if c["chapter"] == 6)
    assert any(e["id"] == "kb6-poison-breast" for e in ch6["events"])


def test_good_putana_story_passes_coverage_gate() -> None:
    result = evaluate_story_coverage(_plan_009(), _good_content())
    assert result.ok, result.errors


def test_after_putana_defeat_without_full_story_fails() -> None:
    text = (
        "Now, after Putana's defeat, the people of Gokula grew anxious.\n"
        "Baby Krishna yawned and the universe shone inside His mouth.\n"
        "Source: Complete Krishna Book Chapter 6\n"
    )
    result = evaluate_package_text("009", text)
    assert not result.ok
    assert any("defeat" in e.lower() or "universe" in e.lower() for e in result.errors)


def test_universal_mouth_in_chapter_6_fails() -> None:
    bad = _good_content()
    bad.main_story = bad.main_story + " Then Mother Yasoda saw the universe in Krishna's mouth."
    bad.audio_script = bad.main_story
    result = evaluate_story_coverage(_plan_009(), bad)
    assert not result.ok


def test_trinavarta_before_chapter_7_in_main_fails() -> None:
    bad = _good_content()
    bad.main_story = "Trinavarta the whirlwind demon attacked Gokula before Putana came."
    bad.audio_script = bad.main_story
    result = evaluate_story_coverage(_plan_009(), bad)
    assert not result.ok


def test_complete_chapter_6_without_putana_units_fails() -> None:
    bad = _good_content()
    bad.main_story = "Gokula was peaceful and baby Krishna smiled."
    bad.audio_script = bad.main_story
    result = evaluate_story_coverage(_plan_009(), bad)
    assert not result.ok


def test_archived_incorrect_009_text_would_fail_if_present() -> None:
    archived = list((ROOT / "work" / "stories" / "009").glob("v172-incorrect-archive-*/009_*/story.md"))
    if not archived:
        return
    text = archived[0].read_text(encoding="utf-8", errors="ignore")
    result = evaluate_package_text("009", text)
    assert not result.ok


def test_live_ledger_integrity_passes_v173() -> None:
    clear_coverage_cache()
    result = evaluate_ledger_integrity()
    assert result.ok, result.errors
    ledger = load_coverage_ledger()
    ch7 = next(c for c in ledger["chapters"] if c["chapter"] == 7)
    ch8 = next(c for c in ledger["chapters"] if c["chapter"] == 8)
    assert {e["id"] for e in ch7["events"] if e["significance"] == "major"} >= {
        "kb7-utthana-cart",
        "kb7-trinavarta",
        "kb7-yawn-universal-mouth",
    }
    assert {e["id"] for e in ch8["events"] if e["significance"] == "major"} >= {
        "kb8-garga-name-giving",
        "kb8-crawling-adventures",
        "kb8-butter-complaints",
        "kb8-dirt-universal-form",
    }


def test_incomplete_chapter7_only_trinavarta_fails() -> None:
    ledger = deepcopy(load_coverage_ledger())
    for chapter in ledger["chapters"]:
        if chapter["chapter"] == 7:
            chapter["events"] = [
                {
                    "id": "kb7-trinavarta",
                    "significance": "major",
                    "summary": "Tṛṇāvarta only",
                    "mapped_stories": ["010"],
                    "lifecycle": "pending",
                    "reviewer": "tester",
                }
            ]
    result = evaluate_ledger_integrity(ledger)
    assert not result.ok
    assert any("trinavarta" in e.lower() or "cart" in e.lower() for e in result.errors)


def test_cart_breaking_absent_fails() -> None:
    ledger = deepcopy(load_coverage_ledger())
    for chapter in ledger["chapters"]:
        if chapter["chapter"] == 7:
            chapter["events"] = [e for e in chapter["events"] if e.get("id") != "kb7-utthana-cart"]
    result = evaluate_ledger_integrity(ledger)
    assert not result.ok
    assert any("kb7-utthana-cart" in e or "cart" in e.lower() for e in result.errors)


def test_first_universal_mouth_absent_fails() -> None:
    ledger = deepcopy(load_coverage_ledger())
    for chapter in ledger["chapters"]:
        if chapter["chapter"] == 7:
            chapter["events"] = [
                e for e in chapter["events"] if e.get("id") != "kb7-yawn-universal-mouth"
            ]
    result = evaluate_ledger_integrity(ledger)
    assert not result.ok
    assert any("yawn" in e.lower() or "universal-mouth" in e.lower() for e in result.errors)


def test_chapter8_only_universal_mouth_fails() -> None:
    ledger = deepcopy(load_coverage_ledger())
    for chapter in ledger["chapters"]:
        if chapter["chapter"] == 8:
            chapter["events"] = [
                {
                    "id": "kb8-universal-mouth",
                    "significance": "major",
                    "summary": "Only universal mouth",
                    "mapped_stories": ["011"],
                    "lifecycle": "planned",
                    "reviewer": "tester",
                }
            ]
    result = evaluate_ledger_integrity(ledger)
    assert not result.ok
    assert any("chapter 8" in e.lower() or "garga" in e.lower() for e in result.errors)


def test_garga_absent_fails() -> None:
    ledger = deepcopy(load_coverage_ledger())
    for chapter in ledger["chapters"]:
        if chapter["chapter"] == 8:
            chapter["events"] = [
                e for e in chapter["events"] if e.get("id") != "kb8-garga-name-giving"
            ]
    result = evaluate_ledger_integrity(ledger)
    assert not result.ok
    assert any("garga" in e.lower() for e in result.errors)


def test_butter_and_dirt_collapsed_summary_fails() -> None:
    ledger = deepcopy(load_coverage_ledger())
    for chapter in ledger["chapters"]:
        if chapter["chapter"] == 8:
            chapter["events"] = [
                {
                    "id": "kb8-collapsed-butter-dirt",
                    "significance": "major",
                    "summary": "Butter-stealing and dirt-eating and universal form in one summary",
                    "mapped_stories": ["015"],
                    "lifecycle": "pending",
                    "reviewer": "tester",
                }
            ]
    result = evaluate_ledger_integrity(ledger)
    assert not result.ok
    assert any("collapsed" in e.lower() or "garga" in e.lower() or "missing" in e.lower() for e in result.errors)


def test_story_010_as_trinavarta_while_cart_uncovered_fails() -> None:
    ledger = deepcopy(load_coverage_ledger())
    for chapter in ledger["chapters"]:
        if chapter["chapter"] == 7:
            for event in chapter["events"]:
                if event.get("id") == "kb7-trinavarta":
                    event["mapped_stories"] = ["010"]
                if event.get("id") == "kb7-utthana-cart":
                    event["mapped_stories"] = ["011"]
    result = evaluate_ledger_integrity(ledger)
    assert not result.ok
    assert any("010" in e and ("trinavarta" in e.lower() or "cart" in e.lower()) for e in result.errors)


def test_one_universal_story_cannot_cover_both_chapters() -> None:
    ledger = deepcopy(load_coverage_ledger())
    for chapter in ledger["chapters"]:
        if chapter["chapter"] == 7:
            for event in chapter["events"]:
                if event.get("id") == "kb7-yawn-universal-mouth":
                    event["mapped_stories"] = ["012"]
        if chapter["chapter"] == 8:
            for event in chapter["events"]:
                if event.get("id") == "kb8-dirt-universal-form":
                    event["mapped_stories"] = ["012"]
    result = evaluate_ledger_integrity(ledger)
    assert not result.ok
    assert any("universal" in e.lower() for e in result.errors)


def _released_project(tmp_path: Path, *, done_through: int = 9) -> Path:
    """Isolated project root: committed plan plus the governed released queue.

    read_next_pending() bootstraps tracking/queue_state.csv on demand, so tests
    must never point it at the repository working tree.
    """
    shutil.copytree(ROOT / "input", tmp_path / "input")
    bootstrap_queue_state(tmp_path)
    path = tmp_path / "tracking" / "queue_state.csv"
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        fields = list(reader.fieldnames or [])
        rows = list(reader)
    for row in rows:
        chapter = int(str(row["chapter_no"]).strip() or 0)
        row["status"] = "done" if 1 <= chapter <= done_through else "pending"
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    return tmp_path


def test_next_pending_is_cart_breaking(tmp_path: Path) -> None:
    nxt = read_next_pending(_released_project(tmp_path))
    assert nxt is not None
    assert nxt.chapter_no == "010"
    assert "cart" in nxt.slug
    queue = {f"{n:03d}": ("done" if n <= 9 else "pending") for n in range(1, 20)}
    assert earliest_pending_major_story(queue) == "010"
    ok = evaluate_queue_advancement("010", queue)
    assert ok.ok, ok.errors
    bad = evaluate_queue_advancement("011", queue)
    assert not bad.ok


@pytest.mark.local_runtime
def test_live_queue_next_pending_is_brahma_stealing() -> None:
    nxt = read_next_pending(ROOT)
    assert nxt is not None
    assert nxt.chapter_no == "021"
    assert "brahma" in nxt.slug or "calves" in nxt.slug or "boys" in nxt.slug
