from __future__ import annotations

import json
import logging
import shutil
import hashlib
import re
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from .audio.tts import AudioGenerator
from .config import Settings
from .content.caption import format_whatsapp_caption
from .csv_store import (
    acquire_pipeline_lock,
    already_completed_production_today,
    append_run_history,
    append_storage_log,
    append_story_log,
    read_next_pending,
    read_plan_by_chapter,
    release_pipeline_lock,
    reset_processing_to_pending,
    update_plan_status,
)
from .generation.story_generator import StoryGenerator
from .generation.source_guard import run_source_guard
from .images.generator import generate_coloring, generate_poster
from .images.client import ImageClient
from .manifest import update_component_manifest, write_manifest
from .models import PipelineResult, PlanRow, StoryContent
from .outputs import FINAL_OUTPUT_FILES
from .paths import make_package_paths
from .activities.planner import ActivityPlanner
from .pdf.activity_sheet import ActivitySheetGenerator, validate_activity_pdf
from .quality.checks import run_quality_checks
from .storage.google_drive_uploader import (
    ensure_story_folder,
    replace_component_files,
    upload_files_to_folder,
    upload_final_package,
    verify_drive_text_links,
)
from .images.vision_qa import review_image, save_review
from .audio.waveform import WaveformMetrics, validate_mp3_waveform
from .activities.qa import semantic_activity_errors
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
    rebuild_components: set[str] | None = None,
) -> dict[str, str | int | bool]:
    if clean_reset:
        clean_reset_local(settings.project_root)

    lock = acquire_pipeline_lock(settings.project_root)
    now = datetime.now(ZoneInfo(settings.app_timezone))
    plan: PlanRow | None = None
    try:
        normal_prod = mode == "prod" and not force and not rebuild and not rebuild_components
        if normal_prod and already_completed_production_today(settings.project_root, settings.app_timezone):
            detail = "A successful production story already completed today."
            append_run_history(
                settings.project_root,
                {
                    "started_at": now.isoformat(timespec="seconds"),
                    "completed_at": now.isoformat(timespec="seconds"),
                    "status": "SKIPPED_ALREADY_COMPLETED_TODAY",
                    "chapter_no": "",
                    "slug": "",
                    "detail": detail,
                    "exit_code": "0",
                },
            )
            return {
                "status": "SKIPPED_ALREADY_COMPLETED_TODAY",
                "detail": detail,
                "errors": "",
            }

        if chapter:
            plan = read_plan_by_chapter(settings.project_root, chapter)
            if not plan:
                return {"status": "NO_PLAN_ROW", "detail": f"Chapter {chapter} not found."}
            if plan.status == "done" and not (force or rebuild or rebuild_components):
                return {"status": "ALREADY_DONE", "detail": f"Chapter {chapter} already completed."}
        else:
            plan = read_next_pending(settings.project_root, rebuild=rebuild)
            if not plan:
                return {"status": "NO_PENDING_STORY", "detail": "No pending row found."}

        if rebuild_components:
            if rebuild_components != {"activity", "coloring"}:
                return {"status": "INVALID_COMPONENTS", "detail": "This release supports exactly: activity,coloring"}
            return _rebuild_components(settings, plan, mode=mode, no_upload=no_upload, debug=debug, now=now)

        if mode != "test":
            update_plan_status(settings.project_root, plan, "processing")
        result = _run_with_repairs(settings, plan, mode=mode, no_upload=no_upload, debug=debug, now=now)
        if mode != "test":
            if result.status == "SUCCESS":
                update_plan_status(settings.project_root, plan, "done", drive_folder_id=_folder_id(result.package_link))
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
        if mode == "prod":
            append_run_history(
                settings.project_root,
                {
                    "started_at": now.isoformat(timespec="seconds"),
                    "completed_at": datetime.now(ZoneInfo(settings.app_timezone)).isoformat(timespec="seconds"),
                    "status": result.status,
                    "chapter_no": plan.chapter_no,
                    "slug": plan.slug,
                    "detail": result.detail or result.errors,
                    "exit_code": "0" if result.status == "SUCCESS" else "1",
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
        if plan and plan.row_index is not None and not rebuild_components and mode != "test":
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
    output_root = settings.project_root / ".work" / "test_preview" if mode == "test" else settings.output_root
    paths = make_package_paths(output_root, plan)
    if paths.root.exists():
        shutil.rmtree(paths.root, ignore_errors=True)
    paths.root.mkdir(parents=True, exist_ok=True)

    work = new_work_paths(settings.project_root, debug=debug or settings.debug_artifacts)
    content = StoryGenerator(settings, mode).generate(plan)
    content.source_reference = plan.source_reference
    content.scripture_reference = plan.scripture_reference
    content.age_range = plan.age_range
    source_errors = run_source_guard(plan, content)
    if source_errors:
        raise PipelineError("Source-fact validation failed: " + " | ".join(source_errors))
    story_md = content.to_markdown()
    paths.story_md.write_text(story_md, encoding="utf-8")

    audio_gen = AudioGenerator(settings, mode)
    audio_source = audio_gen.generate_mp3(content.audio_script, paths.narration_mp3)
    waveform_metrics = _validate_audio(paths.narration_mp3, settings, mode, low_credit=audio_gen.low_credit_mode)

    poster_score, poster_ref = generate_poster(
        settings,
        story_md=story_md,
        content=content,
        output_path=paths.story_poster,
        work_candidates=work.poster_candidates,
        work_reviews=work.reviews,
        mode=mode,
    )
    coloring_score, poster_content_ref, coloring_style_ref, identity_score = generate_coloring(
        settings,
        story_md=story_md,
        content=content,
        output_path=paths.coloring_page,
        work_candidates=work.coloring_candidates,
        work_reviews=work.reviews,
        poster_path=paths.story_poster,
        mode=mode,
    )
    reference_used = poster_ref or poster_content_ref or coloring_style_ref

    activity_planner = ActivityPlanner(settings.project_root / "tracking" / "activity_history.csv", settings=settings)
    activity = activity_planner.plan(plan, story_md)
    pdf_check = ActivitySheetGenerator().generate(plan, activity, paths.activity_sheet)
    render_dir = work.root / "activity_pages"
    pdf_check = validate_activity_pdf(paths.activity_sheet, render_dir, activity=activity)
    if pdf_check.errors:
        raise PipelineError("Activity PDF validation failed: " + " | ".join(pdf_check.errors))
    activity_score = _review_activity(
        settings, story_md, render_dir, work.reviews, mode, activity=activity, chapter_no=plan.chapter_no, slug=plan.slug,
    )
    if activity_score < 90:
        activity = _repair_activity_pack(settings, plan, story_md, activity, activity_score)
        pdf_check = ActivitySheetGenerator().generate(plan, activity, paths.activity_sheet)
        pdf_check = validate_activity_pdf(paths.activity_sheet, render_dir, activity=activity)
        if pdf_check.errors:
            raise PipelineError("Repaired activity PDF validation failed: " + " | ".join(pdf_check.errors))
        activity_score = _review_activity(
            settings, story_md, render_dir, work.reviews, mode, activity=activity, chapter_no=plan.chapter_no, slug=plan.slug,
        )
        if activity_score < 90:
            raise PipelineError(f"Activity vision score {activity_score} below threshold 90 after repair.")
    will_upload = mode != "test" and not no_upload and settings.google_drive_upload_enabled
    package_link = None if mode == "test" else (settings.package_public_link or settings.google_drive_folder_url)
    drive_folder_id = ""
    if will_upload:
        folder = ensure_story_folder(settings, folder_name=paths.root.name)
        if folder.status != "READY" or not folder.folder_id or not folder.package_link:
            raise PipelineError(f"Drive folder ensure failed: {folder.detail}")
        package_link = folder.package_link
        drive_folder_id = folder.folder_id
    caption = (
        f"TEST PREVIEW — NOT PUBLISHABLE\n\n{content.title}\nNo upload or parent delivery was performed."
        if mode == "test" else
        format_whatsapp_caption(story_title=content.title, package_link=package_link,
            activity_title=activity.activity_title, recommended_send_mode=activity.recommended_send_mode)
    )
    paths.whatsapp_caption.write_text(caption, encoding="utf-8")

    ok, quality_errors, quality_warnings = run_quality_checks(
        paths, mode=mode, settings=settings, story_title=content.title, poster_score=poster_score, coloring_score=coloring_score
    )
    if not ok:
        raise PipelineError(" | ".join(quality_errors))

    initial_drive_status = "SKIPPED" if mode == "test" else ("UPLOADING" if will_upload else "PENDING")
    if no_upload and mode != "test":
        initial_drive_status = "SKIPPED"
    write_manifest(
        settings=settings,
        plan=plan,
        content=content,
        paths=paths,
        mode=mode,
        quality_status="TEST_PASS" if mode == "test" else "PASS",
        quality_errors=quality_errors,
        quality_warnings=quality_warnings,
        audio_source=audio_source,
        package_link=package_link,
        drive_status=initial_drive_status,
        drive_detail="" if will_upload else ("Upload disabled by flag." if no_upload else ""),
        poster_score=poster_score,
        coloring_score=coloring_score,
        reference_used=reference_used,
        activity=activity, activity_page_count=pdf_check.page_count, activity_score=activity_score,
        poster_reference_used=poster_content_ref, style_reference_used=coloring_style_ref,
        identity_consistency_score=identity_score,
        waveform_metrics=waveform_metrics,
    )

    drive_status = "SKIPPED"
    drive_detail = "Upload disabled by flag." if no_upload else ""
    if will_upload:
        upload = upload_files_to_folder(
            settings,
            folder_id=drive_folder_id,
            package_link=package_link or "",
            source_dir=paths.root,
            files=FINAL_OUTPUT_FILES,
            folder_name=paths.root.name,
        )
        if upload.status != "UPLOADED":
            raise PipelineError(f"Drive upload failed: {upload.detail}")
        ok_verify, verify_detail = verify_drive_text_links(
            settings, folder_id=drive_folder_id, package_link=package_link or ""
        )
        if not ok_verify:
            raise PipelineError(f"Drive verify failed after upload: {verify_detail}")
        drive_status = "UPLOADED"
        drive_detail = upload.detail
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
            drive_status="UPLOADED",
            drive_detail=drive_detail,
            poster_score=poster_score,
            coloring_score=coloring_score,
            reference_used=reference_used,
            activity=activity, activity_page_count=pdf_check.page_count, activity_score=activity_score,
            poster_reference_used=poster_content_ref, style_reference_used=coloring_style_ref,
            identity_consistency_score=identity_score,
            waveform_metrics=waveform_metrics,
        )
        paths.whatsapp_caption.write_text(
            format_whatsapp_caption(
                story_title=content.title,
                package_link=package_link,
                activity_title=activity.activity_title,
                recommended_send_mode=activity.recommended_send_mode,
            ),
            encoding="utf-8",
        )
        reupload = upload_files_to_folder(
            settings,
            folder_id=drive_folder_id,
            package_link=package_link or "",
            source_dir=paths.root,
            files=("manifest.json", "whatsapp_caption.txt"),
            folder_name=paths.root.name,
        )
        if reupload.status != "UPLOADED":
            raise PipelineError(f"Drive manifest re-upload failed: {reupload.detail}")
        ok_verify2, verify_detail2 = verify_drive_text_links(
            settings, folder_id=drive_folder_id, package_link=package_link or ""
        )
        if not ok_verify2:
            raise PipelineError(f"Drive verify failed after manifest finalize: {verify_detail2}")
        append_storage_log(
            settings.project_root,
            {
                "date": now.date().isoformat(),
                "chapter_no": plan.chapter_no,
                "slug": plan.slug,
                "mode": mode,
                "status": drive_status,
                "detail": drive_detail,
                "folder_link": package_link,
                "created_at": now.isoformat(timespec="seconds"),
            },
        )
    elif mode != "test" and not no_upload and settings.google_drive_local_sync_root:
        upload = upload_final_package(settings, folder_name=paths.root.name, source_dir=paths.root)
        drive_status = upload.status
        drive_detail = upload.detail
        package_link = upload.package_link or package_link
        if upload.status not in {"UPLOADED", "LOCAL_SYNC"}:
            raise PipelineError(f"Drive upload failed: {upload.detail}")
        paths.whatsapp_caption.write_text(
            format_whatsapp_caption(story_title=content.title, package_link=package_link,
                activity_title=activity.activity_title, recommended_send_mode=activity.recommended_send_mode),
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
        quality_status="TEST_PASS" if mode == "test" else "PASS",
        quality_errors=quality_errors,
        quality_warnings=quality_warnings,
        audio_source=audio_source,
        package_link=package_link,
        drive_status=drive_status if mode != "test" else "SKIPPED",
        drive_detail=drive_detail,
        poster_score=poster_score,
        coloring_score=coloring_score,
        reference_used=reference_used,
        activity=activity, activity_page_count=pdf_check.page_count, activity_score=activity_score,
        poster_reference_used=poster_content_ref, style_reference_used=coloring_style_ref,
        identity_consistency_score=identity_score,
        waveform_metrics=waveform_metrics,
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

    if mode != "test":
        activity_planner.record(plan, activity)

    whatsapp_status = "SKIPPED_DISABLED"
    if settings.whatsapp_send_enabled:
        whatsapp_status = "SKIPPED_RELEASE_SCOPE"

    return PipelineResult(
        status="SUCCESS",
        output_dir=str(paths.root),
        quality_status="TEST_PASS" if mode == "test" else "PASS",
        whatsapp_status=whatsapp_status,
        package_link=package_link,
        drive_status=drive_status,
        poster_score=poster_score,
        coloring_score=coloring_score,
        reference_used=reference_used,
        detail=drive_detail,
    )


def _validate_audio(
    path: Path, settings: Settings, mode: str, *, low_credit: bool = False
) -> WaveformMetrics | None:
    if mode == "test":
        return None
    if not path.exists() or path.stat().st_size <= 500 * 1024:
        raise PipelineError("narration.mp3 missing or below 500 KB.")
    duration: float | None = None
    try:
        from mutagen.mp3 import MP3

        duration = float(MP3(path).info.length)
        min_seconds = 150 if low_credit else 180  # 2.5 min only in low-credit mode
        if duration < min_seconds or duration > 360:
            window = "2.5–6" if low_credit else "3–6"
            raise PipelineError(f"Audio duration {duration:.0f}s outside {window} minute window.")
    except ImportError:
        pass

    metrics = validate_mp3_waveform(path, expected_duration=duration)
    if metrics.status != "PASS":
        raise PipelineError(f"Audio waveform validation failed: {metrics.detail}")
    return metrics


def _rebuild_components(
    settings: Settings, plan: PlanRow, *, mode: str, no_upload: bool, debug: bool, now: datetime
) -> dict[str, str | int | bool]:
    paths = make_package_paths(settings.output_root, plan)
    locked = (paths.story_md, paths.narration_mp3, paths.story_poster, paths.whatsapp_caption)
    missing = [path.name for path in (*locked, paths.manifest) if not path.exists()]
    if missing:
        raise PipelineError(f"Component rebuild requires the existing successful package; missing: {missing}")
    before = {path.name: _sha256(path) for path in locked}
    story_md = paths.story_md.read_text(encoding="utf-8")
    content = _content_from_story_md(story_md, plan)
    work = new_work_paths(settings.project_root, debug=True)
    temp_activity = work.root / "activity_sheet.pdf"
    temp_coloring = work.root / "coloring_page.png"
    planner = ActivityPlanner(settings.project_root / "tracking" / "activity_history.csv", settings=settings)
    activity = planner.plan(plan, story_md)
    ActivitySheetGenerator().generate(plan, activity, temp_activity)
    render_dir = work.root / "activity_pages"
    pdf_check = validate_activity_pdf(temp_activity, render_dir, activity=activity)
    if pdf_check.errors:
        raise PipelineError("Activity PDF validation failed: " + " | ".join(pdf_check.errors))
    activity_score = _review_activity(
        settings, story_md, render_dir, work.reviews, mode, activity=activity, chapter_no=plan.chapter_no, slug=plan.slug,
    )
    if activity_score < 90:
        activity = _repair_activity_pack(settings, plan, story_md, activity, activity_score)
        ActivitySheetGenerator().generate(plan, activity, temp_activity)
        pdf_check = validate_activity_pdf(temp_activity, render_dir, activity=activity)
        if pdf_check.errors:
            raise PipelineError("Repaired activity PDF validation failed: " + " | ".join(pdf_check.errors))
        activity_score = _review_activity(
            settings, story_md, render_dir, work.reviews, mode, activity=activity, chapter_no=plan.chapter_no, slug=plan.slug,
        )
        if activity_score < 90:
            raise PipelineError(f"Activity vision score {activity_score} below threshold 90 after repair.")
    coloring_score, poster_ref, style_ref, identity_score = generate_coloring(
        settings, story_md=story_md, content=content, output_path=temp_coloring,
        work_candidates=work.coloring_candidates, work_reviews=work.reviews,
        poster_path=paths.story_poster, mode=mode,
    )
    if coloring_score < 90 or identity_score < 90:
        raise PipelineError(f"Coloring score {coloring_score}, identity score {identity_score}; both must be at least 90.")
    temp_activity.replace(paths.activity_sheet)
    temp_coloring.replace(paths.coloring_page)
    update_component_manifest(
        paths.manifest, activity=activity, activity_page_count=pdf_check.page_count,
        activity_score=activity_score, coloring_score=coloring_score,
        identity_consistency_score=identity_score, poster_reference_used=poster_ref,
        style_reference_used=style_ref, drive_status="SKIPPED" if no_upload else "PENDING_COMPONENT_REPLACE",
        drive_detail="Upload disabled by flag." if no_upload else "",
        coloring_model=ImageClient(settings).model, model_override=ImageClient(settings).model_override,
    )
    upload = None
    if not no_upload:
        upload = replace_component_files(settings, source_dir=paths.root, manifest_path=paths.manifest)
        if upload.status == "SKIPPED":
            update_component_manifest(
                paths.manifest, activity=activity, activity_page_count=pdf_check.page_count,
                activity_score=activity_score, coloring_score=coloring_score,
                identity_consistency_score=identity_score, poster_reference_used=poster_ref,
                style_reference_used=style_ref, drive_status=upload.status, drive_detail=upload.detail,
                coloring_model=ImageClient(settings).model, model_override=ImageClient(settings).model_override,
            )
        if upload.status not in {"UPLOADED", "LOCAL_SYNC", "SKIPPED"}:
            raise PipelineError(upload.detail)
    after = {path.name: _sha256(path) for path in locked}
    if before != after:
        raise PipelineError("Locked package files changed during component-only rebuild.")
    final_names = {path.name for path in paths.root.iterdir() if path.is_file()}
    if final_names != set(FINAL_OUTPUT_FILES):
        raise PipelineError(f"Final folder must contain exactly 7 files, found: {sorted(final_names)}")
    planner.record(plan, activity)
    cleanup_work(work, keep=debug or settings.debug_artifacts)
    return {
        "status": "SUCCESS", "output_dir": str(paths.root), "quality_status": "PASS",
        "whatsapp_status": "SKIPPED_COMPONENT_REBUILD", "activity_type": activity.activity_type,
        "activity_title": activity.activity_title, "activity_score": activity_score,
        "activity_pages": pdf_check.page_count, "coloring_score": coloring_score,
        "identity_consistency_score": identity_score,
        "drive_upload_status": upload.status if upload else "SKIPPED",
        "drive_detail": upload.detail if upload else "Upload disabled by flag.",
        "final_file_count": len(final_names), "queue_unchanged": True,
    }


def _repair_activity_pack(settings: Settings, plan: PlanRow, story_md: str, activity, score: int):
    """One-shot repair for weak activity packs; falls back to deterministic preferred/dynamic pack."""
    import json
    import re

    from .activities.models import pack_from_dict
    from .prompts_loader import load_project_text

    if settings.openai_api_key and getattr(settings, "openai_text_enabled", False):
        try:
            from openai import OpenAI

            repair = load_project_text(settings.project_root, "prompts/activity_bank/08_ACTIVITY_REPAIR.md")
            prompt = (
                f"{repair}\n\nQA_SCORE: {score}\n"
                f"CURRENT_PACK_JSON:\n{json.dumps(activity.to_dict(), ensure_ascii=True)}\n\n"
                f"STORY.MD:\n{story_md[:6000]}\n\n"
                "Return only repaired ActivityPack JSON."
            )
            client = OpenAI(api_key=settings.openai_api_key)
            response = client.responses.create(model=settings.openai_text_model, input=prompt)
            raw = getattr(response, "output_text", "") or ""
            try:
                data = json.loads(raw)
            except json.JSONDecodeError:
                match = re.search(r"\{.*\}", raw, re.DOTALL)
                if not match:
                    raise ValueError("No JSON object found.")
                data = json.loads(match.group(0))
            pack = pack_from_dict(data)
            pack.validate()
            return pack
        except Exception:
            pass
    planner = ActivityPlanner(settings.project_root / "tracking" / "activity_history.csv", settings=settings)
    return planner.plan(plan, story_md)


def _review_activity(
    settings: Settings, story_md: str, render_dir: Path, reviews_dir: Path, mode: str,
    *, activity=None, chapter_no: str = "", slug: str = "",
) -> int:
    pages = sorted(render_dir.glob("activity_page_*.png"))
    if activity is not None:
        semantic_errors = semantic_activity_errors(activity)
        if semantic_errors:
            _retain_activity_qa_evidence(
                settings,
                chapter_no=chapter_no,
                activity=activity,
                contact_sheet=None,
                review_payload={
                    "score": 0,
                    "issues": semantic_errors,
                    "hard_rejection": True,
                    "hard_rejection_reasons": semantic_errors,
                },
            )
            if mode == "test":
                return 0
            return 0
    if mode == "test" or not settings.openai_api_key:
        return 90
    if not pages:
        return 0
    activity_context = ""
    if activity:
        activity_context = (
            f"\nSELECTED ACTIVITY: {activity.activity_type} - {activity.activity_title}.\n"
            f"LEARNING GOAL: {activity.learning_goal}\nSTORY CONNECTION: {activity.story_connection}\n"
            f"REQUIRED PRINTABLE COMPONENTS: {activity.printable_components}\n"
            "Judge the selected activity against this approved design intent. Do not penalize required prompts as generic "
            "when the page visibly anchors them to the pastime."
        )
    rubric = """Score 0-100: story relevance 20, fun and engagement 20, clarity 15,
printable usability 15, age appropriateness 10, visual layout 10, parent effort/value 10.
Reject generic school worksheets, unclear instructions, small components, blank space, missing cut lines,
incomplete assembly, repetitive or burdensome activities, visible answer keys, or unsafe cutting.""" + activity_context
    contact_sheet = _activity_contact_sheet(pages, reviews_dir / "activity_contact_sheet.png")
    review = review_image(settings, story_md=story_md, image_path=contact_sheet, kind="activity", rubric=rubric)
    save_review(reviews_dir, "activity_final", review)
    _retain_activity_qa_evidence(
        settings,
        chapter_no=chapter_no,
        activity=activity,
        contact_sheet=contact_sheet,
        review_payload={
            "score": review.score,
            "issues": review.issues,
            "hard_rejection": review.hard_rejection,
            "hard_rejection_reasons": review.hard_rejection_reasons,
            "raw": review.raw,
        },
    )
    return review.score


def _retain_activity_qa_evidence(
    settings: Settings,
    *,
    chapter_no: str,
    activity=None,
    contact_sheet: Path | None,
    review_payload: dict,
) -> None:
    chapter = (chapter_no or "unknown").strip() or "unknown"
    qa_dir = settings.project_root / ".work" / "qa" / chapter
    qa_dir.mkdir(parents=True, exist_ok=True)
    (qa_dir / "activity_final.json").write_text(
        json.dumps(review_payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    if activity is not None:
        (qa_dir / "activity_pack.json").write_text(
            json.dumps(activity.to_dict(), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
    if contact_sheet and contact_sheet.exists():
        shutil.copy2(contact_sheet, qa_dir / "activity_contact_sheet.png")


def _activity_contact_sheet(pages: list[Path], output: Path) -> Path:
    from PIL import Image

    opened = [Image.open(page).convert("RGB") for page in pages]
    width = max(image.width for image in opened)
    height = sum(image.height for image in opened)
    canvas = Image.new("RGB", (width, height), "white")
    y = 0
    for image in opened:
        canvas.paste(image, ((width - image.width) // 2, y))
        y += image.height
    output.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output, "PNG")
    return output


def _content_from_story_md(story_md: str, plan: PlanRow) -> StoryContent:
    def section(name: str, next_names: tuple[str, ...]) -> str:
        match = re.search(rf"## {re.escape(name)}\s*\n(.*?)(?=\n## (?:{'|'.join(map(re.escape, next_names))})|\n-->|\Z)", story_md, re.S | re.I)
        return match.group(1).strip() if match else ""
    title_match = re.search(r"^#\s+(.+)$", story_md, re.M)
    coloring = section("Coloring Visual Brief", ("Activity Data",))
    return StoryContent(
        title=title_match.group(1).strip() if title_match else plan.title,
        recap=section("Recap", ("Main Story",)), main_story=section("Main Story", ("Moral",)),
        moral=section("Moral", ("Takeaway",)), takeaway=section("Takeaway", ("Five-Star Challenge",)),
        five_star_challenge=[], audio_script=section("Audio Performance Script", ("Poster Visual Brief",)),
        coloring_visual_brief=coloring, line_art_prompt=coloring, coloring_page_prompt=coloring,
        source_reference=plan.source_reference, scripture_reference=plan.scripture_reference, age_range=plan.age_range,
    )


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _folder_id(link: str) -> str:
    match = re.search(r"/folders/([A-Za-z0-9_-]+)", link or "")
    return match.group(1) if match else ""
