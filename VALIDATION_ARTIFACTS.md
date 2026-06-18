# Validation Artifacts

Date: 2026-06-18

## Commands

```powershell
pytest -q
python run_daily_story.py --mode test --force
python scripts/check_audio_quality.py output\004_prayers-in-the-prison\narration.mp3
python scripts/test_whatsapp_cloud.py
python scripts/test_whatsapp_daily_template.py
python scripts/test_google_drive_upload.ps1
```

## Pytest

```text
35 passed
```

## Repetition gate

```text
Padding loops removed from story_generator
Quality FAIL on repeated closings, paragraphs, and filler phrases
Post-generation cleanup runs before quality checks
```

## Latest test run

```text
output/005_krishna-appears/
quality: PASS
drive_upload_status: DISABLED
package_link: parent Google Drive folder URL
whatsapp_template: from local .env (use daily_krishna_story for prod)
```

## Drive upload mode

```text
GOOGLE_DRIVE_UPLOAD_ENABLED=false (default)
Set true + credentials/google_drive_oauth_client.json for API upload
Or set GOOGLE_DRIVE_LOCAL_SYNC_ROOT for local sync copy
See docs/08_GOOGLE_DRIVE_UPLOAD.md
```

## WhatsApp template mode

```text
hello_world = smoke test only (SENT_SMOKE_TEST in prod)
daily_krishna_story = real parent message with title + package link
Set WHATSAPP_TEMPLATE_NAME=daily_krishna_story in local .env
```

## Regenerate

```powershell
.\.venv\Scripts\Activate.ps1
python run_daily_story.py --mode prod --force
```

See [docs/01_DAILY_RUNBOOK.md](docs/01_DAILY_RUNBOOK.md) and [docs/08_GOOGLE_DRIVE_UPLOAD.md](docs/08_GOOGLE_DRIVE_UPLOAD.md).
