from __future__ import annotations

import json
import logging
import shutil
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from .audio.tts import AudioGenerator
from .config import Settings
from .content.caption import format_whatsapp_caption
from .csv_store import (
    acquire_pipeline_lock,
    append_storage_log,
    append_story_log,
    read_next_pending,
    read_plan_by_chapter,
    release_pipeline_lock,
    reset_processing_to_pending,
    update_plan_status,
)
from .generation.story_generator import StoryGenerator
from .images.generator import generate_coloring, generate_poster
from .manifest import write_manifest
from .models import PipelineResult, PlanRow
from .outputs import FINAL_OUTPUT_FILES
from .paths import make_package_paths
from .pdf.activity_sheet import ActivitySheetGenerator
from .quality.checks import run_quality_checks
from .storage.google_drive_uploader import upload_final_package
from .work import cleanup_work, new_work_paths, prune_output_folder

logger = logging.getLogger(__name__)


class PipelineError(RuntimeError):
    pass


def clean_reset_local(project_root: Path) -> None:
    output_root = project_root / "output"
    for item in output_root.iterdir() if output_root.exists() else []:
        if item.name == ".gitkeep":
            continue
        if item.is_dir():
            shutil.rmtree(item, ignore_errors=True)
        else:
            item.unlink(missing_ok=True)
    work_root = project_root / ".work"
    if work_root.exists():
        shutil.rmtree(work_root, ignore_errors=True)
    from .csv_store import reset_series_status, reset_tracking_logs

    reset_tracking_logs(project_root)
    reset_series_status(project_root, [f"{i:03d}" for i in range(1, 11)], status="pending")
    reset_processing_to_pending(project_root)


def run_daily_story(
    settings: Settings,
    *,
    mode: str,
    force: bool = False,
    chapter: str | None = None,
    rebuild: bool = False,
    no_upload: bool = False,
    debug: bool = False,
    clean_reset: bool = False,
) -> dict[str, str | int | bool]:
    if clean_reset:
        clean_reset_local(settings.project_root)

    lock = acquire_pipeline_lock(settings.project_root)
    now = datetime.now(ZoneInfo(settings.app_timezone))
    plan: PlanRow | None = None
    try:
        if chapter:
            plan = read_plan_by_chapter(settings.project_root, chapter)
            if not plan:
                return {"status": "NO_PLAN_ROW", "detail": f"Chapter {chapter} not found."}
            if plan.status == "done" and not (force or rebuild):
                return {"status": "ALREADY_DONE", "detail": f"Chapter {chapter} already completed."}
        else:
            plan = read_next_pending(settings.project_root, rebuild=rebuild)
            if not plan:
                return {"status": "NO_PENDING_STORY", "detail": "No pending row found."}

        update_plan_status(settings.project_root, plan, "processing")
        result = _run_with_repairs(settings, plan, mode=mode, no_upload=no_upload, debug=debug, now=now)
        if result.status == "SUCCESS":
            update_plan_status(settings.project_root, plan, "done")
        else:
            update_plan_status(settings.project_root, plan, "pending")
        append_story_log(
            settings.project_root,
            {
                "date": now.date().isoformat(),
                "chapter_no": plan.chapter_no,
                "slug": plan.slug,
                "title": plan.title,
                "output_dir": result.output_dir,
                "status": result.status,
                "quality_status": result.quality_status,
                "whatsapp_status": result.whatsapp_status,
                "sender_type": settings.whatsapp_sender_type,
                "manifest_path": str(Path(result.output_dir) / "manifest.json") if result.output_dir else "",
                "created_at": now.isoformat(timespec="seconds"),
                "errors": result.errors,
            },
        )
        return {
            "status": result.status,
            "output_dir": result.output_dir,
            "quality_status": result.quality_status,
            "whatsapp_status": result.whatsapp_status,
            "package_link": result.package_link,
            "drive_upload_status": result.drive_status,
            "poster_score": result.poster_score,
            "coloring_score": result.coloring_score,
            "reference_images_used": result.reference_used,
            "detail": result.detail,
            "errors": result.errors,
        }
    except Exception as exc:
        if plan and plan.row_index is not None:
            update_plan_status(settings.project_root, plan, "pending")
        raise PipelineError(str(exc)) from exc
    finally:
        release_pipeline_lock(lock)


def _run_with_repairs(
    settings: Settings,
    plan: PlanRow,
    *,
    mode: str,
    no_upload: bool,
    debug: bool,
    now: datetime,
) -> PipelineResult:
    last_error = ""
    for attempt in range(settings.pipeline_max_repair_attempts):
        try:
            return _run_once(settings, plan, mode=mode, no_upload=no_upload, debug=debug, now=now, attempt=attempt)
        except Exception as exc:
            last_error = str(exc)
            logger.warning("Pipeline attempt %s failed: %s", attempt + 1, last_error)
    return PipelineResult(status="FAILED", errors=last_error)


