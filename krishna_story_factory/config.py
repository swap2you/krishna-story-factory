from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


def str_to_bool(value: str | None, default: bool = False) -> bool:
    if value is None or value == "":
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


@dataclass(frozen=True)
class Settings:
    project_root: Path
    app_timezone: str
    output_root: Path

    openai_text_enabled: bool
    openai_image_enabled: bool
    elevenlabs_enabled: bool
    whatsapp_send_enabled: bool

    openai_api_key: str
    openai_text_model: str
    openai_image_model: str
    openai_image_size: str
    openai_image_quality: str

    elevenlabs_api_key: str
    elevenlabs_voice_id: str
    elevenlabs_model_id: str

    whatsapp_sender_type: str
    whatsapp_graph_api_version: str
    whatsapp_phone_number_id: str
    whatsapp_access_token: str
    whatsapp_target_phone: str
    whatsapp_template_name: str
    whatsapp_language_code: str
    whatsapp_web_test_dir: Path

    telegram_bot_token: str
    telegram_chat_id: str
    slack_webhook_url: str
    discord_webhook_url: str


def _resolve_path(project_root: Path, env_name: str, default: str) -> Path:
    value = Path(os.getenv(env_name, default))
    if not value.is_absolute():
        value = project_root / value
    return value


def load_settings(project_root: Path) -> Settings:
    load_dotenv(project_root / ".env")
    output_root = _resolve_path(project_root, "OUTPUT_ROOT", "output")
    web_test_dir = _resolve_path(project_root, "WHATSAPP_WEB_TEST_DIR", "whatsapp_test_outbox")

    return Settings(
        project_root=project_root,
        app_timezone=os.getenv("APP_TIMEZONE", "America/New_York"),
        output_root=output_root,
        openai_text_enabled=str_to_bool(os.getenv("OPENAI_TEXT_ENABLED"), False),
        openai_image_enabled=str_to_bool(os.getenv("OPENAI_IMAGE_ENABLED"), False),
        elevenlabs_enabled=str_to_bool(os.getenv("ELEVENLABS_ENABLED"), False),
        whatsapp_send_enabled=str_to_bool(os.getenv("WHATSAPP_SEND_ENABLED"), False),
        openai_api_key=os.getenv("OPENAI_API_KEY", ""),
        openai_text_model=os.getenv("OPENAI_TEXT_MODEL", "gpt-4.1"),
        openai_image_model=os.getenv("OPENAI_IMAGE_MODEL", "gpt-image-1"),
        openai_image_size=os.getenv("OPENAI_IMAGE_SIZE", "1024x1024"),
        openai_image_quality=os.getenv("OPENAI_IMAGE_QUALITY", "medium"),
        elevenlabs_api_key=os.getenv("ELEVENLABS_API_KEY", ""),
        elevenlabs_voice_id=os.getenv("ELEVENLABS_VOICE_ID", ""),
        elevenlabs_model_id=os.getenv("ELEVENLABS_MODEL_ID", "eleven_multilingual_v2"),
        whatsapp_sender_type=os.getenv("WHATSAPP_SENDER_TYPE", "manual").strip().lower(),
        whatsapp_graph_api_version=os.getenv("WHATSAPP_GRAPH_API_VERSION", "v23.0"),
        whatsapp_phone_number_id=os.getenv("WHATSAPP_PHONE_NUMBER_ID", ""),
        whatsapp_access_token=os.getenv("WHATSAPP_ACCESS_TOKEN", ""),
        whatsapp_target_phone=os.getenv("WHATSAPP_TARGET_PHONE", ""),
        whatsapp_template_name=os.getenv("WHATSAPP_TEMPLATE_NAME", ""),
        whatsapp_language_code=os.getenv("WHATSAPP_LANGUAGE_CODE", "en_US"),
        whatsapp_web_test_dir=web_test_dir,
        telegram_bot_token=os.getenv("TELEGRAM_BOT_TOKEN", ""),
        telegram_chat_id=os.getenv("TELEGRAM_CHAT_ID", ""),
        slack_webhook_url=os.getenv("SLACK_WEBHOOK_URL", ""),
        discord_webhook_url=os.getenv("DISCORD_WEBHOOK_URL", ""),
    )
