"""Narrow, non-shell adapter boundary for future local factory controls."""
from __future__ import annotations

import re
from typing import Any

from .config import get_settings

ALLOWED_OPERATIONS = frozenset({"preflight", "generate-next", "drive-readback"})
_SECRET_KEY = re.compile(r"(api[_-]?key|token|secret|password|credential)", re.I)


def redact_secrets(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: ("[redacted]" if _SECRET_KEY.search(key) else redact_secrets(item))
                for key, item in value.items()}
    if isinstance(value, list):
        return [redact_secrets(item) for item in value]
    return value


def perform(operation: str) -> dict[str, Any]:
    """Return a controlled result; this Phase 0 adapter never invokes a shell."""
    if operation not in ALLOWED_OPERATIONS:
        raise ValueError("Operation is not allowlisted")
    if not get_settings().factory_actions_enabled:
        return {"operation": operation, "status": "disabled", "detail": "Factory actions are disabled."}
    return {
        "operation": operation,
        "status": "demo",
        "detail": "Action gateway is enabled, but this Phase 0 adapter does not execute generation.",
    }