def _run_once(
    settings: Settings,
    plan: PlanRow,
    *,
    mode: str,
    no_upload: bool,
    debug: bool,
    now: datetime,
    attempt: int,
) -> PipelineResult:
    paths = make_package_paths(settings.output_root, plan)
    if paths.root.exists():
        shutil.rmtree(paths.root, ignore_errors=True)
    paths.root.mkdir(parents=True, exist_ok=True)

    work = new_work_paths(settings.project_root, debug=debug or settings.debug_artifacts)
    content = StoryGenerator(settings, mode).generate(plan)
    content.source_reference = plan.source_reference
    content.scripture_reference = plan.scripture_reference
    content.age_range = plan.age_range
    story_md = content.to_markdown()
    paths.story_md.write_text(story_md, encoding="utf-8")

    audio_source = AudioGenerator(settings, mode).generate_mp3(content.audio_script, paths.narration_mp3)
    _validate_audio(paths.narration_mp3, settings, mode)

    poster_score, poster_ref = generate_poster(
        settings,
        story_md=story_md,
        content=content,
        output_path=paths.story_poster,
        work_candidates=work.poster_candidates,
        work_reviews=work.reviews,
        mode=mode,
    )
    coloring_score, coloring_ref = generate_coloring(
        settings,
        story_md=story_md,
        content=content,
        output_path=paths.coloring_page,
        work_candidates=work.coloring_candidates,
        work_reviews=work.reviews,
        mode=mode,
    )
    reference_used = poster_ref or coloring_ref

    ActivitySheetGenerator().generate(plan, content, paths.activity_sheet)
    package_link = settings.package_public_link or settings.google_drive_folder_url
    paths.whatsapp_caption.write_text(
        format_whatsapp_caption(story_title=content.title, package_link=package_link),
        encoding="utf-8",
    )

    ok, quality_errors, quality_warnings = run_quality_checks(
        paths, mode=mode, settings=settings, story_title=content.title, poster_score=poster_score, coloring_score=coloring_score
    )
    if not ok:
        raise PipelineError(" | ".join(quality_errors))

    write_manifest(
        settings=settings,
        plan=plan,
        content=content,
        paths=paths,
        mode=mode,
        quality_status="PASS",
        quality_errors=quality_errors,
        quality_warnings=quality_warnings,
        audio_source=audio_source,
        package_link=package_link,
        drive_status="PENDING",
        drive_detail="",
        poster_score=poster_score,
        coloring_score=coloring_score,
        reference_used=reference_used,
    )

    drive_status = "SKIPPED"
    drive_detail = "Upload disabled by flag." if no_upload else ""
    if not no_upload and settings.google_drive_upload_enabled:
        upload = upload_final_package(settings, folder_name=paths.root.name, source_dir=paths.root)
        drive_status = upload.status
        drive_detail = upload.detail
        package_link = upload.package_link or package_link
        if upload.status not in {"UPLOADED", "LOCAL_SYNC"}:
            raise PipelineError(f"Drive upload failed: {upload.detail}")
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
                "status": upload.status,
                "detail": upload.detail,
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
        quality_status="PASS",
        quality_errors=quality_errors,
        quality_warnings=quality_warnings,
        audio_source=audio_source,
        package_link=package_link,
        drive_status=drive_status,
        drive_detail=drive_detail,
        poster_score=poster_score,
        coloring_score=coloring_score,
        reference_used=reference_used,
    )

    if not no_upload and settings.google_drive_upload_enabled:
        upload = upload_final_package(settings, folder_name=paths.root.name, source_dir=paths.root)
        package_link = upload.package_link or package_link
        write_manifest(
            settings=settings,
            plan=plan,
            content=content,
            paths=paths,
            mode=mode,
            quality_status="PASS",
            quality_errors=quality_errors,
            quality_warnings=quality_warnings,
            audio_source=audio_source,
            package_link=package_link,
            drive_status=upload.status,
            drive_detail=upload.detail,
            poster_score=poster_score,
            coloring_score=coloring_score,
            reference_used=reference_used,
        )

    ok, quality_errors, quality_warnings = run_quality_checks(
        paths, mode=mode, settings=settings, story_title=content.title, poster_score=poster_score, coloring_score=coloring_score, require_manifest=True
    )
    if not ok:
        raise PipelineError("Post-publish validation failed: " + " | ".join(quality_errors))

    prune_output_folder(paths.root)
    cleanup_work(work, keep=debug or settings.debug_artifacts)

    final_files = [p for p in paths.root.iterdir() if p.is_file()]
    if {p.name for p in final_files} != set(FINAL_OUTPUT_FILES):
        raise PipelineError(f"Final folder must contain exactly 7 files, found: {[p.name for p in final_files]}")

    whatsapp_status = "SKIPPED_DISABLED"
    if settings.whatsapp_send_enabled:
        whatsapp_status = "SKIPPED_RELEASE_SCOPE"

    return PipelineResult(
        status="SUCCESS",
        output_dir=str(paths.root),
        quality_status="PASS",
        whatsapp_status=whatsapp_status,
        package_link=package_link,
        drive_status=drive_status,
        poster_score=poster_score,
        coloring_score=coloring_score,
        reference_used=reference_used,
        detail=drive_detail,
    )


def _validate_audio(path: Path, settings: Settings, mode: str) -> None:
    if mode == "test":
        return
    if not path.exists() or path.stat().st_size <= 500 * 1024:
        raise PipelineError("narration.mp3 missing or below 500 KB.")
    try:
        from mutagen.mp3 import MP3

        duration = float(MP3(path).info.length)
        if duration < 180 or duration > 360:
            raise PipelineError(f"Audio duration {duration:.0f}s outside 3–6 minute window.")
    except ImportError:
        pass
