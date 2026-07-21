"""Deterministic Story 005 repair: story already written; regenerate audio/poster/activity; Drive replace."""
from __future__ import annotations

import json
import re
import shutil
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    from krishna_story_factory.activities.planner import ActivityPlanner
    from krishna_story_factory.audio.tts import AudioGenerator
    from krishna_story_factory.audio.waveform import validate_mp3_waveform
    from krishna_story_factory.config import load_settings
    from krishna_story_factory.content.caption import format_whatsapp_caption
    from krishna_story_factory.csv_store import read_plan_by_chapter
    from krishna_story_factory.images.generator import generate_coloring, generate_poster
    from krishna_story_factory.images.vision_qa import review_image, save_review
    from krishna_story_factory.manifest import write_manifest
    from krishna_story_factory.models import StoryContent
    from krishna_story_factory.paths import make_package_paths
    from krishna_story_factory.pdf.activity_sheet import ActivitySheetGenerator, validate_activity_pdf
    from krishna_story_factory.pipeline import _content_from_story_md, _validate_audio
    from krishna_story_factory.storage.google_drive_uploader import replace_existing_files, verify_drive_text_links
    from krishna_story_factory.work import new_work_paths

    settings = load_settings(ROOT)
    plan = read_plan_by_chapter(ROOT, "005")
    if not plan:
        raise SystemExit("Story 005 plan row missing")
    paths = make_package_paths(settings.output_root, plan)
    story_md = paths.story_md.read_text(encoding="utf-8")
    # Boundary sniff
    lower = story_md.lower()
    for banned in ("guards dozed", "sarasvati", "born as a baby", "four-armed", "yamuna crossing"):
        if banned in lower:
            raise SystemExit(f"Boundary leak: {banned}")
    content = _content_from_story_md(story_md, plan)
    # Enrich briefs from HTML comments if present
    poster_m = re.search(r"## Poster Visual Brief\s*\n(.*?)(?=\n## |\n-->)", story_md, re.S)
    if poster_m:
        content.poster_visual_brief = poster_m.group(1).strip()
        content.poster_one_liner = "The demigods pray while Krishna remains unseen within Devaki."
    audio_m = re.search(r"## Audio Performance Script\s*\n(.*?)(?=\n## |\n-->)", story_md, re.S)
    if audio_m:
        content.audio_script = audio_m.group(1).strip()

    work = new_work_paths(ROOT, debug=True)
    mode = "prod"

    print("AUDIO...")
    audio_gen = AudioGenerator(settings, mode)
    audio_source = audio_gen.generate_mp3(content.audio_script, paths.narration_mp3)
    wave = _validate_audio(paths.narration_mp3, settings, mode, low_credit=audio_gen.low_credit_mode)
    print("AUDIO_OK", audio_source, getattr(wave, "status", wave))

    print("POSTER...")
    # Force stronger iconography into brief
    content.poster_visual_brief = (
        (content.poster_visual_brief or "")
        + " HARD RULES: Devaki centered with sacred glow at womb/heart. "
        "Brahma clearly four-headed. Shiva recognizable. Narada may hold vina. "
        "Krishna MUST NOT appear as a separate visible sky figure or crowned sky deity. "
        "No birth scene. No sleeping guards."
    )
    poster_score, poster_ref = generate_poster(
        settings,
        story_md=story_md,
        content=content,
        output_path=paths.story_poster,
        work_candidates=work.poster_candidates,
        work_reviews=work.reviews,
        mode=mode,
    )
    if poster_score < 90:
        raise SystemExit(f"Poster QA {poster_score} < 90")
    print("POSTER_OK", poster_score)

    print("COLORING check...")
    coloring_score, pref, sref, identity = generate_coloring(
        settings,
        story_md=story_md,
        content=content,
        output_path=work.root / "coloring_check.png",
        work_candidates=work.coloring_candidates,
        work_reviews=work.reviews,
        poster_path=paths.story_poster,
        mode=mode,
        max_candidates=1,
    )
    # Keep existing coloring unless hard mismatch
    if coloring_score < 90 or identity < 90:
        print("COLORING regenerate required", coloring_score, identity)
        shutil.copy2(work.root / "coloring_check.png", paths.coloring_page)
        coloring_score_final = coloring_score
        identity_final = identity
        poster_content_ref, style_ref = pref, sref
    else:
        print("COLORING keep existing", coloring_score, identity)
        coloring_score_final = coloring_score
        identity_final = identity
        poster_content_ref, style_ref = True, False
        # Still run identity against existing file
        from krishna_story_factory.images.vision_qa import COLORING_RUBRIC

        review = review_image(
            settings,
            story_md=story_md,
            image_path=paths.coloring_page,
            kind="coloring",
            rubric=COLORING_RUBRIC,
            comparison_path=paths.story_poster,
        )
        save_review(work.reviews, "coloring_existing", review)
        coloring_score_final = review.score
        identity_final = review.identity_consistency_score
        if coloring_score_final < 90 or identity_final < 90 or review.hard_rejection:
            print("Existing coloring failed; replacing")
            shutil.copy2(work.root / "coloring_check.png", paths.coloring_page)
            coloring_score_final, identity_final = coloring_score, identity
            poster_content_ref, style_ref = pref, sref

    print("ACTIVITY...")
    planner = ActivityPlanner(ROOT / "tracking" / "activity_history.csv", settings=settings)
    activity = planner.plan(plan, story_md)
    assert activity.activity_title == "The Secret Prayer Gathering"
    # Skip expensive poster/coloring if already done this run via env? Always regenerate activity PDF.
    pdf_check = ActivitySheetGenerator().generate(plan, activity, paths.activity_sheet)
    render_dir = work.root / "activity_pages"
    pdf_check = validate_activity_pdf(paths.activity_sheet, render_dir, activity=activity)
    if pdf_check.errors:
        raise SystemExit("Activity PDF errors: " + " | ".join(pdf_check.errors))
    if pdf_check.page_count != 3:
        raise SystemExit(f"Expected 3 pages, got {pdf_check.page_count}")
    if any(c < 0.40 for c in pdf_check.coverage):
        raise SystemExit(f"Coverage below 40%: {pdf_check.coverage}")

    from krishna_story_factory.pipeline import _review_activity

    activity_score = _review_activity(
        settings, story_md, render_dir, work.reviews, mode, activity=activity, chapter_no=plan.chapter_no
    )
    if activity_score < 90:
        raise SystemExit(f"Activity QA {activity_score} < 90")
    print("ACTIVITY_OK", activity_score, pdf_check.page_count)

    folder_id = "1qqox6hHQzMR3HQU12TQv2xRb2IUlbXU3"
    package_link = f"https://drive.google.com/drive/folders/{folder_id}?usp=sharing"
    caption = format_whatsapp_caption(
        story_title=content.title,
        package_link=package_link,
        activity_title=activity.activity_title,
        recommended_send_mode=activity.recommended_send_mode,
    )
    paths.whatsapp_caption.write_text(caption, encoding="utf-8")

    write_manifest(
        settings=settings,
        plan=plan,
        content=content,
        paths=paths,
        mode=mode,
        quality_status="PASS",
        quality_errors=[],
        quality_warnings=[],
        audio_source=audio_source,
        package_link=package_link,
        drive_status="UPLOADED",
        drive_detail="Story 005 final repair upload",
        poster_score=poster_score,
        coloring_score=coloring_score_final,
        reference_used=poster_ref or poster_content_ref or style_ref,
        activity=activity,
        activity_page_count=pdf_check.page_count,
        activity_score=activity_score,
        poster_reference_used=poster_content_ref,
        style_reference_used=style_ref,
        identity_consistency_score=identity_final,
        waveform_metrics=wave if hasattr(wave, "peak") else None,
    )
    # Ensure package link and folder id in manifest
    data = json.loads(paths.manifest.read_text(encoding="utf-8"))
    data["package"]["package_link"] = package_link
    data["package"]["drive_folder_id"] = folder_id
    data["package"]["drive_status"] = "UPLOADED"
    data["queue_transition"] = "done"
    paths.manifest.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    print("DRIVE replace...")
    upload = replace_existing_files(
        settings,
        source_dir=paths.root,
        manifest_path=paths.manifest,
        filenames=(
            "story.md",
            "narration.mp3",
            "story_poster.png",
            "coloring_page.png",
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

    names = sorted(p.name for p in paths.root.iterdir() if p.is_file())
    print("LOCAL_FILES", names)
    print("SUCCESS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
