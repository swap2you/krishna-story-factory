from __future__ import annotations

import json
import re

from .cloud_client import WhatsAppCloudError


def classify_whatsapp_error(exc: WhatsAppCloudError) -> str:
    body = (exc.response_body or "").lower()
    status = exc.status_code

    if status == 401 or "oauth" in body or "access token" in body:
        return "TOKEN_EXPIRED"
    if status == 404 or "template not found" in body or "does not exist" in body and "template" in body:
        return "TEMPLATE_NOT_FOUND"
    if "param" in body and "template" in body:
        return "TEMPLATE_PARAMS_MISMATCH"
    if "not allowed" in body or "recipient" in body and "invalid" in body:
        return "RECIPIENT_NOT_ALLOWED"
    if status and status >= 400:
        return "META_API_ERROR"
    return "UNKNOWN_CLOUD_ERROR"


def format_whatsapp_log_detail(
    exc: WhatsAppCloudError,
    *,
    template_name: str,
    language_code: str,
    recipient_phone: str,
) -> str:
    reason = classify_whatsapp_error(exc)
    meta_message = _extract_meta_message(exc.response_body)
    parts = [
        f"reason={reason}",
        f"template={template_name}",
        f"language={language_code}",
        f"phone={recipient_phone}",
    ]
    if exc.status_code is not None:
        parts.append(f"HTTP {exc.status_code}")
    if meta_message:
        parts.append(f"meta={meta_message}")
    detail = " | ".join(parts)
    return detail.replace("Bearer ", "Bearer [REDACTED] ")


def _extract_meta_message(response_body: str) -> str:
    if not response_body:
        return ""
    try:
        data = json.loads(response_body)
    except json.JSONDecodeError:
        return re.sub(r"Bearer\s+\S+", "Bearer [REDACTED]", response_body[:300])
    error = data.get("error", {})
    if isinstance(error, dict):
        message = str(error.get("message", "")).strip()
        code = error.get("code")
        if message and code is not None:
            return f"{message} (code {code})"
        return message
    return ""
