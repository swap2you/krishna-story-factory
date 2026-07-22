# Setup and Credentials

Condensed from the former setup guide. **Never commit secrets**, `.env`, tokens, or `credentials/`.

## Requirements

- Windows PowerShell  
- Python **3.12** (supported; bootstrap prefers `py -3.12`)  
- Local `.env` copied from `.env.example`

## Install

```powershell
cd C:\Development\Workspace\DevotionalRepo\krishna-story-factory
.\scripts\bootstrap.ps1
copy .env.example .env
```

Wrappers always use `.venv\Scripts\python.exe`. Do not rely on a random global `python` on PATH.

## Essential `.env` flags

```env
# Text / images
OPENAI_TEXT_ENABLED=true
OPENAI_API_KEY=
OPENAI_IMAGE_ENABLED=true

# Audio — ElevenLabs Renee primary
ELEVENLABS_ENABLED=true
ELEVENLABS_API_KEY=
ELEVENLABS_VOICE_ID=Itr6exdQTrvjpW1lNztS
ELEVENLABS_VOICE_NAME=Renee - Rich, Calm and Smooth
ELEVENLABS_MODEL_ID=eleven_v3

# Audio fallback — OpenAI Marin
AUDIO_PROVIDER_MODE=auto
AUDIO_PROVIDER_PRIMARY=elevenlabs
AUDIO_PROVIDER_FALLBACK=openai
AUDIO_REQUIRED=true
OPENAI_TTS_ENABLED=true
OPENAI_TTS_VOICE=marin
OPENAI_TTS_MODEL=gpt-4o-mini-tts-2025-12-15

# Delivery (pilot)
WHATSAPP_SEND_ENABLED=false
TELEGRAM_SEND_ENABLED=false
GOOGLE_DRIVE_UPLOAD_ENABLED=true
GOOGLE_DRIVE_FOLDER_ID=
GOOGLE_DRIVE_FOLDER_URL=
GOOGLE_DRIVE_CREDENTIALS_FILE=credentials/google_drive_oauth_client.json
GOOGLE_DRIVE_TOKEN_FILE=credentials/google_drive_token.json
```

## Google Drive OAuth (local only)

1. Enable Google Drive API.  
2. Create OAuth Desktop client JSON → `credentials/google_drive_oauth_client.json`.  
3. First upload opens a browser; token saved to `credentials/google_drive_token.json`.  
4. Keep parent folder Viewer for parents; Editor for the uploader account.

## Validate install

```powershell
.\scripts\test_all.ps1
.\scripts\run_test.ps1 --force
.\.venv\Scripts\python.exe scripts\diagnose_local_config.py
```

Test mode must not call paid APIs. Keep WhatsApp/Telegram disabled unless you intentionally operate those channels later.
