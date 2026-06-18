from __future__ import annotations

from typing import Any

import requests

from ..config import Settings


class WhatsAppCloudError(RuntimeError):
    def __init__(self, message: str, *, status_code: int | None = None, response_body: str = "") -> None:
        super().__init__(message)
        self.status_code = status_code
        self.response_body = response_body


def build_template_payload(*, to_phone: str, template_name: str, language_code: str) -> dict[str, Any]:
    return {
        "messaging_product": "whatsapp",
        "to": to_phone,
        "type": "template",
        "template": {
            "name": template_name,
            "language": {"code": language_code},
        },
    }


def extract_message_ids(payload: dict[str, Any]) -> list[str]:
    return [str(item.get("id")) for item in payload.get("messages", []) if item.get("id")]


class WhatsAppCloudClient:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def messages_url(self) -> str:
        return (
            f"https://graph.facebook.com/{self.settings.whatsapp_graph_api_version}"
            f"/{self.settings.whatsapp_phone_number_id}/messages"
        )

    def headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.settings.whatsapp_cloud_token}",
            "Content-Type": "application/json",
        }

    def validate_config(self) -> list[str]:
        missing: list[str] = []
        if not self.settings.whatsapp_phone_number_id:
            missing.append("WHATSAPP_PHONE_NUMBER_ID")
        if not self.settings.whatsapp_cloud_token:
            missing.append("WHATSAPP_CLOUD_TOKEN")
        if not self.settings.whatsapp_template_name:
            missing.append("WHATSAPP_TEMPLATE_NAME")
        if not self.settings.whatsapp_template_language:
            missing.append("WHATSAPP_TEMPLATE_LANGUAGE")
        return missing

    def send_template(self, *, to_phone: str, template_name: str | None = None, language_code: str | None = None) -> dict[str, Any]:
        missing = self.validate_config()
        if missing:
            raise WhatsAppCloudError(f"Missing WhatsApp config: {', '.join(missing)}")

        payload = build_template_payload(
            to_phone=to_phone,
            template_name=template_name or self.settings.whatsapp_template_name,
            language_code=language_code or self.settings.whatsapp_template_language,
        )
        response = requests.post(self.messages_url(), headers=self.headers(), json=payload, timeout=60)
        body = response.text[:2000]
        if response.status_code >= 400:
            raise WhatsAppCloudError(
                f"WhatsApp API error: HTTP {response.status_code}",
                status_code=response.status_code,
                response_body=body,
            )

        data = response.json()
        message_ids = extract_message_ids(data)
        if not message_ids:
            raise WhatsAppCloudError(
                "WhatsApp API response did not include a message id.",
                status_code=response.status_code,
                response_body=body,
            )
        return {"message_ids": message_ids, "response": data}
