from __future__ import annotations

from pathlib import Path

from krishna_story_factory.activities.planner import ActivityPlanner
from krishna_story_factory.content.parent_answer_key import (
    build_parent_answer_key,
    validate_parent_answer_key,
)
from krishna_story_factory.content.story_format_v2 import (
    SERIES_NAME,
    build_greeting,
    package_from_llm_dict,
    validate_story_format_v2,
    validate_story_markdown_v2,
)
from krishna_story_factory.models import PlanRow, story_content_from_v2
from krishna_story_factory.pdf.activity_sheet import ActivitySheetGenerator, validate_activity_pdf


def _plan(chapter: str = "005") -> PlanRow:
    return PlanRow(
        chapter,
        "prayers-by-the-demigods-for-lord-krishna-in-the-womb",
        "Prayers by the Demigods for Lord Krishna in the Womb",
        "p",
        "l",
        "Krishna Book Ch. 2",
        "SB 10.2.25-42",
        "Demigods pray to Krishna within Devaki",
        "6-13",
        "daily",
        "",
        "pending",
    )


def test_greeting_uses_configured_names_without_hardcoding_defaults() -> None:
    assert "children and families" in build_greeting("")
    named = build_greeting("Subhu,Gaurangi")
    assert "Subhu" in named and "Gaurangi" in named


def test_story_format_v2_markdown_section_order() -> None:
    plan = _plan()
    package = package_from_llm_dict(
        {
            "greeting": "Hare Kṛṣṇa, dear children and families!",
            "series_name": SERIES_NAME,
            "story_number": "005",
            "title": plan.title,
            "recap": " ".join(["Previously Nārada warned Kaṁsa and the couple remembered the Lord."] * 8),
            "main_story": " ".join(["The demigods prayed with love."] * 120),
            "devotional_meaning": " ".join(["This pastime shows Kṛṣṇa's protection and the power of prayer."] * 12),
            "five_lessons": ["a", "b", "c", "d", "e"],
            "think_about_it": ["Q1?", "Q2?", "Q3?"],
            "five_star_challenge": ["1", "2", "3", "4", "5"],
            "bedtime_prayer": (
                "Dear Kṛṣṇa, thank You. Hare Kṛṣṇa Hare Kṛṣṇa Kṛṣṇa Kṛṣṇa Hare Hare "
                "Hare Rāma Hare Rāma Rāma Rāma Hare Hare. Good night."
            ),
            "next_story_preview": "Next time: Story 006 — The Birth of Lord Kṛṣṇa on a sacred night of wonder and faith.",
            "parent_note": " ".join(["Stay within Chapter 2 boundaries and discuss prayerful courage."] * 6),
            "audio_narration": " ".join(["Tonight we hear the secret prayer gathering."] * 90),
        },
        plan=plan,
        greeting=build_greeting(""),
    )
    md = package.to_markdown()
    assert not validate_story_markdown_v2(md)
    assert "## Devotional Meaning" in md
    assert "## Moral" not in md
    assert "Parent/Teacher Note" in md
    content = story_content_from_v2(package)
    assert content.story_format == "v2"
    assert "Audio Narration" in content.to_markdown()


def test_recap_must_reference_previous_not_current_for_story_005() -> None:
    plan = _plan()
    package = package_from_llm_dict(
        {
            "recap": (
                "In the previous episode, Nārada warned Kaṁsa about the danger he feared. "
                "Kaṁsa became alarmed and acted with cruelty. Devakī and Vasudeva were imprisoned, "
                "and Ugrasena was removed from power. Even in that dark moment, Devakī and Vasudeva "
                "remembered the Lord with faith. Tonight we continue from that imprisonment into the "
                "secret prayers offered for Kṛṣṇa within Devakī."
            ),
            "main_story": " ".join(["Paragraph."] * 200),
            "devotional_meaning": " ".join(["Meaning sentence about protection and prayer."] * 15),
            "five_lessons": ["tattva", "practice", "character", "service", "application"],
            "think_about_it": ["Who came?", "What did they do?", "How can you pray?"],
            "five_star_challenge": ["remember", "speak", "draw", "serve", "pray"],
            "bedtime_prayer": (
                "Dear Kṛṣṇa protect us. Hare Kṛṣṇa Hare Kṛṣṇa Kṛṣṇa Kṛṣṇa Hare Hare "
                "Hare Rāma Hare Rāma Rāma Rāma Hare Hare. Good night."
            ),
            "next_story_preview": "Next time Story 006 The Birth of Lord Kṛṣṇa on a sacred night filled with wonder.",
            "parent_note": " ".join(["Source boundary Chapter 2. Discuss courage. Keep child-safe."] * 5),
            "audio_narration": " ".join(["Audio words for consistency checks with prayer Hare Krishna."] * 80),
        },
        plan=plan,
        greeting=build_greeting(""),
    )
    assert "nārada" in package.recap.lower() or "narada" in package.recap.lower()
    assert "tonight we continue" in package.recap.lower()
    # Recap should not narrate the current demigod prayer gathering as already finished.
    assert "returned to their heavenly homes" not in package.recap.lower()


def test_parent_answer_key_matches_story_005_pack(tmp_path: Path) -> None:
    activity = ActivityPlanner(tmp_path / "history.csv").plan(_plan(), "story")
    key = build_parent_answer_key(activity)
    assert len(key.matching) == 5
    assert len(key.sequence) == 6
    assert key.open_ended_guidance
    assert all(item["no_single_correct_answer"] for item in key.open_ended_guidance)
    assert not validate_parent_answer_key(activity, key)


def test_story_005_pdf_footer_and_lotus_layout(tmp_path: Path) -> None:
    activity = ActivityPlanner(tmp_path / "history.csv").plan(_plan(), "story")
    out = tmp_path / "activity_sheet.pdf"
    ActivitySheetGenerator().generate(_plan(), activity, out)
    check = validate_activity_pdf(out, tmp_path / "pages", activity=activity)
    assert not check.errors, check.errors
    import pypdfium2 as pdfium

    doc = pdfium.PdfDocument(str(out))
    pages = [doc[i].get_textpage().get_text_range() for i in range(len(doc))]
    doc.close()
    p1 = pages[0].lower()
    p3 = pages[2].lower()
    assert "younger: younger" not in p1
    assert "lotus petal" not in p1
    assert "match" not in p3 or "family: discuss" in p3
    assert "my lotus" in p3
    assert "younger: draw inside each lotus petal" in p3
