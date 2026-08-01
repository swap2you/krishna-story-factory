"""Unit tests for Phase 8 visual brief / event-relevance scaffolding."""
from __future__ import annotations

from krishna_story_factory.visuals.event_relevance import (
    STORY_009_EVENT_KEYWORDS,
    STORY_011_EVENT_KEYWORDS,
    STORY_020_EVENT_KEYWORDS,
    validate_event_relevance_keywords,
)
from krishna_story_factory.visuals.models import VisualBrief


def test_must_include_and_must_avoid_required() -> None:
    brief = VisualBrief(title="x", central_scene="a scene", must_include=[], must_avoid=[])
    errors = brief.validate()
    assert any("must_include" in e for e in errors)
    assert any("must_avoid" in e for e in errors)


def test_story_011_keywords_constant_and_helper() -> None:
    assert "whirlwind" in STORY_011_EVENT_KEYWORDS
    assert "trinavarta" in STORY_011_EVENT_KEYWORDS
    ok = validate_event_relevance_keywords(
        "011",
        must_include=["Tṛṇāvarta the whirlwind", "baby Krishna rising"],
        central_scene="Whirlwind lifts Krishna",
    )
    assert ok == []
    bad = validate_event_relevance_keywords(
        "011",
        must_include=["Mother Yasoda cradles the baby"],
        central_scene="Only mother and child in a quiet room",
    )
    assert bad


def test_story_020_keywords_constant_and_helper() -> None:
    assert "aghasura" in STORY_020_EVENT_KEYWORDS
    assert "cave" in STORY_020_EVENT_KEYWORDS or "serpent" in STORY_020_EVENT_KEYWORDS
    ok = validate_event_relevance_keywords(
        "020",
        must_include=["Aghasura serpent cave", "Krishna protects the boys"],
        central_scene="Protection inside the cave mouth",
    )
    assert ok == []
    bad = validate_event_relevance_keywords(
        "020",
        must_include=["calves in a sunny meadow"],
        central_scene="Gentle pasture scene only",
    )
    assert bad


def test_other_stories_skip_event_override() -> None:
    assert (
        validate_event_relevance_keywords(
            "012",
            must_include=["Mother Yasoda"],
            central_scene="Quiet home scene",
        )
        == []
    )


def test_story_009_keywords_constant_and_helper() -> None:
    assert "putana" in STORY_009_EVENT_KEYWORDS or "pūtanā" in STORY_009_EVENT_KEYWORDS
    ok = validate_event_relevance_keywords(
        "009",
        must_include=["Pūtanā nurse visitor", "baby Krishna"],
        central_scene="Beautiful visitor/nurse offers to hold baby Krishna",
    )
    assert ok == []
    bad = validate_event_relevance_keywords(
        "009",
        must_include=["flowers and cows"],
        central_scene="Peaceful garden picnic only",
    )
    assert bad
