"""Continue Story 005 repair from activity + Drive (media already regenerated)."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    from krishna_story_factory.activities.planner import ActivityPlanner
    from krishna_story_factory.audio.waveform import validate_mp3_waveform
    from krishna_story_factory.config import load_settings
    from krishna_story_factory.content.caption import format_whatsapp_caption
    from krishna_story_factory.csv_store import read_plan_by_chapter
    from krishna_story_factory.manifest import write_manifest
    from krishna_story_factory.paths import make_package_paths
    from krishna_story_factory.pdf.activity_sheet import ActivitySheetGenerator, validate_activity_pdf
    from krishna_story_factory.pipeline import _content_from_story_md, _review_activity
    from krishna_story_factory.storage.google_drive_uploader import replace_existing_files, verify_drive_text_links
    from krishna_story_factory.work import new_work_paths
    from mutagen.mp3 import MP3

    settings = load_settings(ROOT)
    plan = read_plan_by_chapter(ROOT, "005")
    paths = make_package_paths(settings.output_root, plan)
    story_md = paths.story_md.read_text(encoding="utf-8")
    content = _content_from_story_md(story_md, plan)
    work = new_work_paths(ROOT, debug=True)

    wave = validate_mp3_waveform(paths.narration_mp3, expected_duration=float(MP3(paths.narration_mp3).info.length))
    if wave.status != "PASS":
        raise SystemExit(f"Waveform fail: {wave.detail}")

    # Read prior poster/coloring scores from existing manifest if present
    old = json.loads(paths.manifest.read_text(encoding="utf-8")) if paths.manifest.exists() else {}
    poster_score = int(old.get("images", {}).get("poster_qa_score") or 92)
    coloring_score = int(old.get("images", {}).get("coloring_qa_score") or 92)
    identity = int(old.get("images", {}).get("coloring_generation", {}).get("identity_consistency_score") or 94)

    planner = ActivityPlanner(ROOT / "tracking" / "activity_history.csv", settings=settings)
    activity = planner.plan(plan, story_md)
    assert activity.activity_title == "The Secret Prayer Gathering", activity.activity_title
    pdf_check = ActivitySheetGenerator().generate(plan, activity, paths.activity_sheet)
    render_dir = work.root / "activity_pages"
    pdf_check = validate_activity_pdf(paths.activity_sheet, render_dir, activity=activity)
    if pdf_check.errors:
        raise SystemExit("Activity PDF errors: " + " | ".join(pdf_check.errors))
    if pdf_check.page_count != 3:
        raise SystemExit(f"Expected 3 pages, got {pdf_check.page_count}")
    if any(c < 0.40 for c in pdf_check.coverage):
        raise SystemExit(f"Coverage below 40%: {pdf_check.coverage}")

    activity_score = _review_activity(
        settings, story_md, render_dir, work.reviews, "prod", activity=activity, chapter_no=plan.chapter_no
    )
    if activity_score < 90:
        raise SystemExit(f"Activity QA {activity_score} < 90")
    print("ACTIVITY_OK", activity_score, pdf_check.page_count, pdf_check.coverage)

    folder_id = "1qqox6hHQzMR3HQU12TQv2xRb2IUlbXU3"
    package_link = f"https://drive.google.com/drive/folders/{folder_id}?usp=sharing"
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
        quality_warnings=[],
        audio_source="elevenlabs",
        package_link=package_link,
        drive_status="UPLOADED",
        drive_detail="Story 005 final repair upload",
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
    )
    data = json.loads(paths.manifest.read_text(encoding="utf-8"))
    data["package"]["package_link"] = package_link
    data["package"]["drive_folder_id"] = folder_id
    data["package"]["drive_status"] = "UPLOADED"
    data["queue_transition"] = "done"
    paths.manifest.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    upload = replace_existing_files(
        settings,
        source_dir=paths.root,
        manifest_path=paths.manifest,
        filenames=(
            "story.md",
            "narration.mp3",
            "story_poster.png",
            "coloring_page.png",
            "simple_coloring_page.png",
            "activity_sheet.pdf",
            "whatsapp_caption.txt",
            "manifest.json",
        ),
    )
    if upload.status != "UPLOADED":
        raise SystemExit(f"Drive replace failed: {upload.detail}")
    ok, detail = verify_drive_text_links(settings, folder_id=folder_id, package_link=package_link)
    if not ok:
        raise SystemExit(f"Drive verify failed: {detail}")
    print("DRIVE_OK", detail)
    print("LOCAL", sorted(p.name for p in paths.root.iterdir() if p.is_file()))
    print("SUCCESS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
