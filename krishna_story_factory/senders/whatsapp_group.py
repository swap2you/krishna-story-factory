from __future__ import annotations

from ..config import Settings
from ..models import PackagePaths, SendResult
from .base import BaseSender


class WhatsAppGroupSender(BaseSender):
    """Group sender interface placeholder.

    Official WhatsApp Cloud API is designed for business messaging to users.
    Ordinary WhatsApp group posting is not implemented here because it usually
    depends on unsupported browser automation or unofficial libraries.
    """

    def send(self, *, settings: Settings, paths: PackagePaths, mode: str) -> SendResult:
        return SendResult(
            status="UNSUPPORTED",
            detail=(
                "WhatsAppGroupSender interface is present, but group posting is not implemented. "
                "Use WhatsAppWebTestSender for private manual testing or WhatsAppCloudSender for official API sending to individual recipients."
            ),
        )
