"""Activity semantic regressions using Story 021 known-bad patterns."""
from __future__ import annotations

from pathlib import Path

from krishna_story_factory.activities.story_map import (
    evaluate_activity_semantic_qa,
    reconstruct_story_map_from_canonical,
    validate_event_list,
)
from krishna_story_factory.activities.qa import matching_coverage_from_pdf_text, sequence_coverage_from_pdf_text
from krishna_story_factory.activities.models import (
    ActivityPack,
    ActivityPage,
    SequenceCard,
)


# Exact mid-word / opening-fragment cards from the failed Story 021 package.
STORY_021_BAD_EVENTS = [
    "The morning in Vṛndāvana shone bright as ever, the grass glistening with tiny drops of dew under the feet of t",
    "Kṛṣṇa’s eyes sparkled with joy as He led His friends deeper into the green forest, calling out, “Come, let us ",
    "” The boys laughed and scampered after Him, their pockets and baskets filled with rice and sweet fruits from h",
    "Soon, they found a soft, shady spot under tall trees",
    "The air was full of music from birds and the soft lowing of calves settling nearby",
    "“Let’s eat our breakfast together",
]


def test_story_021_old_opening_fragments_fail() -> None:
    errors = validate_event_list(STORY_021_BAD_EVENTS, required_chars=["Brahmā", "Kṛṣṇa"])
    assert errors
    qa = evaluate_activity_semantic_qa(
        activity_type="STORY_SEQUENCE",
        events=STORY_021_BAD_EVENTS,
        required_tokens=["Brahmā", "Kṛṣṇa"],
        canonical_story="Brahmā steals the calves and boys. Kṛṣṇa expands. Viṣṇu forms appear.",
    )
    assert qa.result == "FAIL"


def test_unfinished_quotation_let_us_fails() -> None:
    events = list(STORY_021_BAD_EVENTS)
    errors = validate_event_list(events)
    assert any("truncated" in e or "complete sentence" in e for e in errors)


def test_mid_word_event_fails() -> None:
    bad = [
        "Kṛṣṇa smiled at His friends in the forest of Vṛndāvana.",
        "Brahmā decided to test the Lord with mystic power.",
        "Brahmā hid the calves in a secret cave.",
        "Kṛṣṇa expanded Himself into exact forms of the boys.",
        "Brahmā saw shining four-armed Viṣṇu forms everywhere.",
        "Brahmā offered humble prayers and became soft-hearted fr",
    ]
    errors = validate_event_list(bad)
    assert any("truncated" in e or "mid-word" in e or "complete sentence" in e for e in errors)


def test_duplicate_events_fail() -> None:
    dup = [
        "Kṛṣṇa smiled at His friends in the forest of Vṛndāvana.",
        "Brahmā decided to test the Lord with mystic power.",
        "Brahmā hid the calves in a secret cave.",
        "Kṛṣṇa expanded Himself into exact forms of the boys.",
        "Brahmā saw shining four-armed Viṣṇu forms everywhere.",
        "Kṛṣṇa smiled at His friends in the forest of Vṛndāvana.",
    ]
    errors = validate_event_list(dup)
    assert any("duplicate" in e for e in errors)


def test_sequence_expected_zero_fails_coverage() -> None:
    pack = ActivityPack(
        activity_title="Broken",
        activity_type="STORY_SEQUENCE",
        send_mode="SEND_NOW",
        estimated_minutes=10,
        parent_effort="Low",
        learning_goal="order",
        story_connection="test",
        materials=["pencil"],
        pages=[
            ActivityPage(
                page_title="cards",
                page_type="STORY_SEQUENCE_CARDS",
                instructions=["number"],
                components=[],
                story_connection="test",
            )
        ],
    )
    coverage = sequence_coverage_from_pdf_text(pack, "anything")
    assert coverage.pass_ is False
    assert coverage.expected_pairs == 0


def test_story_021_missing_brahma_or_central_fails() -> None:
    picnic_only = [
        "The morning in Vṛndāvana shone bright under the soft dew.",
        "The boys laughed and shared sweet fruits from home.",
        "They found a shady spot under the tall green trees.",
        "The air was full of music from the forest birds.",
        "Kṛṣṇa smiled and sat in the center of His friends.",
        "Everyone felt peaceful and happy in the forest picnic.",
    ]
    qa = evaluate_activity_semantic_qa(
        activity_type="STORY_SEQUENCE",
        events=picnic_only,
        required_tokens=["Brahmā", "Kṛṣṇa"],
        canonical_story="Brahmā steals. Kṛṣṇa expands. Viṣṇu forms appear.",
    )
    assert qa.result == "FAIL"


def test_story_021_canonical_rebuild_passes_semantic_shape() -> None:
    """Hermetic: committed fixture only — never reads developer package trees."""
    fixture = Path(__file__).resolve().parent / "fixtures" / "story_021" / "story.md"
    story = fixture.read_text(encoding="utf-8")
    story_map = reconstruct_story_map_from_canonical(
        story_no="021",
        title="The Stealing of the Boys and Calves by Brahma",
        story_md=story,
    )
    events = story_map.sequence_events()
    assert len(events) == 6
    errors = validate_event_list(events, required_chars=["Brahmā", "Kṛṣṇa"])
    assert not errors, errors
    blob = " ".join(events).lower()
    assert "brahm" in blob.replace("ā", "a")
    assert any(token in blob for token in ("expanded", "viṣṇu", "visnu", "prayer", "humble"))
    qa = evaluate_activity_semantic_qa(
        activity_type="STORY_SEQUENCE",
        events=events,
        parent_answer_events=events,
        required_tokens=["Brahmā", "Kṛṣṇa"],
        canonical_story=story,
    )
    assert qa.result == "PASS", qa.failure_reasons


def test_matching_coverage_routes_sequence_packs() -> None:
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
    pack = ActivityPack(
        activity_title="Order",
        activity_type="STORY_SEQUENCE",
        send_mode="SEND_NOW",
        estimated_minutes=10,
        parent_effort="Low",
        learning_goal="order",
        story_connection="test",
        materials=["pencil"],
        pages=[
            ActivityPage(
                page_title="cards",
                page_type="STORY_SEQUENCE_CARDS",
                instructions=["number"],
                components=cards,
                story_connection="test",
            )
        ],
    )
    text = " ".join(events)
    coverage = matching_coverage_from_pdf_text(pack, text)
    assert coverage.expected_pairs == 6
    assert coverage.pass_ is True
