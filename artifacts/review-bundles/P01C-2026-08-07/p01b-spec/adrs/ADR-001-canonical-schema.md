# ADR-001 — Canonical knowledge record package schema

## Status

Proposed (P01B)

## Context

Schemas are fragmented across roadmap JSON, KnowledgeMeta, prayer_item/shloka contracts, and FastAPI dicts (P01A SCHEMA_DRIFT).

## Decision

One versioned package (`record.json` + companions per CONTENT_MODEL.md) is the sole content truth for Phase 1 prayer pages. Other layers are generated/validated adapters.

## Consequences

- Clear hash parity for web/PDF/DOCX  
- Migration work to write adapters  
- Legacy contracts remain for stories until separate ADR
