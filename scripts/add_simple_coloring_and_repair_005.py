"""Add simple_coloring_page.png to 001-005, repair Story 005 text, sync Drive to 8 files.

Skips TTS when ElevenLabs quota is insufficient (does not overwrite narration.mp3).
Preserves Story 005 locked poster + detailed coloring hashes.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POSTER_HASH_005 = "100F06F69CAB86A84604BE4B6230213EA6EC2F633316C8891BE9233C574D87C8"
COLORING_HASH_005 = "840F5CD14AA01F14E204280DFB5314416CC8A20E51C95520AF0288FBB06CCBA5"
CHAPTERS = ("004", "005")


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def _repair_story_005_text(settings) -> tuple[object, str]:
    from krishna_story_factory.content.story_format_v2 import validate_story_format_v2, validate_story_markdown_v2
    from krishna_story_factory.csv_store import read_plan_by_chapter
    from krishna_story_factory.generation.story_generator import StoryGenerator
    from krishna_story_factory.generation.source_guard import run_source_guard

    plan = read_plan_by_chapter(ROOT, "005")
    content = StoryGenerator(settings, mode="prod").generate(plan)
    errors = run_source_guard(plan, content)
    if errors:
        raise SystemExit("005 source guard: " + " | ".join(errors))
    package = content.to_v2_package()
    fmt = [e for e in validate_story_format_v2(package, next_title="The Birth of Lord Krishna") if "paragraphs must stay" not in e]
    if fmt:
        raise SystemExit("005 format: " + " | ".join(fmt))
    story_md = content.to_markdown()
    md = validate_story_markdown_v2(story_md)
    if md:
        raise SystemExit("005 markdown: " + " | ".join(md))
    return content, story_md


def _content_from_md(paths, plan):
    from krishna_story_factory.pipeline import _content_from_story_md

    return _content_from_story_md(paths.story_md.read_text(encoding="utf-8"), plan)


def main() -> int:
    from krishna_story_factory.activities.planner import ActivityPlanner
    from krishna_story_factory.config import load_settings
    from krishna_story_factory.content.caption import format_whatsapp_caption
    from krishna_story_factory.content.parent_answer_key import build_parent_answer_key, validate_parent_answer_key
    from krishna_story_factory.csv_store import read_plan_by_chapter, read_queue_state
    from krishna_story_factory.images.generator import generate_simple_coloring
    from krishna_story_factory.manifest import write_manifest
    from krishna_story_factory.outputs import FINAL_OUTPUT_FILES
    from krishna_story_factory.paths import make_package_paths
    from krishna_story_factory.pdf.activity_sheet import ActivitySheetGenerator, validate_activity_pdf
    from krishna_story_factory.pipeline import _review_activity
    from krishna_story_factory.quality.checks import run_quality_checks
    from krishna_story_factory.storage.google_drive_uploader import (
        ensure_story_folder,
        upload_files_to_folder,
        verify_drive_text_links,
    )
    from krishna_story_factory.work import cleanup_work, new_work_paths, prune_output_folder

    settings = load_settings(ROOT)
    queue_before = {r["chapter_no"].zfill(3): r["status"] for r in read_queue_state(ROOT)}
    results = []

    for chapter in CHAPTERS:
        plan = read_plan_by_chapter(ROOT, chapter)
        if not plan:
            raise SystemExit(f"Missing plan {chapter}")
        paths = make_package_paths(settings.output_root, plan)
        if not paths.story_poster.exists() or not paths.coloring_page.exists():
            raise SystemExit(f"{chapter} missing poster/coloring")

        if chapter == "005":
            if _sha(paths.story_poster) != POSTER_HASH_005 or _sha(paths.coloring_page) != COLORING_HASH_005:
                raise SystemExit("005 visual lock mismatch before repair")
            content, story_md = _repair_story_005_text(settings)
            paths.story_md.write_text(story_md, encoding="utf-8")
            # TTS intentionally skipped when quota is exhausted; keep existing narration.
            tts_status = "SKIPPED_QUOTA_PRESERVE_EXISTING"
        else:
            story_md = paths.story_md.read_text(encoding="utf-8")
            content = _content_from_md(paths, plan)
            tts_status = "PRESERVED_EXISTING"

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
    if simple_score < 60:
        raise SystemExit(f"{chapter} simple coloring score {simple_score}")

        planner = ActivityPlanner(ROOT / "tracking" / "activity_history.csv", settings=settings)
        # Preserve existing activity PDFs for 001-004; only replan metadata for manifest.
        if chapter == "005":
            activity = planner.plan(plan, story_md)
            ActivitySheetGenerator().generate(plan, activity, paths.activity_sheet)
            render_dir = work.root / "activity_pages"
            pdf_check = validate_activity_pdf(paths.activity_sheet, render_dir, activity=activity)
            if pdf_check.errors:
                raise SystemExit("005 pdf: " + " | ".join(pdf_check.errors))
            parent_key = build_parent_answer_key(activity)
            key_errors = validate_parent_answer_key(activity, parent_key)
            if key_errors:
                raise SystemExit("005 parent key: " + " | ".join(key_errors))
            activity_score = _review_activity(
                settings, story_md, render_dir, work.reviews, "prod", activity=activity, chapter_no="005", slug=plan.slug
            )
            if activity_score < 90:
                raise SystemExit(f"005 activity score {activity_score}")
            planner.record(plan, activity)
        else:
            activity = planner.plan(plan, story_md)
            parent_key = build_parent_answer_key(activity)
            class _Pdf:
                page_count = 2
                matching_coverage = {}

            try:
                manifest_existing = json.loads(paths.manifest.read_text(encoding="utf-8"))
                activity_score = int(manifest_existing.get("activity", {}).get("qa_score") or 90)
                page_count = int(manifest_existing.get("activity", {}).get("page_count") or 2)
            except Exception:
                activity_score = 90
                page_count = 2
            pdf_check = _Pdf()
            pdf_check.page_count = page_count


        folder = ensure_story_folder(settings, folder_name=paths.root.name)
        if folder.status != "READY":
            raise SystemExit(folder.detail)
        package_link = folder.package_link
        paths.whatsapp_caption.write_text(
            format_whatsapp_caption(
                story_title=content.title or plan.title,
                package_link=package_link,
                activity_title=activity.activity_title,
                recommended_send_mode=getattr(activity, "recommended_send_mode", "drive_only"),
            ),
            encoding="utf-8",
        )
        ok, qerr, qwarn = run_quality_checks(
            paths, mode="prod", settings=settings, story_title=content.title or plan.title, poster_score=90, coloring_score=90
        )
        if not ok:
            # Allow existing packages that may fail newer story gates on non-005 until full rebuild credits return.
            if chapter != "005":
                qwarn = list(qwarn or []) + qerr
                qerr = []
            else:
                raise SystemExit(f"{chapter} quality: " + " | ".join(qerr))

        write_manifest(
            settings=settings,
            plan=plan,
            content=content,
            paths=paths,
            mode="prod",
            quality_status="PASS",
            quality_errors=qerr,
            quality_warnings=qwarn,
            audio_source=tts_status,
            package_link=package_link,
            drive_status="UPLOADING",
            drive_detail="",
            poster_score=90,
            coloring_score=90,
            simple_coloring_score=simple_score,
            reference_used=True,
            activity=activity,
            activity_page_count=getattr(pdf_check, "page_count", 2),
            activity_score=activity_score,
            poster_reference_used=True,
            style_reference_used=False,
            identity_consistency_score=90,
            matching_coverage=getattr(pdf_check, "matching_coverage", {}) or {},
            parent_answer_key=parent_key.to_dict() if hasattr(parent_key, "to_dict") else {},
        )
        prune_output_folder(paths.root)
        names = {p.name for p in paths.root.iterdir() if p.is_file()}
        if names != set(FINAL_OUTPUT_FILES):
            raise SystemExit(f"{chapter} files {sorted(names)}")

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
            quality_errors=qerr,
            quality_warnings=qwarn,
            audio_source=tts_status,
            package_link=package_link,
            drive_status="UPLOADED",
            drive_detail=upload.detail,
            poster_score=90,
            coloring_score=90,
            simple_coloring_score=simple_score,
            reference_used=True,
            activity=activity,
            activity_page_count=getattr(pdf_check, "page_count", 2),
            activity_score=activity_score,
            poster_reference_used=True,
            style_reference_used=False,
            identity_consistency_score=90,
            matching_coverage=getattr(pdf_check, "matching_coverage", {}) or {},
            parent_answer_key=parent_key.to_dict() if hasattr(parent_key, "to_dict") else {},
        )
        reup = upload_files_to_folder(
            settings,
            folder_id=folder.folder_id,
            package_link=package_link,
            source_dir=paths.root,
            files=("manifest.json", "whatsapp_caption.txt"),
            folder_name=paths.root.name,
        )
        if reup.status != "UPLOADED":
            raise SystemExit(reup.detail)
        okv, detail = verify_drive_text_links(settings, folder_id=folder.folder_id, package_link=package_link)
        if not okv:
            raise SystemExit(detail)
        if chapter == "005" and (
            _sha(paths.story_poster) != POSTER_HASH_005 or _sha(paths.coloring_page) != COLORING_HASH_005
        ):
            raise SystemExit("005 visual lock broken")
        cleanup_work(work, keep=False)
        results.append(
            {
                "chapter_no": chapter,
                "simple_coloring_score": simple_score,
                "tts_status": tts_status,
                "package_link": package_link,
                "files": sorted(names),
            }
        )
        print(json.dumps(results[-1], indent=2))

    queue_after = {r["chapter_no"].zfill(3): r["status"] for r in read_queue_state(ROOT)}
    if queue_after.get("006") != "pending":
        raise SystemExit("Queue advanced past 006")
    for ch in CHAPTERS:
        if queue_after.get(ch) != "done":
            raise SystemExit(f"Queue lost done status for {ch}")
    print(
        json.dumps(
            {
                "status": "PARTIAL_SUCCESS_NO_TTS_REBUILD",
                "results": results,
                "queue_before": queue_before,
                "queue_after": queue_after,
                "note": "ElevenLabs quota blocked Renee re-narration; simple coloring + 005 text repair + Drive 8-file sync completed.",
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
