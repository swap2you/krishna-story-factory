from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from krishna_story_factory.config import load_settings
from krishna_story_factory.whatsapp.cloud_client import WhatsAppCloudClient, WhatsAppCloudError
from krishna_story_factory.whatsapp.phone import normalize_phone_e164


def main() -> int:
    settings = load_settings(PROJECT_ROOT)
    missing = []
    if not settings.whatsapp_cloud_token:
        missing.append("WHATSAPP_CLOUD_TOKEN")
    if not settings.whatsapp_phone_number_id:
        missing.append("WHATSAPP_PHONE_NUMBER_ID")
    if not settings.whatsapp_test_recipient_phone:
        missing.append("WHATSAPP_TEST_RECIPIENT_PHONE")
    if missing:
        print(f"CONFIG_ERROR: Missing {', '.join(missing)}")
        if "WHATSAPP_CLOUD_TOKEN" in missing:
            print("Paste a fresh Meta temporary token into WHATSAPP_CLOUD_TOKEN in .env, then rerun.")
        return 1

    client = WhatsAppCloudClient(settings)
    phone = normalize_phone_e164(settings.whatsapp_test_recipient_phone)
    try:
        result = client.send_template(to_phone=phone)
        message_id = result["message_ids"][0]
        print("SUCCESS")
        print(f"Meta message id: {message_id}")
        return 0
    except WhatsAppCloudError as exc:
        if exc.status_code is not None:
            print(f"HTTP {exc.status_code}")
        if exc.response_body:
            print(exc.response_body)
        else:
            print(str(exc))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
