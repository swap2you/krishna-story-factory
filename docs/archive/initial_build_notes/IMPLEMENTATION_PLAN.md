# Implementation Plan

## Phase 1 — Validate current base

Commands:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pytest -q
python run_daily_story.py --mode test --force
```

Expected result:

- Tests pass.
- One output folder is created.
- All nine required files exist.
- No paid APIs are called in test mode.

## Phase 2 — Configure API keys

Create `.env` from `.env.example`.

```powershell
copy .env.example .env
```

Fill only the services you plan to use.

Minimum real generation:

```env
OPENAI_TEXT_ENABLED=true
OPENAI_API_KEY=...
```

Full package:

```env
OPENAI_TEXT_ENABLED=true
OPENAI_IMAGE_ENABLED=true
ELEVENLABS_ENABLED=true
```

Full delivery through WhatsApp Cloud:

```env
WHATSAPP_SEND_ENABLED=true
WHATSAPP_SENDER_TYPE=cloud
```

## Phase 3 — One-week private test

Recommended sender for private test:

```env
WHATSAPP_SEND_ENABLED=true
WHATSAPP_SENDER_TYPE=web_test
```

This creates a local outbox. You manually forward to your test WhatsApp group. This avoids fragile browser automation during the first week.

## Phase 4 — Production delivery

Preferred options:

1. WhatsApp Business Cloud API to configured recipients.
2. Telegram channel/group if WhatsApp API restrictions become annoying.
3. Manual/staged outbox if API approval is not ready.

## Phase 5 — Dashboard

Run:

```powershell
streamlit run dashboard.py
```

Use dashboard to edit queue, check logs, and trigger runs. Do not use dashboard as the scheduler.

## Phase 6 — Daily automation

Use Windows Task Scheduler with `scripts/run_daily_story_windows.ps1`.

Do not run a server just for daily automation.
