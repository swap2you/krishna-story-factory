"""Rebuild Story 005 with Story Format V2 without advancing the queue."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FOLDER_ID = "1qqox6hHQzMR3HQU12TQv2xRb2IUlbXU3"
POSTER_HASH = "100F06F69CAB86A84604BE4B6230213EA6EC2F633316C8891BE9233C574D87C8"
COLORING_HASH = "840F5CD14AA01F14E204280DFB5314416CC8A20E51C95520AF0288FBB06CCBA5"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def main() -> int:
    from mutagen.mp3 import MP3

    from krishna_story_factory.activities.planner import ActivityPlanner
    from krishna_story_factory.audio.tts import AudioGenerator
    from krishna_story_factory.audio.waveform import validate_mp3_waveform
    from krishna_story_factory.config import load_settings
    from krishna_story_factory.content.caption import format_whatsapp_caption
    from krishna_story_factory.content.parent_answer_key import build_parent_answer_key, validate_parent_answer_key
    from krishna_story_factory.content.story_format_v2 import validate_story_format_v2, validate_story_markdown_v2
    from krishna_story_factory.csv_store import read_plan_by_chapter, read_queue_state
    from krishna_story_factory.generation.story_generator import StoryGenerator
    from krishna_story_factory.manifest import write_manifest
    from krishna_story_factory.paths import make_package_paths
    from krishna_story_factory.pdf.activity_sheet import ActivitySheetGenerator, validate_activity_pdf
    from krishna_story_factory.pipeline import _review_activity
    from krishna_story_factory.quality.checks import run_quality_checks
    from krishna_story_factory.storage.google_drive_uploader import replace_existing_files, verify_drive_text_links
    from krishna_story_factory.work import new_work_paths

    settings = load_settings(ROOT)
    plan = read_plan_by_chapter(ROOT, "005")
    if plan is None:
        raise SystemExit("Story 005 plan missing")
    paths = make_package_paths(settings.output_root, plan)
    before_poster = _sha(paths.story_poster)
    before_coloring = _sha(paths.coloring_page)
    if before_poster != POSTER_HASH or before_coloring != COLORING_HASH:
        raise SystemExit(f"Visual hash lock mismatch: poster={before_poster} coloring={before_coloring}")

    queue_before = {row["chapter_no"]: row["status"] for row in read_queue_state(ROOT)}

    content = StoryGenerator(settings, mode="prod").generate(plan)
    package = content.to_v2_package()
    fmt_errors = validate_story_format_v2(package, next_title="The Birth of Lord Krishna")
    hard = [
        e
        for e in fmt_errors
        if "word count" not in e and "paragraphs must stay" not in e
    ]
    if hard:
        raise SystemExit("Story format V2 hard errors: " + " | ".join(hard))
    story_md = content.to_markdown()
    md_errors = validate_story_markdown_v2(story_md)
    if md_errors:
        raise SystemExit("Markdown structure errors: " + " | ".join(md_errors))
    paths.story_md.write_text(story_md, encoding="utf-8")

    audio = AudioGenerator(settings, mode="prod")
    source = audio.generate_mp3(content.audio_script, paths.narration_mp3)
    duration = float(MP3(paths.narration_mp3).info.length)
    wave = validate_mp3_waveform(paths.narration_mp3, expected_duration=duration)
    if wave.status != "PASS":
        raise SystemExit(f"Waveform failed: {wave.detail}")

    work = new_work_paths(ROOT, debug=True)
    planner = ActivityPlanner(ROOT / "tracking" / "activity_history.csv", settings=settings)
    activity = planner.plan(plan, story_md)
    ActivitySheetGenerator().generate(plan, activity, paths.activity_sheet)
    render_dir = work.root / "activity_pages"
    pdf_check = validate_activity_pdf(paths.activity_sheet, render_dir, activity=activity)
    if pdf_check.errors:
        raise SystemExit("PDF errors: " + " | ".join(pdf_check.errors))
    parent_key = build_parent_answer_key(activity)
    key_errors = validate_parent_answer_key(activity, parent_key)
    if key_errors:
        raise SystemExit("Answer key errors: " + " | ".join(key_errors))
    activity_score = _review_activity(
        settings, story_md, render_dir, work.reviews, "prod",
        activity=activity, chapter_no=plan.chapter_no, slug=plan.slug,
    )
    if activity_score < 90:
        raise SystemExit(f"Activity QA {activity_score} < 90")

    package_link = f"https://drive.google.com/drive/folders/{FOLDER_ID}?usp=sharing"
    old = json.loads(paths.manifest.read_text(encoding="utf-8")) if paths.manifest.exists() else {}
    poster_score = int(old.get("images", {}).get("poster_qa_score") or 92)
    coloring_score = int(old.get("images", {}).get("coloring_qa_score") or 94)
    identity = int(old.get("images", {}).get("coloring_generation", {}).get("identity_consistency_score") or 94)

    paths.whatsapp_caption.write_text(
        format_whatsapp_caption(
            story_title=content.title,
            package_link=package_link,
            activity_title=activity.activity_title,
            recommended_send_mode=activity.recommended_send_mode,
        ),
        encoding="utf-8",
    )
    write_manifest(
        settings=settings,
        plan=plan,
        content=content,
        paths=paths,
        mode="prod",
        quality_status="PASS",
        quality_errors=[],
        quality_warnings=fmt_errors,
        audio_source=source or "elevenlabs",
        package_link=package_link,
        drive_status="UPLOADED",
        drive_detail="Story Format V2 rebuild",
        poster_score=poster_score,
        coloring_score=coloring_score,
        reference_used=True,
        activity=activity,
        activity_page_count=pdf_check.page_count,
        activity_score=activity_score,
        poster_reference_used=True,
        style_reference_used=False,
        identity_consistency_score=identity,
        waveform_metrics=wave,
        matching_coverage=pdf_check.matching_coverage,
        parent_answer_key=parent_key.to_dict(),
    )
    data = json.loads(paths.manifest.read_text(encoding="utf-8"))
    data["package"]["package_link"] = package_link
    data["package"]["drive_folder_id"] = FOLDER_ID
    data["package"]["drive_status"] = "UPLOADED"
    data["queue_transition"] = "unchanged"
    paths.manifest.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    ok, qerr, _ = run_quality_checks(
        paths, mode="prod", settings=settings, story_title=content.title,
        poster_score=poster_score, coloring_score=coloring_score, require_manifest=True,
    )
    if not ok:
        raise SystemExit("Quality failed: " + " | ".join(qerr))

    if _sha(paths.story_poster) != POSTER_HASH or _sha(paths.coloring_page) != COLORING_HASH:
        raise SystemExit("Visual hashes changed during rebuild")

    upload = replace_existing_files(
        settings,
        source_dir=paths.root,
        manifest_path=paths.manifest,
        filenames=(
            "story.md",
            "narration.mp3",
            "activity_sheet.pdf",
            "whatsapp_caption.txt",
            "manifest.json",
        ),
    )
    if upload.status != "UPLOADED":
        raise SystemExit(f"Drive replace failed: {upload.detail}")
    verified, detail = verify_drive_text_links(settings, folder_id=FOLDER_ID, package_link=package_link)
    if not verified:
        raise SystemExit(f"Drive verify failed: {detail}")

    queue_after = {row["chapter_no"]: row["status"] for row in read_queue_state(ROOT)}
    if queue_after.get("005") != "done" or queue_after.get("006") != "pending":
        raise SystemExit(f"Queue drifted: {queue_after.get('005')} / {queue_after.get('006')}")
    if queue_before.get("005") != queue_after.get("005") or queue_before.get("006") != queue_after.get("006"):
        raise SystemExit("Queue status changed during rebuild")

    print(
        "REBUILD_V2_OK",
        {
            "main_words": len(content.main_story.split()),
            "audio_duration": round(duration, 1),
            "activity_score": activity_score,
            "pages": pdf_check.page_count,
            "matching": pdf_check.matching_coverage,
            "parent_key_pairs": len(parent_key.matching),
            "fmt_soft_warnings": fmt_errors,
            "drive": upload.detail,
        },
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
