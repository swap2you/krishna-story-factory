#!/usr/bin/env python3
from __future__ import annotations

import csv
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv

from krishna_story_factory.config import load_settings, str_to_bool
from krishna_story_factory.csv_store import read_next_pending
from krishna_story_factory.whatsapp.recipients import load_active_recipients


def _flag(name: str) -> bool:
    load_dotenv(PROJECT_ROOT / ".env")
    return str_to_bool(os.getenv(name), False)


def _present(name: str) -> bool:
    load_dotenv(PROJECT_ROOT / ".env")
    return bool(os.getenv(name, "").strip())


def _path_exists(env_name: str) -> bool:
    settings = load_settings(PROJECT_ROOT)
    mapping = {
        "GOOGLE_DRIVE_CREDENTIALS_FILE": settings.google_drive_credentials_file,
        "GOOGLE_DRIVE_TOKEN_FILE": settings.google_drive_token_file,
    }
    path = mapping.get(env_name)
    if path and path.exists():
        return True
    defaults = {
        "GOOGLE_DRIVE_CREDENTIALS_FILE": PROJECT_ROOT / "credentials" / "google_drive_oauth_client.json",
        "GOOGLE_DRIVE_TOKEN_FILE": PROJECT_ROOT / "credentials" / "google_drive_token.json",
    }
    fallback = defaults.get(env_name)
    return bool(fallback and fallback.exists())


def main() -> int:
    settings = load_settings(PROJECT_ROOT)
    recipients_path = settings.whatsapp_recipients_csv
    recipient_rows = 0
    if recipients_path.exists():
        with recipients_path.open("r", newline="", encoding="utf-8-sig") as f:
            recipient_rows = sum(1 for _ in csv.DictReader(f))

    active = load_active_recipients(recipients_path)
    plan = read_next_pending(PROJECT_ROOT)

    print("=== Krishna Story Factory — local config (safe) ===")
    print(f"OPENAI_TEXT_ENABLED: {_flag('OPENAI_TEXT_ENABLED')}")
    print(f"OPENAI_IMAGE_ENABLED: {_flag('OPENAI_IMAGE_ENABLED')}")
    print(f"ELEVENLABS_ENABLED: {_flag('ELEVENLABS_ENABLED')}")
    print(f"WHATSAPP_SEND_ENABLED: {_flag('WHATSAPP_SEND_ENABLED')}")
    print(f"WHATSAPP_TEMPLATE_NAME: {settings.whatsapp_template_name}")
    print(f"WHATSAPP_TEMPLATE_LANGUAGE: {settings.whatsapp_template_language}")
    print(f"WHATSAPP_PHONE_NUMBER_ID present: {'yes' if _present('WHATSAPP_PHONE_NUMBER_ID') else 'no'}")
    print(f"WHATSAPP_CLOUD_TOKEN present: {'yes' if _present('WHATSAPP_CLOUD_TOKEN') or _present('WHATSAPP_ACCESS_TOKEN') else 'no'}")
    print(f"GOOGLE_DRIVE_UPLOAD_ENABLED: {_flag('GOOGLE_DRIVE_UPLOAD_ENABLED')}")
    print(f"GOOGLE_DRIVE_FOLDER_ID present: {'yes' if _present('GOOGLE_DRIVE_FOLDER_ID') else 'no'}")
    print(f"GOOGLE_DRIVE_CREDENTIALS_FILE exists: {'yes' if _path_exists('GOOGLE_DRIVE_CREDENTIALS_FILE') else 'no'}")
    print(f"GOOGLE_DRIVE_TOKEN_FILE exists: {'yes' if _path_exists('GOOGLE_DRIVE_TOKEN_FILE') else 'no'}")
    print(f"Recipient rows: {recipient_rows}")
    print(f"Active opted-in recipients: {len(active)}")
    if plan:
        print(f"Next pending story: {plan.chapter_no}_{plan.slug} — {plan.title}")
    else:
        print("Next pending story: none")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
