from __future__ import annotations

import requests

from ..config import Settings
from ..models import PackagePaths, SendResult
from .base import BaseSender


class DiscordWebhookSender(BaseSender):
    def send(self, *, settings: Settings, paths: PackagePaths, mode: str, plan=None, content=None) -> SendResult:
        if not settings.discord_webhook_url:
            return SendResult(status="FAILED", detail="Discord webhook URL is missing.")
        caption = paths.whatsapp_caption.read_text(encoding="utf-8", errors="ignore")
        try:
            resp = requests.post(settings.discord_webhook_url, json={"content": caption[:1900]}, timeout=30)
            resp.raise_for_status()
            return SendResult(status="SENT_DISCORD", detail="Discord webhook notification sent.")
        except Exception as exc:
            return SendResult(status="FAILED", detail=f"Discord send failed: {exc}")
