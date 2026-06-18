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
    story_source: str,
    audio_source: str,
    image_source: str,
    package_publish_mode: str = "",
    package_link: str = "",
    local_sync_path: str = "",
    word_search_answer_key: dict[str, str] | None = None,
    image_outputs: dict[str, str] | None = None,
) -> None:
    now = datetime.now(ZoneInfo(settings.app_timezone)).isoformat(timespec="seconds")
    outputs = {
        "story_md": paths.story_md.name,
        "audio_script": paths.audio_script.name,
        "whatsapp_caption": paths.whatsapp_caption.name,
        "activity_sheet_pdf": paths.activity_sheet.name,
        "story_card_png": paths.story_card.name,
        "image_prompt": paths.image_prompt.name,
        "hero_image_prompt": paths.hero_image_prompt.name,
        "story_card_square_prompt": paths.story_card_square_prompt.name,
        "story_card_wide_prompt": paths.story_card_wide_prompt.name,
        "line_art_prompt": paths.line_art_prompt.name,
        "coloring_page_prompt": paths.coloring_page_prompt.name,
        "parent_notes": paths.parent_notes.name,
        "manifest_json": paths.manifest.name,
        "narration_mp3": paths.narration_mp3.name,
    }
    if paths.story_card_square.exists():
        outputs["story_card_square_png"] = paths.story_card_square.name
    if paths.story_card_wide.exists():
        outputs["story_card_wide_png"] = paths.story_card_wide.name
    if paths.coloring_page.exists():
        outputs["coloring_page_png"] = paths.coloring_page.name
    if paths.ambient_prompt.exists():
        outputs["ambient_prompt"] = paths.ambient_prompt.name

    manifest = {
        "app": "krishna-story-factory",
        "version": "1.1",
        "mode": mode,
        "generated_at": now,
        "created_at": now,
        "project": plan.project,
        "chapter_no": plan.chapter_no,
        "slug": plan.slug,
        "title": content.title,
        "library_id": plan.library_id,
        "age_range": plan.age_range or "6-12",
        "package_type": plan.package_type,
        "source_reference": plan.source_reference,
        "scripture_reference": plan.scripture_reference,
        "summary_seed": plan.summary_seed,
        "outputs": outputs,
        "generation": {
            "story_source": story_source,
            "audio_source": audio_source,
            "image_source": image_source,
            "text_model": settings.openai_text_model,
            "audio_model": settings.elevenlabs_model_id,
            "image_model": settings.openai_image_model,
            "image_outputs": image_outputs or {},
        },
        "package": {
            "publish_mode": package_publish_mode or settings.package_publish_mode,
            "package_link": package_link,
            "local_sync_path": local_sync_path,
            "google_drive_folder_id": settings.google_drive_folder_id,
        },
        "activity": {
            "word_search_answer_key": word_search_answer_key or {},
        },
        "quality": {"status": quality_status, "errors": quality_errors},
        "daily_send_guard": "enabled unless --force is passed",
    }
    paths.manifest.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
