from __future__ import annotations

from typing import TYPE_CHECKING

from ..models import PackagePaths, extract_main_story, word_count
from ..outputs import FINAL_OUTPUT_FILES
from .repetition import detect_repetition

if TYPE_CHECKING:
    from ..config import Settings

PRE_PUBLISH_FILES = tuple(n for n in FINAL_OUTPUT_FILES if n != "manifest.json")


def run_quality_checks(
    paths: PackagePaths,
    *,
    mode: str = "test",
    settings: Settings | None = None,
    story_title: str = "",
    poster_score: int = 0,
    coloring_score: int = 0,
    require_manifest: bool = False,
) -> tuple[bool, list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    required = FINAL_OUTPUT_FILES if require_manifest else PRE_PUBLISH_FILES

    for name in required:
        path = paths.root / name
        if not path.exists() or path.stat().st_size <= 0:
            errors.append(f"Missing or empty final file: {name}")

    if paths.story_md.exists():
        story_text = paths.story_md.read_text(encoding="utf-8", errors="ignore")
        story = story_text.lower()
        for section in ["## recap", "## main story", "## moral", "## takeaway", "## five-star challenge"]:
            if section not in story:
                errors.append(f"story.md missing section: {section}")
        main_story = extract_main_story(story_text)
        main_words = word_count(main_story)
        if mode == "prod":
            if main_words < 700:
                errors.append(f"Main Story too short ({main_words} words).")
            if main_words > 1300:
                errors.append(f"Main Story too long ({main_words} words).")
        errors.extend(detect_repetition(main_story, content_type="story").errors)

    if mode == "prod" and paths.narration_mp3.exists():
        size = paths.narration_mp3.stat().st_size
        if size <= 500 * 1024:
            errors.append(f"narration.mp3 too small ({size} bytes).")
        try:
            from mutagen.mp3 import MP3

            duration = float(MP3(paths.narration_mp3).info.length)
            if duration < 180 or duration > 360:
                errors.append(f"Audio duration {duration:.0f}s outside 3–6 minutes.")
        except Exception:
            pass

    if mode == "prod" and settings:
        threshold = settings.image_min_acceptance_score
        if poster_score < threshold:
            errors.append(f"Poster vision score {poster_score} below {threshold}.")
        if coloring_score < threshold:
            errors.append(f"Coloring vision score {coloring_score} below {threshold}.")

    if paths.whatsapp_caption.exists() and story_title:
        caption = paths.whatsapp_caption.read_text(encoding="utf-8")
        if story_title.lower() not in caption.lower():
            errors.append("WhatsApp caption must contain story title.")

    if require_manifest:
        final_names = {p.name for p in paths.root.iterdir() if p.is_file()} if paths.root.exists() else set()
        extra = final_names - set(FINAL_OUTPUT_FILES)
        missing = set(FINAL_OUTPUT_FILES) - final_names
        if extra:
            errors.append(f"Unexpected files in output folder: {sorted(extra)}")
        if missing:
            errors.append(f"Missing final files: {sorted(missing)}")

    return not errors, errors, warnings
