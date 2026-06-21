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
python run_daily_story.py --mode prod
```

Test mode (no paid APIs):

```powershell
python run_daily_story.py --mode test --force
```

## Required outputs

```text
output/<chapter_no>_<slug>/
  story.md
  narration.mp3
  story_poster.png
  coloring_page.png
  activity_sheet.pdf
  whatsapp_caption.txt
  manifest.json
```

The adaptive activity sheet is a validated one- or two-page PDF tied to the selected pastime.

## Google Drive package link

Set `GOOGLE_DRIVE_FOLDER_URL` in local `.env` (see `.env.example`). Caption and `daily_krishna_story` template use this link.

## Project layout

```text
input/krishna_book_master_plan.csv # complete static editorial plan
input/series_plan.csv          # CLI-ready static episode metadata
input/whatsapp_recipients.csv  # opted-in parent phones
input/content_quality_rules.md
tracking/queue_state.csv       # ignored mutable execution state
tracking/templates/*.csv      # tracked header-only examples
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
