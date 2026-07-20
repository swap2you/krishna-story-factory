"""Rebuild only Story 005 activity_sheet.pdf + manifest.json with hash locks."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

LOCKED = {
    "story.md": "A13F8AC9BDC583121B962DC66F9AA6587818F31542F9B7F43C5A578E26194CE3",
    "narration.mp3": "9F616C95EAA935A2BCD4428B202E98553D122C7ADAAF0955D14CDB2D8560875C",
    "story_poster.png": "100F06F69CAB86A84604BE4B6230213EA6EC2F633316C8891BE9233C574D87C8",
    "coloring_page.png": "840F5CD14AA01F14E204280DFB5314416CC8A20E51C95520AF0288FBB06CCBA5",
    "whatsapp_caption.txt": "02DCDDCF4B8D7F45D4C842866F6AFBE7EFF47D7E59433557DFE64B252D38A6D1",
}
FOLDER_ID = "1qqox6hHQzMR3HQU12TQv2xRb2IUlbXU3"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def _assert_locked(paths) -> None:
    for name, expected in LOCKED.items():
        actual = _sha256(paths.root / name)
        if actual != expected:
            raise SystemExit(f"Locked hash mismatch for {name}: {actual}")


def main() -> int:
    from krishna_story_factory.activities.planner import ActivityPlanner
    from krishna_story_factory.config import load_settings
    from krishna_story_factory.csv_store import read_plan_by_chapter
    from krishna_story_factory.paths import make_package_paths
    from krishna_story_factory.pdf.activity_sheet import ActivitySheetGenerator, validate_activity_pdf
    from krishna_story_factory.pipeline import _review_activity
    from krishna_story_factory.storage.google_drive_uploader import replace_existing_files, verify_drive_text_links
    from krishna_story_factory.work import new_work_paths

    settings = load_settings(ROOT)
    plan = read_plan_by_chapter(ROOT, "005")
    paths = make_package_paths(settings.output_root, plan)
    _assert_locked(paths)

    story_md = paths.story_md.read_text(encoding="utf-8")
    old = json.loads(paths.manifest.read_text(encoding="utf-8"))
    work = new_work_paths(ROOT, debug=True)

    planner = ActivityPlanner(ROOT / "tracking" / "activity_history.csv", settings=settings)
    activity = planner.plan(plan, story_md)
    if activity.activity_title != "The Secret Prayer Gathering":
        raise SystemExit(f"Wrong activity title: {activity.activity_title}")

    ActivitySheetGenerator().generate(plan, activity, paths.activity_sheet)
    render_dir = work.root / "activity_pages"
    pdf_check = validate_activity_pdf(paths.activity_sheet, render_dir, activity=activity)
    if pdf_check.errors:
        raise SystemExit("Activity PDF errors: " + " | ".join(pdf_check.errors))
    cov = pdf_check.matching_coverage or {}
    if not cov.get("pass") or cov.get("expected_pairs") != 5 or cov.get("rendered_pairs") != 5:
        raise SystemExit(f"Matching coverage failed: {cov}")
    if cov.get("missing_labels") or cov.get("orphan_labels"):
        raise SystemExit(f"Matching coverage labels failed: {cov}")

    activity_score = _review_activity(
        settings, story_md, render_dir, work.reviews, "prod",
        activity=activity, chapter_no=plan.chapter_no, slug=plan.slug,
    )
    if activity_score < 90:
        raise SystemExit(f"Activity QA {activity_score} < 90")

    package_link = f"https://drive.google.com/drive/folders/{FOLDER_ID}?usp=sharing"
    old["generated_at"] = old.get("generated_at", "")
    old["activity"] = {
        "type": activity.activity_type,
        "title": activity.activity_title,
        "recommended_send_mode": activity.recommended_send_mode,
        "estimated_minutes": activity.estimated_minutes,
        "parent_effort": activity.parent_effort,
        "page_count": pdf_check.page_count,
        "qa_score": activity_score,
        "answer_key": activity.answer_key,
        "matching_coverage": cov,
    }
    old.setdefault("package", {})
    old["package"]["package_link"] = package_link
    old["package"]["drive_folder_id"] = FOLDER_ID
    old["package"]["drive_status"] = "UPLOADED"
    old["package"]["drive_detail"] = "Story 005 matching coverage rebuild"
    old["quality"] = {"status": "PASS", "errors": [], "warnings": old.get("quality", {}).get("warnings") or []}
    old["queue_transition"] = "done"
    paths.manifest.write_text(json.dumps(old, indent=2, ensure_ascii=False), encoding="utf-8")

    _assert_locked(paths)

    upload = replace_existing_files(
        settings,
        source_dir=paths.root,
        manifest_path=paths.manifest,
        filenames=("activity_sheet.pdf", "manifest.json"),
    )
    if upload.status != "UPLOADED":
        raise SystemExit(f"Drive replace failed: {upload.detail}")
    ok, detail = verify_drive_text_links(settings, folder_id=FOLDER_ID, package_link=package_link)
    if not ok:
        raise SystemExit(f"Drive verify failed: {detail}")

    print("REBUILD_OK", {
        "activity_score": activity_score,
        "pages": pdf_check.page_count,
        "matching_coverage": cov,
        "drive": upload.detail,
        "verify": detail,
    })
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
