"""Shared secret/error sanitization for logs and user-facing status text."""
from __future__ import annotations

import re

_SECRET_PATTERNS = (
    re.compile(r"sk-[A-Za-z0-9_\-]{8,}", re.IGNORECASE),
    re.compile(r"sk_proj-[A-Za-z0-9_\-]{8,}", re.IGNORECASE),
    re.compile(r"sk_[A-Za-z0-9_\-]{8,}", re.IGNORECASE),
    re.compile(r"xi-[A-Za-z0-9_\-]{8,}", re.IGNORECASE),
    re.compile(r"Bearer\s+[A-Za-z0-9\-._~+/]+=*", re.IGNORECASE),
    re.compile(r"(api[_-]?key|token|authorization)\s*[:=]\s*['\"]?[^'\"\s,;]+", re.IGNORECASE),
)


def sanitize_error_text(text: str, *, limit: int = 500) -> str:
    """Redact credential-like substrings before logging or persisting errors."""
    cleaned = str(text or "")
    for pattern in _SECRET_PATTERNS:
        cleaned = pattern.sub("[REDACTED]", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    if len(cleaned) > limit:
        return cleaned[: limit - 3] + "..."
    return cleaned
