#!/usr/bin/env python3
"""Regenerate activity_sheet.pdf for Stories 021/022 only (layout fix).

Locks story.md + narration.mp3 (+ images/caption). Does not call TTS.
"""
from __future__ import annotations

import hashlib
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

CHAPTERS = ("021", "022")
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
    / "pr47-final-correction-20260804"
)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def _rebuild(chapter: str) -> dict:
    from krishna_story_factory.activities.models import ActivityPack, ActivityPage, SequenceCard
    from krishna_story_factory.activities.planner import _shuffled_sequence_cards
    from krishna_story_factory.activities.story_map import (
        evaluate_activity_semantic_qa,
        reconstruct_story_map_from_canonical,
    )
    from krishna_story_factory.config import load_settings
    from krishna_story_factory.csv_store import read_plan_by_chapter
    from krishna_story_factory.paths import make_package_paths
    from krishna_story_factory.pdf.activity_sheet import ActivitySheetGenerator, validate_activity_pdf
    from krishna_story_factory.storage.google_drive_uploader import replace_existing_files

    settings = load_settings(ROOT)
    plan = read_plan_by_chapter(ROOT, chapter)
    assert plan is not None
    paths = make_package_paths(settings.output_root, plan, create=False)
    before = {name: _sha(paths.root / name) for name in LOCKED}
    before_pdf = _sha(paths.activity_sheet)

    # Evidence: before render
    before_dir = EVIDENCE / "pdf-before" / chapter
    before_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(paths.activity_sheet, before_dir / "activity_sheet.pdf")
    validate_activity_pdf(paths.activity_sheet, before_dir / "renders")

    story_md = paths.story_md.read_text(encoding="utf-8")
    sm = reconstruct_story_map_from_canonical(
        story_no=chapter, title=plan.title, story_md=story_md, age_band=plan.age_range or "6-12"
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
        answer_key=[c.event for c in sorted(cards, key=lambda x: x.source_order)],
    )
    semantic = evaluate_activity_semantic_qa(
        activity_type=activity.activity_type,
        events=sm.sequence_events(),
        parent_answer_events=list(activity.answer_key),
        required_tokens=["Brahmā", "Kṛṣṇa"],
        canonical_story=story_md,
    )
    if semantic.result != "PASS":
        raise SystemExit(f"{chapter} semantic FAIL: {semantic.failure_reasons}")

    pdf_check = ActivitySheetGenerator().generate(plan, activity, paths.activity_sheet)
    after_dir = EVIDENCE / "pdf-after" / chapter
    if after_dir.exists():
        shutil.rmtree(after_dir)
    after_dir.mkdir(parents=True)
    shutil.copy2(paths.activity_sheet, after_dir / "activity_sheet.pdf")
    pdf_check = validate_activity_pdf(paths.activity_sheet, after_dir / "renders", activity=activity)
    if pdf_check.errors:
        raise SystemExit(f"{chapter} PDF FAIL: {pdf_check.errors}")

    after = {name: _sha(paths.root / name) for name in LOCKED}
    if after != before:
        raise SystemExit(f"{chapter} LOCKED FILE DRIFT: {before} vs {after}")

    # Update activity block in manifest without touching audio hashes.
    manifest = json.loads(paths.manifest.read_text(encoding="utf-8"))
    manifest.setdefault("activity", {})
    manifest["activity"]["type"] = activity.activity_type
    manifest["activity"]["title"] = activity.activity_title
    manifest["activity"]["page_count"] = pdf_check.page_count
    manifest["activity"]["answer_key"] = list(activity.answer_key)
    manifest["activity"]["matching_coverage"] = pdf_check.matching_coverage
    manifest["activity"]["semantic_qa"] = semantic.result
    manifest["activity"]["layout_qa"] = "PASS" if not pdf_check.errors else "FAIL"
    paths.manifest.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    upload = replace_existing_files(
        settings,
        source_dir=paths.root,
        manifest_path=paths.manifest,
        filenames=("activity_sheet.pdf", "manifest.json"),
    )
    return {
        "chapter": chapter,
        "before_pdf": before_pdf,
        "after_pdf": _sha(paths.activity_sheet),
        "pages": pdf_check.page_count,
        "errors": pdf_check.errors,
        "drive": getattr(upload, "status", str(upload)),
        "drive_detail": getattr(upload, "detail", ""),
        "locked_ok": True,
    }


def main() -> int:
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    results = [_rebuild(c) for c in CHAPTERS]
    out = EVIDENCE / "pdf-regen-results.json"
    out.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(results, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
