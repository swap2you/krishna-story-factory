from __future__ import annotations

import json
import re
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
    "coloring_page_prompt",
    "parent_notes",
    "manifest",
    "narration_mp3",
]

_MIN_STORY_WORDS = {"test": 200, "prod": 800}
_MIN_AUDIO_SCRIPT_WORDS = {"test": 100, "prod": 600}
_MIN_MP3_BYTES_PROD = 500 * 1024
_MIN_MP3_DURATION_SECONDS = 4 * 60


def run_quality_checks(
    paths: PackagePaths,
    *,
    mode: str = "test",
    settings: Settings | None = None,
    word_search_answer_key: dict[str, str] | None = None,
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
        story_words = _word_count(story_text)
        min_story = _MIN_STORY_WORDS.get(mode, 800)
        if story_words < min_story:
            errors.append(f"story.md is too short ({story_words} words; need at least {min_story}).")
        if story_words > 2400:
            errors.append("story.md appears too long for ages 6-12 bedtime story package.")
        banned = ["graphic violence", "romantic detail", "adult theme"]
        for phrase in banned:
            if phrase in story:
                errors.append(f"story.md contains disallowed phrase marker: {phrase}")

    if paths.audio_script.exists():
        audio_words = _word_count(paths.audio_script.read_text(encoding="utf-8", errors="ignore"))
        min_audio = _MIN_AUDIO_SCRIPT_WORDS.get(mode, 600)
        if audio_words < min_audio:
            errors.append(f"audio_script.txt is too short ({audio_words} words; need at least {min_audio}).")
        if re.search(r"\[\s*pause\s*\]", paths.audio_script.read_text(encoding="utf-8", errors="ignore"), re.I):
            errors.append("audio_script.txt still contains [pause] markers.")

    if paths.whatsapp_caption.exists():
        caption = paths.whatsapp_caption.read_text(encoding="utf-8", errors="ignore").strip()
        if not caption:
            errors.append("WhatsApp caption is blank.")
        if len(caption) > 3500:
            errors.append("WhatsApp caption is too long for practical delivery.")
        if "group" in caption.lower():
            errors.append('WhatsApp caption must not mention "group".')

    if paths.narration_mp3.exists() and paths.narration_mp3.stat().st_size <= 0:
        errors.append("MP3 does not exist or is empty.")

    if mode == "prod" and settings and settings.elevenlabs_enabled and not settings.allow_placeholder_audio:
        from ..audio.tts import AudioGenerator

        if AudioGenerator.is_placeholder_mp3(paths.narration_mp3):
            errors.append("narration.mp3 is placeholder but ElevenLabs is enabled in prod mode.")
        elif paths.narration_mp3.exists():
            size = paths.narration_mp3.stat().st_size
            if size <= _MIN_MP3_BYTES_PROD:
                errors.append(f"narration.mp3 is too small ({size} bytes; need > 500 KB for prod bedtime audio).")
            duration = _mp3_duration_seconds(paths.narration_mp3)
            if duration is not None and duration < _MIN_MP3_DURATION_SECONDS:
                errors.append(
                    f"narration.mp3 is too short ({duration:.0f}s; need at least {_MIN_MP3_DURATION_SECONDS // 60} minutes)."
                )

    if not paths.story_card.exists() and not paths.image_prompt.exists():
        errors.append("Either story_card.png or image_prompt.txt must exist.")

    if word_search_answer_key is not None and len(word_search_answer_key) < 3:
        errors.append("Activity word-search grid did not place enough words.")

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


def _word_count(text: str) -> int:
    return len(re.findall(r"\b[\w']+\b", text))


def _mp3_duration_seconds(path) -> float | None:
    try:
        from mutagen.mp3 import MP3

        return float(MP3(path).info.length)
    except Exception:
        return None
