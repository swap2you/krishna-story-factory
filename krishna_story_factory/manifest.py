from __future__ import annotations

import json
from datetime import datetime
from zoneinfo import ZoneInfo

from .config import Settings
from .models import PackagePaths, PlanRow, StoryContent
from .visuals.models import VisualGenerationResult, make_visual_paths


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
    story_source: str,
    audio_source: str,
    image_source: str,
    package_publish_mode: str = "",
    package_link: str = "",
    local_sync_path: str = "",
    drive_status: str = "",
    drive_detail: str = "",
    drive_folder_id: str = "",
    word_search_answer_key: dict[str, str] | None = None,
    image_outputs: dict[str, str] | None = None,
    visual_result: VisualGenerationResult | None = None,
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

    visual_paths = make_visual_paths(paths.root)
    visual_output_map = {
        "visual_brief_json": visual_paths.visual_brief_json,
        "line_art_prompt": visual_paths.line_art_prompt,
        "line_art_raw_png": visual_paths.line_art_raw,
        "line_art_portrait_png": visual_paths.line_art_portrait,
        "coloring_page_png": visual_paths.coloring_page,
        "coloring_page_print_pdf": visual_paths.coloring_page_print_pdf,
        "poster_art_prompt": visual_paths.poster_art_prompt,
        "poster_art_raw_png": visual_paths.poster_art_raw,
        "poster_copy_json": visual_paths.poster_copy_json,
        "story_poster_png": visual_paths.story_poster,
        "story_poster_whatsapp_jpg": visual_paths.story_poster_whatsapp,
        "visual_generation_manifest_json": visual_paths.visual_generation_manifest,
    }
    for key, vpath in visual_output_map.items():
        if vpath.exists() and vpath.stat().st_size > 0:
            outputs[key] = vpath.name

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
            "drive_status": drive_status,
            "drive_detail": drive_detail,
            "drive_folder_id": drive_folder_id,
        },
        "whatsapp": {
            "template_name": settings.whatsapp_template_name,
            "template_language": settings.whatsapp_template_language,
        },
        "activity": {
            "word_search_answer_key": word_search_answer_key or {},
        },
        "visuals": _visuals_block(settings, visual_result, visual_paths),
        "quality": {
            "status": quality_status,
            "errors": quality_errors,
            "warnings": quality_warnings or [],
        },
        "daily_send_guard": "enabled unless --force is passed",
    }
    paths.manifest.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")


def _visuals_block(
    settings: Settings,
    visual_result: VisualGenerationResult | None,
    visual_paths,
) -> dict:
    if visual_result is None and not visual_paths.visual_brief_json.exists():
        return {}
    result = visual_result or VisualGenerationResult()
    if visual_paths.visual_generation_manifest.exists():
        try:
            data = json.loads(visual_paths.visual_generation_manifest.read_text(encoding="utf-8"))
            return {
                "line_art_status": data.get("line_art_status", result.line_art_status),
                "poster_status": data.get("poster_status", result.poster_status),
                "reference_images_used": data.get("reference_images_used", result.reference_images_used),
                "quality_score": data.get("quality_score", result.quality_score),
                "model": data.get("model", result.model or settings.openai_image_model),
                "quality": data.get("quality", result.quality or settings.openai_image_quality),
                "requested_sizes": data.get("requested_sizes", result.requested_sizes),
                "actual_sizes": data.get("actual_sizes", result.actual_sizes),
            }
        except json.JSONDecodeError:
            pass
    return {
        "line_art_status": result.line_art_status,
        "poster_status": result.poster_status,
        "reference_images_used": result.reference_images_used,
        "quality_score": result.quality_score,
        "model": result.model or settings.openai_image_model,
        "quality": result.quality or settings.openai_image_quality,
        "requested_sizes": result.requested_sizes,
        "actual_sizes": result.actual_sizes,
    }
