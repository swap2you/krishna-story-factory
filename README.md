# Krishna Story Factory — Krishna Book Bedtime v1

Local Python automation for **daily Krishna Book bedtime story packages** (children ages 6–12), plus the Bhāva web portal.

- **CLI first** — `run_daily_story.py` / `.\scripts\create-next-bhava-story.ps1`
- **CSV source of truth** — queue, recipients, logs
- **Streamlit optional** — `dashboard.py`
- **Messaging** — WhatsApp / Telegram sending disabled; Google Drive after validation

Repository: [github.com/swap2you/krishna-story-factory](https://github.com/swap2you/krishna-story-factory)

## Current operational state

- **Public stories:** **001–020** complete (exact-eight packages)
- **Next pending / private:** Story **021** (not generated)
- **Scheduler:** `Krishna Story Factory MWF` — **Disabled** (installer defaults Disabled unless `-Enable`) — [docs/SCHEDULER.md](docs/SCHEDULER.md)
- **Stack:** Node **24** (`package.json` engines / Docker `node:24`); Python **3.14** (`.python-version` / Docker `python:3.14`)
- **Content tags:** `bhava-content-001-020-v2` exists; **v3** is the staging candidate being prepared (quality-completion)
- **Production:** remains on older web/content until later approval; do not promote v3 without explicit approval
- **Messaging:** WhatsApp / Telegram disabled; Google Drive distribution after local PASS
- Pilot 001–006 lock record: [docs/releases/PILOT_001_006_RELEASE_LOCK.md](docs/releases/PILOT_001_006_RELEASE_LOCK.md)

## Start here

1. [docs/PROJECT_SNAPSHOT_V1.md](docs/PROJECT_SNAPSHOT_V1.md) — canonical project snapshot
2. [prompts/KRISHNA_STORY_FACTORY_MASTER_AGENT.md](prompts/KRISHNA_STORY_FACTORY_MASTER_AGENT.md) — agent handoff rules
3. [docs/DAILY_OPERATIONS.md](docs/DAILY_OPERATIONS.md) — Windows inspect / generate / validate / rollback
4. [docs/SETUP_AND_CREDENTIALS.md](docs/SETUP_AND_CREDENTIALS.md) — install and API keys
5. [docs/CONTENT_STANDARD.md](docs/CONTENT_STANDARD.md) — Story Format V2 and content rules
6. [docs/deployment/BHAVA_PUSH_BUTTON_RELEASE_RUNBOOK.md](docs/deployment/BHAVA_PUSH_BUTTON_RELEASE_RUNBOOK.md) — staging/production release

## Supported runtimes

- **Python 3.14** — API Docker/CI and preferred local factory (`.python-version`). Bootstrap creates `.venv`; use repo wrappers, not a random global `python`.
- **Node 24** — web app (`engines.node`: `>=24 <25`, `.nvmrc`, Docker `node:24-bookworm-slim`).

## Core commands

```powershell
.\scripts\create-next-bhava-story.ps1   # next pending story (governed create-next path)
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

WhatsApp and Telegram sending are disabled; Google Drive upload is the package distribution path after local validation. Set `GOOGLE_DRIVE_FOLDER_URL` in local `.env` (see `.env.example`).

## Project layout

```text
input/series_plan.csv          # episode metadata
input/whatsapp_recipients.csv  # opted-in parent phones
tracking/                      # mutable CSV state (mostly gitignored)
docs/
scripts/
krishna_story_factory/
apps/web/                      # Bhāva Next.js portal (Node 24)
apps/api/                      # Bhāva API (Python 3.14)
```

## Git safety

Never commit `.env`, `output/*`, logs, credentials, or `.local_release_archive/`.
