# Krishna Story Factory — Krishna Book Bedtime v1

Local Python automation for **daily Krishna Book bedtime story packages** (children ages 6–12).

- **CLI first** — `run_daily_story.py`
- **CSV source of truth** — queue, recipients, logs
- **Streamlit optional** — `dashboard.py`
- **WhatsApp Cloud v1** — individual template broadcast only (no groups)

Repository: [github.com/swap2you/krishna-story-factory](https://github.com/swap2you/krishna-story-factory)

## Current pilot lock

- **Locked packages:** Stories **001–006** (Story Format V2)
- **Next pending:** Story **007**
- **Scheduler:** disabled pending senior devotee review
- Release record: [docs/releases/PILOT_001_006_RELEASE_LOCK.md](docs/releases/PILOT_001_006_RELEASE_LOCK.md)

## Start here

1. [docs/01_DAILY_RUNBOOK.md](docs/01_DAILY_RUNBOOK.md) — morning production steps
2. [docs/02_SETUP_AND_KEYS.md](docs/02_SETUP_AND_KEYS.md) — install and API keys
3. [docs/04_CONTENT_GUIDE_KRISHNA_BOOK.md](docs/04_CONTENT_GUIDE_KRISHNA_BOOK.md) — content rules and queue

## Supported Python

Python 3.12 is the supported runtime on Windows and Linux. Run `scripts/bootstrap.ps1`
once, then use the repository wrappers below. The project never relies on whichever
global `python` happens to be on `PATH`.

## Core commands

```powershell
.\scripts\run_prod.ps1
.\scripts\run_test.ps1 --force
.\scripts\test_all.ps1
```

Test mode must not call paid APIs.

## Exact eight-file package contract

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

WhatsApp and Telegram sending are disabled for v1 delivery; Google Drive upload is the
package distribution path. Set `GOOGLE_DRIVE_FOLDER_URL` in local `.env` (see `.env.example`).

## Project layout

```text
input/series_plan.csv          # episode metadata
input/whatsapp_recipients.csv  # opted-in parent phones
tracking/                      # mutable CSV state (mostly gitignored)
docs/
scripts/
krishna_story_factory/
```

## Git safety

Never commit `.env`, `output/*`, logs, credentials, or `.local_release_archive/`.
