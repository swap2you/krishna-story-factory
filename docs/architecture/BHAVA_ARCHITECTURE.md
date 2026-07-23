# Bhāva Portal — Architecture Overview

## Shape

Lightweight monorepo inside the existing Krishna Story Factory repository:

```text
apps/web          Next.js App Router (public + teacher + studio UI)
apps/api          FastAPI catalog + loopback factory gateway
packages/ui       Bhāva design system (CSS variables + primitives)
packages/contracts Shared Pydantic / TS types
packages/content  Markdown sanitize + content helpers
data/catalog      Rebuildable SQLite index
Canonical product/architecture docs live under `docs/`. Bootstrap scaffolding is not part of the runtime tree.
```

## Boundaries

| Layer | Responsibility |
| --- | --- |
| Factory (locked) | Generate eight-file packages, queue, Drive, scheduler |
| Catalog indexer | Read manifests + assets from filesystem; write SQLite read model |
| Public API | Read-only collections, stories, assets, search, health |
| Local API | Status, queue view, demo/disabled generate, scheduler view — bind `127.0.0.1` |
| Web | Presentation, device-local notes/bookmarks, PWA shell |

## Data flow

1. Operator (or `reindex` script) scans `output/<chapter>_<slug>/manifest.json`.
2. Indexer normalizes story, source, assets, publication facts into SQLite.
3. Public UI fetches `/api/v1/*` and streams media via asset URLs that map to local files.
4. Factory Studio calls `/api/v1/local/*` only from loopback with CSRF + origin allowlist.
5. Real generation, when enabled by env flag, shells to the existing `run_daily_story.py` entry — never a reimplementation.

## Storage adapters

- **FilesystemCatalogStore** (v1 default)
- **DrivePublicationAdapter** (interface + readback stub; no write in portal build)
- **ObjectStorageAdapter** (future interface)

## Security

- Public build never embeds factory control URLs for remote hosts.
- Local factory routes: loopback bind, CSRF token, origin allowlist, operation allowlist, one active run, redacted secrets, audit log.
- Notes/bookmarks: `localStorage` only.

## Deployment

- Local: web `:3000`, API `127.0.0.1:8000`, SQLite under `data/catalog/`.
- Public later: `bhava.me` without factory endpoints; PostgreSQL-ready repositories.

See ADRs 001–004 and `BHAVA_TECH_BASELINE.md`.
