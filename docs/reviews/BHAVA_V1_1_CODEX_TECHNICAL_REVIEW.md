# Bhāva V1.1 — Codex Technical Review

**Branch:** `feature/bhava-portal-v1`  
**Reviewer role:** technical architecture / security / package protection  
**Date:** 2026-07-23

## Scope reviewed

Portal API (`apps/api/bhava_api`), web app (`apps/web`), derived web-asset pipeline (`data/web-assets` gitignored), CI, multi-instance runtime, factory safety baseline.

## Findings

### Strengths

- Exact eight-file packages remain authoritative; web derivatives live outside `output/`.
- Public reader path uses parser + `reader.md` / `reader.txt`, not raw `story.md`.
- Studio actions stay loopback + CSRF gated; factory real actions remain disabled by default.
- Catalog freshness reconciles without mutating packages.
- CI covers Python portal/factory tests, web lint/typecheck/test/build, Playwright Chromium + Firefox/WebKit/mobile matrix on fixtures.

### Risks / residual items (non-blocking)

1. Full-repo pytest on Windows can fail when fixtures copy `node_modules` (MAX_PATH). Portal + safety baseline suites pass independently.
2. Sentence alignment remains `needs_alignment` for Stories 001–007 (schemas/UI ready; timings not fabricated).
3. Ślokas remain pending by design until curated paste with citations.
4. Public-scale storage ADR documents future Postgres/object storage but no migration was performed (correct for V1.1).

### Security notes

- `KrishnaBook.pdf` is gitignored and not served.
- Path traversal blocked for package assets allowlist.
- No paid provider calls introduced in portal paths.

## Verdict

**PASS for release candidate** with residual research items above. No package-mutation or public-Studio blockers found.
