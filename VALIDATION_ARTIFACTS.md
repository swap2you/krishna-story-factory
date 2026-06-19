# Validation Artifacts

Date: 2026-06-18  
Story: **002 — The Wedding and the Heavenly Voice**

## pytest

```text
45 passed
```

## Story 002 prod run

```json
{
  "status": "SUCCESS",
  "output_dir": "output/002_devaki-and-vasudeva-wedding",
  "quality_status": "PASS",
  "whatsapp_status": "FAILED_CLOUD",
  "drive_upload_status": "FAILED",
  "whatsapp_failure_reason": "TOKEN_EXPIRED"
}
```

## Word counts

| Metric | Value |
|--------|-------|
| Main Story | 1003 |
| Total story.md | 1150 |
| Audio script | 705 |
| MP3 bytes | 3,721,552 |

## Prompt quality

- `story_card_square_prompt.txt`: ultra-realistic 3D devotional cinematic, no modern objects, not crowded
- `coloring_page_prompt.txt`: centered composition, no cropping, thick outlines, white background, premium coloring-book style

## Drive upload

```text
Enabled in local .env but google.auth missing — pip install -r requirements.txt
```

## WhatsApp

```text
daily_krishna_story configured; send blocked by expired token
hello_world remains smoke test (SENT_SMOKE_TEST)
daily_krishna_story success → SENT_CLOUD
```

## Next story

```text
003_vasudevas-promise (pending)
```

## Regenerate

```powershell
.\.venv\Scripts\Activate.ps1
python run_daily_story.py --mode prod
```

See [docs/01_DAILY_RUNBOOK.md](docs/01_DAILY_RUNBOOK.md) and [docs/08_GOOGLE_DRIVE_UPLOAD.md](docs/08_GOOGLE_DRIVE_UPLOAD.md).
