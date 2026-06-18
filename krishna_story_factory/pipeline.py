from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

from .audio.tts import AudioGenerator
from .config import Settings
from .csv_store import already_sent_today, append_story_log, read_next_pending, update_plan_status
from .generation.story_generator import StoryGenerator
from .image.story_card import StoryCardGenerator
from .manifest import write_manifest
from .models import SendResult
from .paths import make_package_paths
from .pdf.activity_sheet import ActivitySheetGenerator
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

    try:
        content = StoryGenerator(settings, mode).generate(plan)

        paths.story_md.write_text(content.to_markdown(), encoding="utf-8")
        paths.audio_script.write_text(content.audio_script, encoding="utf-8")
        paths.whatsapp_caption.write_text(content.whatsapp_caption, encoding="utf-8")
        paths.image_prompt.write_text(content.image_prompt, encoding="utf-8")
        paths.line_art_prompt.write_text(content.line_art_prompt, encoding="utf-8")
        paths.coloring_page_prompt.write_text(content.line_art_prompt, encoding="utf-8")
        paths.parent_notes.write_text(content.parent_notes, encoding="utf-8")

        audio_source = AudioGenerator(settings, mode).generate_mp3(content.audio_script, paths.narration_mp3)
        image_source = StoryCardGenerator(settings, mode).generate(content, paths.story_card, plan=plan)
        ActivitySheetGenerator().generate(plan, content, paths.activity_sheet)

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
        )

        ok, quality_errors = run_quality_checks(paths, mode=mode, settings=settings)
        quality_status = "PASS" if ok else "FAIL"
        if quality_errors:
            errors.extend(quality_errors)

        write_manifest(
            settings=settings,
            plan=plan,
            content=content,
            paths=paths,
            mode=mode,
            quality_status=quality_status,
            quality_errors=quality_errors,
            story_source=story_source,
            audio_source=audio_source,
            image_source=image_source,
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
        return {
            "status": status,
            "output_dir": str(paths.root),
            "quality_status": quality_status,
            "whatsapp_status": send_result.status,
            "errors": " | ".join(errors),
        }

    return {
        "status": status,
        "output_dir": str(paths.root),
        "quality_status": quality_status,
        "whatsapp_status": send_result.status,
        "detail": send_result.detail,
    }
