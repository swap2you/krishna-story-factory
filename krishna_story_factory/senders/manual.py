from __future__ import annotations

from ..config import Settings
from ..models import PackagePaths, SendResult
from .base import BaseSender


class ManualSender(BaseSender):
    def send(self, *, settings: Settings, paths: PackagePaths, mode: str) -> SendResult:
        detail = (
            "Manual sender selected. Package generated locally. "
            f"Copy files from: {paths.root}"
        )
        return SendResult(status="MANUAL_READY", detail=detail)
