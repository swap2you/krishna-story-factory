# Validation Artifacts

Date: 2026-06-18

## Commands

```powershell
pytest -q
python run_daily_story.py --mode test --force
python scripts/test_whatsapp_cloud.py
python run_daily_story.py --mode prod --force
```

## Pytest

```text
11 passed
```

## Latest prod output path (local)

```text
output/001_the-earth-prays-for-krishna/
```

## Required file checklist

```text
story.md
audio_script.txt
whatsapp_caption.txt
activity_sheet.pdf
story_card.png
image_prompt.txt
line_art_prompt.txt
parent_notes.md
manifest.json
narration.mp3
```

## Manifest source fields (prod run)

```text
story_source: openai
audio_source: elevenlabs
image_source: openai or fallback
```

Also verified: `source_reference`, `library_id`, `age_range`, `generated_at`, `project`

## Quality result

```text
PASS
```

## WhatsApp result

```text
SENT_CLOUD — hello_world to 1 active recipient (Swapnil Test)
Wife Test skipped (REPLACE placeholder phone)
```

## Next queue row

```text
002_devaki-and-vasudeva-wedding (pending)
```

## Regenerate

```powershell
.\.venv\Scripts\Activate.ps1
python run_daily_story.py --mode prod --force
```

See [docs/01_DAILY_RUNBOOK.md](docs/01_DAILY_RUNBOOK.md).
