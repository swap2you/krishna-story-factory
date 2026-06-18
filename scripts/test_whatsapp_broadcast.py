from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from krishna_story_factory.config import load_settings
from krishna_story_factory.csv_store import append_send_log
from krishna_story_factory.whatsapp.cloud_client import WhatsAppCloudClient, WhatsAppCloudError
from krishna_story_factory.whatsapp.recipients import load_active_recipients


def main() -> int:
    settings = load_settings(PROJECT_ROOT)
    client = WhatsAppCloudClient(settings)
    missing = client.validate_config()
    if missing:
        print(f"CONFIG_ERROR: Missing {', '.join(missing)}")
        if "WHATSAPP_CLOUD_TOKEN" in missing:
            print("Paste a fresh Meta temporary token into WHATSAPP_CLOUD_TOKEN in .env, then rerun.")
        return 1

    recipients = load_active_recipients(settings.whatsapp_recipients_csv)
    if not recipients:
        print("NO_RECIPIENTS: No active opted-in rows in input/whatsapp_recipients.csv")
        return 1

    now = datetime.now(ZoneInfo(settings.app_timezone))
    sent = 0
    failed = 0

    for recipient in recipients:
        try:
            result = client.send_template(to_phone=recipient.phone_digits)
            message_id = result["message_ids"][0]
            sent += 1
            append_send_log(
                PROJECT_ROOT,
                {
                    "date": now.date().isoformat(),
                    "chapter_no": "broadcast",
                    "slug": "hello_world",
                    "sender_type": "cloud",
                    "recipient_name": recipient.name,
                    "recipient_phone": recipient.phone_digits,
                    "status": "SUCCESS",
                    "detail": f"template={settings.whatsapp_template_name}",
                    "message_id": message_id,
                    "created_at": now.isoformat(timespec="seconds"),
                },
            )
            print(f"SUCCESS {recipient.name} ({recipient.phone_digits}) message_id={message_id}")
        except WhatsAppCloudError as exc:
            failed += 1
            detail = str(exc)
            if exc.response_body:
                detail = f"{detail} | {exc.response_body}"
            append_send_log(
                PROJECT_ROOT,
                {
                    "date": now.date().isoformat(),
                    "chapter_no": "broadcast",
                    "slug": "hello_world",
                    "sender_type": "cloud",
                    "recipient_name": recipient.name,
                    "recipient_phone": recipient.phone_digits,
                    "status": "FAILED",
                    "detail": detail.replace("Bearer ", "Bearer [REDACTED] "),
                    "message_id": "",
                    "created_at": now.isoformat(timespec="seconds"),
                },
            )
            if exc.status_code is not None:
                print(f"FAILED {recipient.name} HTTP {exc.status_code}")
            else:
                print(f"FAILED {recipient.name}")
            if exc.response_body:
                print(exc.response_body)

    print(f"Summary: sent={sent} failed={failed}")
    return 0 if sent > 0 and failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
