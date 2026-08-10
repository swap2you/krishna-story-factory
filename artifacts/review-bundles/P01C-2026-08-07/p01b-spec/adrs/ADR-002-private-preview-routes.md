# ADR-002 — Private-preview routes under Studio

## Status

Proposed (P01B) — OD-09

## Context

Pilot must not be public (P1-F09, D06). Middleware/Caddy already deny `/studio*`.

## Decision

Serve Phase 1 preview at `/studio/knowledge/preview/[slug]` (or equivalent under `/studio`). Do not publish pilot bodies on `/knowledge/prayers/[slug]`.

## Consequences

Free edge protection; Studio IA owns preview; public prayers stubs remain honest empty until later publication gate.
