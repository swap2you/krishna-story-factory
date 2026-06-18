# Krishna Story Factory — Krishna Book Bedtime v1

Local Python automation for **daily Krishna Book bedtime story packages** (children ages 6–12).

- **CLI first** — `run_daily_story.py`
- **CSV source of truth** — queue, recipients, logs
- **Streamlit optional** — `dashboard.py`
- **WhatsApp Cloud v1** — individual template broadcast only (no groups)

Repository: [github.com/swap2you/krishna-story-factory](https://github.com/swap2you/krishna-story-factory)

## Start here

1. [docs/01_DAILY_RUNBOOK.md](docs/01_DAILY_RUNBOOK.md) — morning production steps
2. [docs/02_SETUP_AND_KEYS.md](docs/02_SETUP_AND_KEYS.md) — install and API keys
3. [docs/04_CONTENT_GUIDE_KRISHNA_BOOK.md](docs/04_CONTENT_GUIDE_KRISHNA_BOOK.md) — content rules and queue

## Core command

```powershell
python run_daily_story.py --mode prod --force
```

Test mode (no paid APIs):

```powershell
python run_daily_story.py --mode test --force
```

## Required outputs

```text
output/<chapter_no>_<slug>/
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

## Project layout

```text
input/series_plan.csv          # Krishna Book queue
input/whatsapp_recipients.csv  # opted-in parent phones
input/content_quality_rules.md
tracking/*.csv
docs/01-07_*.md
prompts/*.md
scripts/
krishna_story_factory/
```

## WhatsApp v1

- Template only (`hello_world` for Meta test)
- Broadcast to active opted-in CSV recipients
- No group sending
- Future: `daily_krishna_story` + package link

```powershell
python scripts/test_whatsapp_cloud.py
```

## Validation

```powershell
pytest -q
python run_daily_story.py --mode test --force
```

## Git safety

Never commit `.env`, `output/*`, logs, or secrets.
