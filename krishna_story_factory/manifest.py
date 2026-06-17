from __future__ import annotations

import json
from datetime import datetime
from zoneinfo import ZoneInfo

from .config import Settings
from .models import PackagePaths, PlanRow, StoryContent


def write_manifest(
    *,
    settings: Settings,
    plan: PlanRow,
    content: StoryContent,
    paths: PackagePaths,
    mode: str,
    quality_status: str,
    quality_errors: list[str],
    image_mode: str,
    audio_mode: str,
) -> None:
    now = datetime.now(ZoneInfo(settings.app_timezone)).isoformat(timespec="seconds")
    manifest = {
        "app": "krishna-story-factory",
        "version": "1.0-buildpack",
        "mode": mode,
        "generated_at": now,
        "created_at": now,
        "chapter_no": plan.chapter_no,
        "slug": plan.slug,
        "title": content.title,
        "library_id": plan.library_id,
        "age_range": plan.age_range or "7-11",
        "package_type": plan.package_type,
        "source_reference": plan.source_reference,
        "scripture_reference": plan.scripture_reference,
        "summary_seed": plan.summary_seed,
        "devotional_focus": plan.devotional_focus,
        "activity_type": plan.activity_type,
        "outputs": {
            "story_md": paths.story_md.name,
            "audio_script": paths.audio_script.name,
            "whatsapp_caption": paths.whatsapp_caption.name,
            "activity_sheet_pdf": paths.activity_sheet.name,
            "story_card_png": paths.story_card.name,
            "image_prompt": paths.image_prompt.name,
            "parent_notes": paths.parent_notes.name,
            "manifest_json": paths.manifest.name,
            "narration_mp3": paths.narration_mp3.name,
        },
        "generation": {
            "text_provider": "mock" if mode == "test" or not settings.openai_text_enabled else "openai",
            "text_model": settings.openai_text_model,
            "audio_provider": audio_mode,
            "audio_model": settings.elevenlabs_model_id,
            "image_provider": image_mode,
            "image_model": settings.openai_image_model,
        },
        "quality": {"status": quality_status, "errors": quality_errors},
        "daily_send_guard": "enabled unless --force is passed",
    }
    paths.manifest.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
