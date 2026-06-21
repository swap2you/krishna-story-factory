from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from .models import PlanRow

REQUIRED_SERIES_FIELDS = ["chapter_no", "slug", "title", "source_reference", "summary_seed"]
SERIES_FIELDS = [
    "chapter_no", "slug", "title", "project", "library_id", "source_reference",
    "scripture_reference", "summary_seed", "age_range", "package_type", "send_date", "notes",
    "must_include", "must_avoid", "start_boundary", "end_boundary",
]
QUEUE_FIELDS = [
    "chapter_no", "slug", "status", "attempts", "last_error", "completed_at",
    "drive_folder_id", "updated_at",
]
LOG_FIELDS = ["date", "chapter_no", "slug", "title", "output_dir", "status", "quality_status", "whatsapp_status", "sender_type", "manifest_path", "created_at", "errors"]
SEND_LOG_FIELDS = ["date", "chapter_no", "slug", "sender_type", "recipient_name", "recipient_phone", "template_name", "story_title", "package_link", "status", "detail", "message_id", "created_at"]
QUALITY_LOG_FIELDS = ["date", "chapter_no", "slug", "quality_status", "errors", "created_at"]
STORAGE_LOG_FIELDS = ["date", "chapter_no", "slug", "mode", "status", "detail", "folder_link", "created_at"]
RUN_HISTORY_FIELDS = ["started_at", "completed_at", "status", "chapter_no", "slug", "detail", "exit_code"]
WHATSAPP_RECIPIENT_FIELDS = ["name", "phone_e164", "opt_in", "status", "notes"]


def _write_header_if_absent(path: Path, fieldnames: list[str]) -> None:
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", newline="", encoding="utf-8") as handle:
            csv.DictWriter(handle, fieldnames=fieldnames).writeheader()


def ensure_csv_files(project_root: Path) -> None:
    input_dir = project_root / "input"
    tracking_dir = project_root / "tracking"
    input_dir.mkdir(parents=True, exist_ok=True)
    tracking_dir.mkdir(parents=True, exist_ok=True)
    _write_header_if_absent(input_dir / "series_plan.csv", SERIES_FIELDS)
    _write_header_if_absent(input_dir / "whatsapp_recipients.csv", WHATSAPP_RECIPIENT_FIELDS)
    bootstrap_queue_state(project_root)
    for name, fields in (
        ("story_log.csv", LOG_FIELDS), ("send_log.csv", SEND_LOG_FIELDS),
        ("quality_log.csv", QUALITY_LOG_FIELDS), ("storage_log.csv", STORAGE_LOG_FIELDS),
        ("run_history.csv", RUN_HISTORY_FIELDS),
    ):
        _write_header_if_absent(tracking_dir / name, fields)


def _read_static_rows(project_root: Path) -> tuple[list[str], list[dict[str, str]]]:
    path = project_root / "input" / "series_plan.csv"
    with path.open("r", newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        missing = set(REQUIRED_SERIES_FIELDS) - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"series_plan.csv is missing required columns: {sorted(missing)}")
        return list(reader.fieldnames or []), list(reader)


def bootstrap_queue_state(project_root: Path) -> Path:
    path = project_root / "tracking" / "queue_state.csv"
    if path.exists():
        _sync_queue_file(project_root, path)
        return path
    _, plan_rows = _read_static_rows(project_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    now = datetime.now().isoformat(timespec="seconds")
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=QUEUE_FIELDS)
        writer.writeheader()
        for row in plan_rows:
            chapter = row.get("chapter_no", "").strip().zfill(3)
            legacy = row.get("status", "").strip().lower()
            status = legacy if legacy in {"pending", "processing", "done", "disabled"} else ("done" if chapter in {"001", "002"} else "pending")
            writer.writerow({
                "chapter_no": chapter, "slug": row.get("slug", "").strip(), "status": status,
                "attempts": "0", "last_error": "", "completed_at": now if status == "done" else "",
                "drive_folder_id": "", "updated_at": now,
            })
    return path


