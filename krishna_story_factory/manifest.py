from __future__ import annotations

import json
from datetime import datetime
from zoneinfo import ZoneInfo

from .config import Settings
from .models import PackagePaths, PlanRow, StoryContent, extract_main_story, word_count
from .outputs import FINAL_OUTPUT_FILES


def write_manifest(
    *,
    settings: Settings,
    plan: PlanRow,
    content: StoryContent,
    paths: PackagePaths,
    mode: str,
    quality_status: str,
    quality_errors: list[str],
    quality_warnings: list[str] | None = None,
    audio_source: str = "",
    package_link: str = "",
    drive_status: str = "",
    drive_detail: str = "",
    poster_score: int = 0,
    coloring_score: int = 0,
    reference_used: bool = False,
) -> None:
    now = datetime.now(ZoneInfo(settings.app_timezone)).isoformat(timespec="seconds")
    story_text = paths.story_md.read_text(encoding="utf-8") if paths.story_md.exists() else ""
    main_story_words = word_count(extract_main_story(story_text))
    audio_words = word_count(content.audio_script)
    audio_duration = _mp3_duration(paths.narration_mp3)
    audio_size = paths.narration_mp3.stat().st_size if paths.narration_mp3.exists() else 0
    manifest = {
        "app": "krishna-story-factory",
        "version": "2.0",
        "generated_at": now,
        "chapter_no": plan.chapter_no,
        "slug": plan.slug,
        "title": content.title,
        "source_reference": plan.source_reference,
        "scripture_reference": plan.scripture_reference,
        "age_range": plan.age_range,
        "outputs": list(FINAL_OUTPUT_FILES),
        "metrics": {
            "main_story_words": main_story_words,
            "audio_script_words": audio_words,
            "audio_duration_seconds": audio_duration,
            "audio_bytes": audio_size,
        },
        "images": {
            "model": settings.openai_image_model,
            "quality": settings.openai_image_quality,
            "requested_size": settings.openai_image_size,
            "reference_image_used": reference_used,
            "poster_qa_score": poster_score,
            "coloring_qa_score": coloring_score,
        },
        "quality": {
            "status": quality_status,
            "errors": quality_errors,
            "warnings": quality_warnings or [],
        },
        "package": {
            "package_link": package_link,
            "drive_status": drive_status,
            "drive_detail": drive_detail,
        },
        "queue_transition": "done" if quality_status == "PASS" else "pending",
        "mode": mode,
        "audio_source": audio_source,
    }
    paths.manifest.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")


def _mp3_duration(path) -> float | None:
    try:
        from mutagen.mp3 import MP3

        return round(float(MP3(path).info.length), 1)
    except Exception:
        return None
