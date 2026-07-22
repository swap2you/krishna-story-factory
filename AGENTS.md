# Agent Instructions

Krishna Book Bedtime v1 — lightweight local Python automation.

Canonical reading order:

1. [README.md](README.md)  
2. [docs/PROJECT_SNAPSHOT_V1.md](docs/PROJECT_SNAPSHOT_V1.md)  
3. [prompts/KRISHNA_STORY_FACTORY_MASTER_AGENT.md](prompts/KRISHNA_STORY_FACTORY_MASTER_AGENT.md)  
4. [docs/CONTENT_STANDARD.md](docs/CONTENT_STANDARD.md)

Rules:

1. CSV files are source of truth for plans (`input/series_plan.csv`) and runtime queue (`tracking/queue_state.csv`).  
2. CLI (`run_daily_story.py --mode prod|test`) is source of truth; wrappers: `scripts/run_prod.ps1`, `scripts/run_test.ps1`.  
3. Dashboard is optional.  
4. Do not commit `.env`, output packages, credentials, or secrets.  
5. Krishna Book sequence only — never skip; one pending story per run.  
6. Exact **eight-file** package only: `story.md`, `narration.mp3`, `story_poster.png`, `coloring_page.png`, `simple_coloring_page.png`, `activity_sheet.pdf`, `whatsapp_caption.txt`, `manifest.json`. (`line_art_prompt.txt` is not a required final output.)  
7. TTS: ElevenLabs Renee primary, OpenAI Marin fallback. Drive via `GOOGLE_DRIVE_UPLOAD_ENABLED`. WhatsApp/Telegram disabled for the pilot.  
8. Never modify locked Stories **001–006** without explicit approval. Senior devotee review pending.  
9. Scheduler: `Krishna Story Factory MWF` (Mon/Wed/Fri 6:00) via `scripts/install_mwf_story_task.ps1` and `scripts/run_daily_story_scheduled.ps1`.

Before finishing:

```powershell
.\scripts\test_all.ps1
.\scripts\run_test.ps1 --force
```

Ops: [docs/DAILY_OPERATIONS.md](docs/DAILY_OPERATIONS.md). Release: [docs/RELEASE_AND_ROLLBACK.md](docs/RELEASE_AND_ROLLBACK.md).
