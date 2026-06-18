#!/usr/bin/env python3
from __future__ import annotations

import sys
import tempfile
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from krishna_story_factory.config import load_settings
from krishna_story_factory.csv_store import append_storage_log
from krishna_story_factory.storage.google_drive_uploader import upload_story_package


def main() -> int:
    settings = load_settings(PROJECT_ROOT)
    if not settings.google_drive_upload_enabled:
        print("GOOGLE_DRIVE_UPLOAD_ENABLED is false. Set it true in local .env to test upload.")
        return 1
    if not settings.google_drive_credentials_file or not settings.google_drive_credentials_file.exists():
        print("Missing credentials file. Save OAuth client JSON to credentials/google_drive_oauth_client.json")
        return 1

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    folder_name = f"KSF_TEST_UPLOAD_{stamp}"

    with tempfile.TemporaryDirectory() as tmp:
        source = Path(tmp)
        test_file = source / "drive_upload_test.txt"
        test_file.write_text("Krishna Story Factory Drive upload test.", encoding="utf-8")
        result = upload_story_package(
            settings,
            folder_name=folder_name,
            source_dir=source,
        )
        append_storage_log(
            PROJECT_ROOT,
            {
                "date": datetime.now().date().isoformat(),
                "chapter_no": "TEST",
                "slug": folder_name,
                "mode": "test",
                "status": result.status,
                "detail": result.detail,
                "folder_link": result.package_link,
                "created_at": datetime.now().isoformat(timespec="seconds"),
            },
        )
        print(f"status: {result.status}")
        print(f"publish_mode: {result.publish_mode}")
        print(f"folder_name: {result.folder_name or folder_name}")
        print(f"folder_link: {result.package_link}")
        print(f"uploaded_files: {', '.join(result.uploaded_files)}")
        print(f"detail: {result.detail}")
        return 0 if result.status == "UPLOADED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
