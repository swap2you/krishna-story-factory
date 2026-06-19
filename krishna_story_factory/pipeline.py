from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

from .audio.tts import AudioGenerator
from .config import Settings
from .content.caption import format_whatsapp_caption
from .csv_store import already_sent_today, append_storage_log, append_story_log, read_next_pending, update_plan_status
from .generation.source_guard import run_source_guard
from .generation.story_generator import StoryGenerator
from .image.story_card import StoryCardGenerator
from .manifest import write_manifest
from .models import SendResult
from .paths import make_package_paths
from .pdf.activity_sheet import ActivitySheetGenerator
from .publish.drive_sync import publish_package, resolve_package_link
from .quality.checks import run_quality_checks
from .senders import build_sender


class PipelineError(RuntimeError):
    pass


def run_daily_story(settings: Settings, *, mode: str, force: bool = False) -> dict[str, str]:
    plan = read_next_pending(settings.project_root)
    if not plan:
        return {"status": "NO_PENDING_STORY", "detail": "No pending row found in input/series_plan.csv."}

    paths = make_package_paths(settings.output_root, plan)
    now = datetime.now(ZoneInfo(settings.app_timezone))
    errors: list[str] = []
    quality_status = "UNKNOWN"
    send_result = SendResult(status="NOT_ATTEMPTED", detail="WhatsApp send disabled.")
    story_source = "deterministic_test" if mode == "test" or not settings.openai_text_enabled else "openai"
    package_link = resolve_package_link(settings)
    word_search_answer_key: dict[str, str] = {}
    image_outputs: dict[str, str] = {}
    publish_result = None

    try:
        content = StoryGenerator(settings, mode).generate(plan)

        guard_errors = run_source_guard(plan, content)
        if guard_errors:
            raise PipelineError(" | ".join(guard_errors))

        paths.story_md.write_text(content.to_markdown(), encoding="utf-8")
        paths.audio_script.write_text(content.audio_script, encoding="utf-8")
        paths.image_prompt.write_text(content.image_prompt, encoding="utf-8")
        paths.hero_image_prompt.write_text(content.hero_image_prompt or content.image_prompt, encoding="utf-8")
        paths.story_card_square_prompt.write_text(
            content.story_card_square_prompt or content.image_prompt,
            encoding="utf-8",
        )
        paths.story_card_wide_prompt.write_text(
            content.story_card_wide_prompt or content.story_card_square_prompt or content.image_prompt,
            encoding="utf-8",
        )
        paths.line_art_prompt.write_text(content.line_art_prompt, encoding="utf-8")
        paths.coloring_page_prompt.write_text(
            content.coloring_page_prompt or content.line_art_prompt,
            encoding="utf-8",
        )
        paths.parent_notes.write_text(content.parent_notes, encoding="utf-8")

        if settings.enable_ambient_audio and settings.elevenlabs_sfx_enabled:
            ambient_prompt = (
                f"Soft peaceful night ambience for Krishna Book bedtime story: {content.title}. "
                "Gentle temple bells far away, calm night breeze, no voices, child-safe."
            )
            paths.ambient_prompt.write_text(ambient_prompt, encoding="utf-8")

        audio_source = AudioGenerator(settings, mode).generate_mp3(content.audio_script, paths.narration_mp3)
        image_outputs = StoryCardGenerator(settings, mode).generate_all(content, paths, plan=plan)
        image_source = image_outputs.get("story_card", "fallback")

        puzzle = ActivitySheetGenerator().generate(
            plan,
            content,
            paths.activity_sheet,
            coloring_page_path=paths.coloring_page if paths.coloring_page.exists() else None,
        )
        word_search_answer_key = puzzle.answer_key

        publish_result = publish_package(settings, plan, paths)
        package_link = publish_result.package_link or package_link
        paths.whatsapp_caption.write_text(
            format_whatsapp_caption(story_title=content.title, package_link=package_link),
            encoding="utf-8",
        )

        append_storage_log(
            settings.project_root,
            {
                "date": now.date().isoformat(),
                "chapter_no": plan.chapter_no,
                "slug": plan.slug,
                "mode": mode,
                "status": publish_result.drive_status,
                "detail": publish_result.drive_detail,
                "folder_link": package_link,
                "created_at": now.isoformat(timespec="seconds"),
            },
        )

        write_manifest(
            settings=settings,
            plan=plan,
            content=content,
            paths=paths,
            mode=mode,
            quality_status="PENDING",
            quality_errors=[],
            story_source=story_source,
            audio_source=audio_source,
            image_source=image_source,
            package_publish_mode=publish_result.publish_mode,
            package_link=package_link,
            local_sync_path=publish_result.local_sync_path,
            drive_status=publish_result.drive_status,
            drive_detail=publish_result.drive_detail,
            drive_folder_id=publish_result.drive_folder_id,
            word_search_answer_key=word_search_answer_key,
            image_outputs=image_outputs,
        )

        ok, quality_errors, quality_warnings = run_quality_checks(
            paths,
            mode=mode,
            settings=settings,
            word_search_answer_key=word_search_answer_key,
            story_title=content.title,
        )
        quality_status = "PASS" if ok else "FAIL"
        if quality_errors:
            errors.extend(quality_errors)
        if quality_warnings:
            for warning in quality_warnings:
                errors.append(f"WARNING: {warning}")

        write_manifest(
            settings=settings,
            plan=plan,
            content=content,
            paths=paths,
            mode=mode,
            quality_status=quality_status,
            quality_errors=quality_errors,
            quality_warnings=quality_warnings,
            story_source=story_source,
            audio_source=audio_source,
            image_source=image_source,
            package_publish_mode=publish_result.publish_mode,
            package_link=package_link,
            local_sync_path=publish_result.local_sync_path,
            drive_status=publish_result.drive_status,
            drive_detail=publish_result.drive_detail,
            drive_folder_id=publish_result.drive_folder_id,
            word_search_answer_key=word_search_answer_key,
            image_outputs=image_outputs,
        )

        if not ok:
            raise PipelineError("Quality checks failed. See tracking/story_log.csv and manifest.json.")

        if settings.whatsapp_send_enabled and mode == "prod":
            if already_sent_today(settings.project_root, settings.app_timezone) and not force:
                send_result = SendResult(
                    status="SKIPPED_DAILY_LIMIT",
                    detail="A story was already sent today. Use --force to override.",
                )
            else:
                send_result = build_sender(settings).send(
                    settings=settings,
                    paths=paths,
                    mode=mode,
                    plan=plan,
                    content=content,
                    package_link=package_link,
                )

        update_plan_status(settings.project_root, plan, "done")
        status = "SUCCESS"
    except Exception as exc:
        status = "FAILED"
        errors.append(str(exc))

    append_story_log(
        settings.project_root,
        {
            "date": now.date().isoformat(),
            "chapter_no": plan.chapter_no,
            "slug": plan.slug,
            "title": plan.title,
            "output_dir": str(paths.root),
            "status": status,
            "quality_status": quality_status,
            "whatsapp_status": send_result.status,
            "sender_type": settings.whatsapp_sender_type,
            "manifest_path": str(paths.manifest),
            "created_at": now.isoformat(timespec="seconds"),
            "errors": " | ".join(errors),
        },
    )

    if status == "FAILED":
        result = {
            "status": status,
            "output_dir": str(paths.root),
            "quality_status": quality_status,
            "whatsapp_status": send_result.status,
            "errors": " | ".join(errors),
        }
        if send_result.failure_reason:
            result["whatsapp_failure_reason"] = send_result.failure_reason
        return result

    result = {
        "status": status,
        "output_dir": str(paths.root),
        "quality_status": quality_status,
        "whatsapp_status": send_result.status,
        "detail": send_result.detail,
        "package_link": package_link,
        "drive_upload_status": publish_result.drive_status if publish_result else "",
        "whatsapp_template": settings.whatsapp_template_name,
    }
    if send_result.failure_reason:
        result["whatsapp_failure_reason"] = send_result.failure_reason
    return result
