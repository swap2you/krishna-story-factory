"""Regression tests for canonical narration exact-match (Story 021+)."""
from __future__ import annotations

from krishna_story_factory.content.canonical_narration import (
    apply_approved_tts_transforms,
    evaluate_canonical_narration_exact,
)
from krishna_story_factory.content.story_tts_equivalence import evaluate_story_tts_equivalence

MAIN = (
    "Kṛṣṇa led the boys into the forest. Brahmā hid the calves in a cave. "
    "Kṛṣṇa expanded Himself into every missing boy and calf. "
    "Brahmā saw the Viṣṇu forms and offered humble prayers."
)

STORY = f"## Main Story\n{MAIN}\n"


def test_exact_canonical_match_passes() -> None:
    qa = evaluate_canonical_narration_exact(story_no="021", story_md=STORY, tts_source=MAIN)
    assert qa.result == "PASS"
    assert qa.exact_match is True


def test_partial_62_percent_style_overlap_fails() -> None:
    # Oral paraphrase covering some tokens but not exact text — must FAIL.
    partial = (
        "Hare Kṛṣṇa dear children Tonight Brahmā tested Kṛṣṇa in Vṛndāvana "
        "and the boys played happily near the calves under the trees."
    )
    gate = evaluate_story_tts_equivalence(story_md=STORY, tts_source=partial, require_exact_canonical=True)
    assert gate.status == "FAIL"
    assert "CANONICAL_EXACT_MATCH_FAIL" in gate.notes or gate.token_coverage < 1.0


def test_paraphrase_fails() -> None:
    paraphrase = (
        "The Supreme Lord guided His friends among the trees. The creator concealed the young cows. "
        "The Lord multiplied Himself as each absent child and animal. "
        "The creator witnessed the divine forms and prayed."
    )
    qa = evaluate_canonical_narration_exact(story_no="021", story_md=STORY, tts_source=paraphrase)
    assert qa.result == "FAIL"
    assert qa.exact_match is False


def test_summary_fails() -> None:
    summary = "Brahmā stole the boys and calves, then Kṛṣṇa revealed His supremacy."
    qa = evaluate_canonical_narration_exact(story_no="021", story_md=STORY, tts_source=summary)
    assert qa.result == "FAIL"
    assert qa.omitted_sentences or qa.failure_reasons


def test_reordered_sentences_fail() -> None:
    sentences = [
        "Kṛṣṇa led the boys into the forest.",
        "Brahmā hid the calves in a cave.",
        "Kṛṣṇa expanded Himself into every missing boy and calf.",
        "Brahmā saw the Viṣṇu forms and offered humble prayers.",
    ]
    reordered = " ".join(reversed(sentences))
    qa = evaluate_canonical_narration_exact(story_no="021", story_md=STORY, tts_source=reordered)
    assert qa.result == "FAIL"


def test_missing_sentence_fails() -> None:
    missing = (
        "Kṛṣṇa led the boys into the forest. Brahmā hid the calves in a cave. "
        "Brahmā saw the Viṣṇu forms and offered humble prayers."
    )
    qa = evaluate_canonical_narration_exact(story_no="021", story_md=STORY, tts_source=missing)
    assert qa.result == "FAIL"
    assert qa.omitted_sentences


def test_extra_sentence_fails() -> None:
    extra = MAIN + " An invented epilogue appears here."
    qa = evaluate_canonical_narration_exact(story_no="021", story_md=STORY, tts_source=extra)
    assert qa.result == "FAIL"
    assert qa.added_sentences


def test_pronunciation_alias_transform_passes() -> None:
    aliases = {"Kṛṣṇa": "Krishna", "Brahmā": "Brahma", "Viṣṇu": "Vishnu"}
    tts, applied = apply_approved_tts_transforms(MAIN, pronunciation_aliases=aliases)
    assert any(a.startswith("pronunciation_alias:") for a in applied)
    qa = evaluate_canonical_narration_exact(
        story_no="021",
        story_md=STORY,
        tts_source=tts,
        pronunciation_aliases=aliases,
    )
    assert qa.result == "PASS"


def test_deterministic_ssml_strip_passes() -> None:
    with_ssml = MAIN.replace(
        "cave.",
        'cave.<break time="0.4s" />',
    )
    qa = evaluate_canonical_narration_exact(story_no="021", story_md=STORY, tts_source=with_ssml)
    assert qa.result == "PASS"
    assert "strip_ssml_tags" in qa.approved_transformations
