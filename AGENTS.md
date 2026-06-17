# Agent Instructions

This repository is intentionally lightweight.

Rules for coding agents:

1. Do not use Notion.
2. Do not add a database unless explicitly requested.
3. Keep CSV files as the source of truth.
4. Keep CLI as the source of truth.
5. Dashboard must call CLI or edit CSV only.
6. Do not hardcode secrets.
7. Do not commit `.env`.
8. Do not build unsafe WhatsApp Web scraping automation.
9. Use tests and deterministic test mode.
10. Preserve all nine required output files.

Before finishing, run:

```bash
pytest -q
python run_daily_story.py --mode test --force
```
