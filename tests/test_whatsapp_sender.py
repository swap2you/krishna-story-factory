from __future__ import annotations

import csv
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from krishna_story_factory.config import Settings
from krishna_story_factory.senders.whatsapp_cloud import WhatsAppCloudSender
from krishna_story_factory.whatsapp.cloud_client import WhatsAppCloudClient, WhatsAppCloudError, build_template_payload
from krishna_story_factory.whatsapp.phone import normalize_phone_e164
from krishna_story_factory.whatsapp.recipients import load_active_recipients


def test_normalize_phone_e164() -> None:
    assert normalize_phone_e164("+1 (714) 307-4266") == "17143074266"
    assert normalize_phone_e164("17143074266") == "17143074266"
    assert normalize_phone_e164("+17143074266") == "17143074266"


def test_build_template_payload_shape() -> None:
    payload = build_template_payload(to_phone="17143074266", template_name="hello_world", language_code="en_US")
    assert payload == {
        "messaging_product": "whatsapp",
        "to": "17143074266",
        "type": "template",
        "template": {"name": "hello_world", "language": {"code": "en_US"}},
    }


def test_missing_cloud_token_fails_cleanly(tmp_path: Path) -> None:
    settings = _settings(tmp_path, cloud_token="", phone_number_id="1186584224540331")
    client = WhatsAppCloudClient(settings)
    assert "WHATSAPP_CLOUD_TOKEN" in client.validate_config()


def test_missing_phone_number_id_fails_cleanly(tmp_path: Path) -> None:
    settings = _settings(tmp_path, cloud_token="test-token", phone_number_id="")
    client = WhatsAppCloudClient(settings)
    assert "WHATSAPP_PHONE_NUMBER_ID" in client.validate_config()


def test_opt_in_false_recipient_skipped(tmp_path: Path) -> None:
    csv_path = tmp_path / "recipients.csv"
    csv_path.write_text(
        "name,phone_e164,opt_in,status,notes\n"
        "Opted Out,+17143074266,false,active,skip opt out\n",
        encoding="utf-8",
    )
    assert load_active_recipients(csv_path) == []


def test_inactive_recipient_skipped(tmp_path: Path) -> None:
    csv_path = tmp_path / "recipients.csv"
    csv_path.write_text(
        "name,phone_e164,opt_in,status,notes\n"
        "Inactive,+17143074266,true,inactive,skip inactive\n",
        encoding="utf-8",
    )
    assert load_active_recipients(csv_path) == []


@patch("krishna_story_factory.whatsapp.cloud_client.requests.post")
def test_mocked_meta_success_logs_message_id(mock_post: MagicMock, tmp_path: Path) -> None:
    mock_post.return_value.status_code = 200
    mock_post.return_value.text = '{"messages":[{"id":"wamid.TEST123"}]}'
    mock_post.return_value.json.return_value = {"messages": [{"id": "wamid.TEST123"}]}

    settings = _settings(tmp_path, cloud_token="secret-token-value", phone_number_id="1186584224540331")
    client = WhatsAppCloudClient(settings)
    result = client.send_template(to_phone="17143074266")
    assert result["message_ids"] == ["wamid.TEST123"]

    _, kwargs = mock_post.call_args
    headers = kwargs["headers"]
    assert "secret-token-value" in headers["Authorization"]
    assert "Bearer" in headers["Authorization"]


@patch("krishna_story_factory.whatsapp.cloud_client.requests.post")
def test_no_token_in_error_output(mock_post: MagicMock, tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    mock_post.return_value.status_code = 401
    mock_post.return_value.text = '{"error":{"message":"Invalid OAuth access token"}}'
    mock_post.return_value.json.return_value = {"error": {"message": "Invalid OAuth access token"}}

    settings = _settings(tmp_path, cloud_token="super-secret-token", phone_number_id="1186584224540331")
    client = WhatsAppCloudClient(settings)
    with pytest.raises(WhatsAppCloudError) as exc_info:
        client.send_template(to_phone="17143074266")

    captured = str(exc_info.value) + exc_info.value.response_body
    assert "super-secret-token" not in captured


@patch("krishna_story_factory.senders.whatsapp_cloud.append_send_log")
@patch("krishna_story_factory.senders.whatsapp_cloud.WhatsAppCloudClient.send_template")
def test_sender_broadcast_logs_success(mock_send: MagicMock, mock_log: MagicMock, tmp_path: Path) -> None:
    mock_send.return_value = {"message_ids": ["wamid.ABC"]}
    recipients = tmp_path / "input" / "whatsapp_recipients.csv"
    recipients.parent.mkdir(parents=True)
    recipients.write_text(
        "name,phone_e164,opt_in,status,notes\nSwapnil,+17143074266,true,active,test\n",
        encoding="utf-8",
    )
    settings = _settings(tmp_path, cloud_token="token", phone_number_id="1186584224540331", recipients_csv=recipients)
    paths = _package_paths(tmp_path)
    result = WhatsAppCloudSender().send(settings=settings, paths=paths, mode="prod")
    assert result.status == "SENT_CLOUD"
    mock_log.assert_called_once()
    assert mock_log.call_args[0][1]["message_id"] == "wamid.ABC"


def _settings(
    tmp_path: Path,
    *,
    cloud_token: str,
    phone_number_id: str,
    recipients_csv: Path | None = None,
) -> Settings:
    return Settings(
        project_root=tmp_path,
        app_timezone="America/New_York",
        output_root=tmp_path / "output",
        openai_text_enabled=False,
        openai_image_enabled=False,
        elevenlabs_enabled=False,
        whatsapp_send_enabled=True,
        openai_api_key="",
        openai_text_model="gpt-4.1",
        openai_image_model="gpt-image-1",
        openai_image_size="1024x1024",
        openai_image_quality="medium",
        elevenlabs_api_key="",
        elevenlabs_voice_id="",
        elevenlabs_model_id="eleven_multilingual_v2",
        whatsapp_sender_type="cloud",
        whatsapp_graph_api_version="v25.0",
        whatsapp_business_account_id="1484151732955311",
        whatsapp_phone_number_id=phone_number_id,
        whatsapp_cloud_token=cloud_token,
        whatsapp_access_token="",
        whatsapp_target_phone="",
        whatsapp_test_recipient_phone="17143074266",
        whatsapp_template_name="hello_world",
        whatsapp_template_language="en_US",
        whatsapp_language_code="en_US",
        whatsapp_recipients_csv=recipients_csv or (tmp_path / "input" / "whatsapp_recipients.csv"),
        whatsapp_web_test_dir=tmp_path / "whatsapp_test_outbox",
        telegram_bot_token="",
        telegram_chat_id="",
        slack_webhook_url="",
        discord_webhook_url="",
    )


def _package_paths(tmp_path: Path):
    from krishna_story_factory.models import PackagePaths

    root = tmp_path / "output" / "004_prahlada"
    root.mkdir(parents=True)
    return PackagePaths(
        root=root,
        story_md=root / "story.md",
        audio_script=root / "audio_script.txt",
        whatsapp_caption=root / "whatsapp_caption.txt",
        activity_sheet=root / "activity_sheet.pdf",
        story_card=root / "story_card.png",
        image_prompt=root / "image_prompt.txt",
        parent_notes=root / "parent_notes.md",
        manifest=root / "manifest.json",
        narration_mp3=root / "narration.mp3",
    )
