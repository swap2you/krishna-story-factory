"""Small same-origin CSRF gate for local state-changing routes."""
from __future__ import annotations

import secrets

from fastapi import HTTPException, Request, status

TOKEN_HEADER = "X-Bhava-CSRF-Token"


def issue_token() -> str:
    return secrets.token_urlsafe(32)


def require_csrf(request: Request) -> None:
    expected = getattr(request.app.state, "csrf_token", None)
    provided = request.headers.get(TOKEN_HEADER)
    if not expected or not provided or not secrets.compare_digest(expected, provided):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="CSRF token required")
