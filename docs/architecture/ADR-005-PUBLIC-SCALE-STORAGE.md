# ADR-005 — Public Scale Storage Path

## Status

Accepted

## Context

Bhāva v1.1 runs as a local-first portal: catalog metadata in SQLite, locked eight-file packages under `output/`, and derived public-safe reader artifacts under `data/web-assets/`. Public hosting at scale will need Postgres, object storage, and a CDN without rewriting the product UX contracts.

Large binaries (narration audio, posters, PDFs, models) must never enter git.

## Decision

### Now (local operator workstation)

1. **Catalog:** SQLite at `data/catalog/bhava.sqlite` (or `BHAVA_CATALOG_DB`).
2. **Packages:** Filesystem under `output/<nnn>_*/` — exact eight-file contract; never mutated by the portal.
3. **Derived web assets:** Filesystem under `data/web-assets/<nnn>/` (`reader.*`, `sync.json`, `reflections.json`, `source_links.json`, `shlokas.json`, `web_manifest.json`). Built by `scripts/build_bhava_web_assets.py` or on-demand API fallback; gitignored except `.gitkeep`.
4. **Learner state:** Browser `localStorage` only (notes, resume) — no server collection.
5. **Media serving:** Local API streams package files from disk; Drive adapters remain optional for ops.

### Future (hosted public scale)

1. **Catalog:** PostgreSQL behind the same repository interfaces.
2. **Packages & media:** Object storage (S3-compatible or equivalent) with signed/CDN URLs.
3. **Web assets:** Object storage or CDN-backed JSON/text; rebuild jobs replace local CLI.
4. **CDN:** Edge cache for posters, audio, PDFs, and static reader text.
5. **Never git:** Narration MP3s, posters, activity PDFs, Krishna Book PDFs, TTS/voice models, or other large media.

### Scale triggers (when to leave pure local FS + SQLite)

Move when any of the following become true:

- Concurrent public readers outgrow a single workstation or need multi-region latency.
- Catalog write contention or backup/ops requires managed Postgres.
- Asset bandwidth / egress needs CDN fronting.
- Multiple operators need shared non-git asset storage.

Until then, keep local FS + SQLite + `data/web-assets/`.

## Consequences

- Clear upgrade path without changing public API shapes (`/stories`, `/reader`, `/sync`, `/shlokas`).
- Operators rebuild web assets deliberately (`BHAVA_AUTO_WEB_ASSETS` defaults false; Studio rebuild requires `BHAVA_FACTORY_ACTIONS_ENABLED`).
- Repository stays lightweight; CI never depends on committed media blobs.
