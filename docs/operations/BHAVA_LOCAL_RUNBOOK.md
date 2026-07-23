# Bhāva Local Runbook

## Prerequisites

- Python `.venv` (existing factory bootstrap)
- `npm install` at repository root (Node 20+)
- Stories 001–007 present under `output/`

## Start

```powershell
cd C:\Development\Workspace\DevotionalRepo\krishna-story-factory
.\scripts\start_bhava_local.ps1
```

- Web: http://localhost:3000
- API: http://127.0.0.1:8000/api/v1/health
- Studio: http://localhost:3000/studio (loopback API only)

## Stop

```powershell
.\scripts\stop_bhava_local.ps1
```

## Reindex catalog

```powershell
.\scripts\reindex_bhava_catalog.ps1
```

## Test

```powershell
.\scripts\test_bhava.ps1
```

## Web assets

```powershell
.\.venv\Scripts\python.exe scripts\build_bhava_web_assets.py
```

Writes derived reader files under `data/web-assets/<nnn>/` (gitignored). Studio can rebuild one story via `POST /api/v1/local/rebuild-web-assets/{story_no}` only when factory actions are enabled.

## Safety

- `BHAVA_FACTORY_ACTIONS_ENABLED` defaults to false — Studio cannot generate Story 008 or rebuild web assets.
- `BHAVA_AUTO_WEB_ASSETS` defaults to false — catalog refresh does not auto-build web assets unless explicitly set.
- Do not expose `/api/v1/local/*` publicly.
- Notes/bookmarks stay in browser localStorage.
