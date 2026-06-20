from __future__ import annotations

from pathlib import Path

from krishna_story_factory.visuals.models import StoryBeat, StoryCharacter, VisualBrief
from krishna_story_factory.visuals.prompt_renderer import render_line_art_prompt, render_poster_art_prompt
from krishna_story_factory.visuals.visual_quality import check_prompt_requirements


def _sample_brief(**overrides) -> VisualBrief:
    brief = VisualBrief(
        title="The Chariot Promise",
        central_scene="Vasudeva speaks calmly while the chariot waits at the palace gate.",
        setting="Ancient Mathura palace road",
        main_characters=[
            StoryCharacter(name="Vasudeva", role="husband", expression="calm", pose="speaking"),
            StoryCharacter(name="Devaki", role="wife", expression="faithful", pose="seated"),
        ],
        key_emotions=["faith", "protection"],
        sacred_mood="devotional hope",
        story_beats=[StoryBeat(sequence=1, scene="Wedding departure", visual_action="chariot moves")],
        must_include=["chariot", "palace gate"],
        must_avoid=["modern objects", "weapons"],
    )
    for key, value in overrides.items():
        setattr(brief, key, value)
    return brief


def _other_story_brief() -> VisualBrief:
    return VisualBrief(
        title="Forest Pastime",
        central_scene="A cowherd boy plays flute under a kadamba tree.",
        setting="Vrindavan forest grove",
        main_characters=[StoryCharacter(name="Gopala", role="hero", expression="joyful")],
        key_emotions=["joy"],
        must_include=["flute", "kadamba tree"],
        must_avoid=["palace", "chariot"],
    )


def test_story_characters_passed_into_both_templates() -> None:
    root = Path(__file__).resolve().parents[1]
    brief = _sample_brief()
    line = render_line_art_prompt(root, brief)
    poster = render_poster_art_prompt(root, brief)
    assert "Vasudeva" in line
    assert "Devaki" in poster
    assert "chariot" in line.lower()


def test_line_art_prompt_contains_required_style_constraints() -> None:
    root = Path(__file__).resolve().parents[1]
    prompt = render_line_art_prompt(root, _sample_brief())
    issues = check_prompt_requirements(prompt, kind="line_art")
    assert not issues, issues


def test_poster_prompt_contains_required_cinematic_constraints() -> None:
    root = Path(__file__).resolve().parents[1]
    prompt = render_poster_art_prompt(root, _sample_brief())
    issues = check_prompt_requirements(prompt, kind="poster")
    assert not issues, issues


def test_poster_prompt_says_no_generated_typography() -> None:
    root = Path(__file__).resolve().parents[1]
    prompt = render_poster_art_prompt(root, _sample_brief()).lower()
    assert "do not generate final typography" in prompt or "no text fragments" in prompt


def test_templates_do_not_hardcode_vasudeva_or_kamsa() -> None:
    root = Path(__file__).resolve().parents[1]
    for rel in (
        "prompts/visuals/02_line_art_portrait.md",
        "prompts/visuals/03_cinematic_poster_art.md",
        "prompts/visuals/01_story_visual_brief.md",
    ):
        text = (root / rel).read_text(encoding="utf-8").lower()
        assert "vasudeva" not in text
        assert "kamsa" not in text
        assert "devaki" not in text


def test_different_story_uses_different_characters_and_setting() -> None:
    root = Path(__file__).resolve().parents[1]
    a = render_line_art_prompt(root, _sample_brief())
    b = render_line_art_prompt(root, _other_story_brief())
    assert "Mathura" in a or "chariot" in a.lower()
    assert "Vrindavan" in b or "kadamba" in b.lower()
    assert "Gopala" in b
    assert "Gopala" not in a


def test_reference_note_only_when_enabled() -> None:
    root = Path(__file__).resolve().parents[1]
    with_ref = render_poster_art_prompt(root, _sample_brief(), use_reference=True)
    without_ref = render_poster_art_prompt(root, _sample_brief(), use_reference=False)
    assert "STYLE REFERENCE NOTE" in with_ref
    assert "STYLE REFERENCE NOTE" not in without_ref
    assert "current story content must override" in with_ref.lower()
