from __future__ import annotations

import json
import shutil
from datetime import datetime
from zoneinfo import ZoneInfo

from ..config import Settings
from ..models import PackagePaths, SendResult
from .base import BaseSender


class WhatsAppWebTestSender(BaseSender):
    """Private local test sender.

    This does not automate WhatsApp Web. It copies the story package into a local
    outbox so you can manually forward it to a private test group.
    """

    def send(self, *, settings: Settings, paths: PackagePaths, mode: str, plan=None, content=None, package_link: str = "") -> SendResult:
        if mode != "test":
            return SendResult(status="BLOCKED", detail="WhatsAppWebTestSender is allowed only in --mode test.")
        target = settings.whatsapp_web_test_dir / paths.root.name
        target.mkdir(parents=True, exist_ok=True)
        for file in paths.root.iterdir():
            if file.is_file():
                shutil.copy2(file, target / file.name)
        receipt = {
            "status": "LOCAL_TEST_OUTBOX_READY",
            "created_at": datetime.now(ZoneInfo(settings.app_timezone)).isoformat(timespec="seconds"),
            "source": str(paths.root),
            "target": str(target),
            "note": "Manual forward from this local folder to your private WhatsApp test group.",
        }
        (target / "send_receipt.json").write_text(json.dumps(receipt, indent=2), encoding="utf-8")
        return SendResult(status="SENT_TEST_OUTBOX", detail=f"Copied package to {target}")
