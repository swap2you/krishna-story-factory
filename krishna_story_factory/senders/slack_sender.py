from __future__ import annotations

import requests

from ..config import Settings
from ..models import PackagePaths, SendResult
from .base import BaseSender


class SlackWebhookSender(BaseSender):
    def send(self, *, settings: Settings, paths: PackagePaths, mode: str) -> SendResult:
        if not settings.slack_webhook_url:
            return SendResult(status="FAILED", detail="Slack webhook URL is missing.")
        caption = paths.whatsapp_caption.read_text(encoding="utf-8", errors="ignore")
        local_files = "\n".join(
            f"- {p.name}" for p in [paths.story_card, paths.activity_sheet, paths.narration_mp3] if p.exists()
        )
        text = f"{caption}\n\nGenerated files are available locally in `{paths.root}`:\n{local_files}"
        try:
            resp = requests.post(settings.slack_webhook_url, json={"text": text}, timeout=30)
            resp.raise_for_status()
            return SendResult(status="SENT_SLACK", detail="Slack webhook notification sent.")
        except Exception as exc:
            return SendResult(status="FAILED", detail=f"Slack send failed: {exc}")
