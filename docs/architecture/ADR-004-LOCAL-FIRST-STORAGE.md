# ADR-004 — Local-First Storage

## Status

Accepted

## Context

v1 must run on an operator workstation without cloud dependencies. Later public hosting needs PostgreSQL and object storage without a rewrite.

## Decision

1. Catalog: SQLite locally; repository interfaces remain PostgreSQL-ready.
2. Assets: filesystem paths under `output/` for local; Drive/object-storage adapters defined but write paths unused in this build.
3. Learner state (notes, bookmarks, resume, playlists): browser `localStorage` only — no server collection in v1.
4. No analytics, ads, or child tracking by default.

## Consequences

- Instant local demos and offline-friendly PWA shell.
- Clear upgrade path to hosted `bhava.me` without changing public UX contracts.
