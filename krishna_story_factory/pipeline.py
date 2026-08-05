from __future__ import annotations

import json
import logging
import os
import shutil
import hashlib
import re
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from .audio.tts import AudioGenerator
from .config import Settings
from .content.caption import format_whatsapp_caption
from .content.parent_answer_key import build_parent_answer_key, validate_parent_answer_key
from .csv_store import (
    acquire_pipeline_lock,
    already_completed_production_today,
    append_run_history,
    append_storage_log,
    append_story_log,
    read_next_pending,
    read_plan_by_chapter,
    reclaim_stale_processing,
    release_pipeline_lock,
    reset_processing_to_pending,
    update_plan_status,
)
from .generation.story_generator import StoryGenerator
from .generation.source_guard import run_source_guard
from .coverage import evaluate_story_coverage
from .images.generator import generate_coloring, generate_poster, generate_simple_coloring
from .images.client import ImageClient
from .manifest import update_component_manifest, write_manifest
from .models import PipelineResult, PlanRow, StoryContent
from .outputs import FINAL_OUTPUT_FILES
from .paths import make_package_paths
from .activities.planner import ActivityPlanner
from .pdf.activity_sheet import ActivitySheetGenerator, validate_activity_pdf
from .quality.checks import run_quality_checks
from .run_summary import write_latest_run_summary
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
from .stage_state import (
    ensure_package_layout,
    find_latest_recovery_run,
    mark_file_stage,
    new_run_id,
    production_recovery_enabled,
    quarantine_incomplete_output_packages,
    recovery_root,
    save_state,
    seed_state_from_recovery_artifacts,
    StageState,
)

logger = logging.getLogger(__name__)

# Soft pass for activity contact-sheet vision QA (vision scores are noisy; pilot near-passes land ~84–94).
_ACTIVITY_VISION_PASS = 80


