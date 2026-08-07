# ADR-007 — Additive package migration and rollback

## Status

Proposed (P01B)

## Decision

- Add packages under allowlisted content paths; never mutate private corpus originals in Git.  
- Validate via schema + `manifest.json` hashes.  
- SQLite FTS is derived — safe wipe/rebuild.  
- Rollback = git revert package commit + rebuild FTS.  
- Do not rewrite applied SQL migrations.  
- Out of scope: RELEASE_CONTENT, Story Factory, scheduler, Postgres cutover.

## Consequences

Low-risk pilot content ops; clear rollback story for G3+.
