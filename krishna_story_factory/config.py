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
    allow_placeholder_audio: bool

    openai_api_key: str
    openai_text_model: str
    openai_image_model: str
    openai_image_size: str
    openai_image_quality: str
    image_generate_coloring_page: bool
    image_generate_wide_card: bool
    image_size_story_card: str
    image_size_coloring_page: str

    elevenlabs_api_key: str
    elevenlabs_voice_id: str
    elevenlabs_model_id: str
    elevenlabs_stability: float | None
    elevenlabs_similarity_boost: float | None
    elevenlabs_style: float | None
    elevenlabs_use_speaker_boost: bool | None
    elevenlabs_speed: float | None
    elevenlabs_pronunciation_dictionary_id: str
    enable_ambient_audio: bool
    elevenlabs_sfx_enabled: bool
    ambient_audio_mix_level: float

    package_publish_mode: str
    google_drive_upload_enabled: bool
    google_drive_folder_id: str
    google_drive_folder_url: str
    google_drive_local_sync_root: Path | None
    google_drive_credentials_file: Path | None
    google_drive_token_file: Path | None
    google_drive_share_role: str
    package_public_link: str

    whatsapp_sender_type: str
    whatsapp_graph_api_version: str
    whatsapp_business_account_id: str
    whatsapp_phone_number_id: str
    whatsapp_cloud_token: str
    whatsapp_access_token: str
    whatsapp_target_phone: str
    whatsapp_test_recipient_phone: str
    whatsapp_template_name: str
    whatsapp_template_language: str
    whatsapp_language_code: str
    whatsapp_recipients_csv: Path
    whatsapp_web_test_dir: Path

    telegram_bot_token: str
    telegram_chat_id: str
    slack_webhook_url: str
    discord_webhook_url: str


def _optional_float(env_name: str) -> float | None:
    raw = os.getenv(env_name, "").strip()
    if not raw:
        return None
    return float(raw)


def _optional_bool(env_name: str) -> bool | None:
    raw = os.getenv(env_name, "").strip()
    if raw == "":
        return None
    return str_to_bool(raw)


def _optional_path(project_root: Path, env_name: str) -> Path | None:
    raw = os.getenv(env_name, "").strip()
    if not raw:
        return None
    value = Path(raw)
    if not value.is_absolute():
        value = project_root / value
    return value


def _resolve_path(project_root: Path, env_name: str, default: str) -> Path:
    value = Path(os.getenv(env_name, default))
    if not value.is_absolute():
        value = project_root / value
    return value


