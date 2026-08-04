"""Story 022 activity semantic regressions — return + prayer beats required."""
from __future__ import annotations

from pathlib import Path

from krishna_story_factory.activities.story_map import (
    evaluate_activity_semantic_qa,
    reconstruct_story_map_from_canonical,
    validate_story_022_sequence_beats,
)

# Committed excerpt capturing the 022 arc without reading developer output/.
_FIXTURE = """# Krishna Book Bedtime

## Main Story
After Brahmā, the creator of the universe, had hidden the cowherd boys and calves, he left thinking he had tested Kṛṣṇa’s power.
But for Kṛṣṇa, not even a single moment went by.
Instead, by His mysterious ability, Kṛṣṇa expanded Himself into every missing boy and every single calf.
He copied them perfectly, right down to their laughter, their voices, how they walked, and all their playful habits.
Then, one bright morning, Brahmā returned.
He expected to find confusion or sadness in Vṛndāvana, imagining the cowherd boys and calves were still missing.
Before Brahmā’s astonished gaze, each one turned into a four-armed Viṣṇu form.
Realizing how tiny he was before the Lord of all, he descended from his graceful white swan and with trembling hands bowed all four of his heads to Kṛṣṇa’s lotus feet.
He prayed for forgiveness, thanking Kṛṣṇa for this lesson—a lesson that even the highest knowledge, without devotion, is hollow.
"""


def test_story_022_reconstructed_sequence_has_return_and_prayer() -> None:
    sm = reconstruct_story_map_from_canonical(
        story_no="022",
        title="Prayers Offered by Lord Brahma to Lord Krishna",
        story_md=_FIXTURE,
    )
    events = sm.sequence_events()
    errors = validate_story_022_sequence_beats(events)
    assert not errors, errors
    qa = evaluate_activity_semantic_qa(
        activity_type="STORY_SEQUENCE",
        events=events,
        parent_answer_events=events,
        required_tokens=["Brahmā", "Kṛṣṇa"],
        canonical_story=_FIXTURE,
    )
    assert qa.result == "PASS", qa.failure_reasons


def test_story_022_fails_without_return_beat() -> None:
    bad = [
        "After Brahmā had hidden the cowherd boys and calves, he left thinking he had tested Kṛṣṇa’s power.",
        "By His mysterious ability, Kṛṣṇa expanded Himself into every missing boy and every single calf.",
        "He copied them perfectly, right down to their laughter and playful habits.",
        "Before Brahmā’s astonished gaze, each one turned into a four-armed Viṣṇu form.",
        "He descended from his graceful white swan and bowed all four of his heads.",
        "He prayed for forgiveness, thanking Kṛṣṇa for this lesson with a humble heart.",
    ]
    # Remove return explicitly; "returned" must be absent.
    assert not any("returned" in e.lower() for e in bad)
    errors = validate_story_022_sequence_beats(bad)
    assert any("returned" in e for e in errors)


def test_story_022_fails_without_prayer_beat() -> None:
    bad = [
        "After Brahmā had hidden the cowherd boys and calves, he left thinking he had tested Kṛṣṇa’s power.",
        "By His mysterious ability, Kṛṣṇa expanded Himself into every missing boy and every single calf.",
        "One bright morning, Brahmā returned to the peaceful forest of Vṛndāvana.",
        "Before Brahmā’s astonished gaze, each one turned into a four-armed Viṣṇu form.",
        "He descended from his graceful white swan and bowed all four of his heads.",
        "Brahmā looked at Kṛṣṇa with wonder beneath the blossoming forest trees.",
    ]
    errors = validate_story_022_sequence_beats(bad)
    assert any("prayer" in e for e in errors)


def test_story_022_fails_on_lone_moment_fragment() -> None:
    bad = [
        "After Brahmā had hidden the cowherd boys and calves, he left thinking he had tested Kṛṣṇa’s power.",
        "But for Kṛṣṇa, not even a single moment went by.",
        "By His mysterious ability, Kṛṣṇa expanded Himself into every missing boy and every single calf.",
        "One bright morning, Brahmā returned to the peaceful forest of Vṛndāvana.",
        "Before Brahmā’s astonished gaze, each one turned into a four-armed Viṣṇu form.",
        "He prayed for forgiveness, thanking Kṛṣṇa for this lesson with a humble heart.",
    ]
    errors = validate_story_022_sequence_beats(bad)
    assert any("moment" in e for e in errors)


def test_story_022_fails_when_only_character_tokens_without_beats() -> None:
    picnic = [
        "Kṛṣṇa smiled at His friends in the forest of Vṛndāvana.",
        "Brahmā watched the boys play beneath the soft green trees.",
        "The calves rested near the river while birds sang sweetly.",
        "Everyone felt peaceful and happy in the forest picnic.",
        "Kṛṣṇa played His flute as sunlight touched the leaves.",
        "Brahmā and Kṛṣṇa remained near the blossoming forest trees.",
    ]
    errors = validate_story_022_sequence_beats(picnic)
    assert errors
    assert any("beat missing" in e for e in errors)
