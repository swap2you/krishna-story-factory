from __future__ import annotations

import mimetypes
from pathlib import Path

import requests

from ..config import Settings
from ..models import PackagePaths, SendResult
from .base import BaseSender


class WhatsAppCloudSender(BaseSender):
    def send(self, *, settings: Settings, paths: PackagePaths, mode: str) -> SendResult:
        missing = []
        if not settings.whatsapp_phone_number_id:
            missing.append("WHATSAPP_PHONE_NUMBER_ID")
        if not settings.whatsapp_access_token:
            missing.append("WHATSAPP_ACCESS_TOKEN")
        if not settings.whatsapp_target_phone:
            missing.append("WHATSAPP_TARGET_PHONE")
        if missing:
            return SendResult(status="CONFIG_ERROR", detail=f"Missing WhatsApp config: {', '.join(missing)}")

        provider_ids: list[str] = []
        self._send_text(settings, paths.whatsapp_caption.read_text(encoding="utf-8"), provider_ids)
        self._send_media(settings, "image", paths.story_card, provider_ids)
        self._send_media(settings, "document", paths.activity_sheet, provider_ids, caption="Activity sheet")
        self._send_media(settings, "audio", paths.narration_mp3, provider_ids)
        return SendResult(status="SENT_CLOUD", detail="Sent via WhatsApp Cloud API.", provider_ids=provider_ids)

    def _base_url(self, settings: Settings) -> str:
        return f"https://graph.facebook.com/{settings.whatsapp_graph_api_version}/{settings.whatsapp_phone_number_id}"

    def _headers(self, settings: Settings) -> dict[str, str]:
        return {"Authorization": f"Bearer {settings.whatsapp_access_token}"}

    def _send_text(self, settings: Settings, text: str, provider_ids: list[str]) -> None:
        url = f"{self._base_url(settings)}/messages"
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": settings.whatsapp_target_phone,
            "type": "text",
            "text": {"preview_url": False, "body": text[:4096]},
        }
        response = requests.post(url, headers={**self._headers(settings), "Content-Type": "application/json"}, json=payload, timeout=60)
        self._raise_for_response(response)
        provider_ids.extend(self._extract_message_ids(response.json()))

    def _upload_media(self, settings: Settings, path: Path) -> str:
        url = f"{self._base_url(settings)}/media"
        mime_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        with path.open("rb") as f:
            files = {"file": (path.name, f, mime_type)}
            data = {"messaging_product": "whatsapp", "type": mime_type}
            response = requests.post(url, headers=self._headers(settings), files=files, data=data, timeout=120)
        self._raise_for_response(response)
        media_id = response.json().get("id")
        if not media_id:
            raise RuntimeError(f"Media upload did not return id: {response.text[:500]}")
        return str(media_id)

    def _send_media(self, settings: Settings, media_type: str, path: Path, provider_ids: list[str], caption: str | None = None) -> None:
        media_id = self._upload_media(settings, path)
        url = f"{self._base_url(settings)}/messages"
        body: dict[str, object] = {"id": media_id}
        if media_type == "document":
            body["filename"] = path.name
        if caption and media_type in {"image", "document", "video"}:
            body["caption"] = caption
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": settings.whatsapp_target_phone,
            "type": media_type,
            media_type: body,
        }
        response = requests.post(url, headers={**self._headers(settings), "Content-Type": "application/json"}, json=payload, timeout=60)
        self._raise_for_response(response)
        provider_ids.extend(self._extract_message_ids(response.json()))

    def _raise_for_response(self, response: requests.Response) -> None:
        if response.status_code >= 400:
            raise RuntimeError(f"WhatsApp API error: {response.status_code} {response.text[:800]}")

    def _extract_message_ids(self, payload: dict) -> list[str]:
        return [str(item.get("id")) for item in payload.get("messages", []) if item.get("id")]
