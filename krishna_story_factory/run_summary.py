"""Write deterministic latest-run summary files after production/manual runs."""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any


def write_latest_run_summary(
    project_root: Path,
    *,
    started_at: str,
    completed_at: str,
    status: str,
    chapter_no: str = "",
    title: str = "",
    package_local_path: str = "",
    drive_folder_url: str = "",
    provider: str = "",
    audio_duration: float | None = None,
    publishable: bool | None = None,
    exact_eight_files: bool | None = None,
    queue_advanced: bool | None = None,
    next_pending: str = "",
    error_code: str = "",
    error_summary: str = "",
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "run_started_at": started_at,
        "run_completed_at": completed_at,
        "status": status,
        "chapter_no": chapter_no,
        "title": title,
        "package_local_path": package_local_path,
        "drive_folder_url": drive_folder_url,
        "provider": provider,
        "audio_duration": audio_duration,
        "publishable": publishable,
        "exact_eight_files": exact_eight_files,
        "queue_advanced": queue_advanced,
        "next_pending": next_pending,
        "error_code": error_code,
        "error_summary": error_summary,
    }
    tracking = project_root / "tracking"
    logs = project_root / "logs"
    tracking.mkdir(parents=True, exist_ok=True)
    logs.mkdir(parents=True, exist_ok=True)
    json_path = tracking / "latest_run_summary.json"
    txt_path = logs / "latest_run_summary.txt"
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    lines = [
        f"Status: {status}",
        f"Started: {started_at}",
        f"Completed: {completed_at}",
        f"Chapter: {chapter_no}",
        f"Title: {title}",
        f"Local package: {package_local_path}",
        f"Drive folder: {drive_folder_url or '(none)'}",
        f"Provider: {provider or '(n/a)'}",
        f"Audio duration: {audio_duration if audio_duration is not None else '(n/a)'}",
        f"Publishable: {publishable}",
        f"Exact eight files: {exact_eight_files}",
        f"Queue advanced: {queue_advanced}",
        f"Next pending: {next_pending or '(none)'}",
    ]
    if error_code or error_summary:
        lines.extend([f"Error code: {error_code}", f"Error: {error_summary}"])
    txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return payload


def iso_now(tz_name: str) -> str:
    from zoneinfo import ZoneInfo

    return datetime.now(ZoneInfo(tz_name)).isoformat(timespec="seconds")