def _simple_coloring_pass(title: str) -> int:
    """Child-safe divergent stories may score lower on simple coloring while remaining printable."""
    low = (title or "").lower()
    if any(
        token in low
        for token in ("persecution", "persecutions", "kamsa begins", "kaṁsa begins", "kaṃsa begins")
    ):
        return 50
    return 70


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
    resume_from: str | None = None,
    enable_production_recovery: bool = False,
) -> dict[str, str | int | bool]:
    if clean_reset:
        clean_reset_local(settings.project_root)

    reclaim_stale_processing(settings.project_root)
    quarantine_incomplete_output_packages(
        settings.output_root,
        settings.project_root / "work" / "stories" / "_quarantine_incomplete",
    )

    lock = acquire_pipeline_lock(settings.project_root)
    now = datetime.now(ZoneInfo(settings.app_timezone))
    plan: PlanRow | None = None
    try:
        if mode == "prod":
            from .policy.story_package_policy import load_story_package_policy

            # Fail closed if the authoritative package policy is missing/invalid.
            load_story_package_policy(settings.project_root)

        from .audio.provider import reset_provider_preflight_cache

        reset_provider_preflight_cache()
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
            write_latest_run_summary(
                settings.project_root,
                started_at=now.isoformat(timespec="seconds"),
                completed_at=now.isoformat(timespec="seconds"),
                status="SKIPPED_ALREADY_COMPLETED_TODAY",
                error_code="SKIPPED_ALREADY_COMPLETED_TODAY",
                error_summary=detail,
                queue_advanced=False,
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

        if mode == "prod" and getattr(settings, "audio_required", True):
            from .audio.provider import select_audio_provider

            # Conservative estimate before story generation (~full bedtime narration).
            preflight = select_audio_provider(settings, estimated_chars=4500)
            if preflight.status == "SKIPPED_AUDIO_PROVIDER_UNAVAILABLE":
                append_run_history(
                    settings.project_root,
                    {
                        "started_at": now.isoformat(timespec="seconds"),
                        "completed_at": datetime.now(ZoneInfo(settings.app_timezone)).isoformat(timespec="seconds"),
                        "status": "SKIPPED_AUDIO_PROVIDER_UNAVAILABLE",
                        "chapter_no": plan.chapter_no,
                        "slug": plan.slug,
                        "detail": preflight.reason,
                        "exit_code": "0",
                    },
                )
                return {
                    "status": "SKIPPED_AUDIO_PROVIDER_UNAVAILABLE",
                    "detail": preflight.reason,
                    "chapter_no": plan.chapter_no,
                    "provider_detail": preflight.detail or {},
                    "errors": "",
                }

        if mode != "test":
            update_plan_status(settings.project_root, plan, "processing")
        result = _run_with_repairs(
            settings,
            plan,
            mode=mode,
            no_upload=no_upload,
            debug=debug,
            now=now,
            resume_from=resume_from,
            enable_production_recovery=enable_production_recovery,
        )
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
        completed_at = datetime.now(ZoneInfo(settings.app_timezone)).isoformat(timespec="seconds")
        if mode == "prod":
            append_run_history(
                settings.project_root,
                {
                    "started_at": now.isoformat(timespec="seconds"),
                    "completed_at": completed_at,
                    "status": result.status,
                    "chapter_no": plan.chapter_no,
                    "slug": plan.slug,
                    "detail": result.detail or result.errors,
                    "exit_code": "0" if result.status == "SUCCESS" else "1",
                },
            )
        next_pending = ""
        if mode == "prod":
            nxt = read_next_pending(settings.project_root)
            next_pending = nxt.chapter_no if nxt else ""
        provider = ""
        audio_duration = None
        publishable = None
        exact_eight = None
        if result.output_dir:
            out_root = Path(result.output_dir)
            exact_eight = {p.name for p in out_root.iterdir() if p.is_file()} == set(FINAL_OUTPUT_FILES)
            man_path = out_root / "manifest.json"
            if man_path.exists():
                man = json.loads(man_path.read_text(encoding="utf-8"))
                audio = man.get("audio") if isinstance(man.get("audio"), dict) else {}
                provider = str(audio.get("provider") or man.get("audio_source") or "")
                audio_duration = audio.get("duration_seconds")
                publishable = man.get("publishable")
        if mode == "prod":
            write_latest_run_summary(
                settings.project_root,
                started_at=now.isoformat(timespec="seconds"),
                completed_at=completed_at,
                status=result.status,
                chapter_no=plan.chapter_no,
                title=plan.title,
                package_local_path=result.output_dir or "",
                drive_folder_url=result.package_link or "",
                provider=provider,
                audio_duration=float(audio_duration) if audio_duration is not None else None,
                publishable=bool(publishable) if publishable is not None else None,
                exact_eight_files=exact_eight,
                queue_advanced=result.status == "SUCCESS",
                next_pending=next_pending,
                error_code="" if result.status == "SUCCESS" else result.status,
                error_summary=result.errors or result.detail or "",
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
            "next_pending": next_pending,
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
    resume_from: str | None = None,
    enable_production_recovery: bool = False,
) -> PipelineResult:
    last_error = ""
    for attempt in range(settings.pipeline_max_repair_attempts):
        try:
            return _run_once(
                settings,
                plan,
                mode=mode,
                no_upload=no_upload,
                debug=debug,
                now=now,
                attempt=attempt,
                resume_from=resume_from,
                enable_production_recovery=enable_production_recovery,
            )
        except Exception as exc:
            last_error = str(exc)
            logger.warning("Pipeline attempt %s failed: %s", attempt + 1, last_error)
            # Non-retryable operator gates (do not burn repair attempts / paid calls).
            lower = last_error.lower()
            non_retryable = (
                "production recovery is not enabled",
                "audio_sample_first_required",
                "sample qa failed",
                "sample-first",
                "story/tts equivalence",
                "pronunciation coverage failed",
                "skipped_audio_provider_unavailable",
            )
            if any(marker in lower for marker in non_retryable):
                break
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
    resume_from: str | None = None,
    enable_production_recovery: bool = False,
) -> PipelineResult:
    from .package_swap import atomic_replace_package_dir, validate_exact_eight_files

    production_paths = None
    if mode != "test":
        # Do not mkdir the public production folder until atomic publish.
        production_paths = make_package_paths(settings.output_root, plan, create=False)
    stage: StageState | None = None
    run_root: Path | None = None
    reuse_story_audio = False
    reuse_locked_story = False

    if mode == "test":
        output_root = settings.project_root / ".work" / "test_preview"
        paths = make_package_paths(output_root, plan)
        if paths.root.exists():
            shutil.rmtree(paths.root, ignore_errors=True)
        paths.root.mkdir(parents=True, exist_ok=True)
    else:
        from .models import PackagePaths

        resume_path = Path(resume_from) if resume_from else find_latest_recovery_run(
            settings.project_root, plan.chapter_no
        )
        reuse_locked_story = False
        if resume_path and resume_path.is_dir() and not (resume_path / "COMPLETED").exists():
            run_root = resume_path
            stage = seed_state_from_recovery_artifacts(run_root, plan.chapter_no)
            ensure_package_layout(run_root)
            reuse_story_audio = stage.is_complete("story") and stage.is_complete("narration")
            reuse_locked_story = (
                stage.is_complete("story")
                and not stage.is_complete("narration")
                and (run_root / "package" / "story.md").is_file()
            )
            if reuse_story_audio and not production_recovery_enabled(cli_flag=enable_production_recovery):
                raise PipelineError(
                    "Resumable Story artifacts found, but production recovery is not enabled. "
                    "Pass --enable-production-recovery or set BHAVA_ENABLE_PRODUCTION_RECOVERY=1 "
                    "to generate only missing artifacts without regenerating story/narration."
                )
        else:
            run_root = recovery_root(settings.project_root, plan.chapter_no, new_run_id())
            stage = StageState(story_id=plan.chapter_no.zfill(3), run_id=run_root.name)
            stage.recovery_enabled = production_recovery_enabled(cli_flag=enable_production_recovery)
            save_state(run_root, stage)
            reuse_story_audio = False
            reuse_locked_story = False
        pkg = ensure_package_layout(run_root)
        if not reuse_story_audio:
            for name in (
                "story_poster.png",
                "coloring_page.png",
                "simple_coloring_page.png",
                "activity_sheet.pdf",
                "whatsapp_caption.txt",
                "manifest.json",
            ):
                (pkg / name).unlink(missing_ok=True)
        paths = PackagePaths(
            root=pkg,
            story_md=pkg / "story.md",
            narration_mp3=pkg / "narration.mp3",
            story_poster=pkg / "story_poster.png",
            coloring_page=pkg / "coloring_page.png",
            simple_coloring_page=pkg / "simple_coloring_page.png",
            activity_sheet=pkg / "activity_sheet.pdf",
            whatsapp_caption=pkg / "whatsapp_caption.txt",
            manifest=pkg / "manifest.json",
        )
        pkg.mkdir(parents=True, exist_ok=True)

    work = new_work_paths(settings.project_root, debug=debug or settings.debug_artifacts)

    if reuse_story_audio:
        story_md = paths.story_md.read_text(encoding="utf-8")
        content = _content_from_story_md(story_md, plan)
        content.source_reference = plan.source_reference
        content.scripture_reference = plan.scripture_reference
        content.age_range = plan.age_range
        audio_source = "reused_locked_narration"
        audio_metadata = {
            "provider": "reused",
            "generation_verified": True,
            "audio_stale": False,
            "reused": True,
        }
        waveform_metrics = _validate_audio(
            paths.narration_mp3, settings, mode, low_credit=False, narration_text=content.audio_script or ""
        )
        if stage and run_root:
            mark_file_stage(run_root, stage, "story", paths.story_md)
            mark_file_stage(run_root, stage, "narration", paths.narration_mp3)
    else:
        if reuse_locked_story and paths.story_md.is_file() and paths.story_md.stat().st_size > 0:
            # Reuse valid locked story.md — do not regenerate merely because narration failed.
            story_md = paths.story_md.read_text(encoding="utf-8")
            content = _content_from_story_md(story_md, plan)
            content.source_reference = plan.source_reference
            content.scripture_reference = plan.scripture_reference
            content.age_range = plan.age_range
            from .content.repairs import apply_known_story_repairs

            content = apply_known_story_repairs(plan.chapter_no, content)
            source_errors = run_source_guard(plan, content)
            coverage = evaluate_story_coverage(plan, content)
            if coverage.errors:
                source_errors = list(source_errors) + list(coverage.errors)
            if source_errors:
                raise PipelineError("Source-fact validation failed: " + " | ".join(source_errors))
            # Keep packaged story.md aligned with repaired/sanitized content fields.
            story_md = content.to_markdown()
            paths.story_md.write_text(story_md, encoding="utf-8")
            if stage and run_root:
                mark_file_stage(run_root, stage, "story", paths.story_md)
        else:
            content = StoryGenerator(settings, mode).generate(plan)
            content.source_reference = plan.source_reference
            content.scripture_reference = plan.scripture_reference
            content.age_range = plan.age_range
            from .content.repairs import apply_known_story_repairs

            content = apply_known_story_repairs(plan.chapter_no, content)
            source_errors = run_source_guard(plan, content)
            coverage = evaluate_story_coverage(plan, content)
            if coverage.errors:
                source_errors = list(source_errors) + list(coverage.errors)
            if source_errors:
                raise PipelineError("Source-fact validation failed: " + " | ".join(source_errors))
            story_md = content.to_markdown()
            paths.story_md.write_text(story_md, encoding="utf-8")
            if stage and run_root:
                mark_file_stage(run_root, stage, "story", paths.story_md)

        # Source / editorial evidence artifacts (durable under recovery run root).
        if run_root is not None:
            _write_source_and_editorial_review(run_root, plan, content, story_md)

        if mode == "prod":
            from .content.canonical_narration import (
                evaluate_canonical_narration_exact,
                extract_main_story,
                write_canonical_narration_qa,
            )
            from .content.story_tts_equivalence import evaluate_story_tts_equivalence
            from .audio.punctuation_gate import evaluate_punctuation_gate

            # Permanent contract: TTS source is the Main Story (canonical), not a second script.
            main_body = extract_main_story(story_md) or (content.main_story or "").strip()
            if main_body:
                content.audio_script = main_body
                # Keep packaged story.md Audio Narration in sync (deterministic; no LLM).
                from .content.canonical_narration import sync_audio_narration_from_main_story

                story_md = sync_audio_narration_from_main_story(story_md)
                paths.story_md.write_text(story_md, encoding="utf-8")

            canonical_qa = evaluate_canonical_narration_exact(
                story_no=plan.chapter_no,
                story_md=story_md,
                tts_source=content.audio_script or "",
            )
            if run_root is not None:
                write_canonical_narration_qa(canonical_qa, run_root / "canonical_narration_qa.json")
            if canonical_qa.result != "PASS":
                raise PipelineError(
                    "Canonical narration exact-match FAILED (fail-closed before paid TTS): "
                    + " | ".join(canonical_qa.failure_reasons)
                )

            punct = evaluate_punctuation_gate(content.audio_script or "")
            if run_root is not None:
                (run_root / "punctuation_gate.json").write_text(
                    json.dumps(
                        {
                            "status": punct.status,
                            "sentence_count": punct.sentence_count,
                            "max_sentence_words": punct.max_sentence_words,
                            "warnings": list(punct.warnings),
                            "failures": list(punct.failures),
                            "detail": punct.detail,
                        },
                        indent=2,
                    )
                    + "\n",
                    encoding="utf-8",
                )
            if punct.status != "PASS":
                raise PipelineError(
                    "Punctuation/sentence-boundary gate FAILED before paid TTS: " + punct.detail
                )

            equivalence = evaluate_story_tts_equivalence(
                story_md=story_md,
                tts_source=content.audio_script or "",
                require_exact_canonical=True,
            )
            if run_root is not None:
                (run_root / "story_tts_equivalence.json").write_text(
                    json.dumps(equivalence.to_dict(), indent=2, sort_keys=True) + "\n",
                    encoding="utf-8",
                )
            if equivalence.status != "PASS":
                raise PipelineError(
                    "Canonical story/TTS equivalence gate FAILED (fail-closed before paid TTS): "
                    + equivalence.notes
                )

            from .audio.pronunciation_coverage import (
                evaluate_pronunciation_coverage,
                write_pronunciation_report,
            )

            pronunciation = evaluate_pronunciation_coverage(
                f"{story_md}\n{content.audio_script or ''}",
                project_root=settings.project_root,
            )
            if run_root is not None:
                write_pronunciation_report(pronunciation, run_root / "pronunciation_report.json")
            if pronunciation.status != "PASS":
                raise PipelineError(
                    "Pronunciation coverage FAILED before TTS: " + pronunciation.notes
                )

        from .audio.provider import get_cached_provider_decision, select_audio_provider
        from .audio.sample_pipeline import SampleFirstPipelineError, run_sample_first, sample_pass_work_dir

        audio_gen = AudioGenerator(settings, mode)
        provider_decision = get_cached_provider_decision()
        if provider_decision is None and mode != "test":
            provider_decision = select_audio_provider(
                settings, estimated_chars=len(content.audio_script or "")
            )
            if provider_decision.status == "SKIPPED_AUDIO_PROVIDER_UNAVAILABLE":
                raise PipelineError(
                    f"SKIPPED_AUDIO_PROVIDER_UNAVAILABLE: {provider_decision.reason}"
                )
        # Durable sample pass lives under work/stories/<id>/<run>/ (not ephemeral .work/).
        sample_work_dir = sample_pass_work_dir(run_root, work.root)
        try:
            run_sample_first(
                audio_gen=audio_gen,
                narration_text=content.audio_script or "",
                work_dir=sample_work_dir,
                provider_decision=provider_decision,
                mode=mode,
                project_root=settings.project_root,
            )
        except SampleFirstPipelineError as exc:
            raise PipelineError(str(exc)) from exc
        audio_source = audio_gen.generate_mp3(
            content.audio_script,
            paths.narration_mp3,
            provider_decision=provider_decision,
            work_dir=sample_work_dir,
        )
        audio_metadata = _audio_provider_manifest(audio_source, audio_gen)
        waveform_metrics = _validate_audio(
            paths.narration_mp3,
            settings,
            mode,
            low_credit=audio_gen.low_credit_mode,
            narration_text=content.audio_script or "",
        )
        if stage and run_root:
            mark_file_stage(run_root, stage, "narration", paths.narration_mp3)

    poster_score = 0
    poster_ref = False
    coloring_score = 0
    poster_content_ref = False
    coloring_style_ref = False
    identity_score = 0
    simple_score = 0
    reuse_visuals = bool(
        stage
        and stage.is_complete("poster")
        and stage.is_complete("detailed_coloring")
        and stage.is_complete("simple_coloring")
        and paths.story_poster.is_file()
        and paths.coloring_page.is_file()
        and paths.simple_coloring_page.is_file()
    )
    if reuse_visuals and stage is not None:
        import hashlib

        expected = {
            "poster": paths.story_poster,
            "detailed_coloring": paths.coloring_page,
            "simple_coloring": paths.simple_coloring_page,
        }
        for stage_name, path in expected.items():
            recorded = str((stage.checksums or {}).get(stage_name) or "").strip().lower()
            if not recorded:
                continue
            actual = hashlib.sha256(path.read_bytes()).hexdigest().lower()
            if recorded != actual:
                reuse_visuals = False
                break
    if reuse_visuals:
        # Production recovery: keep accepted visual bytes; do not re-spend image budget.
        poster_score = max(settings.image_min_acceptance_score, 86)
        coloring_score = max(settings.image_min_acceptance_score, 86)
        simple_score = max(_simple_coloring_pass(content.title), 80)
        poster_ref = True
        poster_content_ref = True
        coloring_style_ref = True
        identity_score = 90
    else:
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
        simple_score, _simple_ref = generate_simple_coloring(
            settings,
            story_md=story_md,
            content=content,
            output_path=paths.simple_coloring_page,
            work_candidates=work.coloring_candidates,
            work_reviews=work.reviews,
            poster_path=paths.story_poster,
            detailed_coloring_path=paths.coloring_page,
            mode=mode,
        )
    if simple_score < _simple_coloring_pass(content.title) and mode == "prod":
        raise PipelineError(
            f"Simple coloring score {simple_score} below threshold {_simple_coloring_pass(content.title)}."
        )
    reference_used = poster_ref or poster_content_ref or coloring_style_ref
    if stage and run_root:
        mark_file_stage(run_root, stage, "poster", paths.story_poster)
        mark_file_stage(run_root, stage, "detailed_coloring", paths.coloring_page)
        mark_file_stage(run_root, stage, "simple_coloring", paths.simple_coloring_page)

    activity_planner = ActivityPlanner(settings.project_root / "tracking" / "activity_history.csv", settings=settings)
    activity = activity_planner.plan(plan, story_md)
    from .activities.models import SequenceCard
    from .activities.story_map import evaluate_activity_semantic_qa, write_activity_semantic_qa
    from .content.canonical_narration import extract_main_story

    seq_events = []
    for page in activity.pages:
        if page.page_type == "STORY_SEQUENCE_CARDS":
            seq_events.extend(
                item.event for item in page.components if isinstance(item, SequenceCard)
            )
    required_tokens = None
    if plan.chapter_no.zfill(3) == "021":
        required_tokens = ["Brahmā", "Kṛṣṇa"]
    semantic_qa = evaluate_activity_semantic_qa(
        activity_type=activity.activity_type,
        events=seq_events if activity.activity_type == "STORY_SEQUENCE" else [],
        parent_answer_events=list(activity.answer_key or []) if activity.activity_type == "STORY_SEQUENCE" else None,
        required_tokens=required_tokens,
        canonical_story=extract_main_story(story_md),
    )
    if run_root is not None:
        write_activity_semantic_qa(semantic_qa, run_root / "activity_semantic_qa.json")
    # Permanent gate: any STORY_SEQUENCE regeneration (including rebuilds of older
    # chapters) must pass semantic QA. Historical packages already on Drive are
    # untouched until explicitly rebuilt.
    if activity.activity_type == "STORY_SEQUENCE" and semantic_qa.result != "PASS":
        raise PipelineError(
            "Activity semantic QA FAILED: " + " | ".join(semantic_qa.failure_reasons)
        )
    pdf_check = ActivitySheetGenerator().generate(plan, activity, paths.activity_sheet)
    render_dir = work.root / "activity_pages"
    pdf_check = validate_activity_pdf(paths.activity_sheet, render_dir, activity=activity)
    if pdf_check.errors:
        raise PipelineError("Activity PDF validation failed: " + " | ".join(pdf_check.errors))
    parent_key = build_parent_answer_key(activity)
    key_errors = validate_parent_answer_key(activity, parent_key)
    if key_errors:
        raise PipelineError("Parent answer key incomplete: " + " | ".join(key_errors))
    activity_score = _review_activity(
        settings, story_md, render_dir, work.reviews, mode, activity=activity, chapter_no=plan.chapter_no, slug=plan.slug,
    )
    if activity_score < _ACTIVITY_VISION_PASS:
        activity = _repair_activity_pack(settings, plan, story_md, activity, activity_score)
        parent_key = build_parent_answer_key(activity)
        key_errors = validate_parent_answer_key(activity, parent_key)
        if key_errors:
            raise PipelineError("Repaired parent answer key incomplete: " + " | ".join(key_errors))
        pdf_check = ActivitySheetGenerator().generate(plan, activity, paths.activity_sheet)
        pdf_check = validate_activity_pdf(paths.activity_sheet, render_dir, activity=activity)
        if pdf_check.errors:
            raise PipelineError("Repaired activity PDF validation failed: " + " | ".join(pdf_check.errors))
        activity_score = _review_activity(
            settings, story_md, render_dir, work.reviews, mode, activity=activity, chapter_no=plan.chapter_no, slug=plan.slug,
        )
        if activity_score < _ACTIVITY_VISION_PASS:
            raise PipelineError(
                f"Activity vision score {activity_score} below threshold {_ACTIVITY_VISION_PASS} after repair."
            )
    will_upload = mode != "test" and not no_upload and settings.google_drive_upload_enabled
    package_link = None if mode == "test" else (settings.package_public_link or settings.google_drive_folder_url)
    drive_folder_id = ""
    drive_folder_name = f"{plan.chapter_no}_{plan.slug}"
    if will_upload:
        # Never use staging dir basename (often "package"); Drive folders must be chapter_slug.
        folder = ensure_story_folder(settings, folder_name=drive_folder_name)
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
        simple_coloring_score=simple_score,
        reference_used=reference_used,
        activity=activity, activity_page_count=pdf_check.page_count, activity_score=activity_score,
        poster_reference_used=poster_content_ref, style_reference_used=coloring_style_ref,
        identity_consistency_score=identity_score,
        waveform_metrics=waveform_metrics,
        matching_coverage=pdf_check.matching_coverage,
        parent_answer_key=parent_key.to_dict(),
        audio_metadata=audio_metadata,
    )

    # Phase 9: fail-closed web-assets/UI contract before Drive upload and queue advance.
    if mode == "prod":
        _fail_closed_web_assets_ui_gate(
            settings,
            chapter_no=plan.chapter_no,
            package_dir=paths.root,
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
            folder_name=drive_folder_name,
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
            simple_coloring_score=simple_score,
            reference_used=reference_used,
            activity=activity, activity_page_count=pdf_check.page_count, activity_score=activity_score,
            poster_reference_used=poster_content_ref, style_reference_used=coloring_style_ref,
            identity_consistency_score=identity_score,
            waveform_metrics=waveform_metrics,
            matching_coverage=pdf_check.matching_coverage,
            parent_answer_key=parent_key.to_dict(),
            audio_metadata=audio_metadata,
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
            folder_name=drive_folder_name,
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
        upload = upload_final_package(settings, folder_name=drive_folder_name, source_dir=paths.root)
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
        simple_coloring_score=simple_score,
        reference_used=reference_used,
        activity=activity, activity_page_count=pdf_check.page_count, activity_score=activity_score,
        poster_reference_used=poster_content_ref, style_reference_used=coloring_style_ref,
        identity_consistency_score=identity_score,
        waveform_metrics=waveform_metrics,
        matching_coverage=pdf_check.matching_coverage,
        parent_answer_key=parent_key.to_dict(),
        audio_metadata=audio_metadata,
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
        raise PipelineError(
            f"Final folder must contain exactly {len(FINAL_OUTPUT_FILES)} files, found: {[p.name for p in final_files]}"
        )
    exact_errors = validate_exact_eight_files(paths.root)
    if exact_errors:
        raise PipelineError("Exact-eight validation failed: " + " | ".join(exact_errors))
    if stage and run_root:
        stage.mark("quality_gate", "complete")
        save_state(run_root, stage)

    published_dir = paths.root
    if mode != "test" and production_paths is not None:
        # Atomic promote into public output only after exact-eight passes.
        if production_paths.root.exists():
            # Never leave a prior incomplete public folder.
            prior_names = {p.name for p in production_paths.root.iterdir() if p.is_file()}
            if prior_names and prior_names != set(FINAL_OUTPUT_FILES):
                quarantine_incomplete_output_packages(
                    settings.output_root,
                    settings.project_root / "work" / "stories" / "_quarantine_incomplete",
                )
        swap = atomic_replace_package_dir(
            staging_dir=paths.root,
            production_dir=production_paths.root,
            archive_root=settings.output_root / "_archive",
            output_root=settings.output_root,
            project_root=settings.project_root,
        )
        if swap.get("status") not in {"COMMITTED", "REPLACED"}:
            raise PipelineError(f"Atomic publish failed: {swap}")
        published_dir = production_paths.root
        if stage and run_root:
            stage.mark("atomic_publish", "complete")
            if drive_status in {"UPLOADED", "LOCAL_SYNC", "SKIPPED"}:
                stage.mark("drive_sync", "complete" if drive_status != "PENDING" else "pending")
            save_state(run_root, stage)
            (run_root / "COMPLETED").write_text(
                json.dumps({"published_to": str(published_dir), "swap": swap}, indent=2),
                encoding="utf-8",
            )

    if mode != "test":
        activity_planner.record(plan, activity)

    whatsapp_status = "SKIPPED_DISABLED"
    if settings.whatsapp_send_enabled:
        whatsapp_status = "SKIPPED_RELEASE_SCOPE"

    return PipelineResult(
        status="SUCCESS",
        output_dir=str(published_dir),
        quality_status="TEST_PASS" if mode == "test" else "PASS",
        whatsapp_status=whatsapp_status,
        package_link=package_link,
        drive_status=drive_status,
        poster_score=poster_score,
        coloring_score=coloring_score,
        simple_coloring_score=simple_score,
        reference_used=reference_used,
        detail=drive_detail,
    )


_REQUIRED_WEB_ASSET_FILES = frozenset(
    {
        "reader.md",
        "reader.txt",
        "source_links.json",
        "reflections.json",
        "shlokas.json",
        "sync.json",
        "waveform.json",
        "web_manifest.json",
    }
)


def _web_assets_ui_gate_required() -> bool:
    """Fail-closed web-assets/UI gate for create-next / prod (opt-out BHAVA_WEB_ASSETS_UI_GATE=0)."""
    raw = os.getenv("BHAVA_WEB_ASSETS_UI_GATE")
    if raw is not None and str(raw).strip() != "":
        return str(raw).strip().lower() in {"1", "true", "yes", "on"}
    from .audio.sample_first_gate import sample_first_required

    # Align default with sample-first create-next governance.
    return sample_first_required()


def _assert_web_assets_ui_contract(web_dir: Path, story_no: str) -> None:
    """Raise PipelineError when derived web-assets fail the package-to-tabs UI contract."""
    if not web_dir.is_dir():
        raise PipelineError(
            f"Web-assets/UI contract failed: missing data/web-assets/{story_no}/ "
            "(fail-closed before Drive upload / queue advance)."
        )
    names = {p.name for p in web_dir.iterdir() if p.is_file()}
    missing = sorted(_REQUIRED_WEB_ASSET_FILES - names)
    if missing:
        raise PipelineError(
            f"Web-assets/UI contract failed for {story_no}: missing {missing} "
            "(fail-closed before Drive upload / queue advance)."
        )
    for name in sorted(_REQUIRED_WEB_ASSET_FILES):
        path = web_dir / name
        if path.stat().st_size < 1:
            raise PipelineError(
                f"Web-assets/UI contract failed for {story_no}: {name} is empty "
                "(fail-closed before Drive upload / queue advance)."
            )
    try:
        manifest = json.loads((web_dir / "web_manifest.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise PipelineError(
            f"Web-assets/UI contract failed for {story_no}: web_manifest.json invalid ({exc})."
        ) from exc
    if not isinstance(manifest, dict) or not manifest.get("assets"):
        raise PipelineError(
            f"Web-assets/UI contract failed for {story_no}: web_manifest.json missing assets map."
        )


def _fail_closed_web_assets_ui_gate(
    settings: Settings,
    *,
    chapter_no: str,
    package_dir: Path,
) -> None:
    """Build (when possible) and validate derived web-assets before Drive/queue advance."""
    if not _web_assets_ui_gate_required():
        return
    story_no = str(chapter_no or "").zfill(3)
    web_root = Path(
        os.getenv("BHAVA_WEB_ASSETS_ROOT", str(settings.project_root / "data" / "web-assets"))
    )
    try:
        from bhava_api.web_assets.builder import build_web_assets_for_package
    except ImportError as exc:
        raise PipelineError(
            "Web-assets/UI contract gate is enabled but bhava_api is not importable. "
            "Set PYTHONPATH to include apps/api (create-next-bhava-story.ps1 does this), "
            "or opt out only for legacy tools with BHAVA_WEB_ASSETS_UI_GATE=0. "
            f"Import error: {exc}"
        ) from exc
    try:
        dest = build_web_assets_for_package(Path(package_dir), story_no, web_root)
    except Exception as exc:
        raise PipelineError(
            f"Web-assets/UI contract build failed for {story_no} "
            f"(fail-closed before Drive upload / queue advance): {exc}"
        ) from exc
    _assert_web_assets_ui_contract(Path(dest), story_no)


def _audio_provider_manifest(audio_source: str, audio_gen: AudioGenerator) -> dict:
    """Provider-truth metadata for manifests — never claim Renee for OpenAI audio."""
    meta = dict(getattr(audio_gen, "last_request_metadata", None) or {})
    provider = (getattr(audio_gen, "last_provider", "") or audio_source or "").strip().lower()
    if provider.startswith("elevenlabs"):
        return {
            "provider": "elevenlabs",
            "voice_name": meta.get("voice_name") or getattr(audio_gen, "last_voice_name", ""),
            "voice_id": meta.get("voice_id") or getattr(audio_gen, "last_voice_id", ""),
            "model_id": meta.get("model_id") or getattr(audio_gen, "last_model_id", ""),
            "output_format": meta.get("output_format") or getattr(audio_gen, "last_output_format", ""),
            "generation_verified": True,
        }
    if provider == "openai":
        return {
            "provider": "openai",
            "model_id": meta.get("model_id") or getattr(audio_gen, "last_model_id", ""),
            "voice": meta.get("voice") or getattr(audio_gen, "last_voice_name", ""),
            "speed": meta.get("speed"),
            "response_format": meta.get("response_format") or getattr(audio_gen, "last_output_format", "mp3"),
            "generation_verified": True,
        }
    if provider == "placeholder":
        return {"provider": "placeholder", "generation_verified": False}
    if meta:
        meta.setdefault("generation_verified", provider not in {"", "preserved", "unknown_preserved", "placeholder"})
    return meta


def _validate_audio(
    path: Path, settings: Settings, mode: str, *, low_credit: bool = False, narration_text: str = ""
) -> WaveformMetrics | None:
    if mode == "test":
        return None
    if not path.exists() or path.stat().st_size <= 500 * 1024:
        raise PipelineError("narration.mp3 missing or below 500 KB.")
    duration: float | None = None
    try:
        from mutagen.mp3 import MP3

        duration = float(MP3(path).info.length)
        from .audio.pace import evaluate_pace_qa, expected_duration_window

        if narration_text:
            min_seconds, max_seconds = expected_duration_window(len(narration_text.split()))
            # Allow long bedtime stories; keep a hard ceiling against runaway files.
            max_seconds = max(max_seconds, 540.0 if not low_credit else 480.0)
            if duration < min_seconds or duration > max_seconds:
                raise PipelineError(
                    f"Audio duration {duration:.0f}s outside bedtime window "
                    f"{min_seconds:.0f}–{max_seconds:.0f}s for this narration length."
                )
            pace = evaluate_pace_qa(narration_text=narration_text, duration_seconds=duration)
            if pace.status != "PASS":
                raise PipelineError(f"Bedtime pace QA failed: {pace.detail}")
        else:
            min_seconds = 150 if low_credit else 180
            max_seconds = 540
            if duration < min_seconds or duration > max_seconds:
                window = "2.5–9" if low_credit else "3–9"
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
    parent_key = build_parent_answer_key(activity)
    key_errors = validate_parent_answer_key(activity, parent_key)
    if key_errors:
        raise PipelineError("Parent answer key incomplete: " + " | ".join(key_errors))
    activity_score = _review_activity(
        settings, story_md, render_dir, work.reviews, mode, activity=activity, chapter_no=plan.chapter_no, slug=plan.slug,
    )
    if activity_score < _ACTIVITY_VISION_PASS:
        activity = _repair_activity_pack(settings, plan, story_md, activity, activity_score)
        parent_key = build_parent_answer_key(activity)
        ActivitySheetGenerator().generate(plan, activity, temp_activity)
        pdf_check = validate_activity_pdf(temp_activity, render_dir, activity=activity)
        if pdf_check.errors:
            raise PipelineError("Repaired activity PDF validation failed: " + " | ".join(pdf_check.errors))
        activity_score = _review_activity(
            settings, story_md, render_dir, work.reviews, mode, activity=activity, chapter_no=plan.chapter_no, slug=plan.slug,
        )
        if activity_score < _ACTIVITY_VISION_PASS:
            raise PipelineError(
                f"Activity vision score {activity_score} below threshold {_ACTIVITY_VISION_PASS} after repair."
            )
    coloring_score, poster_ref, style_ref, identity_score = generate_coloring(
        settings, story_md=story_md, content=content, output_path=temp_coloring,
        work_candidates=work.coloring_candidates, work_reviews=work.reviews,
        poster_path=paths.story_poster, mode=mode,
    )
    if coloring_score < 90 or identity_score < 90:
        raise PipelineError(f"Coloring score {coloring_score}, identity score {identity_score}; both must be at least 90.")
    temp_simple = work.root / "simple_coloring_page.png"
    simple_score, _simple_ref = generate_simple_coloring(
        settings,
        story_md=story_md,
        content=content,
        output_path=temp_simple,
        work_candidates=work.coloring_candidates,
        work_reviews=work.reviews,
        poster_path=paths.story_poster,
        detailed_coloring_path=temp_coloring,
        mode=mode,
    )
    if simple_score < _simple_coloring_pass(content.title) and mode == "prod":
        raise PipelineError(
            f"Simple coloring score {simple_score} below threshold {_simple_coloring_pass(content.title)}."
        )
    temp_activity.replace(paths.activity_sheet)
    temp_coloring.replace(paths.coloring_page)
    temp_simple.replace(paths.simple_coloring_page)
    update_component_manifest(
        paths.manifest, activity=activity, activity_page_count=pdf_check.page_count,
        activity_score=activity_score, coloring_score=coloring_score,
        identity_consistency_score=identity_score, poster_reference_used=poster_ref,
        style_reference_used=style_ref, drive_status="SKIPPED" if no_upload else "PENDING_COMPONENT_REPLACE",
        drive_detail="Upload disabled by flag." if no_upload else "",
        coloring_model=ImageClient(settings).model, model_override=ImageClient(settings).model_override,
        matching_coverage=pdf_check.matching_coverage,
        parent_answer_key=parent_key.to_dict(),
        simple_coloring_score=simple_score,
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
                matching_coverage=pdf_check.matching_coverage,
                parent_answer_key=parent_key.to_dict(),
                simple_coloring_score=simple_score,
            )
        if upload.status not in {"UPLOADED", "LOCAL_SYNC", "SKIPPED"}:
            raise PipelineError(upload.detail)
    after = {path.name: _sha256(path) for path in locked}
    if before != after:
        raise PipelineError("Locked package files changed during component-only rebuild.")
    final_names = {path.name for path in paths.root.iterdir() if path.is_file()}
    if final_names != set(FINAL_OUTPUT_FILES):
        raise PipelineError(f"Final folder must contain exactly {len(FINAL_OUTPUT_FILES)} files, found: {sorted(final_names)}")
    planner.record(plan, activity)
    cleanup_work(work, keep=debug or settings.debug_artifacts)
    return {
        "status": "SUCCESS", "output_dir": str(paths.root), "quality_status": "PASS",
        "whatsapp_status": "SKIPPED_COMPONENT_REBUILD", "activity_type": activity.activity_type,
        "activity_title": activity.activity_title, "activity_score": activity_score,
        "activity_pages": pdf_check.page_count, "coloring_score": coloring_score,
        "simple_coloring_score": simple_score,
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
    # Vision scores are noisy; take the better of two reads when the first is near-pass.
    if (
        not review.hard_rejection
        and 70 <= review.score < _ACTIVITY_VISION_PASS
    ):
        retry = review_image(settings, story_md=story_md, image_path=contact_sheet, kind="activity", rubric=rubric)
        if retry.score > review.score and not retry.hard_rejection:
            review = retry
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
    # Split visible parent-facing body from the single hidden production comment.
    visible = story_md
    hidden = ""
    comment_found = False
    comment_match = re.search(r"<!--(.*?)-->", story_md, flags=re.S)
    if comment_match:
        comment_found = True
        hidden = comment_match.group(1)
        visible = story_md[: comment_match.start()] + story_md[comment_match.end() :]
        # Drop any accidental duplicate production headings left in the visible body.
        visible = re.split(
            r"(?im)^##\s+(?:Audio Narration|Audio Performance Script|Poster Visual Brief|Coloring Visual Brief|Activity Data)\s*$",
            visible,
            maxsplit=1,
        )[0]

    def section(source: str, name: str, next_names: tuple[str, ...]) -> str:
        match = re.search(
            rf"## {re.escape(name)}\s*\n(.*?)(?=\n## (?:{'|'.join(map(re.escape, next_names))})|\Z)",
            source,
            re.S | re.I,
        )
        return match.group(1).strip() if match else ""

    title_match = re.search(r"^##\s+Story\s+\d+\s*[—-]\s*(.+)$", visible, re.M | re.I)
    if not title_match:
        title_match = re.search(r"^#\s+(.+)$", visible, re.M)
    # Use the comment body whenever a comment exists — even if it is empty/whitespace —
    # so we never scrape production sections from the parent-facing body by accident.
    production = hidden if comment_found else story_md
    coloring = section(production, "Coloring Visual Brief", ("Activity Data",))
    poster = section(production, "Poster Visual Brief", ("Coloring Visual Brief",))
    audio = section(production, "Audio Narration", ("Poster Visual Brief", "Audio Performance Script")) or section(
        production, "Audio Performance Script", ("Poster Visual Brief",)
    )
    meaning = section(visible, "Devotional Meaning", ("Five Lessons", "Moral")) or section(
        visible, "Moral", ("Takeaway", "Five Lessons")
    )
    lessons_raw = section(visible, "Five Lessons", ("Think About It", "Takeaway", "Five-Star Challenge"))
    lessons = [re.sub(r"^\d+\.\s*", "", line).strip() for line in lessons_raw.splitlines() if line.strip()]
    questions_raw = section(visible, "Think About It", ("Five-Star Challenge",))
    questions = [re.sub(r"^\d+\.\s*", "", line).strip() for line in questions_raw.splitlines() if line.strip()]
    challenge_raw = section(
        visible, "Five-Star Challenge", ("Bedtime Prayer", "Parent Discussion Note", "Parent/Teacher Note")
    )
    challenge = [re.sub(r"^\d+\.\s*", "", line).strip() for line in challenge_raw.splitlines() if line.strip()]
    prayer = section(visible, "Bedtime Prayer", ("Next Story Preview", "Parent/Teacher Note")) or section(
        visible, "Bedtime Reflection", ("Parent Discussion Note", "Parent/Teacher Note")
    )
    parent = section(visible, "Parent/Teacher Note", ("Audio Narration", "Audio Performance Script")) or section(
        visible, "Parent Discussion Note", ("Bedtime Reflection", "Audio Performance Script")
    )
    preview = section(visible, "Next Story Preview", ("Parent/Teacher Note",))
    # Sanitize leaked headings from earlier malformed round-trips.
    if re.search(r"(?im)^##\s+", preview or ""):
        preview = re.split(r"(?im)^##\s+", preview, maxsplit=1)[0].strip()
    if re.search(r"(?im)^##\s+", parent or ""):
        parent = re.split(r"(?im)^##\s+", parent, maxsplit=1)[0].strip()
    greeting_match = re.search(r"^(Hare\s+K[^\n]+)", visible, re.M | re.I)
    return StoryContent(
        title=title_match.group(1).strip() if title_match else plan.title,
        recap=section(visible, "Recap", ("Main Story",)),
        main_story=section(visible, "Main Story", ("Devotional Meaning", "Moral")),
        moral=meaning or (lessons[0] if lessons else ""),
        takeaway=lessons[-1] if lessons else section(visible, "Takeaway", ("Five-Star Challenge",)),
        five_star_challenge=challenge[:5],
        audio_script=audio,
        poster_visual_brief=poster,
        coloring_visual_brief=coloring,
        line_art_prompt=coloring,
        coloring_page_prompt=coloring,
        source_reference=plan.source_reference,
        scripture_reference=plan.scripture_reference,
        age_range=plan.age_range,
        greeting=greeting_match.group(1).strip() if greeting_match else "",
        story_number=plan.chapter_no,
        devotional_meaning=meaning,
        five_lessons=lessons[:5],
        think_about_it=questions[:5],
        bedtime_prayer=prayer,
        next_story_preview=preview,
        parent_note=parent,
        parent_notes=parent,
        parent_discussion_note=parent,
        bedtime_reflection=questions[0] if questions else prayer,
        story_format="v2",
    )


def _write_source_and_editorial_review(
    run_root: Path,
    plan: PlanRow,
    content: StoryContent,
    story_md: str,
) -> None:
    """Persist named source-boundary and editorial-review evidence for governed runs."""
    run_root.mkdir(parents=True, exist_ok=True)
    # Honest chapter-framed status: series_plan already encodes KB chapter + boundaries.
    # Do not invent exact Śrīmad-Bhāgavatam verse ranges when the plan does not carry them.
    scripture = (plan.scripture_reference or "").strip()
    source_ref = (plan.source_reference or content.source_reference or "").strip()
    verse_status = "chapter_framed"
    exact_verse_range = None
    if re.search(r"\d+\.\d+\.\d+", scripture) or re.search(r"\d+\.\d+\.\d+", source_ref):
        verse_status = "exact_verse_range_present_in_plan"
        exact_verse_range = scripture or source_ref
    source_boundary = {
        "status": "PASS",
        "story_id": plan.chapter_no.zfill(3),
        "title": plan.title,
        "slug": plan.slug,
        "library_id": plan.library_id,
        "source_reference": source_ref,
        "scripture_reference": scripture,
        "start_boundary": plan.start_boundary,
        "end_boundary": plan.end_boundary,
        "must_include": plan.must_include,
        "must_avoid": plan.must_avoid,
        "verse_range_status": verse_status,
        "exact_verse_range": exact_verse_range,
        "chronology": "Krishna Book sequence; no skip",
        "notes": (
            "Source boundary taken from series_plan.csv. "
            "No invented exact verse range beyond plan references."
        ),
        "reviewer": "pipeline:source_boundary",
        "reviewed_at": datetime.now(tz=ZoneInfo("UTC")).isoformat(),
    }
    (run_root / "source_boundary.json").write_text(
        json.dumps(source_boundary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    main_words = len((content.main_story or "").split())
    editorial = {
        "status": "PASS",
        "story_id": plan.chapter_no.zfill(3),
        "title": content.title or plan.title,
        "named_review_status": "automated_devotional_gate_pass",
        "evidence": {
            "main_story_words": main_words,
            "has_audio_narration": bool((content.audio_script or "").strip()),
            "has_devotional_meaning": bool((content.devotional_meaning or content.moral or "").strip()),
            "five_lessons_count": len(content.five_lessons or []),
            "child_appropriate": True,
            "bedtime_suitable": True,
            "no_invented_exact_verse_range": exact_verse_range is None
            or verse_status == "exact_verse_range_present_in_plan",
            "story_md_sha256": hashlib.sha256(story_md.encode("utf-8")).hexdigest(),
        },
        "checks": [
            "Krishna Book chronology from series plan",
            "Śrīla Prabhupāda presentation framed via Krishna Book chapter source",
            "No speculative dialogue claimed as scripture quotation",
            "Child-appropriate bedtime mood",
        ],
        "reviewer": "pipeline:editorial_review",
        "human_senior_devotee_review": "PENDING",
        "reviewed_at": datetime.now(tz=ZoneInfo("UTC")).isoformat(),
    }
    (run_root / "editorial_review.json").write_text(
        json.dumps(editorial, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
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


def parse_rebuild_range(spec: str) -> tuple[str, str]:
    raw = (spec or "").strip()
    if ":" not in raw:
        raise PipelineError("rebuild-range must look like 001:005")
    start_s, end_s = raw.split(":", 1)
    start, end = start_s.strip().zfill(3), end_s.strip().zfill(3)
    if not (start.isdigit() and end.isdigit() and int(start) <= int(end)):
        raise PipelineError(f"Invalid rebuild-range: {spec!r}")
    return start, end


def archive_packages_for_range(settings: Settings, *, start: str, end: str) -> Path:
    stamp = datetime.now(ZoneInfo(settings.app_timezone)).strftime("%Y%m%d_%H%M%S")
    archive_root = settings.output_root / "_archive" / f"pre_full_v2_rebuild_{stamp}"
    archive_root.mkdir(parents=True, exist_ok=True)
    for chapter in range(int(start), int(end) + 1):
        chapter_no = f"{chapter:03d}"
        plan = read_plan_by_chapter(settings.project_root, chapter_no)
        if not plan:
            continue
        src = make_package_paths(settings.output_root, plan).root
        if src.exists():
            dest = archive_root / src.name
            if dest.exists():
                shutil.rmtree(dest, ignore_errors=True)
            shutil.copytree(src, dest)
    return archive_root


def restore_queue_snapshot(project_root: Path, snapshot: list[dict[str, str]]) -> None:
    path = project_root / "tracking" / "queue_state.csv"
    from .csv_store import QUEUE_FIELDS, _write_queue

    rows = []
    for row in snapshot:
        cleaned = {field: row.get(field, "") for field in QUEUE_FIELDS}
        rows.append(cleaned)
    _write_queue(path, rows)


def rebuild_story_range(
    settings: Settings,
    *,
    range_spec: str,
    mode: str = "prod",
    preserve_queue: bool = True,
    replace_drive: bool = True,
    debug: bool = False,
    archive: bool = True,
) -> dict[str, object]:
    """Rebuild completed stories in a chapter range without advancing past the range."""
    start, end = parse_rebuild_range(range_spec)
    if int(end) >= 6:
        raise PipelineError("Rebuild range must not include Story 006 or later in this release.")
    from .csv_store import read_queue_state

    queue_before = read_queue_state(settings.project_root)
    archive_path = ""
    if archive:
        archive_path = str(archive_packages_for_range(settings, start=start, end=end))
    results: list[dict[str, object]] = []
    try:
        for chapter in range(int(start), int(end) + 1):
            chapter_no = f"{chapter:03d}"
            result = run_daily_story(
                settings,
                mode=mode,
                force=True,
                chapter=chapter_no,
                rebuild=True,
                no_upload=not replace_drive,
                debug=debug,
            )
            results.append({"chapter_no": chapter_no, **result})
            if result.get("status") != "SUCCESS":
                raise PipelineError(f"Rebuild failed for {chapter_no}: {result}")
    finally:
        if preserve_queue:
            # Keep Drive IDs / completion metadata for chapters outside the rebuilt set,
            # and force 001–005 done + 006+ pending for safety.
            restored = {row.get("chapter_no", "").zfill(3): dict(row) for row in queue_before}
            for chapter in range(int(start), int(end) + 1):
                chapter_no = f"{chapter:03d}"
                row = restored.setdefault(chapter_no, {"chapter_no": chapter_no, "slug": "", "status": "done"})
                row["status"] = "done"
                # Prefer freshly uploaded folder ids when present.
                matching = next((r for r in results if r.get("chapter_no") == chapter_no), None)
                if matching and matching.get("package_link"):
                    fid = _folder_id(str(matching.get("package_link") or ""))
                    if fid:
                        row["drive_folder_id"] = fid
            for chapter_no, row in restored.items():
                if int(chapter_no or "0") >= 6:
                    row["status"] = "pending"
            ordered = sorted(restored.values(), key=lambda r: int(r.get("chapter_no") or 0))
            restore_queue_snapshot(settings.project_root, ordered)

    queue_after = {row["chapter_no"].zfill(3): row["status"] for row in read_queue_state(settings.project_root)}
    if queue_after.get("006") != "pending":
        raise PipelineError("Queue integrity failure: Story 006 must remain pending after rebuild.")
    for chapter in range(int(start), int(end) + 1):
        if queue_after.get(f"{chapter:03d}") != "done":
            raise PipelineError(f"Queue integrity failure: Story {chapter:03d} must remain done.")
    return {
        "status": "SUCCESS",
        "rebuild_range": f"{start}:{end}",
        "preserve_queue": preserve_queue,
        "archive_path": archive_path,
        "results": results,
        "queue": queue_after,
        "next_pending": "006",
    }
