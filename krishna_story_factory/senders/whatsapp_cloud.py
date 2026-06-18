from __future__ import annotations

from ..config import Settings
from ..csv_store import append_send_log
from ..models import PackagePaths, PlanRow, SendResult, StoryContent
from ..whatsapp.cloud_client import WhatsAppCloudClient, WhatsAppCloudError
from ..whatsapp.recipients import load_active_recipients
from .base import BaseSender


class WhatsAppCloudSender(BaseSender):
    def send(
        self,
        *,
        settings: Settings,
        paths: PackagePaths,
        mode: str,
        plan: PlanRow | None = None,
        content: StoryContent | None = None,
    ) -> SendResult:
        if mode == "test":
            return SendResult(status="SKIPPED_TEST_MODE", detail="WhatsApp Cloud send skipped in test mode.")

        client = WhatsAppCloudClient(settings)
        missing = client.validate_config()
        if missing:
            return SendResult(status="CONFIG_ERROR", detail=f"Missing WhatsApp config: {', '.join(missing)}")

        recipients = load_active_recipients(settings.whatsapp_recipients_csv)
        if not recipients:
            return SendResult(status="NO_RECIPIENTS", detail="No active opted-in recipients found in whatsapp_recipients.csv.")

        template_name = settings.whatsapp_template_name
        provider_ids: list[str] = []
        sent_count = 0
        failed_count = 0
        skipped_template = False
        chapter_no = plan.chapter_no if plan else _chapter_from_paths(paths)
        slug = plan.slug if plan else paths.root.name.split("_", 1)[-1]

        for recipient in recipients:
            body_params = None
            if template_name == "daily_krishna_story" and content:
                package_ref = str(paths.root)
                body_params = [recipient.name or "Family", content.title, package_ref]

            try:
                result = client.send_template(
                    to_phone=recipient.phone_digits,
                    template_name=template_name,
                    body_parameters=body_params,
                )
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
                        "detail": f"template={template_name}",
                        "message_id": message_id,
                        "created_at": _now_iso(settings),
                    },
                )
            except WhatsAppCloudError as exc:
                if template_name == "daily_krishna_story":
                    skipped_template = True
                    append_send_log(
                        settings.project_root,
                        {
                            "date": _today(settings),
                            "chapter_no": chapter_no,
                            "slug": slug,
                            "sender_type": "cloud",
                            "recipient_name": recipient.name,
                            "recipient_phone": recipient.phone_digits,
                            "status": "SKIPPED",
                            "detail": "daily_krishna_story template not enabled or not approved yet",
                            "message_id": "",
                            "created_at": _now_iso(settings),
                        },
                    )
                    break
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
            if skipped_template:
                return SendResult(
                    status="SKIPPED_TEMPLATE",
                    detail="Package generated. daily_krishna_story is not enabled/approved yet. Set WHATSAPP_TEMPLATE_NAME=hello_world for smoke tests.",
                    provider_ids=provider_ids,
                )
            return SendResult(
                status="FAILED_CLOUD",
                detail=f"WhatsApp template send failed for all {failed_count} recipient(s).",
                provider_ids=provider_ids,
            )

        detail = f"Sent template '{template_name}' to {sent_count} recipient(s)."
        if failed_count:
            detail += f" {failed_count} failed."
        if skipped_template:
            detail += " daily_krishna_story not sent (not approved)."
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
