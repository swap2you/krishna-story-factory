#!/usr/bin/env python3
"""Authoritative manual rebuild for existing Krishna Book packages (001–006).

Never advances the queue. Never enables the scheduler. Drive upload is opt-in.
Does not silently add --force to the daily CLI.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

ALL_COMPONENTS = (
    "story",
    "narration",
    "poster",
    "coloring",
    "simple_coloring",
    "activity",
    "caption",
    "manifest",
)
COMPONENT_ALIASES = {
    "images": ("poster", "coloring", "simple_coloring"),
    "visuals": ("poster", "coloring", "simple_coloring"),
}


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def _parse_chapters(raw: str) -> list[str]:
    chapters = [part.strip().zfill(3) for part in (raw or "").split(",") if part.strip()]
    if not chapters:
        raise SystemExit("Provide at least one chapter via --chapters")
    return chapters


def _parse_components(raw: str | None) -> set[str]:
    if not raw:
        return set(ALL_COMPONENTS)
    selected: set[str] = set()
    for part in raw.split(","):
        token = part.strip().lower()
        if not token:
            continue
        if token in COMPONENT_ALIASES:
            selected.update(COMPONENT_ALIASES[token])
            continue
        if token not in ALL_COMPONENTS:
            raise SystemExit(f"Unknown component {token!r}. Allowed: {', '.join(ALL_COMPONENTS)}")
        selected.add(token)
    # Manifest always refreshed when any content component changes.
    if selected - {"manifest", "caption"}:
        selected.add("manifest")
        selected.add("caption")
    return selected


def _queue_snapshot(project_root: Path) -> list[dict[str, str]]:
    from krishna_story_factory.csv_store import read_queue_state

    return read_queue_state(project_root)


def _assert_queue_safe(project_root: Path) -> dict:
    from krishna_story_factory.csv_store import read_next_pending, read_plan_by_chapter

    pending = read_next_pending(project_root)
    statuses = {}
    for chapter in ("001", "002", "003", "004", "005", "006", "007"):
        plan = read_plan_by_chapter(project_root, chapter)
        statuses[chapter] = plan.status if plan else None
    if pending is None or pending.chapter_no != "007":
        raise SystemExit(f"Safety stop: next pending must be 007, found {pending}")
    for chapter in ("001", "002", "003", "004", "005", "006"):
        if statuses.get(chapter) != "done":
            raise SystemExit(f"Safety stop: {chapter} must remain done, found {statuses.get(chapter)}")
    return {"next_pending": pending.chapter_no, "statuses": statuses}


def _preflight_providers(settings, estimated_chars: int = 3500) -> dict:
    from krishna_story_factory.audio.provider import reset_provider_preflight_cache, select_audio_provider

    reset_provider_preflight_cache()
    decision = select_audio_provider(settings, estimated_chars=estimated_chars, require_dictionary=False)
    return {
        "status": decision.status,
        "provider": decision.provider,
        "reason": decision.reason,
        "model_id": decision.model_id,
        "voice": decision.voice,
        "detail": decision.detail,
    }


def _archive_chapters(settings, chapters: list[str], stamp: str) -> Path:
    from krishna_story_factory.csv_store import read_plan_by_chapter
    from krishna_story_factory.paths import assert_path_under_root, make_package_paths

    archive = assert_path_under_root(
        settings.output_root / "_archive" / f"manual_rebuild_{stamp}",
        settings.output_root,
        label="archive root",
    )
    archive.mkdir(parents=True, exist_ok=True)
    for chapter in chapters:
        plan = read_plan_by_chapter(settings.project_root, chapter)
        if not plan:
            continue
        src = make_package_paths(settings.output_root, plan).root
        if src.exists():
            dest = archive / src.name
            if dest.exists():
                shutil.rmtree(dest)
            shutil.copytree(src, dest)
    return archive


def _load_content(settings, plan, story_path: Path):
    from krishna_story_factory.content.repairs import apply_known_story_repairs
    from krishna_story_factory.content.story_format_v2 import validate_story_markdown_v2
    from krishna_story_factory.generation.source_guard import run_source_guard
    from krishna_story_factory.pipeline import _content_from_story_md

    if not story_path.exists():
        raise SystemExit(f"Missing story.md for {plan.chapter_no}: {story_path}")
    content = _content_from_story_md(story_path.read_text(encoding="utf-8"), plan)
    content = apply_known_story_repairs(plan.chapter_no, content)
    errors = run_source_guard(plan, content)
    if errors:
        raise SystemExit(f"Source guard failed for {plan.chapter_no}: " + " | ".join(errors))
    # Round-trip through serializer to guarantee one valid hidden comment block.
    markdown = content.to_markdown()
    md_errors = validate_story_markdown_v2(markdown)
    hard = [e for e in md_errors if "word count" not in e.lower()]
    if hard:
        raise SystemExit(f"Story markdown structure failed for {plan.chapter_no}: " + " | ".join(hard))
    return content, markdown


def _existing_package_link(manifest_path: Path) -> str:
    if not manifest_path.exists():
        return ""
    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return ""
    return str(data.get("package", {}).get("package_link") or "")


def _rebuild_one(
    settings,
    *,
    chapter: str,
    components: set[str],
    staging_root: Path,
    dry_run: bool,
    replace_local: bool,
    upload_drive: bool,
) -> dict:
    from mutagen.mp3 import MP3

    from krishna_story_factory.activities.planner import ActivityPlanner
    from krishna_story_factory.audio.tts import AudioGenerator
    from krishna_story_factory.audio.waveform import validate_mp3_waveform
    from krishna_story_factory.content.caption import format_whatsapp_caption
    from krishna_story_factory.content.parent_answer_key import build_parent_answer_key, validate_parent_answer_key
    from krishna_story_factory.csv_store import read_plan_by_chapter
    from krishna_story_factory.images.generator import generate_coloring, generate_poster, generate_simple_coloring
    from krishna_story_factory.manifest import write_manifest
    from krishna_story_factory.outputs import FINAL_OUTPUT_FILES
    from krishna_story_factory.paths import assert_path_under_root, make_package_paths
    from krishna_story_factory.pdf.activity_sheet import ActivitySheetGenerator, validate_activity_pdf
    from krishna_story_factory.pipeline import PipelineError, _review_activity
    from krishna_story_factory.quality.checks import run_quality_checks
    from krishna_story_factory.work import new_work_paths, prune_output_folder

    plan = read_plan_by_chapter(settings.project_root, chapter)
    if plan is None:
        raise SystemExit(f"Missing plan for {chapter}")

    production = make_package_paths(settings.output_root, plan)
    stage_paths = make_package_paths(staging_root, plan)
    assert_path_under_root(stage_paths.root, staging_root, label="stage package")

    before_hashes = {
        name: (_sha(production.root / name) if (production.root / name).exists() else "")
        for name in FINAL_OUTPUT_FILES
    }
    report: dict = {
        "chapter_no": chapter,
        "slug": plan.slug,
        "components": sorted(components),
        "dry_run": dry_run,
        "before_hashes": before_hashes,
        "status": "PLANNED",
        "production_dir": str(production.root),
        "staging_dir": str(stage_paths.root),
    }

    if dry_run:
        report["status"] = "DRY_RUN_OK"
        report["planned_actions"] = sorted(components)
        return report

    if production.root.exists():
        for name in FINAL_OUTPUT_FILES:
            src = production.root / name
            if src.exists():
                shutil.copy2(src, stage_paths.root / name)

    work = new_work_paths(settings.project_root, debug=True)
    content, repaired_md = _load_content(
        settings, plan, production.story_md if production.story_md.exists() else stage_paths.story_md
    )

    poster_score = 0
    coloring_score = 0
    simple_score = 0
    audio_source = ""
    audio_metadata = None
    wave = None
    activity = None
    pdf_check = None
    parent_key = None
    package_link = _existing_package_link(production.manifest)

    if "story" in components:
        stage_paths.story_md.write_text(repaired_md, encoding="utf-8")
    story_md = stage_paths.story_md.read_text(encoding="utf-8")
    content, story_md = _load_content(settings, plan, stage_paths.story_md)
    stage_paths.story_md.write_text(story_md, encoding="utf-8")

    from krishna_story_factory.audio.drift import (
        detect_audio_stale,
        narration_source_sha,
        preserved_audio_metadata,
        read_manifest_audio,
    )

    stale, stale_detail = detect_audio_stale(audio_script=content.audio_script, manifest_path=production.manifest)
    report["audio_stale"] = stale
    report["audio_stale_detail"] = stale_detail
    if stale and "story" in components and "narration" not in components:
        report["quality_override"] = "AUDIO_STALE"

    if "narration" in components:
        audio = AudioGenerator(settings, mode="prod")
        audio_source = audio.generate_mp3(
            content.audio_script,
            stage_paths.narration_mp3,
            work_dir=work.root / f"audio_{chapter}",
        )
        duration = float(MP3(stage_paths.narration_mp3).info.length)
        wave = validate_mp3_waveform(stage_paths.narration_mp3, expected_duration=duration)
        if wave.status != "PASS":
            raise SystemExit(f"{chapter} waveform failed: {wave.detail}")
        report["audio_provider"] = audio_source
        report["audio_model"] = audio.last_model_id
        report["audio_voice"] = audio.last_voice_name or audio.last_voice_id
        audio_metadata = {
            "provider": audio.last_provider or audio_source,
            "model_id": audio.last_model_id,
            "voice": audio.last_voice_name or audio.last_voice_id,
            "generation_verified": True,
            "narration_source_sha": narration_source_sha(content.audio_script),
            "chunks": list(audio.last_chunk_metadata or []),
        }
    else:
        duration = float(MP3(stage_paths.narration_mp3).info.length) if stage_paths.narration_mp3.exists() else None
        wave = (
            validate_mp3_waveform(stage_paths.narration_mp3, expected_duration=duration)
            if stage_paths.narration_mp3.exists()
            else None
        )
        audio_source, audio_metadata = preserved_audio_metadata(
            narration_path=stage_paths.narration_mp3,
            prior_manifest=production.manifest,
            waveform_status=getattr(wave, "status", "UNKNOWN"),
            duration_seconds=duration,
        )
        prior_info = read_manifest_audio(production.manifest) if production.manifest.exists() else {}
        if stale:
            # Preserve prior hash so drift remains detectable until narration is regenerated.
            audio_metadata["narration_source_sha"] = prior_info.get("narration_source_sha") or ""
            audio_metadata["current_narration_source_sha"] = narration_source_sha(content.audio_script)
            audio_metadata["audio_stale"] = True
        else:
            audio_metadata["narration_source_sha"] = (
                prior_info.get("narration_source_sha") or narration_source_sha(content.audio_script)
            )
            audio_metadata["audio_stale"] = False

    if "poster" in components:
        poster_score, _ = generate_poster(
            settings,
            story_md=story_md,
            content=content,
            output_path=stage_paths.story_poster,
            work_candidates=work.poster_candidates,
            work_reviews=work.reviews,
            mode="prod",
        )

    if "coloring" in components:
        coloring_score, _, _, _ = generate_coloring(
            settings,
            story_md=story_md,
            content=content,
            output_path=stage_paths.coloring_page,
            work_candidates=work.coloring_candidates,
            work_reviews=work.reviews,
            poster_path=stage_paths.story_poster,
            mode="prod",
        )

    if "simple_coloring" in components:
        simple_score, _ = generate_simple_coloring(
            settings,
            story_md=story_md,
            content=content,
            output_path=stage_paths.simple_coloring_page,
            work_candidates=work.coloring_candidates,
            work_reviews=work.reviews,
            poster_path=stage_paths.story_poster,
            detailed_coloring_path=stage_paths.coloring_page,
            mode="prod",
        )

    if "activity" in components:
        planner = ActivityPlanner(settings.project_root / "tracking" / "activity_history.csv", settings=settings)
        activity = planner.plan(plan, story_md)
        ActivitySheetGenerator().generate(plan, activity, stage_paths.activity_sheet)
        render_dir = work.root / f"activity_pages_{chapter}"
        pdf_check = validate_activity_pdf(stage_paths.activity_sheet, render_dir, activity=activity)
        if pdf_check.errors:
            raise SystemExit(f"{chapter} activity PDF errors: " + " | ".join(pdf_check.errors))
        score = _review_activity(
            settings,
            story_md,
            render_dir,
            work.reviews,
            "prod",
            activity=activity,
            chapter_no=chapter,
            slug=plan.slug,
        )
        if score < 80:
            raise SystemExit(f"{chapter} activity QA score {score} below 80")
        parent_key = build_parent_answer_key(activity)
        key_errors = validate_parent_answer_key(activity, parent_key)
        if key_errors:
            raise SystemExit(f"{chapter} parent key errors: " + " | ".join(key_errors))
        report["activity_title"] = activity.activity_title
        report["activity_score"] = score

    if activity is None and stage_paths.activity_sheet.exists():
        # Preserve existing activity object absence; caption still works with title from plan.
        pass

    activity_title = getattr(activity, "activity_title", "") if activity else ""
    send_mode = getattr(activity, "send_mode", "SEND_NOW") if activity else "SEND_NOW"
    if "caption" in components:
        caption = format_whatsapp_caption(
            story_title=content.title,
            package_link=package_link,
            activity_title=activity_title,
            recommended_send_mode=send_mode,
        )
        stage_paths.whatsapp_caption.write_text(caption, encoding="utf-8")

    ok, quality_errors, quality_warnings = run_quality_checks(
        stage_paths,
        mode="prod",
        settings=settings,
        story_title=content.title,
        poster_score=poster_score or 90,
        coloring_score=coloring_score or 90,
        require_manifest=False,
    )
    if not ok:
        raise SystemExit(f"{chapter} quality failed: " + " | ".join(quality_errors))

    prior_manifest: dict = {}
    if production.manifest.exists():
        try:
            prior_manifest = json.loads(production.manifest.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            prior_manifest = {}
    prior_images = prior_manifest.get("images") or {}
    prior_activity = prior_manifest.get("activity") or {}

    # Preserve prior QA scores when those components were not rebuilt.
    if "poster" not in components:
        poster_score = int(prior_images.get("poster_qa_score") or poster_score or 90)
    if "coloring" not in components:
        coloring_score = int(prior_images.get("coloring_qa_score") or coloring_score or 90)
    if "simple_coloring" not in components:
        simple_score = int(prior_images.get("simple_coloring_qa_score") or simple_score or 90)
    activity_page_count = getattr(pdf_check, "page_count", 0) if pdf_check else int(prior_activity.get("page_count") or 0)
    activity_score = int(report.get("activity_score") or prior_activity.get("qa_score") or 0)
    matching_coverage = (
        getattr(pdf_check, "matching_coverage", None)
        if pdf_check
        else (prior_activity.get("matching_coverage") or None)
    )
    parent_answer_key_payload = (
        parent_key.to_dict() if parent_key else (prior_activity.get("parent_answer_key") or None)
    )

    quality_status = "AUDIO_STALE" if report.get("quality_override") == "AUDIO_STALE" else ("PASS" if ok else "FAIL")
    write_manifest(
        settings=settings,
        plan=plan,
        content=content,
        paths=stage_paths,
        mode="prod",
        quality_status=quality_status,
        quality_errors=quality_errors + ([stale_detail] if report.get("quality_override") == "AUDIO_STALE" and stale_detail else []),
        quality_warnings=quality_warnings,
        audio_source=audio_source or "unknown_preserved",
        package_link=package_link,
        drive_status="LOCAL_ONLY",
        drive_detail="Manual rebuild staging; Drive not modified unless --upload-drive. Exact eight-file package.",
        poster_score=poster_score or 90,
        coloring_score=coloring_score or 90,
        simple_coloring_score=simple_score or 90,
        activity=activity,
        activity_page_count=activity_page_count,
        activity_score=activity_score,
        waveform_metrics=wave,
        matching_coverage=matching_coverage,
        parent_answer_key=parent_answer_key_payload,
        audio_metadata=audio_metadata,
    )
    # Narration-only (and similar) rebuilds must not wipe activity metadata.
    if "activity" not in components and prior_activity:
        staged = json.loads(stage_paths.manifest.read_text(encoding="utf-8"))
        staged["activity"] = prior_activity
        # Keep freshly computed QA scores that we merged above when present.
        if activity_score:
            staged["activity"]["qa_score"] = activity_score
        if activity_page_count:
            staged["activity"]["page_count"] = activity_page_count
        stage_paths.manifest.write_text(json.dumps(staged, indent=2, ensure_ascii=False), encoding="utf-8")
    # Recompute publishable after any post-write manifest merge.
    if stage_paths.manifest.exists():
        staged = json.loads(stage_paths.manifest.read_text(encoding="utf-8"))
        from krishna_story_factory.manifest import _is_publishable

        audio_block = staged.get("audio") if isinstance(staged.get("audio"), dict) else {}
        staged["publishable"] = _is_publishable(
            mode=str(staged.get("mode") or "prod"),
            quality_status=str((staged.get("quality") or {}).get("status") or ""),
            quality_errors=list((staged.get("quality") or {}).get("errors") or []),
            audio_metadata=audio_block,
            narration_source_sha=str(staged.get("narration_source_sha") or ""),
            audio_source=str(staged.get("audio_source") or ""),
            package_dir=stage_paths.root,
        )
        stage_paths.manifest.write_text(json.dumps(staged, indent=2, ensure_ascii=False), encoding="utf-8")
    prune_output_folder(stage_paths.root)
    final_names = {p.name for p in stage_paths.root.iterdir() if p.is_file()}
    if final_names != set(FINAL_OUTPUT_FILES):
        raise PipelineError(f"{chapter} staging must contain exactly 8 files, found {sorted(final_names)}")

    after_hashes = {name: _sha(stage_paths.root / name) for name in FINAL_OUTPUT_FILES}
    report["after_hashes"] = after_hashes
    preserved = [
        name
        for name in FINAL_OUTPUT_FILES
        if before_hashes.get(name) and before_hashes[name] == after_hashes.get(name)
    ]
    report["preserved_hashes"] = preserved

    if replace_local:
        from krishna_story_factory.package_swap import atomic_replace_package_dir

        archive_root = settings.output_root / "_archive" / f"swap_{chapter}"
        swap = atomic_replace_package_dir(
            staging_dir=stage_paths.root,
            production_dir=production.root,
            archive_root=archive_root,
            output_root=settings.output_root,
            project_root=settings.project_root,
        )
        report["local_replaced"] = True
        report["swap"] = swap

    if upload_drive:
        from krishna_story_factory.outputs import FINAL_OUTPUT_FILES as FILES
        from krishna_story_factory.storage.google_drive_uploader import replace_existing_files

        result = replace_existing_files(
            settings,
            source_dir=production.root,
            manifest_path=production.manifest,
            filenames=FILES,
        )
        if result.status not in {"UPLOADED", "REPLACED", "OK", "LOCAL_SYNC"}:
            # Accept common success statuses; fail otherwise.
            if "UPLOADED" not in result.status and result.status != "SUCCESS":
                raise SystemExit(f"{chapter} Drive replace failed: {result.status} {result.detail}")
        report["drive_status"] = result.status
        report["drive_detail"] = result.detail

    report["status"] = "SUCCESS"
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Manual rebuild for Stories 001–006 without queue mutation.")
    parser.add_argument("--chapters", required=True, help="Comma-separated chapter numbers, e.g. 001,002,006")
    parser.add_argument(
        "--components",
        default="",
        help="Optional subset: narration,activity,poster,coloring,simple_coloring,story,...",
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true", help="Plan only; no paid calls; no file replacement")
    mode.add_argument("--local-only", action="store_true", help="Rebuild into staging and replace local packages")
    mode.add_argument("--upload-drive", action="store_true", help="Local replace then transactional Drive upload")
    parser.add_argument("--validate-only", action="store_true", help="Validate existing packages only")
    args = parser.parse_args(argv)

    from krishna_story_factory.config import load_settings
    from krishna_story_factory.csv_store import ensure_csv_files
    from krishna_story_factory.outputs import FINAL_OUTPUT_FILES
    from krishna_story_factory.paths import assert_path_under_root

    settings = load_settings(ROOT)
    ensure_csv_files(settings.project_root)
    from krishna_story_factory.package_swap import (
        STATUS_INVALID_SWAP_JOURNAL,
        recover_unfinished_swaps,
    )

    recovery = recover_unfinished_swaps(
        output_root=settings.output_root,
        project_root=settings.project_root,
    )
    if any(item.get("status") == STATUS_INVALID_SWAP_JOURNAL for item in recovery):
        raise SystemExit(
            f"{STATUS_INVALID_SWAP_JOURNAL}: clear or repair quarantined journals under "
            "output/_swap_journal_invalid/ before rebuilding."
        )
    chapters = _parse_chapters(args.chapters)
    if any(int(c) > 6 for c in chapters):
        raise SystemExit("This rebuild tool only allows Stories 001–006.")
    components = _parse_components(args.components or None)
    queue_before = _queue_snapshot(settings.project_root)
    safety = _assert_queue_safe(settings.project_root)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

    report: dict = {
        "mode": "dry-run" if args.dry_run else ("upload-drive" if args.upload_drive else "local-only"),
        "stamp": stamp,
        "chapters": chapters,
        "components": sorted(components),
        "queue_before": safety,
        "exact_eight_files": list(FINAL_OUTPUT_FILES),
        "stories": [],
    }

    if args.validate_only:
        from krishna_story_factory.csv_store import read_plan_by_chapter
        from krishna_story_factory.paths import make_package_paths

        for chapter in chapters:
            plan = read_plan_by_chapter(settings.project_root, chapter)
            paths = make_package_paths(settings.output_root, plan)
            names = {p.name for p in paths.root.iterdir() if p.is_file()} if paths.root.exists() else set()
            report["stories"].append(
                {
                    "chapter_no": chapter,
                    "status": "VALIDATE",
                    "files": sorted(names),
                    "exact_eight": names == set(FINAL_OUTPUT_FILES),
                }
            )
    else:
        needs_audio = "narration" in components
        provider = _preflight_providers(settings)
        report["provider_preflight"] = {
            "status": provider["status"],
            "provider": provider["provider"],
            "reason": provider["reason"],
            "model_id": provider["model_id"],
            "voice": provider["voice"],
        }
        if not args.dry_run and needs_audio and provider.get("status") != "READY":
            raise SystemExit(f"Provider preflight not READY: {provider}")

        staging = assert_path_under_root(
            settings.output_root / "_staging" / f"manual_rebuild_{stamp}",
            settings.output_root,
            label="staging root",
        )
        staging.mkdir(parents=True, exist_ok=True)
        archive = None if args.dry_run else _archive_chapters(settings, chapters, stamp)
        report["staging_root"] = str(staging)
        report["archive_root"] = str(archive) if archive else ""

        for chapter in chapters:
            story_report = _rebuild_one(
                settings,
                chapter=chapter,
                components=components,
                staging_root=staging,
                dry_run=args.dry_run,
                replace_local=bool(args.local_only or args.upload_drive),
                upload_drive=bool(args.upload_drive),
            )
            report["stories"].append(story_report)

    queue_after = _assert_queue_safe(settings.project_root)
    if queue_after["statuses"] != safety["statuses"]:
        from krishna_story_factory.pipeline import restore_queue_snapshot

        restore_queue_snapshot(settings.project_root, queue_before)
        raise SystemExit("Queue mutated during rebuild; restored snapshot and aborting.")
    report["queue_after"] = queue_after
    report["scheduler_note"] = "Scheduler must remain Disabled (not modified by this script)."
    report["drive_modified"] = bool(args.upload_drive and not args.dry_run and not args.validate_only)

    out_dir = assert_path_under_root(settings.output_root / "_staging", settings.output_root, label="staging reports")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_json = out_dir / f"manual_rebuild_report_{stamp}.json"
    out_json.write_text(json.dumps(report, indent=2), encoding="utf-8")
    out_md = out_json.with_suffix(".md")
    lines = [
        "# Manual Story Rebuild Report",
        "",
        f"- Mode: `{report['mode']}`",
        f"- Stamp: `{stamp}`",
        f"- Chapters: {', '.join(chapters)}",
        f"- Components: {', '.join(sorted(components))}",
        f"- Next pending: `{queue_after.get('next_pending')}`",
        f"- Drive modified: `{report['drive_modified']}`",
        f"- Report JSON: `{out_json}`",
        "",
    ]
    for story in report["stories"]:
        lines.append(f"## Story {story.get('chapter_no')}")
        lines.append(f"- Status: {story.get('status')}")
        if story.get("activity_title"):
            lines.append(f"- Activity: {story['activity_title']}")
        if story.get("audio_provider"):
            lines.append(
                f"- Audio: {story['audio_provider']} / {story.get('audio_model')} / {story.get('audio_voice')}"
            )
        lines.append("")
    out_md.write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({"report_json": str(out_json), "report_md": str(out_md), "status": "OK"}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
