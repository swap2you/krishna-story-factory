from __future__ import annotations

import json
import re
from typing import TYPE_CHECKING

from ..models import PackagePaths
from .repetition import detect_repetition

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

_MIN_MAIN_STORY_WORDS = {"test": 200, "prod": 750}
_MAX_MAIN_STORY_WORDS = {"test": 2400, "prod": 1050}
_TOTAL_MARKDOWN_WARNING_WORDS = 1300
_MIN_AUDIO_SCRIPT_WORDS = {"test": 100, "prod": 500}
_MAX_AUDIO_SCRIPT_WORDS = {"test": 2400, "prod": 750}
_MIN_MP3_BYTES_PROD = 250 * 1024


def run_quality_checks(
    paths: PackagePaths,
    *,
    mode: str = "test",
    settings: Settings | None = None,
    word_search_answer_key: dict[str, str] | None = None,
    story_title: str = "",
) -> tuple[bool, list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    path_map = {name: getattr(paths, name) for name in REQUIRED_FILES}

    for name, path in path_map.items():
        if not path.exists():
            errors.append(f"Missing file: {name} -> {path.name}")
        elif path.stat().st_size <= 0:
            errors.append(f"Empty file: {name} -> {path.name}")

    main_story_text = ""
    if paths.story_md.exists():
        story_text = paths.story_md.read_text(encoding="utf-8", errors="ignore")
        story = story_text.lower()
        for section in ["## recap", "## main story", "## moral", "## takeaway", "## five-star challenge"]:
            if section not in story:
                errors.append(f"story.md missing section: {section}")
        story_words = _word_count(story_text)
        main_story_text = _extract_main_story(story_text)
        main_story_words = _word_count(main_story_text) if main_story_text else 0
        min_main = _MIN_MAIN_STORY_WORDS.get(mode, 750)
        max_main = _MAX_MAIN_STORY_WORDS.get(mode, 1050)
        if main_story_text:
            if main_story_words < min_main:
                errors.append(
                    f"Main Story is too short ({main_story_words} words; need at least {min_main})."
                )
            if mode == "prod" and main_story_words > max_main:
                errors.append(
                    f"Main Story is too long ({main_story_words} words; target at most {max_main})."
                )
            errors.extend(detect_repetition(main_story_text, content_type="story").errors)
        elif mode == "prod":
            errors.append("story.md Main Story section could not be parsed for word count.")
        if mode == "prod" and story_words > _TOTAL_MARKDOWN_WARNING_WORDS:
            warnings.append(
                f"Total story.md is {story_words} words (above {_TOTAL_MARKDOWN_WARNING_WORDS} warning threshold)."
            )
        banned = ["graphic violence", "romantic detail", "adult theme"]
        for phrase in banned:
            if phrase in story:
                errors.append(f"story.md contains disallowed phrase marker: {phrase}")

    if paths.audio_script.exists():
        audio_text = paths.audio_script.read_text(encoding="utf-8", errors="ignore")
        audio_words = _word_count(audio_text)
        min_audio = _MIN_AUDIO_SCRIPT_WORDS.get(mode, 500)
        max_audio = _MAX_AUDIO_SCRIPT_WORDS.get(mode, 750)
        if audio_words < min_audio:
            errors.append(f"audio_script.txt is too short ({audio_words} words; need at least {min_audio}).")
        if mode == "prod" and audio_words > max_audio:
            errors.append(f"audio_script.txt is too long ({audio_words} words; target at most {max_audio}).")
        if re.search(r"\[\s*pause\s*\]", audio_text, re.I):
            errors.append("audio_script.txt still contains [pause] markers.")
        errors.extend(detect_repetition(audio_text, content_type="audio").errors)

    if paths.whatsapp_caption.exists():
        caption = paths.whatsapp_caption.read_text(encoding="utf-8", errors="ignore").strip()
        if not caption:
            errors.append("WhatsApp caption is blank.")
        if len(caption) > 3500:
            errors.append("WhatsApp caption is too long for practical delivery.")
        if "group" in caption.lower():
            errors.append('WhatsApp caption must not mention "group".')
        if mode == "prod" and story_title and story_title.lower() not in caption.lower():
            errors.append("WhatsApp caption must contain the story title.")
        if settings and mode == "prod":
            expected_link = settings.package_public_link or settings.google_drive_folder_url
            if expected_link and expected_link not in caption:
                errors.append("WhatsApp caption must contain the package link when Drive URL is configured.")

    if paths.narration_mp3.exists() and paths.narration_mp3.stat().st_size <= 0:
        errors.append("MP3 does not exist or is empty.")

    if mode == "prod" and settings and settings.elevenlabs_enabled and not settings.allow_placeholder_audio:
        from ..audio.tts import AudioGenerator

        if AudioGenerator.is_placeholder_mp3(paths.narration_mp3):
            errors.append("narration.mp3 is placeholder but ElevenLabs is enabled in prod mode.")
        elif paths.narration_mp3.exists():
            size = paths.narration_mp3.stat().st_size
            if size <= _MIN_MP3_BYTES_PROD:
                errors.append(f"narration.mp3 is too small ({size} bytes; need > 250 KB for prod bedtime audio).")

    if not paths.story_card.exists():
        errors.append("story_card.png is required.")

    if settings and (settings.image_generate_coloring_page or settings.image_generate_line_art) and mode == "prod":
        if not paths.coloring_page.exists():
            errors.append("coloring_page.png is required when coloring or line-art visuals are enabled.")

    if mode == "prod" and settings and (settings.image_generate_line_art or settings.image_generate_coloring_page):
        prompt_path = paths.line_art_prompt if settings.image_generate_line_art else paths.coloring_page_prompt
        if prompt_path.exists():
            prompt = prompt_path.read_text(encoding="utf-8", errors="ignore").lower()
            coloring_checks = [
                ("centered composition", ("centered composition", "portrait composition")),
                ("no cropping", ("no cropping",)),
                ("large colorable spaces", ("large colorable spaces",)),
                ("white background", ("white background", "white")),
                ("thick black outlines", ("thick", "outline", "confident")),
                ("cute/sweet expressive faces", ("cute", "sweet expressive faces", "sweet", "expressive faces")),
            ]
            for label, terms in coloring_checks:
                if not any(term in prompt for term in terms):
                    errors.append(f"{prompt_path.name} should describe {label}.")

    if mode == "prod" and paths.story_card_square_prompt.exists():
        card_prompt = paths.story_card_square_prompt.read_text(encoding="utf-8", errors="ignore").lower()
        square_checks = [
            ("devotional style", ("devotional",)),
            ("cinematic style", ("cinematic",)),
            ("ultra-realistic or 3D style", ("ultra-realistic", "ultra realistic", "3d")),
            ("no modern objects", ("no modern objects",)),
            ("not crowded or clear focal scene", ("not crowded", "clear focal")),
        ]
        for label, terms in square_checks:
            if not any(term in card_prompt for term in terms):
                errors.append(f"story_card_square_prompt.txt should describe {label}.")
    elif mode == "prod" and paths.image_prompt.exists():
        card_prompt = paths.image_prompt.read_text(encoding="utf-8", errors="ignore").lower()
        if card_prompt and not any(x in card_prompt for x in ["cinematic", "3d", "devotional", "realistic"]):
            errors.append("story card prompt should describe cinematic/devotional style.")

    if word_search_answer_key is not None and len(word_search_answer_key) < 3:
        errors.append("Activity word-search grid did not place enough words.")

    manifest_data: dict = {}
    if paths.manifest.exists():
        try:
            manifest_data = json.loads(paths.manifest.read_text(encoding="utf-8"))
            for field in ["source_reference", "library_id", "age_range", "generated_at"]:
                if not manifest_data.get(field):
                    errors.append(f"manifest.json missing {field}.")
            age = str(manifest_data.get("age_range", ""))
            if age not in {"6-12", "7-11"}:
                errors.append("manifest.json age_range must be 6-12 (or legacy 7-11).")
            for src_field in ["story_source", "audio_source", "image_source"]:
                if not manifest_data.get("generation", {}).get(src_field):
                    errors.append(f"manifest.json missing generation.{src_field}.")
            if mode == "prod" and settings:
                expected_link = settings.package_public_link or settings.google_drive_folder_url
                package_link = str(manifest_data.get("package", {}).get("package_link", "")).strip()
                if expected_link and not package_link:
                    errors.append("manifest.package.package_link is empty but Drive URL is configured.")
        except json.JSONDecodeError as exc:
            errors.append(f"manifest.json is invalid JSON: {exc}")
    else:
        errors.append("manifest.json missing source reference because manifest is absent.")

    return not errors, errors, warnings


def _extract_main_story(story_text: str) -> str:
    lowered = story_text.lower()
    marker = "## main story"
    if marker not in lowered:
        return ""
    start = lowered.index(marker) + len(marker)
    tail = story_text[start:].lstrip(":\n ")
    end_markers = ["## moral", "## takeaway", "## five-star challenge"]
    end = len(tail)
    tail_lower = tail.lower()
    for end_marker in end_markers:
        if end_marker in tail_lower:
            end = min(end, tail_lower.index(end_marker))
    return tail[:end].strip()


def _word_count(text: str) -> int:
    return len(re.findall(r"\b[\w']+\b", text))


def _mp3_duration_seconds(path) -> float | None:
    try:
        from mutagen.mp3 import MP3

        return float(MP3(path).info.length)
    except Exception:
        return None
