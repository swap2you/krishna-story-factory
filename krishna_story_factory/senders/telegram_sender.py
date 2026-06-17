from __future__ import annotations

import requests

from ..config import Settings
from ..models import PackagePaths, SendResult
from .base import BaseSender


class TelegramSender(BaseSender):
    def send(self, *, settings: Settings, paths: PackagePaths, mode: str) -> SendResult:
        if not settings.telegram_bot_token or not settings.telegram_chat_id:
            return SendResult(status="FAILED", detail="Telegram bot token or chat id is missing.")
        caption = paths.whatsapp_caption.read_text(encoding="utf-8", errors="ignore")
        base = f"https://api.telegram.org/bot{settings.telegram_bot_token}"
        sent_ids: list[str] = []
        try:
            msg = requests.post(
                f"{base}/sendMessage",
                json={"chat_id": settings.telegram_chat_id, "text": caption},
                timeout=30,
            )
            msg.raise_for_status()
            sent_ids.append(str(msg.json().get("result", {}).get("message_id", "")))
            for file_path in [paths.story_card, paths.activity_sheet, paths.narration_mp3]:
                if not file_path.exists():
                    continue
                endpoint = "sendDocument"
                field = "document"
                if file_path.suffix.lower() in {".png", ".jpg", ".jpeg"}:
                    endpoint = "sendPhoto"
                    field = "photo"
                with file_path.open("rb") as f:
                    resp = requests.post(
                        f"{base}/{endpoint}",
                        data={"chat_id": settings.telegram_chat_id},
                        files={field: (file_path.name, f)},
                        timeout=90,
                    )
                resp.raise_for_status()
                sent_ids.append(str(resp.json().get("result", {}).get("message_id", "")))
            return SendResult(status="SENT_TELEGRAM", detail="Package sent to Telegram.", provider_ids=sent_ids)
        except Exception as exc:
            return SendResult(status="FAILED", detail=f"Telegram send failed: {exc}")
