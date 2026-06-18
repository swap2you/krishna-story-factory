# Validation Artifacts

Date: 2026-06-18  
Story: **001 — The Earth Prays for Krishna to Come**

## Commands

```powershell
pytest -q
python scripts/diagnose_local_config.py
python scripts/test_google_drive_upload.py
python scripts/test_whatsapp_daily_template.py
python run_daily_story.py --mode prod --force
python scripts/check_audio_quality.py output\001_the-earth-prays-for-krishna\narration.mp3
```

## Pytest

```text
36 passed
```

## Local config (safe)

```text
OPENAI_TEXT_ENABLED: true
OPENAI_IMAGE_ENABLED: true
ELEVENLABS_ENABLED: true
WHATSAPP_SEND_ENABLED: true
WHATSAPP_TEMPLATE_NAME: daily_krishna_story
WHATSAPP_TEMPLATE_LANGUAGE: en_US
WHATSAPP_PHONE_NUMBER_ID present: yes
WHATSAPP_CLOUD_TOKEN present: yes
GOOGLE_DRIVE_UPLOAD_ENABLED: false
GOOGLE_DRIVE_FOLDER_ID present: no
GOOGLE_DRIVE_CREDENTIALS_FILE exists: yes (on disk)
GOOGLE_DRIVE_TOKEN_FILE exists: no
Active opted-in recipients: 2
Next pending story: 002_devaki-and-vasudeva-wedding
```

## Drive upload test

```text
SKIPPED — GOOGLE_DRIVE_UPLOAD_ENABLED=false in local .env
OAuth client JSON present locally (not committed)
```

## WhatsApp daily template test

```text
FAILED — HTTP 404 (standalone test) / HTTP 401 TOKEN_EXPIRED (prod send)
Template name: daily_krishna_story (not hello_world)
Status logged as FAILED_CLOUD, not SENT_CLOUD
```

## Fresh prod run

```text
Folder: output/001_the-earth-prays-for-krishna/
Quality: PASS
Story words: 1002
Audio words: 509
MP3: 3028158 bytes
Repetition: PASS
Activity PDF: 3 pages
Images: story_card.png, story_card_square.png, coloring_page.png
Drive: DISABLED (parent folder URL in manifest/caption)
WhatsApp: FAILED_CLOUD (2 recipients, token expired)
```

## Repetition gate

```text
Same sentence >2x: FAIL
Same paragraph >1x: FAIL
Same 8-word phrase >2x: FAIL
Forbidden closings: FAIL
Post-generation cleanup + re-check enabled
Story 001 unrelated pastime guard enabled
```

## Regenerate next story

```powershell
.\.venv\Scripts\Activate.ps1
python run_daily_story.py --mode prod
```

See [docs/01_DAILY_RUNBOOK.md](docs/01_DAILY_RUNBOOK.md) and [docs/08_GOOGLE_DRIVE_UPLOAD.md](docs/08_GOOGLE_DRIVE_UPLOAD.md).