def _sync_queue_file(project_root: Path, path: Path) -> None:
    _, plan_rows = _read_static_rows(project_root)
    with path.open("r", newline="", encoding="utf-8-sig") as handle:
        queue_rows = list(csv.DictReader(handle))
    by_chapter = {row.get("chapter_no", "").strip().zfill(3): row for row in queue_rows}
    now = datetime.now().isoformat(timespec="seconds")
    changed = False
    for plan_row in plan_rows:
        chapter = plan_row.get("chapter_no", "").strip().zfill(3)
        slug = plan_row.get("slug", "").strip()
        if chapter not in by_chapter:
            row = {field: "" for field in QUEUE_FIELDS}
            row.update({"chapter_no": chapter, "slug": slug, "status": "pending", "attempts": "0", "updated_at": now})
            queue_rows.append(row); by_chapter[chapter] = row; changed = True
        elif by_chapter[chapter].get("slug") != slug:
            by_chapter[chapter]["slug"] = slug; by_chapter[chapter]["updated_at"] = now; changed = True
    if changed:
        _write_queue(path, queue_rows)


def read_queue_state(project_root: Path) -> list[dict[str, str]]:
    path = bootstrap_queue_state(project_root)
    with path.open("r", newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def _queue_by_chapter(project_root: Path) -> dict[str, dict[str, str]]:
    return {row.get("chapter_no", "").strip().zfill(3): row for row in read_queue_state(project_root)}


def read_next_pending(project_root: Path, *, rebuild: bool = False) -> PlanRow | None:
    _, rows = _read_static_rows(project_root)
    queue = _queue_by_chapter(project_root)
    for idx, row in enumerate(rows):
        chapter = row.get("chapter_no", "").strip().zfill(3)
        state = queue.get(chapter, {})
        status = state.get("status", "pending").strip().lower()
        if status == "pending" or (rebuild and status == "done"):
            return _row_to_plan(row, idx, status)
    return None


def read_plan_by_chapter(project_root: Path, chapter_no: str) -> PlanRow | None:
    normalized = chapter_no.strip().zfill(3)
    _, rows = _read_static_rows(project_root)
    queue = _queue_by_chapter(project_root)
    for idx, row in enumerate(rows):
        if row.get("chapter_no", "").strip().zfill(3) == normalized:
            return _row_to_plan(row, idx, queue.get(normalized, {}).get("status", "pending"))
    return None


def _row_to_plan(row: dict[str, str], idx: int, status: str) -> PlanRow:
    return PlanRow(
        chapter_no=row.get("chapter_no", "").strip().zfill(3), slug=row.get("slug", "").strip(),
        title=row.get("title", "").strip(), project=row.get("project", "krishna_book_bedtime").strip() or "krishna_book_bedtime",
        library_id=row.get("library_id", "krishna_book").strip() or "krishna_book",
        source_reference=row.get("source_reference", "").strip(), scripture_reference=row.get("scripture_reference", "").strip(),
        summary_seed=row.get("summary_seed", "").strip(), age_range=row.get("age_range", "6-12").strip() or "6-12",
        package_type=row.get("package_type", "bedtime_story").strip() or "bedtime_story",
        send_date=row.get("send_date", "").strip(), status=status, notes=row.get("notes", "").strip(), row_index=idx,
        must_include=row.get("must_include", "").strip(), must_avoid=row.get("must_avoid", "").strip(),
        start_boundary=row.get("start_boundary", "").strip(), end_boundary=row.get("end_boundary", "").strip(),
    )


def _write_queue(path: Path, rows: list[dict[str, str]]) -> None:
    temp = path.with_suffix(".tmp")
    with temp.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=QUEUE_FIELDS, extrasaction="ignore")
        writer.writeheader(); writer.writerows(rows)
    temp.replace(path)


