# Validation Artifacts

Date: 2026-06-18

## Commands

```powershell
pytest -q
python run_daily_story.py --mode test --force
python run_daily_story.py --mode prod --force
.\scripts\diagnose_whatsapp_failure.ps1
```

## Pytest

```text
28 passed
```

## CSV queue checks

```text
series_plan.csv: 10 rows
001 done, 002 done after prod validation, 003–010 pending
next pending: 003_vasudevas-promise
whatsapp_recipients.csv: 2 rows; Wife Test skipped (REPLACE phone)
```

## Latest prod output path (local)

```text
output/002_devaki-and-vasudeva-wedding/
```

## Required file checklist

```text
story.md
audio_script.txt (no [pause]; uses <break time="..."/>)
whatsapp_caption.txt (reply here, today, no group)
activity_sheet.pdf (3 pages, word-search grid)
story_card.png
story_card_square.png
coloring_page.png
coloring_page_prompt.txt
hero_image_prompt.txt
story_card_square_prompt.txt
parent_notes.md
manifest.json
narration.mp3 (> 500 KB in prod)
```

## Prod run summary

```text
quality: PASS
story_source: openai
audio_source: elevenlabs
image_source: openai
activity: word_search_answer_key in manifest.json
package_link: (empty — add GOOGLE_DRIVE_FOLDER_URL to local .env)
whatsapp_status: FAILED_CLOUD
whatsapp_failure_reason: TOKEN_EXPIRED
```

## WhatsApp diagnostics

```powershell
Get-Content tracking\send_log.csv -Tail 10
.\scripts\diagnose_whatsapp_failure.ps1
```

Latest send_log detail includes `reason=TOKEN_EXPIRED | template=hello_world | HTTP 401`.

## Regenerate

```powershell
.\.venv\Scripts\Activate.ps1
python run_daily_story.py --mode prod --force
```

See [docs/01_DAILY_RUNBOOK.md](docs/01_DAILY_RUNBOOK.md).
