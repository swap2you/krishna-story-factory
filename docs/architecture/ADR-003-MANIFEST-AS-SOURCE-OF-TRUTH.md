# ADR-003 — Manifest as Source of Truth

## Status

Accepted

## Context

Each story package ships `manifest.json` with chapter, slug, title, source references, quality, audio provenance, and package publication facts. Manual duplicate metadata would drift.

## Decision

- `manifest.json` remains authoritative for package facts.
- The catalog indexer reads manifests and normalizes a rebuildable SQLite read model.
- UI never invents story titles, source boundaries, or ślokas that contradict the package.
- Missing optional content (e.g. curated ślokas) uses explicit “not yet curated” placeholders.

## Consequences

- Reindex is always safe and idempotent.
- Portal schema versioning lives in the catalog, not in mutated package files.
