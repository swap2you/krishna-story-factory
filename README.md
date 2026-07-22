# Krishna Story Factory — Krishna Book Bedtime v1

Local Python automation for **daily Krishna Book bedtime story packages** (children ages 6–12).

- **CLI first** — `run_daily_story.py`
- **CSV source of truth** — queue, recipients, logs
- **Streamlit optional** — `dashboard.py`
- **WhatsApp Cloud v1** — individual template broadcast only (no groups)

Repository: [github.com/swap2you/krishna-story-factory](https://github.com/swap2you/krishna-story-factory)

## Current operational state

- **Locked pilot packages:** Stories **001–006** (Story Format V2); senior devotee review **pending**
- **Released:** Stories **001–007** done on the live queue
- **Next pending:** Story **008** — The Meeting of Nanda and Vasudeva
- **Story 007 release:** [docs/releases/STORY_007_RELEASE.md](docs/releases/STORY_007_RELEASE.md)
- **Pilot tag:** `v1.0.0-pilot-stories-001-006` (001–006 baseline; not moved for Story 007)
- **Scheduler:** `Krishna Story Factory MWF` enabled (Mon/Wed/Fri 6:00 Eastern) — [docs/SCHEDULER.md](docs/SCHEDULER.md)
- **Messaging:** WhatsApp / Telegram disabled; Google Drive distribution
- Pilot 001–006 lock record: [docs/releases/PILOT_001_006_RELEASE_LOCK.md](docs/releases/PILOT_001_006_RELEASE_LOCK.md)
- Hash evidence: [docs/releases/PILOT_001_006_HASHES.json](docs/releases/PILOT_001_006_HASHES.json)

## Start here

1. [docs/PROJECT_SNAPSHOT_V1.md](docs/PROJECT_SNAPSHOT_V1.md) — canonical project snapshot
2. [prompts/KRISHNA_STORY_FACTORY_MASTER_AGENT.md](prompts/KRISHNA_STORY_FACTORY_MASTER_AGENT.md) — agent handoff rules
3. [docs/DAILY_OPERATIONS.md](docs/DAILY_OPERATIONS.md) — Windows inspect / generate / validate / rollback
4. [docs/SETUP_AND_CREDENTIALS.md](docs/SETUP_AND_CREDENTIALS.md) — install and API keys
5. [docs/CONTENT_STANDARD.md](docs/CONTENT_STANDARD.md) — Story Format V2 and content rules

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
