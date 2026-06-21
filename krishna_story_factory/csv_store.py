from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from .models import PlanRow

REQUIRED_SERIES_FIELDS = [
    "chapter_no",
    "slug",
    "title",
    "source_reference",
    "scripture_reference",
    "summary_seed",
    "status",
]

SERIES_FIELDS = [
    "chapter_no",
    "slug",
    "title",
    "project",
    "library_id",
    "source_reference",
    "scripture_reference",
    "summary_seed",
    "age_range",
    "package_type",
    "send_date",
    "status",
    "created_at",
    "updated_at",
    "notes",
]

LOG_FIELDS = [
    "date",
    "chapter_no",
    "slug",
    "title",
    "output_dir",
    "status",
    "quality_status",
    "whatsapp_status",
    "sender_type",
    "manifest_path",
    "created_at",
    "errors",
]

SEND_LOG_FIELDS = [
    "date",
    "chapter_no",
    "slug",
    "sender_type",
    "recipient_name",
    "recipient_phone",
    "template_name",
    "story_title",
    "package_link",
    "status",
    "detail",
    "message_id",
    "created_at",
]

QUALITY_LOG_FIELDS = [
    "date",
    "chapter_no",
    "slug",
    "quality_status",
    "errors",
    "created_at",
]

WHATSAPP_RECIPIENT_FIELDS = [
    "name",
    "phone_e164",
    "opt_in",
    "status",
    "notes",
]

STORAGE_LOG_FIELDS = [
    "date",
    "chapter_no",
    "slug",
    "mode",
    "status",
    "detail",
    "folder_link",
    "created_at",
]


def _write_header_if_absent(path: Path, fieldnames: list[str]) -> None:
    if not path.exists():
        with path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()


def ensure_csv_files(project_root: Path) -> None:
    input_dir = project_root / "input"
    tracking_dir = project_root / "tracking"
    input_dir.mkdir(parents=True, exist_ok=True)
    tracking_dir.mkdir(parents=True, exist_ok=True)
    _write_header_if_absent(input_dir / "series_plan.csv", SERIES_FIELDS)
    _write_header_if_absent(input_dir / "whatsapp_recipients.csv", WHATSAPP_RECIPIENT_FIELDS)
    _write_header_if_absent(tracking_dir / "story_log.csv", LOG_FIELDS)
    _write_header_if_absent(tracking_dir / "send_log.csv", SEND_LOG_FIELDS)
    _write_header_if_absent(tracking_dir / "quality_log.csv", QUALITY_LOG_FIELDS)
    _write_header_if_absent(tracking_dir / "storage_log.csv", STORAGE_LOG_FIELDS)


def read_next_pending(project_root: Path, *, rebuild: bool = False) -> PlanRow | None:
    path = project_root / "input" / "series_plan.csv"
    with path.open("r", newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        missing = set(REQUIRED_SERIES_FIELDS) - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"series_plan.csv is missing required columns: {sorted(missing)}")
        for idx, row in enumerate(reader):
            status = row.get("status", "").strip().lower()
            if status == "pending" or (rebuild and status == "done"):
                return _row_to_plan(row, idx)
    return None


