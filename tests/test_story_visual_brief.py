from __future__ import annotations

import json
from pathlib import Path

import pytest

from krishna_story_factory.config import load_settings
from krishna_story_factory.visuals.models import StoryCharacter, VisualBrief
from krishna_story_factory.visuals.story_visual_brief import (
    VisualBriefError,
    generate_visual_brief,
    load_visual_brief_json,
    visual_brief_from_dict,
)


def test_visual_brief_json_parses() -> None:
    data = {
        "title": "Sample Story",
        "central_scene": "A chariot pauses at the palace gate.",
        "main_characters": [{"name": "Hero", "role": "protagonist"}],
    }
    brief = visual_brief_from_dict(data)
    assert brief.title == "Sample Story"
    assert brief.main_characters[0].name == "Hero"


def test_visual_brief_rejects_missing_title() -> None:
    brief = VisualBrief(title="", central_scene="Scene")
    assert "missing title" in brief.validate()[0].lower()


def test_visual_brief_rejects_empty_central_scene() -> None:
    brief = VisualBrief(title="Title", central_scene="")
    assert "central_scene" in brief.validate()[0]


def test_load_visual_brief_json(tmp_path: Path) -> None:
    path = tmp_path / "visual_brief.json"
    path.write_text(
        json.dumps({"title": "T", "central_scene": "Scene"}),
        encoding="utf-8",
    )
    brief = load_visual_brief_json(path)
    assert brief.title == "T"


def test_generate_visual_brief_fallback_without_openai(tmp_path: Path) -> None:
    project = Path(__file__).resolve().parents[1]
    settings = load_settings(project)
    story = "# Test Title\n\n## Main Story\nOnce upon a time in Mathura."
    brief = generate_visual_brief(settings, story)
    assert brief.title
    assert brief.central_scene


def test_visual_brief_from_dict_invalid_raises_on_load(tmp_path: Path) -> None:
    path = tmp_path / "visual_brief.json"
    path.write_text(json.dumps({"title": "", "central_scene": ""}), encoding="utf-8")
    with pytest.raises(VisualBriefError):
        load_visual_brief_json(path)
