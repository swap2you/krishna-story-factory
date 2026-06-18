from __future__ import annotations

import json
from typing import TYPE_CHECKING

from ..models import PackagePaths

if TYPE_CHECKING:
    from ..config import Settings

REQUIRED_FILES = [
    "story_md",
    "audio_script",
    "whatsapp_caption",
    "activity_sheet",
    "story_card",
    "image_prompt",
    "line_art_prompt",
    "parent_notes",
    "manifest",
    "narration_mp3",
]


def run_quality_checks(
    paths: PackagePaths,
    *,
    mode: str = "test",
    settings: Settings | None = None,
) -> tuple[bool, list[str]]:
    errors: list[str] = []
    path_map = {name: getattr(paths, name) for name in REQUIRED_FILES}

    for name, path in path_map.items():
        if not path.exists():
            errors.append(f"Missing file: {name} -> {path.name}")
        elif path.stat().st_size <= 0:
            errors.append(f"Empty file: {name} -> {path.name}")

    if paths.story_md.exists():
        story_text = paths.story_md.read_text(encoding="utf-8", errors="ignore")
        story = story_text.lower()
        for section in ["## recap", "## main story", "## moral", "## takeaway", "## five-star challenge"]:
            if section not in story:
                errors.append(f"story.md missing section: {section}")
        story_words = story.split()
        if len(story_words) < 200:
            errors.append("story.md appears too short for ages 6-12 bedtime story package.")
        if len(story_words) > 2400:
            errors.append("story.md appears too long for ages 6-12 bedtime story package.")
        banned = ["graphic violence", "romantic detail", "adult theme"]
        for phrase in banned:
            if phrase in story:
                errors.append(f"story.md contains disallowed phrase marker: {phrase}")

    if paths.whatsapp_caption.exists():
        caption = paths.whatsapp_caption.read_text(encoding="utf-8", errors="ignore").strip()
        if not caption:
            errors.append("WhatsApp caption is blank.")
        if len(caption) > 3500:
            errors.append("WhatsApp caption is too long for practical delivery.")

    if paths.narration_mp3.exists() and paths.narration_mp3.stat().st_size <= 0:
        errors.append("MP3 does not exist or is empty.")

    if mode == "prod" and settings and settings.elevenlabs_enabled and not settings.allow_placeholder_audio:
        from ..audio.tts import AudioGenerator

        if AudioGenerator.is_placeholder_mp3(paths.narration_mp3):
            errors.append("narration.mp3 is placeholder but ElevenLabs is enabled in prod mode.")

    if not paths.story_card.exists() and not paths.image_prompt.exists():
        errors.append("Either story_card.png or image_prompt.txt must exist.")

    if paths.manifest.exists():
        try:
            data = json.loads(paths.manifest.read_text(encoding="utf-8"))
            for field in ["source_reference", "library_id", "age_range", "generated_at"]:
                if not data.get(field):
                    errors.append(f"manifest.json missing {field}.")
            age = str(data.get("age_range", ""))
            if age not in {"6-12", "7-11"}:
                errors.append("manifest.json age_range must be 6-12 (or legacy 7-11).")
            for src_field in ["story_source", "audio_source", "image_source"]:
                if not data.get("generation", {}).get(src_field):
                    errors.append(f"manifest.json missing generation.{src_field}.")
        except json.JSONDecodeError as exc:
            errors.append(f"manifest.json is invalid JSON: {exc}")
    else:
        errors.append("manifest.json missing source reference because manifest is absent.")

    return not errors, errors
