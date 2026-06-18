from __future__ import annotations

from ..config import Settings
from ..csv_store import append_send_log
from ..models import PackagePaths, SendResult
from ..whatsapp.cloud_client import WhatsAppCloudClient, WhatsAppCloudError
from ..whatsapp.recipients import load_active_recipients
from .base import BaseSender


class WhatsAppCloudSender(BaseSender):
    def send(self, *, settings: Settings, paths: PackagePaths, mode: str) -> SendResult:
        if mode == "test":
            return SendResult(status="SKIPPED_TEST_MODE", detail="WhatsApp Cloud send skipped in test mode.")

        client = WhatsAppCloudClient(settings)
        missing = client.validate_config()
        if missing:
            return SendResult(status="CONFIG_ERROR", detail=f"Missing WhatsApp config: {', '.join(missing)}")

        recipients = load_active_recipients(settings.whatsapp_recipients_csv)
        if not recipients:
            return SendResult(status="NO_RECIPIENTS", detail="No active opted-in recipients found in whatsapp_recipients.csv.")

        provider_ids: list[str] = []
        sent_count = 0
        failed_count = 0
        chapter_no = _chapter_from_paths(paths)
        slug = paths.root.name.split("_", 1)[-1] if "_" in paths.root.name else paths.root.name

        for recipient in recipients:
            try:
                result = client.send_template(to_phone=recipient.phone_digits)
                message_id = result["message_ids"][0]
                provider_ids.append(message_id)
                sent_count += 1
                append_send_log(
                    settings.project_root,
                    {
                        "date": _today(settings),
                        "chapter_no": chapter_no,
                        "slug": slug,
                        "sender_type": "cloud",
                        "recipient_name": recipient.name,
                        "recipient_phone": recipient.phone_digits,
                        "status": "SUCCESS",
                        "detail": f"template={settings.whatsapp_template_name}",
                        "message_id": message_id,
                        "created_at": _now_iso(settings),
                    },
                )
            except WhatsAppCloudError as exc:
                failed_count += 1
                append_send_log(
                    settings.project_root,
                    {
                        "date": _today(settings),
                        "chapter_no": chapter_no,
                        "slug": slug,
                        "sender_type": "cloud",
                        "recipient_name": recipient.name,
                        "recipient_phone": recipient.phone_digits,
                        "status": "FAILED",
                        "detail": _safe_error_detail(exc),
                        "message_id": "",
                        "created_at": _now_iso(settings),
                    },
                )

        if sent_count == 0:
            return SendResult(
                status="FAILED_CLOUD",
                detail=f"WhatsApp template send failed for all {failed_count} recipient(s).",
                provider_ids=provider_ids,
            )

        detail = f"Sent template '{settings.whatsapp_template_name}' to {sent_count} recipient(s)."
        if failed_count:
            detail += f" {failed_count} failed."
        return SendResult(status="SENT_CLOUD", detail=detail, provider_ids=provider_ids)


def _chapter_from_paths(paths: PackagePaths) -> str:
    name = paths.root.name
    if "_" in name:
        return name.split("_", 1)[0]
    return ""


def _safe_error_detail(exc: WhatsAppCloudError) -> str:
    parts = [str(exc)]
    if exc.status_code is not None:
        parts.append(f"HTTP {exc.status_code}")
    if exc.response_body:
        parts.append(exc.response_body)
    detail = " | ".join(parts)
    return detail.replace("Bearer ", "Bearer [REDACTED] ")


def _today(settings: Settings) -> str:
    from datetime import datetime
    from zoneinfo import ZoneInfo

    return datetime.now(ZoneInfo(settings.app_timezone)).date().isoformat()


def _now_iso(settings: Settings) -> str:
    from datetime import datetime
    from zoneinfo import ZoneInfo

    return datetime.now(ZoneInfo(settings.app_timezone)).isoformat(timespec="seconds")
