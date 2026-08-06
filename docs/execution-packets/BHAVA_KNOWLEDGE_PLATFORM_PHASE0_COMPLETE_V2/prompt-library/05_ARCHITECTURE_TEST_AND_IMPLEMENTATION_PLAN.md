---
id: PL-05
version: 1.0.0
phase: P01B
preconditions: UX/content requirements complete
---

# Architecture, tests, and implementation plan

Design the smallest change that reuses the current stack.

- one versioned canonical record/block schema; generated/validated TypeScript/Python/SQL adapters rather than competing models;
- source dossier and asset manifest boundaries; immutable private originals;
- server-rendered core with small client islands for lens/focus/motion;
- age-lens URL/state behavior and no-account/on-device preference;
- Studio lifecycle/count visibility and public filter enforcement;
- image optimization, alt/long-description model, asset crop/rights/versioning;
- Unicode normalization, font licensing/embedding, glyph fixtures;
- PDF/DOCX technical spike and chosen strategy after evidence;
- versioned migrations/backfill/rollback; no rewrite of applied migrations;
- route/API/auth/search/sitemap/privacy/security boundaries;
- threat model and dependency/license review;
- implementation allowlist, file ownership, commit plan, test matrix, rollback.

Write ADRs for material choices and explicitly reject unnecessary framework migration, live authoring-tool embeds, duplicate age content, and public corpus access.

## Outputs

`ARCHITECTURE.md`, ADRs, `IMPLEMENTATION_PLAN.md`, `TEST_AND_SECURITY_PLAN.md`, migration/rollback plan, path ownership map, proposed branch name/base SHA, cost/provider policy, and G3 build-authorization request.

