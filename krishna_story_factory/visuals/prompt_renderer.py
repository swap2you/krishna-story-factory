from __future__ import annotations

from ..prompts_loader import load_project_text
from .models import VisualBrief


def _character_block(brief: VisualBrief) -> str:
    lines: list[str] = []
    for char in brief.main_characters:
        parts = [
            char.name,
            char.role,
            char.appearance,
            char.clothing,
            char.expression,
            char.pose,
            char.position_in_scene,
        ]
        lines.append(" — ".join(p for p in parts if p))
    return "\n".join(lines) if lines else "Characters as described in the central scene."


def _list_block(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items if item)


def _beats_summary(brief: VisualBrief) -> str:
    parts = []
    for beat in sorted(brief.story_beats, key=lambda b: b.sequence)[:3]:
        parts.append(beat.scene or beat.visual_action)
    return " → ".join(p for p in parts if p) or brief.central_scene


def _reference_note(use_reference: bool) -> str:
    if not use_reference:
        return ""
    return (
        "STYLE REFERENCE NOTE: An optional approved reference image guides layout richness, line quality, "
        "lighting, and devotional mood only. The current story content must override reference people, "
        "composition, title, and quotation. Do not copy the reference literally."
    )


def render_line_art_prompt(
    project_root,
    brief: VisualBrief,
    *,
    use_reference: bool = False,
) -> str:
    template = load_project_text(project_root, "prompts/visuals/02_line_art_portrait.md")
    replacements = {
        "{{central_scene}}": brief.central_scene,
        "{{setting}}": brief.setting,
        "{{environment_details}}": _list_block(brief.environment_details),
        "{{character_descriptions}}": _character_block(brief),
        "{{key_emotions}}": ", ".join(brief.key_emotions) or brief.sacred_mood,
        "{{must_include}}": _list_block(brief.must_include),
        "{{must_avoid}}": _list_block(brief.must_avoid),
        "{{reference_style_note}}": _reference_note(use_reference),
        "{{title}}": brief.title,
    }
    rendered = template
    for key, value in replacements.items():
        rendered = rendered.replace(key, value)
    return rendered.strip()


def render_poster_art_prompt(
    project_root,
    brief: VisualBrief,
    *,
    use_reference: bool = False,
) -> str:
    template = load_project_text(project_root, "prompts/visuals/03_cinematic_poster_art.md")
    replacements = {
        "{{central_scene}}": brief.central_scene,
        "{{setting}}": brief.setting,
        "{{environment_details}}": _list_block(brief.environment_details),
        "{{character_descriptions}}": _character_block(brief),
        "{{key_emotions}}": ", ".join(brief.key_emotions),
        "{{sacred_mood}}": brief.sacred_mood,
        "{{story_beats_summary}}": _beats_summary(brief),
        "{{symbolic_elements}}": _list_block(brief.symbolic_elements),
        "{{must_include}}": _list_block(brief.must_include),
        "{{must_avoid}}": _list_block(brief.must_avoid),
        "{{reference_style_note}}": _reference_note(use_reference),
        "{{title}}": brief.title,
    }
    rendered = template
    for key, value in replacements.items():
        rendered = rendered.replace(key, value)
    return rendered.strip()
