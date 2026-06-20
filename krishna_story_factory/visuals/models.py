from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class StoryCharacter:
    name: str
    role: str = ""
    appearance: str = ""
    clothing: str = ""
    expression: str = ""
    pose: str = ""
    position_in_scene: str = ""


@dataclass(slots=True)
class StoryBeat:
    sequence: int
    scene: str = ""
    emotion: str = ""
    visual_action: str = ""


@dataclass(slots=True)
class VisualBrief:
    title: str
    short_title: str = ""
    source_reference: str = ""
    age_range: str = "6-13"
    central_scene: str = ""
    setting: str = ""
    time_of_day: str = ""
    main_characters: list[StoryCharacter] = field(default_factory=list)
    key_emotions: list[str] = field(default_factory=list)
    sacred_mood: str = ""
    important_objects: list[str] = field(default_factory=list)
    environment_details: list[str] = field(default_factory=list)
    symbolic_elements: list[str] = field(default_factory=list)
    story_beats: list[StoryBeat] = field(default_factory=list)
    heavenly_message_or_quote: str = ""
    poster_one_liner: str = ""
    poster_supporting_captions: list[str] = field(default_factory=list)
    line_art_focus: str = ""
    poster_focus: str = ""
    must_include: list[str] = field(default_factory=list)
    must_avoid: list[str] = field(default_factory=list)

    def validate(self) -> list[str]:
        errors: list[str] = []
        if not self.title.strip():
            errors.append("Visual brief missing title.")
        if not self.central_scene.strip():
            errors.append("Visual brief missing central_scene.")
        return errors

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "short_title": self.short_title,
            "source_reference": self.source_reference,
            "age_range": self.age_range,
            "central_scene": self.central_scene,
            "setting": self.setting,
            "time_of_day": self.time_of_day,
            "main_characters": [
                {
                    "name": c.name,
                    "role": c.role,
                    "appearance": c.appearance,
                    "clothing": c.clothing,
                    "expression": c.expression,
                    "pose": c.pose,
                    "position_in_scene": c.position_in_scene,
                }
                for c in self.main_characters
            ],
            "key_emotions": self.key_emotions,
            "sacred_mood": self.sacred_mood,
            "important_objects": self.important_objects,
            "environment_details": self.environment_details,
            "symbolic_elements": self.symbolic_elements,
            "story_beats": [
                {
                    "sequence": b.sequence,
                    "scene": b.scene,
                    "emotion": b.emotion,
                    "visual_action": b.visual_action,
                }
                for b in self.story_beats
            ],
            "heavenly_message_or_quote": self.heavenly_message_or_quote,
            "poster_one_liner": self.poster_one_liner,
            "poster_supporting_captions": self.poster_supporting_captions,
            "line_art_focus": self.line_art_focus,
            "poster_focus": self.poster_focus,
            "must_include": self.must_include,
            "must_avoid": self.must_avoid,
        }


@dataclass(slots=True)
class SupportingCaption:
    label: str
    text: str


@dataclass(slots=True)
class PosterCopy:
    title: str
    subtitle: str = ""
    heavenly_quote: str = ""
    one_liner: str = ""
    supporting_captions: list[SupportingCaption] = field(default_factory=list)

    def validate(self) -> list[str]:
        errors: list[str] = []
        if not self.title.strip():
            errors.append("Poster copy missing title.")
        return errors

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "subtitle": self.subtitle,
            "heavenly_quote": self.heavenly_quote,
            "one_liner": self.one_liner,
            "supporting_captions": [{"label": c.label, "text": c.text} for c in self.supporting_captions],
        }


@dataclass(slots=True)
class VisualPaths:
    root: Path
    visual_brief_json: Path
    line_art_prompt: Path
    line_art_raw: Path
    line_art_portrait: Path
    coloring_page: Path
    coloring_page_print_pdf: Path
    poster_art_prompt: Path
    poster_art_raw: Path
    poster_copy_json: Path
    story_poster: Path
    story_poster_whatsapp: Path
    visual_generation_manifest: Path


@dataclass(slots=True)
class VisualGenerationResult:
    line_art_status: str = "SKIPPED"
    poster_status: str = "SKIPPED"
    reference_images_used: bool = False
    quality_score: int = 0
    model: str = ""
    quality: str = ""
    requested_sizes: dict[str, str] = field(default_factory=dict)
    actual_sizes: dict[str, str] = field(default_factory=dict)
    issues: list[str] = field(default_factory=list)
    dry_run: bool = False


def make_visual_paths(output_dir: Path) -> VisualPaths:
    output_dir.mkdir(parents=True, exist_ok=True)
    return VisualPaths(
        root=output_dir,
        visual_brief_json=output_dir / "visual_brief.json",
        line_art_prompt=output_dir / "line_art_prompt.txt",
        line_art_raw=output_dir / "line_art_raw.png",
        line_art_portrait=output_dir / "line_art_portrait.png",
        coloring_page=output_dir / "coloring_page.png",
        coloring_page_print_pdf=output_dir / "coloring_page_print.pdf",
        poster_art_prompt=output_dir / "poster_art_prompt.txt",
        poster_art_raw=output_dir / "poster_art_raw.png",
        poster_copy_json=output_dir / "poster_copy.json",
        story_poster=output_dir / "story_poster.png",
        story_poster_whatsapp=output_dir / "story_poster_whatsapp.jpg",
        visual_generation_manifest=output_dir / "visual_generation_manifest.json",
    )
