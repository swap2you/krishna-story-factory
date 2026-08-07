# TEST_RESULTS — P01C (remediation for PR #70)

**Head (pre-push):** see final response for SHA after force-push  
**Date:** 2026-08-07  
**Environment:** Windows local — Node 24.19.0 · repo `.venv` Python 3.14  

## Local execution (this remediation)

| Suite | Result | Notes |
|---|---|---|
| `pytest` source-unit style (`not slow…`) | **PASS** (395) | Includes P01C Letter/A4, fonts, footer, loopback |
| `tests/test_knowledge_packages_p01c.py` | **PASS** | Vendored Noto + Unicode extract |
| `tests/test_publication_copyright.py` footer | **PASS** | Approved OD-08 footer; civil name absent |
| `npm run lint:web` | **PASS** | Next Link fix |
| `npm run typecheck:web` | **PASS** | |
| `npm run test:web` (vitest) | **PASS** (62) | Includes studio-guard loopback matrix |
| `npm run build:web` | **PASS** | |
| `docker compose … config` | **PASS** | |
| `docker build` API image | **NOT RUN locally** | Docker Desktop daemon unavailable on workstation |
| Playwright browser matrix (full CI) | **DEFERRED to GitHub CI** after push |
| axe + keyboard (P01C e2e specs) | **IMPLEMENTED**; full matrix via CI `browser-local` / public jobs |
| Secret/dependency scanning | **PASS previously on PR** (`production-security`); re-confirmed by CI after push |

## Prior PR #70 CI (pre-remediation) — FAILED

- CI run: https://github.com/swap2you/krishna-story-factory/actions/runs/31184911888  
- CI run (dup): https://github.com/swap2you/krishna-story-factory/actions/runs/31184907561  
- Production CI: https://github.com/swap2you/krishna-story-factory/actions/runs/31184910667  

Failures remediated: missing Devanāgarī font on Linux, obsolete footer assertion, `@next/next/no-html-link-for-pages`.

## Post-remediation CI

Update after force-push — see final response for new run URLs.
