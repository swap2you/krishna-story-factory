# Private draft scheduler — operator notes (M4)

Loopback-only controls for **Knowledge / Vāṇī / audio-pilot private draft** work.
This is **not** the Story Factory MWF scheduler.

## Boundaries

| Allowed | Forbidden |
| --- | --- |
| View schedule status | Approve records |
| Choose queue (`knowledge`, `vani`, `audio_pilot`) | Merge / deploy / publish |
| Set idempotency key, retries, cost limits | Trigger story generation |
| Dry-run enqueue | Call `run_daily_story` / `generate-next` |
| Disable switch | Voice clone or auto-publish audio |

Story scheduler scripts (`scripts/install_mwf_story_task.ps1`, `scripts/run_daily_story_scheduled.ps1`) remain unchanged and separate.

## API (loopback, CSRF required for POST)

Base: `/api/v1/local/draft-scheduler`

- `GET /` — status, capabilities, forbidden list
- `POST /enable` · `POST /disable`
- `POST /configure` — queue, dry_run, retries, cost limits
- `POST /enqueue-dry-run` — `{ "idempotency_key": "..." }`
- `POST /approve|merge|deploy|publish|generate-story` — always **refused**

## Studio

Factory Studio (`/studio`) shows a **Private draft scheduler** panel that reads the status endpoint.
It cannot approve, merge, deploy, publish, or generate stories.

## Default posture

Disabled + dry-run. Paid providers off. Non-dry-run stays blocked unless cost limits explicitly allow paid work (still cannot publish).
