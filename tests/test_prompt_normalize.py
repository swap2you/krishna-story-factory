from __future__ import annotations

from krishna_story_factory.generation.prompt_normalize import (
    _ensure_coloring_prompt,
    _ensure_story_card_square_prompt,
    normalize_image_prompts,
)
from krishna_story_factory.models import PlanRow, StoryContent


def _plan(chapter_no: str = "002") -> PlanRow:
    return PlanRow(
        chapter_no=chapter_no,
        slug="devaki-and-vasudeva-wedding",
        title="The Wedding and the Heavenly Voice",
        project="krishna_book_bedtime",
        library_id="krishna_book",
        source_reference="Krishna Book Chapter 1",
        scripture_reference="SB 10.1",
        summary_seed="seed",
        age_range="6-12",
        package_type="bedtime_story",
        send_date="",
        status="pending",
    )


def test_story_card_square_prompt_includes_required_style() -> None:
    prompt = _ensure_story_card_square_prompt("Focused scene from the wedding chariot.", _plan()).lower()
    assert "devotional" in prompt
    assert "cinematic" in prompt
    assert "ultra-realistic" in prompt or "3d" in prompt
    assert "no modern objects" in prompt
    assert "not crowded" in prompt or "clear focal" in prompt


def test_coloring_prompt_includes_required_style() -> None:
    prompt = _ensure_coloring_prompt("Wedding chariot scene for children.", _plan()).lower()
    assert "centered composition" in prompt
    assert "no cropping" in prompt
    assert "large colorable spaces" in prompt
    assert "white background" in prompt
    assert "thick" in prompt or "outline" in prompt
    assert "cute" in prompt or "sweet" in prompt


def test_normalization_preserves_reflection_and_source_metadata() -> None:
    content = StoryContent(
        title="Title", recap="Recap", main_story="Story", moral="Moral", takeaway="Takeaway",
        five_star_challenge=["1"], audio_script="Audio", bedtime_reflection="What will you remember?",
        parent_discussion_note="Discuss truthfulness.", source_reference="Krishna Book Chapter 1",
        scripture_reference="SB 10.1.56-61", age_range="6-12",
    )
    normalized = normalize_image_prompts(content, _plan("003"))
    assert normalized.bedtime_reflection == content.bedtime_reflection
    assert normalized.parent_discussion_note == content.parent_discussion_note
    assert normalized.scripture_reference == content.scripture_reference
