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

## Supported Python

Python 3.12 is the supported runtime on Windows and Linux. Run `scripts/bootstrap.ps1`
once, then use the repository wrappers below. The project never relies on whichever
global `python` happens to be on `PATH`.

## Core command

```powershell
.\scripts\run_prod.ps1
```

Test mode (no paid APIs):

```powershell
.\scripts\run_test.ps1 --force
```

## Required outputs

```text
output/<chapter_no>_<slug>/
  story.md
  narration.mp3
  story_poster.png
  coloring_page.png
  simple_coloring_page.png
  activity_sheet.pdf
  whatsapp_caption.txt
  manifest.json
```

The adaptive activity sheet is a validated 2–4 page ActivityPack PDF (1 page only for
simple types). See [docs/11_ACTIVITY_ENGINE_V2.md](docs/11_ACTIVITY_ENGINE_V2.md).

WhatsApp and Telegram sending are disabled for v1 delivery; Google Drive upload is the
package distribution path.

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
.\scripts\test_all.ps1
.\scripts\run_test.ps1 --force
```

## Git safety

Never commit `.env`, `output/*`, logs, or secrets.
