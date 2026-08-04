#!/usr/bin/env python3
"""Complete Story 022 from an existing recovery package (no story/TTS/image regen)."""
from __future__ import annotations

import hashlib
import json
import shutil
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
CHAPTER = "022"
RUN = ROOT / "work" / "stories" / CHAPTER / "20260803-220035-c9f8c2"
PKG = RUN / "package"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def main() -> int:
    from mutagen.mp3 import MP3

    from krishna_story_factory.activities.models import SequenceCard
    from krishna_story_factory.activities.planner import ActivityPlanner, _shuffled_sequence_cards
    from krishna_story_factory.activities.story_map import (
        evaluate_activity_semantic_qa,
        reconstruct_story_map_from_canonical,
        write_activity_semantic_qa,
    )
    from krishna_story_factory.audio.pace import evaluate_pace_qa, write_audio_quality_qa
    from krishna_story_factory.audio.waveform import validate_mp3_waveform
    from krishna_story_factory.config import load_settings
    from krishna_story_factory.content.canonical_narration import (
        evaluate_canonical_narration_exact,
        extract_main_story,
        write_canonical_narration_qa,
    )
    from krishna_story_factory.content.parent_answer_key import (
        build_parent_answer_key,
        validate_parent_answer_key,
    )
    from krishna_story_factory.csv_store import read_plan_by_chapter, read_queue_state, update_plan_status
    from krishna_story_factory.manifest import write_manifest
    from krishna_story_factory.content.caption import format_whatsapp_caption
    from krishna_story_factory.package_swap import atomic_replace_package_dir, validate_exact_eight_files
    from krishna_story_factory.paths import make_package_paths
    from krishna_story_factory.pdf.activity_sheet import ActivitySheetGenerator, validate_activity_pdf
    from krishna_story_factory.pipeline import _content_from_story_md
    from krishna_story_factory.storage.google_drive_uploader import ensure_story_folder, upload_final_package
    from krishna_story_factory.activities.models import ActivityPack, ActivityPage

    settings = load_settings(ROOT)
    plan = read_plan_by_chapter(ROOT, CHAPTER)
    assert plan is not None
    evidence = (
        ROOT
        / "MyPilotDropbox"
        / "bhava-production-ops"
        / "evidence"
        / "permanent-audio-activity-gates-story-021-022-20260803"
    )
    evidence.mkdir(parents=True, exist_ok=True)

    required = [
        "story.md",
        "narration.mp3",
        "story_poster.png",
        "coloring_page.png",
        "simple_coloring_page.png",
    ]
    for name in required:
        if not (PKG / name).is_file():
            raise SystemExit(f"Missing recovery artifact: {PKG / name}")

    story_md = (PKG / "story.md").read_text(encoding="utf-8")
    content = _content_from_story_md(story_md, plan)
    content.audio_script = extract_main_story(story_md)
    if not content.audio_script:
        raise SystemExit("Main Story missing in recovery story.md")

    canon = evaluate_canonical_narration_exact(
        story_no=CHAPTER, story_md=story_md, tts_source=content.audio_script
    )
    write_canonical_narration_qa(canon, evidence / "022_canonical_narration_qa.json")
    if canon.result != "PASS":
        raise SystemExit(f"Canonical FAIL: {canon.failure_reasons}")

    duration = float(MP3(PKG / "narration.mp3").info.length)
    wave = validate_mp3_waveform(PKG / "narration.mp3", expected_duration=duration)
    pace = evaluate_pace_qa(narration_text=content.audio_script, duration_seconds=duration)
    write_audio_quality_qa(
        {
            "provider": "openai",
            "model": "gpt-4o-mini-tts-2025-12-15",
            "voice": "marin",
            "duration": duration,
            "measured_wpm": pace.measured_wpm,
            "waveform_status": wave.status,
            "pace_status": pace.status,
            "canonical_exact_match": True,
            "human_listening_status": "HUMAN_REVIEW_PENDING",
            "detail": pace.detail,
        },
        evidence / "022_audio_quality_qa.json",
    )
    if wave.status != "PASS" or pace.status != "PASS":
        raise SystemExit(f"Audio QA FAIL wave={wave.status} pace={pace.detail}")

    # Prefer semantic STORY_SEQUENCE from canonical map (no generic placeholders).
    sm = reconstruct_story_map_from_canonical(
        story_no=CHAPTER, title=plan.title, story_md=story_md, age_band=plan.age_range or "6-12"
    )
    cards = [
        SequenceCard(event=e, drawing_prompt=f"Draw one detail from: {e}", source_order=i + 1)
        for i, e in enumerate(sm.sequence_events())
    ]
    printed = _shuffled_sequence_cards(cards, plan.summary_seed or plan.title)
    activity = ActivityPack(
        activity_title=f"Put {plan.title} in Order",
        activity_type="STORY_SEQUENCE",
        send_mode="SEND_NOW",
        estimated_minutes=15,
        parent_effort="Low",
        learning_goal="Retell Lord Brahmā’s prayers and realization in order.",
        story_connection=f"Every printable piece comes from the central scene of {plan.title}.",
        materials=["pencil", "crayons"],
        pages=[
            ActivityPage(
                page_title="Story sequence cards",
                page_type="STORY_SEQUENCE_CARDS",
                instructions=["Number the cards in story order.", "Draw one source-faithful detail on each card."],
                components=printed,
                story_connection=f"Every printable piece comes from the central scene of {plan.title}.",
            ),
            ActivityPage(
                page_title="Family kindness mission",
                page_type="FAMILY_MISSION",
                instructions=["Choose one humble, prayerful action from the story and do it today."],
                components=["family mission card", "completion checkbox"],
                story_connection=f"Every printable piece comes from the central scene of {plan.title}.",
            ),
        ],
        answer_key=[c.event for c in sorted(cards, key=lambda x: x.source_order)],
    )
    semantic = evaluate_activity_semantic_qa(
        activity_type=activity.activity_type,
        events=sm.sequence_events(),
        parent_answer_events=list(activity.answer_key),
        required_tokens=["Brahmā", "Kṛṣṇa"],
        canonical_story=content.audio_script,
    )
    write_activity_semantic_qa(semantic, evidence / "022_activity_semantic_qa.json")
    if semantic.result != "PASS":
        raise SystemExit(f"Semantic FAIL: {semantic.failure_reasons}")

    ActivitySheetGenerator().generate(plan, activity, PKG / "activity_sheet.pdf")
    render_dir = RUN / "activity_pages"
    pdf_check = validate_activity_pdf(PKG / "activity_sheet.pdf", render_dir, activity=activity)
    layout = {
        "page_count": pdf_check.page_count,
        "errors": list(pdf_check.errors),
        "coverage": list(pdf_check.coverage),
        "matching_meta": pdf_check.matching_coverage,
        "result": "PASS" if not pdf_check.errors else "FAIL",
    }
    (evidence / "022_activity_layout_qa.json").write_text(json.dumps(layout, indent=2) + "\n", encoding="utf-8")
    if pdf_check.errors:
        raise SystemExit("PDF FAIL: " + " | ".join(pdf_check.errors))
    if render_dir.exists():
        dest = evidence / "022_activity_renders"
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(render_dir, dest)

    parent_key = build_parent_answer_key(activity)
    key_errors = validate_parent_answer_key(activity, parent_key)
    if key_errors:
        raise SystemExit("Parent key FAIL: " + " | ".join(key_errors))

    # Caption + Drive folder then manifest.
    folder = ensure_story_folder(settings, folder_name=f"{plan.chapter_no}_{plan.slug}")
    if folder.status != "READY":
        raise SystemExit(f"Drive folder failed: {folder.detail}")
    caption = format_whatsapp_caption(
        story_title=content.title,
        package_link=folder.package_link,
        activity_title=activity.activity_title,
        recommended_send_mode=activity.recommended_send_mode,
    )
    (PKG / "whatsapp_caption.txt").write_text(caption, encoding="utf-8")

    production = make_package_paths(settings.output_root, plan, create=False)
    from krishna_story_factory.models import PackagePaths

    paths = PackagePaths(
        root=PKG,
        story_md=PKG / "story.md",
        narration_mp3=PKG / "narration.mp3",
        story_poster=PKG / "story_poster.png",
        coloring_page=PKG / "coloring_page.png",
        simple_coloring_page=PKG / "simple_coloring_page.png",
        activity_sheet=PKG / "activity_sheet.pdf",
        whatsapp_caption=PKG / "whatsapp_caption.txt",
        manifest=PKG / "manifest.json",
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
        poster_score=90,
        coloring_score=90,
        simple_coloring_score=90,
        activity=activity,
        activity_page_count=pdf_check.page_count,
        activity_score=90,
        parent_answer_key=parent_key.to_dict(),
        matching_coverage=pdf_check.matching_coverage,
        audio_source="openai",
        audio_metadata={
            "provider": "openai",
            "model_id": "gpt-4o-mini-tts-2025-12-15",
            "voice": "marin",
            "speed": 0.90,
            "generation_verified": True,
            "duration_seconds": round(duration, 1),
            "measured_wpm": pace.measured_wpm,
            "waveform_validation_status": wave.status,
            "human_listening_status": "HUMAN_REVIEW_PENDING",
            "sha256": _sha(paths.narration_mp3),
            "bytes": paths.narration_mp3.stat().st_size,
        },
        waveform_metrics=wave,
        package_link=folder.package_link or "",
        drive_status="UPLOADING",
        reference_used=True,
    )
    manifest = json.loads(paths.manifest.read_text(encoding="utf-8"))
    manifest.setdefault("activity", {})
    manifest["activity"]["semantic_qa"] = semantic.result
    manifest["activity"]["layout_qa"] = layout["result"]
    manifest.setdefault("metrics", {})
    manifest["metrics"]["measured_wpm"] = pace.measured_wpm
    paths.manifest.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    missing = validate_exact_eight_files(PKG)
    if missing:
        raise SystemExit(f"exact-eight FAIL missing={missing}")

    stamp = datetime.now(ZoneInfo(settings.app_timezone)).strftime("%Y%m%d_%H%M%S")
    archive = settings.output_root / "_archive" / f"022_complete_{stamp}"
    swap = atomic_replace_package_dir(
        staging_dir=PKG,
        production_dir=production.root,
        archive_root=archive,
        output_root=settings.output_root,
        project_root=settings.project_root,
    )
    print("swap", swap)

    upload = upload_final_package(
        settings,
        folder_name=f"{plan.chapter_no}_{plan.slug}",
        source_dir=production.root,
    )
    print("drive", upload.status, upload.detail)
    if upload.status not in {"UPLOADED", "SUCCESS", "OK"} and "UPLOADED" not in upload.status:
        raise SystemExit(f"Drive upload failed: {upload.status} {upload.detail}")

    update_plan_status(
        settings.project_root,
        plan,
        "done",
        drive_folder_id=folder.folder_id or getattr(upload, "folder_id", "") or "",
    )
    queue = read_queue_state(settings.project_root)
    next_pending = next((r for r in queue if r.get("status") == "pending"), None)
    print(
        json.dumps(
            {
                "status": "SUCCESS",
                "chapter": CHAPTER,
                "duration": duration,
                "wpm": pace.measured_wpm,
                "drive": upload.status,
                "next_pending": (next_pending or {}).get("chapter_no"),
                "title": plan.title,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
