"""Regression tests for Krishna Book non-skipping / coverage gates."""
from __future__ import annotations

from pathlib import Path

from krishna_story_factory.coverage import (
    evaluate_package_text,
    evaluate_story_coverage,
    load_coverage_ledger,
)
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
