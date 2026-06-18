#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from krishna_story_factory.config import load_settings
from krishna_story_factory.whatsapp.cloud_client import WhatsAppCloudClient, WhatsAppCloudError


def main() -> int:
    settings = load_settings(PROJECT_ROOT)
    if settings.whatsapp_template_name != "daily_krishna_story":
        print("Set WHATSAPP_TEMPLATE_NAME=daily_krishna_story in local .env for this test.")
        return 1
    if not settings.whatsapp_test_recipient_phone:
        print("Set WHATSAPP_TEST_RECIPIENT_PHONE in local .env.")
        return 1

    client = WhatsAppCloudClient(settings)
    missing = client.validate_config()
    if missing:
        print(f"Missing WhatsApp config: {', '.join(missing)}")
        return 1

    link = settings.package_public_link or settings.google_drive_folder_url or "https://drive.example/test"
    try:
        result = client.send_template(
            to_phone=settings.whatsapp_test_recipient_phone,
            template_name="daily_krishna_story",
            body_parameters=["Test Family", "Test Krishna Story", link],
        )
    except WhatsAppCloudError as exc:
        print(f"FAILED: HTTP {exc.status_code}")
        print(str(exc).replace("Bearer ", "Bearer [REDACTED] "))
        return 1

    print(f"SUCCESS message_ids={result['message_ids']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
