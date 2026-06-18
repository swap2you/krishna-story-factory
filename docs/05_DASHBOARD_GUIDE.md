# Dashboard Guide

Optional Streamlit UI. CLI remains source of truth.

## Run

```powershell
python -m streamlit run dashboard.py
```

Or:

```powershell
.\scripts\run_dashboard.ps1
```

## Shows

- Project: Krishna Book Bedtime
- Library: Krishna Book
- Next pending story
- Queue table
- Generated outputs
- Story, send, and quality logs
- Sender mode and model flags from `.env`

## Note

Do not use the dashboard as the scheduler. Use `scripts/run_daily_story_windows.ps1` for automation.