def load_settings(project_root: Path) -> Settings:
    load_dotenv(project_root / ".env")
    output_root = _resolve_path(project_root, "OUTPUT_ROOT", "output")
    web_test_dir = _resolve_path(project_root, "WHATSAPP_WEB_TEST_DIR", "whatsapp_test_outbox")
    recipients_csv = _resolve_path(project_root, "WHATSAPP_RECIPIENTS_CSV", "input/whatsapp_recipients.csv")
    cloud_token = os.getenv("WHATSAPP_CLOUD_TOKEN", "").strip() or os.getenv("WHATSAPP_ACCESS_TOKEN", "").strip()
    template_language = os.getenv("WHATSAPP_TEMPLATE_LANGUAGE", "").strip() or os.getenv("WHATSAPP_LANGUAGE_CODE", "en_US")

    return Settings(
        project_root=project_root,
        app_timezone=os.getenv("APP_TIMEZONE", "America/New_York"),
        output_root=output_root,
        openai_text_enabled=str_to_bool(os.getenv("OPENAI_TEXT_ENABLED"), False),
        openai_image_enabled=str_to_bool(os.getenv("OPENAI_IMAGE_ENABLED"), False),
        elevenlabs_enabled=str_to_bool(os.getenv("ELEVENLABS_ENABLED"), False),
        whatsapp_send_enabled=str_to_bool(os.getenv("WHATSAPP_SEND_ENABLED"), False),
        allow_placeholder_audio=str_to_bool(os.getenv("ALLOW_PLACEHOLDER_AUDIO"), False),
        openai_api_key=os.getenv("OPENAI_API_KEY", ""),
        openai_text_model=os.getenv("OPENAI_TEXT_MODEL", "gpt-4.1"),
        openai_image_model=os.getenv("OPENAI_IMAGE_MODEL", "gpt-image-1"),
        openai_image_size=os.getenv("OPENAI_IMAGE_SIZE", "1024x1024"),
        openai_image_quality=os.getenv("OPENAI_IMAGE_QUALITY", "medium"),
        image_generate_coloring_page=str_to_bool(os.getenv("IMAGE_GENERATE_COLORING_PAGE"), True),
        image_generate_wide_card=str_to_bool(os.getenv("IMAGE_GENERATE_WIDE_CARD"), False),
        image_size_story_card=os.getenv("IMAGE_SIZE_STORY_CARD", "1024x1024"),
        image_size_coloring_page=os.getenv("IMAGE_SIZE_COLORING_PAGE", "1024x1024"),
        elevenlabs_api_key=os.getenv("ELEVENLABS_API_KEY", ""),
        elevenlabs_voice_id=os.getenv("ELEVENLABS_VOICE_ID", ""),
        elevenlabs_model_id=os.getenv("ELEVENLABS_MODEL_ID", "eleven_multilingual_v2"),
        elevenlabs_stability=_optional_float("ELEVENLABS_STABILITY"),
        elevenlabs_similarity_boost=_optional_float("ELEVENLABS_SIMILARITY_BOOST"),
        elevenlabs_style=_optional_float("ELEVENLABS_STYLE"),
        elevenlabs_use_speaker_boost=_optional_bool("ELEVENLABS_USE_SPEAKER_BOOST"),
        elevenlabs_speed=_optional_float("ELEVENLABS_SPEED"),
        elevenlabs_pronunciation_dictionary_id=os.getenv("ELEVENLABS_PRONUNCIATION_DICTIONARY_ID", "").strip(),
        enable_ambient_audio=str_to_bool(os.getenv("ENABLE_AMBIENT_AUDIO"), False),
        elevenlabs_sfx_enabled=str_to_bool(os.getenv("ELEVENLABS_SFX_ENABLED"), False),
        ambient_audio_mix_level=float(os.getenv("AMBIENT_AUDIO_MIX_LEVEL", "0.12") or "0.12"),
        package_publish_mode=os.getenv("PACKAGE_PUBLISH_MODE", "local"),
        google_drive_upload_enabled=str_to_bool(os.getenv("GOOGLE_DRIVE_UPLOAD_ENABLED"), False),
        google_drive_folder_id=os.getenv("GOOGLE_DRIVE_FOLDER_ID", ""),
        google_drive_folder_url=os.getenv("GOOGLE_DRIVE_FOLDER_URL", ""),
        google_drive_local_sync_root=_optional_path(project_root, "GOOGLE_DRIVE_LOCAL_SYNC_ROOT"),
        google_drive_credentials_file=_optional_path(project_root, "GOOGLE_DRIVE_CREDENTIALS_FILE"),
        google_drive_token_file=_optional_path(project_root, "GOOGLE_DRIVE_TOKEN_FILE"),
        google_drive_share_role=os.getenv("GOOGLE_DRIVE_SHARE_ROLE", "reader"),
        package_public_link=os.getenv("PACKAGE_PUBLIC_LINK", ""),
        whatsapp_sender_type=os.getenv("WHATSAPP_SENDER_TYPE", "manual").strip().lower(),
        whatsapp_graph_api_version=os.getenv("WHATSAPP_GRAPH_API_VERSION", "v25.0"),
        whatsapp_business_account_id=os.getenv("WHATSAPP_BUSINESS_ACCOUNT_ID", ""),
        whatsapp_phone_number_id=os.getenv("WHATSAPP_PHONE_NUMBER_ID", ""),
        whatsapp_cloud_token=cloud_token,
        whatsapp_access_token=os.getenv("WHATSAPP_ACCESS_TOKEN", ""),
        whatsapp_target_phone=os.getenv("WHATSAPP_TARGET_PHONE", ""),
        whatsapp_test_recipient_phone=os.getenv("WHATSAPP_TEST_RECIPIENT_PHONE", ""),
        whatsapp_template_name=os.getenv("WHATSAPP_TEMPLATE_NAME", "hello_world"),
        whatsapp_template_language=template_language,
        whatsapp_language_code=os.getenv("WHATSAPP_LANGUAGE_CODE", "en_US"),
        whatsapp_recipients_csv=recipients_csv,
        whatsapp_web_test_dir=web_test_dir,
        telegram_bot_token=os.getenv("TELEGRAM_BOT_TOKEN", ""),
        telegram_chat_id=os.getenv("TELEGRAM_CHAT_ID", ""),
        slack_webhook_url=os.getenv("SLACK_WEBHOOK_URL", ""),
        discord_webhook_url=os.getenv("DISCORD_WEBHOOK_URL", ""),
    )
