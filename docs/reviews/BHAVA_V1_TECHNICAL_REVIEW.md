# Bhāva v1 — Technical Review

## Scope

Local portal on `feature/bhava-portal-v1` around locked Stories 001–007.

## Findings

1. **Architecture** — Portal isolated under `apps/` + `packages/` + `data/catalog/`; factory package remains the generation authority.
2. **Public/private** — `/api/v1/local/*` requires loopback + CSRF; Studio UI defaults actions off.
3. **Factory preservation** — Hash and queue guards in `tests/portal` lock Stories 001–007 and queue fingerprint.
4. **Test integrity** — Existing pytest suite remains; portal tests avoid paid providers.

## Residual risks (non-blocking)

- Windows npm workspace installs can race if multiple agents run `npm install` concurrently.
- SWC optional dependency must be present for Next production builds on win32.

## Verdict

Technically acceptable for local v1 acceptance pending browser inspection evidence.
