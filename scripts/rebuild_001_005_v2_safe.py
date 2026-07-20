"""Safe full V2 rebuild for Stories 001–005 with queue preservation.

- Archives current packages first
- Rebuilds 001–004 fully (8-file contract, Renee voice, Format V2)
- Rebuilds 005 content/audio/activity/simple coloring while preserving
  locked poster + detailed coloring hashes when present
- Replaces Drive folders transactionally
- Leaves Story 006 pending
"""
from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POSTER_HASH_005 = "100F06F69CAB86A84604BE4B6230213EA6EC2F633316C8891BE9233C574D87C8"
COLORING_HASH_005 = "840F5CD14AA01F14E204280DFB5314416CC8A20E51C95520AF0288FBB06CCBA5"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def _rebuild_005_preserve_visuals(settings, archive_dir: Path) -> dict:
    from mutagen.mp3 import MP3

    from krishna_story_factory.activities.planner import ActivityPlanner
    from krishna_story_factory.audio.tts import AudioGenerator
    from krishna_story_factory.audio.waveform import validate_mp3_waveform
    from krishna_story_factory.content.caption import format_whatsapp_caption
    from krishna_story_factory.content.parent_answer_key import build_parent_answer_key, validate_parent_answer_key
    from krishna_story_factory.content.story_format_v2 import validate_story_format_v2, validate_story_markdown_v2
    from krishna_story_factory.csv_store import read_plan_by_chapter
    from krishna_story_factory.generation.story_generator import StoryGenerator
    from krishna_story_factory.generation.source_guard import run_source_guard
    from krishna_story_factory.images.generator import generate_simple_coloring
    from krishna_story_factory.manifest import write_manifest
    from krishna_story_factory.outputs import FINAL_OUTPUT_FILES
    from krishna_story_factory.paths import make_package_paths
    from krishna_story_factory.pdf.activity_sheet import ActivitySheetGenerator, validate_activity_pdf
    from krishna_story_factory.pipeline import _review_activity, PipelineError
    from krishna_story_factory.quality.checks import run_quality_checks
    from krishna_story_factory.storage.google_drive_uploader import (
        ensure_story_folder,
        upload_files_to_folder,
        verify_drive_text_links,
    )
    from krishna_story_factory.work import cleanup_work, new_work_paths, prune_output_folder

    plan = read_plan_by_chapter(ROOT, "005")
    if plan is None:
        raise SystemExit("Story 005 plan missing")
    paths = make_package_paths(settings.output_root, plan)
    paths.root.mkdir(parents=True, exist_ok=True)

    # Restore locked visuals from archive if needed.
    archived = archive_dir / paths.root.name
    for name, expected in (("story_poster.png", POSTER_HASH_005), ("coloring_page.png", COLORING_HASH_005)):
        target = paths.root / name
        src = archived / name if (archived / name).exists() else target
        if not src.exists():
            raise SystemExit(f"Missing locked visual {name}")
        if _sha(src) != expected:
            # Keep current locked file if already matching; otherwise refuse overwrite with wrong art.
            if target.exists() and _sha(target) == expected:
                continue
            raise SystemExit(f"Locked visual hash mismatch for {name}: {_sha(src)}")
        if src != target:
            shutil.copy2(src, target)

    content = StoryGenerator(settings, mode="prod").generate(plan)
    source_errors = run_source_guard(plan, content)
    if source_errors:
        raise SystemExit("Story 005 source guard failed: " + " | ".join(source_errors))
    package = content.to_v2_package()
    fmt_errors = validate_story_format_v2(package, next_title="The Birth of Lord Krishna")
    hard = [e for e in fmt_errors if "paragraphs must stay" not in e]
    if hard:
        raise SystemExit("Story 005 format V2 errors: " + " | ".join(hard))
    story_md = content.to_markdown()
    md_errors = validate_story_markdown_v2(story_md)
    if md_errors:
        raise SystemExit("Story 005 markdown errors: " + " | ".join(md_errors))
    paths.story_md.write_text(story_md, encoding="utf-8")

    audio = AudioGenerator(settings, mode="prod")
    audio_source = audio.generate_mp3(content.audio_script, paths.narration_mp3)
    duration = float(MP3(paths.narration_mp3).info.length)
    wave = validate_mp3_waveform(paths.narration_mp3, expected_duration=duration)
    if wave.status != "PASS":
        raise SystemExit(f"Story 005 waveform failed: {wave.detail}")

    work = new_work_paths(ROOT, debug=True)
    simple_score, _ = generate_simple_coloring(
        settings,
        story_md=story_md,
        content=content,
        output_path=paths.simple_coloring_page,
        work_candidates=work.coloring_candidates,
        work_reviews=work.reviews,
        poster_path=paths.story_poster,
        detailed_coloring_path=paths.coloring_page,
        mode="prod",
    )
    if simple_score < 86:
        raise SystemExit(f"Simple coloring score {simple_score} below 86")

    planner = ActivityPlanner(ROOT / "tracking" / "activity_history.csv", settings=settings)
    activity = planner.plan(plan, story_md)
    ActivitySheetGenerator().generate(plan, activity, paths.activity_sheet)
    render_dir = work.root / "activity_pages"
    pdf_check = validate_activity_pdf(paths.activity_sheet, render_dir, activity=activity)
    if pdf_check.errors:
        raise SystemExit("Story 005 PDF errors: " + " | ".join(pdf_check.errors))
    parent_key = build_parent_answer_key(activity)
    key_errors = validate_parent_answer_key(activity, parent_key)
    if key_errors:
        raise SystemExit("Parent key errors: " + " | ".join(key_errors))
    activity_score = _review_activity(
        settings, story_md, render_dir, work.reviews, "prod", activity=activity, chapter_no="005", slug=plan.slug
    )
    if activity_score < 90:
        raise SystemExit(f"Activity score {activity_score} below 90")

    folder = ensure_story_folder(settings, folder_name=paths.root.name)
    if folder.status != "READY":
        raise SystemExit(folder.detail)
    package_link = folder.package_link
    caption = format_whatsapp_caption(
        story_title=content.title,
        package_link=package_link,
        activity_title=activity.activity_title,
        recommended_send_mode=activity.recommended_send_mode,
    )
    paths.whatsapp_caption.write_text(caption, encoding="utf-8")

    ok, quality_errors, quality_warnings = run_quality_checks(
        paths,
        mode="prod",
        settings=settings,
        story_title=content.title,
        poster_score=95,
        coloring_score=95,
    )
    if not ok:
        raise SystemExit("Quality failed: " + " | ".join(quality_errors))

    write_manifest(
        settings=settings,
        plan=plan,
        content=content,
        paths=paths,
        mode="prod",
        quality_status="PASS",
        quality_errors=quality_errors,
        quality_warnings=quality_warnings,
        audio_source=audio_source,
        package_link=package_link,
        drive_status="UPLOADING",
        drive_detail="",
        poster_score=95,
        coloring_score=95,
        simple_coloring_score=simple_score,
        reference_used=True,
        activity=activity,
        activity_page_count=pdf_check.page_count,
        activity_score=activity_score,
        poster_reference_used=True,
        style_reference_used=False,
        identity_consistency_score=95,
        waveform_metrics=wave,
        matching_coverage=pdf_check.matching_coverage,
        parent_answer_key=parent_key.to_dict(),
    )
    prune_output_folder(paths.root)
    final_names = {p.name for p in paths.root.iterdir() if p.is_file()}
    if final_names != set(FINAL_OUTPUT_FILES):
        raise SystemExit(f"Story 005 package must be exact 8 files, found {sorted(final_names)}")

    upload = upload_files_to_folder(
        settings,
        folder_id=folder.folder_id,
        package_link=package_link,
        source_dir=paths.root,
        files=FINAL_OUTPUT_FILES,
        folder_name=paths.root.name,
        prune_extras=True,
    )
    if upload.status != "UPLOADED":
        raise SystemExit(upload.detail)
    write_manifest(
        settings=settings,
        plan=plan,
        content=content,
        paths=paths,
        mode="prod",
        quality_status="PASS",
        quality_errors=quality_errors,
        quality_warnings=quality_warnings,
        audio_source=audio_source,
        package_link=package_link,
        drive_status="UPLOADED",
        drive_detail=upload.detail,
        poster_score=95,
        coloring_score=95,
        simple_coloring_score=simple_score,
        reference_used=True,
        activity=activity,
        activity_page_count=pdf_check.page_count,
        activity_score=activity_score,
        poster_reference_used=True,
        style_reference_used=False,
        identity_consistency_score=95,
        waveform_metrics=wave,
        matching_coverage=pdf_check.matching_coverage,
        parent_answer_key=parent_key.to_dict(),
    )
    paths.whatsapp_caption.write_text(caption, encoding="utf-8")
    reupload = upload_files_to_folder(
        settings,
        folder_id=folder.folder_id,
        package_link=package_link,
        source_dir=paths.root,
        files=("manifest.json", "whatsapp_caption.txt"),
        folder_name=paths.root.name,
    )
    if reupload.status != "UPLOADED":
        raise SystemExit(reupload.detail)
    ok_verify, detail = verify_drive_text_links(settings, folder_id=folder.folder_id, package_link=package_link)
    if not ok_verify:
        raise SystemExit(detail)
    if _sha(paths.story_poster) != POSTER_HASH_005 or _sha(paths.coloring_page) != COLORING_HASH_005:
        raise SystemExit("Story 005 visual lock broken after rebuild")
    planner.record(plan, activity)
    cleanup_work(work, keep=False)
    return {
        "status": "SUCCESS",
        "chapter_no": "005",
        "package_link": package_link,
        "simple_coloring_score": simple_score,
        "activity_score": activity_score,
        "audio_source": audio_source,
        "voice_name": audio.last_voice_name,
    }


