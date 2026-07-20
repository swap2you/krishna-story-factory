# Setup and API Keys

## Requirements

- Python 3.11+
- Windows PowerShell
- Local `.env` (never committed)

## Install

```powershell
cd C:\Development\Workspace\DevotionalRepo\krishna-story-factory
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```

## OpenAI (story text and optional image)

```env
OPENAI_TEXT_ENABLED=true
OPENAI_API_KEY=your_key
OPENAI_TEXT_MODEL=gpt-4.1
OPENAI_IMAGE_ENABLED=true
OPENAI_IMAGE_MODEL=gpt-image-1
```

## ElevenLabs (narration)

```env
ELEVENLABS_ENABLED=true
ELEVENLABS_API_KEY=your_key
ELEVENLABS_VOICE_ID=your_voice_id
```

Prod requires real audio unless:

```env
ALLOW_PLACEHOLDER_AUDIO=true
```

## WhatsApp Cloud (individual CSV broadcast)

```env
WHATSAPP_SEND_ENABLED=true
WHATSAPP_SENDER_TYPE=cloud
WHATSAPP_GRAPH_API_VERSION=v25.0
WHATSAPP_BUSINESS_ACCOUNT_ID=
WHATSAPP_PHONE_NUMBER_ID=
WHATSAPP_CLOUD_TOKEN=
WHATSAPP_TEST_RECIPIENT_PHONE=
WHATSAPP_TEMPLATE_NAME=hello_world
WHATSAPP_TEMPLATE_LANGUAGE=en_US
WHATSAPP_RECIPIENTS_CSV=input/whatsapp_recipients.csv
```

Never commit tokens. Use `hello_world` for Meta test setup. Switch to `daily_krishna_story` after Meta approval.

## Validate

```powershell
.\scripts\test_all.ps1
.\scripts\run_test.ps1 --force
python scripts/test_whatsapp_cloud.py
```
