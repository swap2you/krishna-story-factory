# Agent Instructions

Krishna Book Bedtime v1 — lightweight local Python automation.

Rules:

1. CSV files are source of truth (`input/series_plan.csv`, `input/whatsapp_recipients.csv`).
2. CLI (`run_daily_story.py`) is source of truth.
3. Dashboard is optional.
4. Do not commit `.env`, output packages, or secrets.
5. Krishna Book sequence only — do not mix unrelated pastimes.
6. WhatsApp v1: individual CSV broadcast, templates only, no groups.
7. Preserve required output files including `line_art_prompt.txt`.

Before finishing:

```powershell
.\scripts\test_all.ps1
.\scripts\run_test.ps1 --force
```

Start with [docs/01_DAILY_RUNBOOK.md](docs/01_DAILY_RUNBOOK.md).
