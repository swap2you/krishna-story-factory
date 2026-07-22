# Architecture

Lightweight local Python system. No Docker, FastAPI, Postgres, Redis, or Celery.

```text
CSV plans + queue
        │
        ▼
run_daily_story.py  (--mode prod|test)
        │
        ▼
krishna_story_factory.pipeline
  ├─ story generation (OpenAI text) → Story Format V2
  ├─ source guards
  ├─ TTS (ElevenLabs Renee → OpenAI Marin)
  ├─ images (poster, coloring, simple coloring)
  ├─ Activity Engine V2 → activity_sheet.pdf
  ├─ caption + manifest
  ├─ staging → validate exact eight → atomic promote
  └─ Google Drive upload + readback (optional via env)
        │
        ▼
tracking/*.csv  +  output/<chapter>_<slug>/
```

| Layer | Responsibility |
| --- | --- |
| `input/` | Static series metadata (tracked) |
| `tracking/` | Runtime queue and logs (gitignored) |
| `krishna_story_factory/` | Domain logic |
| `scripts/*.ps1` | Windows wrappers, bootstrap, MWF scheduler |
| `dashboard.py` | Optional Streamlit UI only |
| `docs/` + `prompts/` | Canonical ops + generation prompts |

One story per successful prod run. Messaging senders exist in code but are disabled for the pilot; Drive is the distribution path.
