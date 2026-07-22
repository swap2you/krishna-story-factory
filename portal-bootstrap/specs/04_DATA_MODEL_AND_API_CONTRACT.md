# Data Model and API Contract

## Primary entities

- Collection
- Work
- Volume
- Canto
- Chapter
- PassageBoundary
- Story
- StoryVersion
- Asset
- Activity
- Shloka
- SourceReference
- ReviewDecision
- Publication
- Playlist
- Bookmark
- LocalNote
- QueueItem
- JobRun
- ProviderUsage
- DrivePublication
- ContactProfile
- BlogPost

## Manifest principle

The existing `manifest.json` remains authoritative for package facts. The catalog indexes and normalizes manifests; it does not replace them.

## Public read API

```text
GET /api/v1/collections
GET /api/v1/collections/{slug}
GET /api/v1/stories
GET /api/v1/stories/{story_no}
GET /api/v1/stories/{story_no}/assets
GET /api/v1/stories/{story_no}/source
GET /api/v1/stories/{story_no}/shlokas
GET /api/v1/search
GET /api/v1/health
```

## Local-only factory API

```text
GET  /api/v1/local/status
GET  /api/v1/local/queue
GET  /api/v1/local/runs
POST /api/v1/local/preflight
POST /api/v1/local/generate-next
POST /api/v1/local/drive/readback
GET  /api/v1/local/scheduler
POST /api/v1/local/scheduler/enable
POST /api/v1/local/scheduler/disable
```

Controls:
- bind to `127.0.0.1`
- CSRF protection
- origin allowlist
- explicit operation allowlist
- one active production run
- no arbitrary command or path input
- structured audit records
