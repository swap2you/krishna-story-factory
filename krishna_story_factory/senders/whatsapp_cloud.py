from __future__ import annotations

from ..config import Settings
from ..csv_store import append_send_log
from ..models import PackagePaths, PlanRow, SendResult, StoryContent
from ..whatsapp.cloud_client import WhatsAppCloudClient, WhatsAppCloudError
from ..whatsapp.errors import classify_whatsapp_error, format_whatsapp_log_detail
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
        package_link: str = "",
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
        language_code = settings.whatsapp_template_language
        provider_ids: list[str] = []
        sent_count = 0
        failed_count = 0
        last_failure_reason = ""
        chapter_no = plan.chapter_no if plan else _chapter_from_paths(paths)
        slug = plan.slug if plan else paths.root.name.split("_", 1)[-1]
        link = package_link or _read_package_link(paths)

        story_title = content.title if content else ""
        for recipient in recipients:
            body_params = None
            if template_name == "daily_krishna_story" and content:
                body_params = [recipient.name or "Family", content.title, link or "Package link pending"]

            try:
                result = client.send_template(
                    to_phone=recipient.phone_digits,
                    template_name=template_name,
                    language_code=language_code,
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
                        "template_name": template_name,
                        "story_title": story_title,
                        "package_link": link,
                        "status": "SUCCESS",
                        "detail": f"template={template_name} | language={language_code}",
                        "message_id": message_id,
                        "created_at": _now_iso(settings),
                    },
                )
            except WhatsAppCloudError as exc:
                failure_reason = classify_whatsapp_error(exc)
                last_failure_reason = failure_reason
                failed_count += 1
                detail = format_whatsapp_log_detail(
                    exc,
                    template_name=template_name,
                    language_code=language_code,
                    recipient_phone=recipient.phone_digits,
                )
                append_send_log(
                    settings.project_root,
                    {
                        "date": _today(settings),
                        "chapter_no": chapter_no,
                        "slug": slug,
                        "sender_type": "cloud",
                        "recipient_name": recipient.name,
                        "recipient_phone": recipient.phone_digits,
                        "template_name": template_name,
                        "story_title": story_title,
                        "package_link": link,
                        "status": "FAILED",
                        "detail": detail,
                        "message_id": "",
                        "created_at": _now_iso(settings),
                    },
                )

        if sent_count == 0:
            return SendResult(
                status="FAILED_CLOUD",
                detail=f"WhatsApp template send failed for all {failed_count} recipient(s).",
                failure_reason=last_failure_reason or "UNKNOWN_CLOUD_ERROR",
                provider_ids=provider_ids,
            )

        detail = f"Sent template '{template_name}' ({language_code}) to {sent_count} recipient(s)."
        if failed_count:
            detail += f" {failed_count} failed."
        status = "SENT_CLOUD"
        if template_name == "hello_world":
            status = "SENT_SMOKE_TEST"
            detail += (
                " Smoke-test template sent. Real story message was not sent. "
                "Set WHATSAPP_TEMPLATE_NAME=daily_krishna_story after Meta approval."
            )
        return SendResult(status=status, detail=detail, provider_ids=provider_ids)


def _chapter_from_paths(paths: PackagePaths) -> str:
    name = paths.root.name
    if "_" in name:
        return name.split("_", 1)[0]
    return ""


def _read_package_link(paths: PackagePaths) -> str:
    import json

    if not paths.manifest.exists():
        return ""
    try:
        data = json.loads(paths.manifest.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return ""
    return str(data.get("package", {}).get("package_link", "")).strip()


def _today(settings: Settings) -> str:
    from datetime import datetime
    from zoneinfo import ZoneInfo

    return datetime.now(ZoneInfo(settings.app_timezone)).date().isoformat()


def _now_iso(settings: Settings) -> str:
    from datetime import datetime
    from zoneinfo import ZoneInfo

    return datetime.now(ZoneInfo(settings.app_timezone)).isoformat(timespec="seconds")
