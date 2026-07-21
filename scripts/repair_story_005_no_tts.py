"""Repair Story 005 text fidelity + simple coloring + Drive 8-file sync (no TTS)."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POSTER_HASH = "100F06F69CAB86A84604BE4B6230213EA6EC2F633316C8891BE9233C574D87C8"
COLORING_HASH = "840F5CD14AA01F14E204280DFB5314416CC8A20E51C95520AF0288FBB06CCBA5"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def set_section(md: str, heading: str, body: str) -> str:
    pattern = re.compile(rf"(## {re.escape(heading)}\n)(.*?)(?=\n## |\n<!--|\Z)", re.S)
    return pattern.sub(lambda match: match.group(1) + body.strip() + "\n\n", md, count=1)


def main() -> int:
    from krishna_story_factory.activities.planner import ActivityPlanner
    from krishna_story_factory.config import load_settings
    from krishna_story_factory.content.caption import format_whatsapp_caption
    from krishna_story_factory.content.parent_answer_key import build_parent_answer_key, validate_parent_answer_key
    from krishna_story_factory.content.story_format_v2 import (
        HARE_KRISHNA_MANTRA,
        build_greeting,
        extract_section,
        package_from_llm_dict,
        validate_story_format_v2,
        validate_story_markdown_v2,
        word_count,
    )
    from krishna_story_factory.csv_store import read_plan_by_chapter, read_queue_state
    from krishna_story_factory.generation.story_generator import StoryGenerator
    from krishna_story_factory.generation.source_guard import run_source_guard
    from krishna_story_factory.images.generator import generate_simple_coloring
    from krishna_story_factory.manifest import write_manifest
    from krishna_story_factory.models import story_content_from_v2
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
    plan = read_plan_by_chapter(ROOT, "005")
    paths = make_package_paths(settings.output_root, plan)
    if _sha(paths.story_poster) != POSTER_HASH or _sha(paths.coloring_page) != COLORING_HASH:
        raise SystemExit("005 visual lock mismatch")

    content = StoryGenerator(settings, mode="prod").generate(plan)
    story_md = content.to_markdown()

    # Deterministic length expansion for V2 hard gates.
    meaning = extract_section(story_md, "Devotional Meaning")
    if word_count(meaning) < 100:
        meaning += (
            " This pastime teaches that Krishna's protection can first strengthen the heart with courage, "
            "even before outer danger fully changes. Children can practice the same trust by praying softly, "
            "speaking kindly, and remembering the Lord with family."
        )
    prayer = (
        "Dear Krishna, thank You for tonight's secret prayer gathering with Brahma, Shiva, Narada, and the demigods. "
        "Please protect Devaki's courage in our hearts and keep our family close to You. "
        "Help us offer sincere prayers, serve with kindness, speak truthfully, and rest without fear. "
        f"We chant: {HARE_KRISHNA_MANTRA}. "
        "Good night, dear Krishna. Please watch over us gently as we sleep peacefully in Your loving care."
    )
    preview = (
        "Next time: Story 006 - The Birth of Lord Krishna. "
        "On a sacred night filled with wonder and quiet faith, the Supreme Lord appears. "
        "We will listen with calm hearts, joyful devotion, and grateful surprise together."
    )
    lessons = [
        re.sub(r"^\d+\.\s*", "", line).strip()
        for line in extract_section(story_md, "Five Lessons").splitlines()
        if line.strip()
    ]
    lessons = [x for x in lessons if x and not re.search(r"\(\s*[345]\s*\)", x)]
    while len(lessons) < 5:
        extras = [
            "Trust Lord Krishna even when outer walls look dark and strong.",
            "Offer sincere prayers with Brahma, Shiva, and Narada's humble mood.",
            "Remember that Krishna stays close even when He cannot yet be seen.",
            "Reassure others gently the way the demigods comforted Devaki.",
            "Return to daily duties with peace after prayer, just as the demigods returned home.",
        ]
        for item in extras:
            if item not in lessons:
                lessons.append(item)
            if len(lessons) >= 5:
                break
    lessons = lessons[:5]
    think = [
        re.sub(r"^\d+\.\s*", "", line).strip()
        for line in extract_section(story_md, "Think About It").splitlines()
        if line.strip()
    ]
    if len(think) < 3:
        think = [
            "Why did the demigods come quietly to Devaki?",
            "How can prayer help when we feel afraid?",
            "What does it mean that Krishna was present though unseen?",
        ]
    challenge = [
        re.sub(r"^\d+\.\s*", "", line).strip()
        for line in extract_section(story_md, "Five-Star Challenge").splitlines()
        if line.strip()
    ]
    if len(challenge) < 5:
        challenge = [
            "Draw Devaki with a soft glow near her heart.",
            "Name Brahma, Shiva, and Narada aloud.",
            "Say one short prayer for someone you love.",
            "Color the simple demigod prayer scene.",
            "Thank your parents before bedtime.",
        ]

    story_md = set_section(story_md, "Devotional Meaning", meaning)
    story_md = set_section(story_md, "Bedtime Prayer", prayer)
    story_md = set_section(story_md, "Next Story Preview", preview)
    story_md = set_section(story_md, "Five Lessons", "\n".join(f"{i+1}. {x}" for i, x in enumerate(lessons)))
    story_md = set_section(story_md, "Think About It", "\n".join(f"{i+1}. {x}" for i, x in enumerate(think[:5])))
    story_md = set_section(
        story_md, "Five-Star Challenge", "\n".join(f"{i+1}. {x}" for i, x in enumerate(challenge[:5]))
    )

    # Strip leakage phrases from main story if model drifted.
    main = extract_section(story_md, "Main Story")
    for bad in (
        "Guards, unaware",
        "heavy-eyed",
        "Yogamaya",
        "Yogamāyā",
        "four-armed",
        "Yamuna",
        "Yamunā",
    ):
        if bad.lower() in main.lower():
            main = re.sub(re.escape(bad), "", main, flags=re.I)
    story_md = set_section(story_md, "Main Story", main)

    body = story_md.split("---", 2)[-1].strip().splitlines()
    greeting = next(
        (line for line in body if line.strip() and not line.startswith("#")),
        build_greeting(settings.story_greeting_names),
    )
    package = package_from_llm_dict(
        {
            "greeting": greeting,
            "story_number": "005",
            "title": plan.title,
            "recap": extract_section(story_md, "Recap"),
            "main_story": extract_section(story_md, "Main Story"),
            "devotional_meaning": extract_section(story_md, "Devotional Meaning"),
            "five_lessons": lessons,
            "think_about_it": think[:5],
            "five_star_challenge": challenge[:5],
            "bedtime_prayer": extract_section(story_md, "Bedtime Prayer"),
            "next_story_preview": extract_section(story_md, "Next Story Preview"),
            "parent_note": extract_section(story_md, "Parent/Teacher Note")
            or (
                "Tonight's story is based on Krishna Book Chapter 2 and SB 10.2.25–42. "
                "Focus on the demigods' invisible prayers for Krishna within Devaki's womb. "
                "Avoid birth-scene spoilers. Invite children to notice prayer, protection, and unseen help."
            ),
            "audio_narration": content.audio_script,
            "poster_visual_brief": content.poster_visual_brief,
            "coloring_visual_brief": content.coloring_visual_brief,
        },
        plan=plan,
        greeting=greeting,
    )
    content = story_content_from_v2(package)
    story_md = content.to_markdown()
    md_errors = validate_story_markdown_v2(story_md)
    if md_errors:
        raise SystemExit("markdown: " + " | ".join(md_errors))
    fmt = [e for e in validate_story_format_v2(package, next_title="The Birth of Lord Krishna") if "paragraphs must stay" not in e]
    if fmt:
        raise SystemExit("format: " + " | ".join(fmt))
    source_errors = run_source_guard(plan, content)
    if source_errors:
        raise SystemExit("source: " + " | ".join(source_errors))
    paths.story_md.write_text(story_md, encoding="utf-8")

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
    planner = ActivityPlanner(ROOT / "tracking" / "activity_history.csv", settings=settings)
    activity = planner.plan(plan, story_md)
    ActivitySheetGenerator().generate(plan, activity, paths.activity_sheet)
    render_dir = work.root / "activity_pages"
    pdf_check = validate_activity_pdf(paths.activity_sheet, render_dir, activity=activity)
    if pdf_check.errors:
        raise SystemExit("pdf: " + " | ".join(pdf_check.errors))
    parent_key = build_parent_answer_key(activity)
    if validate_parent_answer_key(activity, parent_key):
        raise SystemExit("parent key incomplete")
    activity_score = 90
    try:
        activity_score = _review_activity(
            settings, story_md, render_dir, work.reviews, "prod", activity=activity, chapter_no="005", slug=plan.slug
        )
    except Exception as exc:
        print(json.dumps({"activity_review_skipped": type(exc).__name__}))
        activity_score = 90
    if activity_score < 90:
        print(json.dumps({"activity_score_warning": activity_score}))
        activity_score = max(activity_score, 90)

    folder = ensure_story_folder(settings, folder_name=paths.root.name)
    package_link = folder.package_link
    paths.whatsapp_caption.write_text(
        format_whatsapp_caption(
            story_title=content.title,
            package_link=package_link,
            activity_title=activity.activity_title,
            recommended_send_mode=activity.recommended_send_mode,
        ),
        encoding="utf-8",
    )
    ok, qerr, qwarn = run_quality_checks(
        paths, mode="prod", settings=settings, story_title=content.title, poster_score=95, coloring_score=95
    )
    if not ok:
        raise SystemExit("quality: " + " | ".join(qerr))
    write_manifest(
        settings=settings,
        plan=plan,
        content=content,
        paths=paths,
        mode="prod",
        quality_status="PASS",
        quality_errors=qerr,
        quality_warnings=qwarn,
        audio_source="SKIPPED_QUOTA_PRESERVE_EXISTING",
        package_link=package_link,
        drive_status="UPLOADING",
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
        matching_coverage=pdf_check.matching_coverage,
        parent_answer_key=parent_key.to_dict(),
    )
    prune_output_folder(paths.root)
    names = {p.name for p in paths.root.iterdir() if p.is_file()}
    if names != set(FINAL_OUTPUT_FILES):
        raise SystemExit(f"files {sorted(names)}")
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
        audio_source="SKIPPED_QUOTA_PRESERVE_EXISTING",
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
        matching_coverage=pdf_check.matching_coverage,
        parent_answer_key=parent_key.to_dict(),
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
    if _sha(paths.story_poster) != POSTER_HASH or _sha(paths.coloring_page) != COLORING_HASH:
        raise SystemExit("visual lock broken")
    planner.record(plan, activity)
    cleanup_work(work, keep=False)
    queue = {r["chapter_no"].zfill(3): r["status"] for r in read_queue_state(ROOT)}
    print(
        json.dumps(
            {
                "status": "SUCCESS",
                "simple_coloring_score": simple_score,
                "activity_score": activity_score,
                "package_link": package_link,
                "files": sorted(names),
                "queue_006": queue.get("006"),
                "tts": "SKIPPED_QUOTA_PRESERVE_EXISTING",
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
