from __future__ import annotations

import re


def normalize_phone_e164(phone: str) -> str:
    """Return digits-only phone number for WhatsApp Cloud API."""
    cleaned = phone.strip()
    cleaned = cleaned.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
    if cleaned.startswith("+"):
        cleaned = cleaned[1:]
    return re.sub(r"\D", "", cleaned)
