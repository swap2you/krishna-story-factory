from __future__ import annotations

from ..config import Settings
from .base import BaseSender
from .discord_sender import DiscordWebhookSender
from .manual import ManualSender
from .slack_sender import SlackWebhookSender
from .telegram_sender import TelegramSender
from .whatsapp_cloud import WhatsAppCloudSender
from .whatsapp_group import WhatsAppGroupSender
from .whatsapp_web_test import WhatsAppWebTestSender


def build_sender(settings: Settings) -> BaseSender:
    sender_type = settings.whatsapp_sender_type
    if sender_type == "manual":
        return ManualSender()
    if sender_type == "cloud":
        return WhatsAppCloudSender()
    if sender_type == "group":
        return WhatsAppGroupSender()
    if sender_type == "web_test":
        return WhatsAppWebTestSender()
    if sender_type == "telegram":
        return TelegramSender()
    if sender_type == "slack":
        return SlackWebhookSender()
    if sender_type == "discord":
        return DiscordWebhookSender()
    raise ValueError(f"Unsupported WHATSAPP_SENDER_TYPE: {sender_type}")