def update_plan_status(project_root: Path, plan: PlanRow, status: str, *, error: str = "", drive_folder_id: str = "") -> None:
    path = bootstrap_queue_state(project_root)
    rows = read_queue_state(project_root)
    now = datetime.now().isoformat(timespec="seconds")
    target = next((row for row in rows if row.get("chapter_no", "").strip().zfill(3) == plan.chapter_no.zfill(3)), None)
    if target is None:
        target = {field: "" for field in QUEUE_FIELDS}; target.update({"chapter_no": plan.chapter_no.zfill(3), "slug": plan.slug, "attempts": "0"}); rows.append(target)
    previous = target.get("status", "")
    target["status"] = status; target["updated_at"] = now
    if status == "processing" and previous != "processing":
        target["attempts"] = str(int(target.get("attempts", "0") or 0) + 1)
    if error:
        target["last_error"] = error[:1000]
    elif status in {"processing", "done"}:
        target["last_error"] = ""
    if status == "done":
        target["completed_at"] = now
    if drive_folder_id:
        target["drive_folder_id"] = drive_folder_id
    _write_queue(path, rows)


def reset_processing_to_pending(project_root: Path) -> None:
    for row in read_queue_state(project_root):
        if row.get("status", "").lower() == "processing":
            plan = PlanRow(row["chapter_no"], row.get("slug", ""), "", "", "", "", "", "", "6-12", "", "", "processing")
            update_plan_status(project_root, plan, "pending", error="Recovered interrupted processing state")


def reset_series_status(project_root: Path, chapters: list[str], status: str = "pending") -> None:
    for chapter in chapters:
        plan = read_plan_by_chapter(project_root, chapter)
        if plan:
            update_plan_status(project_root, plan, status)


def reset_tracking_logs(project_root: Path) -> None:
    for name, fields in (("story_log.csv", LOG_FIELDS), ("send_log.csv", SEND_LOG_FIELDS), ("quality_log.csv", QUALITY_LOG_FIELDS), ("storage_log.csv", STORAGE_LOG_FIELDS), ("run_history.csv", RUN_HISTORY_FIELDS)):
        path = project_root / "tracking" / name; path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", newline="", encoding="utf-8") as handle: csv.DictWriter(handle, fieldnames=fields).writeheader()


def acquire_pipeline_lock(project_root: Path) -> Path:
    lock = project_root / ".pipeline.lock"
    if lock.exists(): raise RuntimeError("Another pipeline run appears to be in progress (.pipeline.lock exists).")
    lock.write_text(datetime.now().isoformat(), encoding="utf-8"); return lock


def release_pipeline_lock(lock_path: Path) -> None:
    lock_path.unlink(missing_ok=True)


def _append(project_root: Path, name: str, fields: list[str], row: dict[str, str]) -> None:
    path = project_root / "tracking" / name; _write_header_if_absent(path, fields)
    with path.open("a", newline="", encoding="utf-8") as handle:
        csv.DictWriter(handle, fieldnames=fields).writerow({field: row.get(field, "") for field in fields})


def append_story_log(project_root: Path, row: dict[str, str]) -> None: _append(project_root, "story_log.csv", LOG_FIELDS, row)
def append_send_log(project_root: Path, row: dict[str, str]) -> None: _append(project_root, "send_log.csv", SEND_LOG_FIELDS, row)
def append_storage_log(project_root: Path, row: dict[str, str]) -> None: _append(project_root, "storage_log.csv", STORAGE_LOG_FIELDS, row)
def append_run_history(project_root: Path, row: dict[str, str]) -> None: _append(project_root, "run_history.csv", RUN_HISTORY_FIELDS, row)


def already_sent_today(project_root: Path, timezone_name: str) -> bool:
    path = project_root / "tracking" / "story_log.csv"; today = datetime.now(ZoneInfo(timezone_name)).date().isoformat()
    if not path.exists(): return False
    with path.open("r", newline="", encoding="utf-8-sig") as handle:
        return any(row.get("date") == today and (row.get("whatsapp_status", "").upper().startswith("SENT") or row.get("whatsapp_status") == "DELIVERED") for row in csv.DictReader(handle))