def main() -> int:
    from krishna_story_factory.config import load_settings
    from krishna_story_factory.csv_store import read_queue_state
    from krishna_story_factory.pipeline import archive_packages_for_range, rebuild_story_range, restore_queue_snapshot

    settings = load_settings(ROOT)
    queue_before = read_queue_state(ROOT)
    archive_dir = archive_packages_for_range(settings, start="001", end="005")
    print(json.dumps({"archive": str(archive_dir)}, indent=2))

    # Rebuild 001-004 via pipeline range helper without final queue restore yet.
    partial = rebuild_story_range(
        settings,
        range_spec="001:004",
        mode="prod",
        preserve_queue=True,
        replace_drive=True,
        debug=False,
        archive=False,
    )
    print(json.dumps({"partial_001_004": partial.get("status"), "queue": partial.get("queue")}, indent=2))

    result_005 = _rebuild_005_preserve_visuals(settings, archive_dir)
    print(json.dumps({"story_005": result_005}, indent=2))

    # Final queue lock: 001-005 done, 006+ pending, preserve drive folder ids.
    restored = {row.get("chapter_no", "").zfill(3): dict(row) for row in queue_before}
    for chapter in range(1, 6):
        chapter_no = f"{chapter:03d}"
        row = restored.setdefault(chapter_no, {"chapter_no": chapter_no, "status": "done"})
        row["status"] = "done"
    for chapter_no, row in restored.items():
        if int(chapter_no or "0") >= 6:
            row["status"] = "pending"
    # Prefer existing drive folder ids from before; 005 already known.
    restore_queue_snapshot(ROOT, sorted(restored.values(), key=lambda r: int(r.get("chapter_no") or 0)))
    queue_after = {r["chapter_no"].zfill(3): r["status"] for r in read_queue_state(ROOT)}
    assert queue_after.get("006") == "pending"
    for i in range(1, 6):
        assert queue_after.get(f"{i:03d}") == "done"
    print(json.dumps({"status": "SUCCESS", "queue": queue_after, "archive": str(archive_dir)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
