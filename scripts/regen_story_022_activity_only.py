#!/usr/bin/env python3
"""Regenerate Story 022 activity_sheet.pdf only (locked audio/images/caption/story)."""
from __future__ import annotations

import hashlib
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
CHAPTER = "022"
LOCKED = (
    "story.md",
    "narration.mp3",
    "story_poster.png",
    "coloring_page.png",
    "simple_coloring_page.png",
    "whatsapp_caption.txt",
)
EVIDENCE = (
    Path.home()
    / "MyPilotDropbox"
    / "bhava-production-ops"
    / "evidence"
    / "final-uat-blockers-021-022-20260804"
)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def main() -> int:
    from krishna_story_factory.activities.models import ActivityPack, ActivityPage, SequenceCard
    from krishna_story_factory.activities.planner import _shuffled_sequence_cards
    from krishna_story_factory.activities.story_map import (
        evaluate_activity_semantic_qa,
        reconstruct_story_map_from_canonical,
        validate_story_022_sequence_beats,
        write_activity_semantic_qa,
    )
    from krishna_story_factory.config import load_settings
    from krishna_story_factory.csv_store import read_plan_by_chapter
    from krishna_story_factory.paths import make_package_paths
    from krishna_story_factory.pdf.activity_sheet import ActivitySheetGenerator, validate_activity_pdf
    from krishna_story_factory.storage.google_drive_uploader import replace_existing_files

    settings = load_settings(ROOT)
    plan = read_plan_by_chapter(ROOT, CHAPTER)
    assert plan is not None
    paths = make_package_paths(settings.output_root, plan, create=False)
    before = {n: _sha(paths.root / n) for n in LOCKED}
    before_pdf = _sha(paths.activity_sheet)

    story_md = paths.story_md.read_text(encoding="utf-8")
    sm = reconstruct_story_map_from_canonical(
        story_no=CHAPTER, title=plan.title, story_md=story_md, age_band=plan.age_range or "6-12"
    )
    events = sm.sequence_events()
    beat_errors = validate_story_022_sequence_beats(events)
    if beat_errors:
        raise SystemExit("022 beat FAIL: " + " | ".join(beat_errors))

    cards = [
        SequenceCard(event=e, drawing_prompt=f"Draw one detail from: {e}", source_order=i + 1)
        for i, e in enumerate(events)
    ]
    printed = _shuffled_sequence_cards(cards, plan.summary_seed or plan.title)
    activity = ActivityPack(
        activity_title=f"Put {plan.title} in Order",
        activity_type="STORY_SEQUENCE",
        send_mode="SEND_NOW",
        estimated_minutes=15,
        parent_effort="Low",
        learning_goal=f"Retell {plan.title} in order.",
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
        answer_key=list(events),
    )
    semantic = evaluate_activity_semantic_qa(
        activity_type=activity.activity_type,
        events=events,
        parent_answer_events=list(activity.answer_key),
        required_tokens=["Brahmā", "Kṛṣṇa"],
        canonical_story=story_md,
    )
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    write_activity_semantic_qa(semantic, EVIDENCE / "022_activity_semantic_qa.json")
    if semantic.result != "PASS":
        raise SystemExit(f"semantic FAIL: {semantic.failure_reasons}")

    pdf_check = ActivitySheetGenerator().generate(plan, activity, paths.activity_sheet)
    render_dir = EVIDENCE / "pdf" / "022_renders"
    if render_dir.exists():
        shutil.rmtree(render_dir)
    pdf_check = validate_activity_pdf(paths.activity_sheet, render_dir, activity=activity)
    if pdf_check.errors:
        raise SystemExit("PDF FAIL: " + " | ".join(pdf_check.errors))
    shutil.copy2(paths.activity_sheet, EVIDENCE / "pdf" / "022_activity_sheet.pdf")

    after = {n: _sha(paths.root / n) for n in LOCKED}
    if after != before:
        raise SystemExit(f"LOCKED DRIFT {before} vs {after}")

    manifest = json.loads(paths.manifest.read_text(encoding="utf-8"))
    manifest.setdefault("activity", {})
    manifest["activity"].update(
        {
            "type": activity.activity_type,
            "title": activity.activity_title,
            "page_count": pdf_check.page_count,
            "answer_key": list(activity.answer_key),
            "matching_coverage": pdf_check.matching_coverage,
            "semantic_qa": semantic.result,
            "layout_qa": "PASS",
        }
    )
    paths.manifest.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    upload = replace_existing_files(
        settings,
        source_dir=paths.root,
        manifest_path=paths.manifest,
        filenames=("activity_sheet.pdf", "manifest.json"),
    )
    result = {
        "before_pdf": before_pdf,
        "after_pdf": _sha(paths.activity_sheet),
        "events": events,
        "drive": getattr(upload, "status", ""),
        "drive_detail": getattr(upload, "detail", ""),
        "locked_ok": True,
    }
    (EVIDENCE / "022_activity_regen.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