def read_plan_by_chapter(project_root: Path, chapter_no: str) -> PlanRow | None:
    normalized = chapter_no.strip().zfill(3)
    path = project_root / "input" / "series_plan.csv"
    with path.open("r", newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for idx, row in enumerate(reader):
            if row.get("chapter_no", "").strip().zfill(3) == normalized:
                return _row_to_plan(row, idx)
    return None


def _row_to_plan(row: dict[str, str], idx: int) -> PlanRow:
    return PlanRow(
        chapter_no=row.get("chapter_no", "").strip(),
        slug=row.get("slug", "").strip(),
        title=row.get("title", "").strip(),
        project=row.get("project", "krishna_book_bedtime").strip() or "krishna_book_bedtime",
        library_id=row.get("library_id", "krishna_book").strip() or "krishna_book",
        source_reference=row.get("source_reference", "").strip(),
        scripture_reference=row.get("scripture_reference", "").strip(),
        summary_seed=row.get("summary_seed", "").strip(),
        age_range=row.get("age_range", "6-12").strip() or "6-12",
        package_type=row.get("package_type", "bedtime_story").strip() or "bedtime_story",
        send_date=row.get("send_date", "").strip(),
        status=row.get("status", "").strip(),
        created_at=row.get("created_at", "").strip(),
        updated_at=row.get("updated_at", "").strip(),
        notes=row.get("notes", "").strip(),
        row_index=idx,
    )


def reset_processing_to_pending(project_root: Path) -> None:
    path = project_root / "input" / "series_plan.csv"
    with path.open("r", newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames or SERIES_FIELDS)
        rows = list(reader)
    changed = False
    for row in rows:
        if row.get("status", "").strip().lower() == "processing":
            row["status"] = "pending"
            changed = True
    if changed:
        with path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(rows)


def reset_series_status(project_root: Path, chapters: list[str], status: str = "pending") -> None:
    normalized = {c.strip().zfill(3) for c in chapters}
    path = project_root / "input" / "series_plan.csv"
    with path.open("r", newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames or SERIES_FIELDS)
        rows = list(reader)
    for row in rows:
        if row.get("chapter_no", "").strip().zfill(3) in normalized:
            row["status"] = status
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def reset_tracking_logs(project_root: Path) -> None:
    tracking_dir = project_root / "tracking"
    tracking_dir.mkdir(parents=True, exist_ok=True)
    _write_header_if_absent(tracking_dir / "story_log.csv", LOG_FIELDS)
    _write_header_if_absent(tracking_dir / "send_log.csv", SEND_LOG_FIELDS)
    _write_header_if_absent(tracking_dir / "quality_log.csv", QUALITY_LOG_FIELDS)
    _write_header_if_absent(tracking_dir / "storage_log.csv", STORAGE_LOG_FIELDS)
    for name, fields in (
        ("story_log.csv", LOG_FIELDS),
        ("send_log.csv", SEND_LOG_FIELDS),
        ("quality_log.csv", QUALITY_LOG_FIELDS),
        ("storage_log.csv", STORAGE_LOG_FIELDS),
    ):
        path = tracking_dir / name
        with path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()


def acquire_pipeline_lock(project_root: Path) -> Path:
    lock = project_root / ".pipeline.lock"
    if lock.exists():
        raise RuntimeError("Another pipeline run appears to be in progress (.pipeline.lock exists).")
    lock.write_text(datetime.now().isoformat(), encoding="utf-8")
    return lock


def release_pipeline_lock(lock_path: Path) -> None:
    lock_path.unlink(missing_ok=True)


def update_plan_status(project_root: Path, plan: PlanRow, status: str) -> None:
    path = project_root / "input" / "series_plan.csv"
    with path.open("r", newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames or SERIES_FIELDS)
        rows = list(reader)
    if plan.row_index is None or plan.row_index >= len(rows):
        raise ValueError("Cannot update plan row because row index is missing or invalid.")
    if "status" not in fieldnames:
        fieldnames.append("status")
    if "created_at" not in fieldnames:
        fieldnames.append("created_at")
    if "updated_at" not in fieldnames:
        fieldnames.append("updated_at")
    rows[plan.row_index]["status"] = status
    rows[plan.row_index]["updated_at"] = datetime.now().isoformat(timespec="seconds")
    if not rows[plan.row_index].get("created_at"):
        rows[plan.row_index]["created_at"] = datetime.now().isoformat(timespec="seconds")
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=fieldnames,
            extrasaction="ignore",
            quoting=csv.QUOTE_MINIMAL,
        )
        writer.writeheader()
        writer.writerows(rows)


def append_story_log(project_root: Path, row: dict[str, str]) -> None:
    path = project_root / "tracking" / "story_log.csv"
    if not path.exists():
        ensure_csv_files(project_root)
    with path.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=LOG_FIELDS)
        writer.writerow({field: row.get(field, "") for field in LOG_FIELDS})


def append_send_log(project_root: Path, row: dict[str, str]) -> None:
    path = project_root / "tracking" / "send_log.csv"
    if not path.exists():
        ensure_csv_files(project_root)
    with path.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=SEND_LOG_FIELDS)
        writer.writerow({field: row.get(field, "") for field in SEND_LOG_FIELDS})


def append_storage_log(project_root: Path, row: dict[str, str]) -> None:
    path = project_root / "tracking" / "storage_log.csv"
    if not path.exists():
        ensure_csv_files(project_root)
    with path.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=STORAGE_LOG_FIELDS)
        writer.writerow({field: row.get(field, "") for field in STORAGE_LOG_FIELDS})


def already_sent_today(project_root: Path, timezone_name: str) -> bool:
    path = project_root / "tracking" / "story_log.csv"
    today = datetime.now(ZoneInfo(timezone_name)).date().isoformat()
    if not path.exists():
        return False
    with path.open("r", newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            status = row.get("whatsapp_status", "").upper()
            if row.get("date") == today and (status.startswith("SENT") or status == "DELIVERED"):
                return True
    return False
