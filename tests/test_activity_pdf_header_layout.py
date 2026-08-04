"""Activity PDF header geometry regressions (title must not cross box border)."""
from __future__ import annotations

from pathlib import Path

from reportlab.lib.units import inch

from krishna_story_factory.pdf.activity_sheet import (
    PAGE_H,
    ActivitySheetGenerator,
    _HEADER_TITLE_BOX_GAP,
    measure_header_layout,
    validate_activity_pdf,
)
from krishna_story_factory.activities.models import ActivityPack, ActivityPage, SequenceCard
from krishna_story_factory.models import PlanRow


def _plan(title: str = "The Stealing of the Boys and Calves by Brahma") -> PlanRow:
    return PlanRow(
        chapter_no="021",
        slug="the-stealing-of-the-boys-and-calves-by-brahma",
        title=title,
        project="krishna-book-bedtime",
        library_id="kb",
        source_reference="KB 13",
        scripture_reference="SB 10.13",
        summary_seed="brahma calves",
        age_range="6-12",
        package_type="exact-eight",
        send_date="",
        status="pending",
    )


def _sequence_pack(page1_title: str, page2_title: str, story_title: str) -> ActivityPack:
    events = [
        "Kṛṣṇa smiled at His friends in the forest of Vṛndāvana.",
        "Brahmā decided to test the Lord with mystic power.",
        "Brahmā hid the calves in a secret cave.",
        "Kṛṣṇa expanded Himself into exact forms of the boys.",
        "Brahmā saw shining four-armed Viṣṇu forms everywhere.",
        "Brahmā offered humble prayers to Lord Kṛṣṇa with love.",
    ]
    cards = [
        SequenceCard(event=e, drawing_prompt="draw", source_order=i + 1) for i, e in enumerate(events)
    ]
    return ActivityPack(
        activity_title=f"Put {story_title} in Order",
        activity_type="STORY_SEQUENCE",
        send_mode="SEND_NOW",
        estimated_minutes=15,
        parent_effort="Low",
        learning_goal="order",
        story_connection="Every printable piece comes from the central scene.",
        materials=["pencil"],
        pages=[
            ActivityPage(
                page_title=page1_title,
                page_type="STORY_SEQUENCE_CARDS",
                instructions=["Number the cards in story order."],
                components=cards,
                story_connection="Every printable piece comes from the central scene.",
            ),
            ActivityPage(
                page_title=page2_title,
                page_type="FAMILY_MISSION",
                instructions=["Choose one humble action from the story and do it today."],
                components=["family mission card", "completion checkbox"],
                story_connection="Every printable piece comes from the central scene.",
            ),
        ],
        answer_key=events,
    )


def test_title_box_separation_sequence_heading() -> None:
    layout = measure_header_layout("Story sequence cards", "The Stealing of the Boys and Calves by Brahma")
    assert layout.title_box_gap >= _HEADER_TITLE_BOX_GAP - 1e-6
    # Title baseline must sit above the box top (title entirely above the border).
    assert layout.title_baseline_y > layout.box_top
    # Subtitle sits inside the box.
    assert layout.box_bottom < layout.subtitle_y < layout.box_top


def test_title_box_separation_family_mission_heading() -> None:
    layout = measure_header_layout("Family kindness mission", "Prayers Offered by Lord Brahma to Lord Krishna")
    assert layout.title_box_gap >= _HEADER_TITLE_BOX_GAP - 1e-6
    assert layout.title_baseline_y > layout.box_top


def test_long_story_title_header_geometry() -> None:
    long_title = (
        "Prayers Offered by Lord Brahma to Lord Krishna After Seeing "
        "the Unlimited Expansions in Vrindavana Forest Pastimes"
    )
    layout = measure_header_layout("Story sequence cards", long_title)
    assert layout.title_box_gap >= _HEADER_TITLE_BOX_GAP - 1e-6
    assert layout.title_baseline_y > layout.box_top
    assert layout.content_top_y < layout.box_bottom
    assert layout.content_top_y > 0.5 * inch


def test_rendered_pdf_preserves_headings_and_events(tmp_path: Path) -> None:
    plan = _plan()
    pack = _sequence_pack("Story sequence cards", "Family kindness mission", plan.title)
    out = tmp_path / "activity_sheet.pdf"
    result = ActivitySheetGenerator().generate(plan, pack, out)
    assert not result.errors, result.errors
    assert result.page_count == 2
    render_dir = tmp_path / "renders"
    check = validate_activity_pdf(out, render_dir, activity=pack)
    assert not check.errors, check.errors
    # Text extraction must retain both page headings and all six events.
    try:
        import fitz
    except ImportError:
        import pypdfium2 as pdfium

        doc = pdfium.PdfDocument(str(out))
        text = "\n".join(doc[i].get_textpage().get_text_bounded() for i in range(len(doc)))
    else:
        doc = fitz.open(out)
        text = "\n".join(page.get_text() for page in doc)
    assert "Story sequence cards" in text
    assert "Family kindness mission" in text
    for event in pack.answer_key:
        assert event.split()[0] in text or event[:24] in text
    assert PAGE_H > 0
