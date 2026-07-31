# Bhāva Platform Modernization Report

**Branch:** `chore/platform-modernization-and-release-automation`  
**Base:** `origin/develop` @ `ab37275`  
**Production left untouched during implementation:** SHA `19af3c4…`, content `bhava-content-001-009-v1`  
**Date:** 2026-07-31

## Objectives completed in this change set

1. Technology inventory + runtime support policy  
2. GitHub Actions upgraded off Node 20 action runtimes (`checkout@v6`, `setup-node@v6`, `setup-python@v6`, `upload-artifact@v6`)  
3. Application targets: Node **24** LTS, Python **3.14** (API Docker + CI)  
4. Production smoke environment-aware indexing (staging noindex; production must not be globally noindex)  
5. TLS/ACME readiness script with diagnostics; production workflow separates TLS wait from app smoke; rollback only on app smoke failure; first-release rollback messaging  
6. Composite actions: pinned SSH, smoke-with-tls helper  
7. Push-button `scripts/release-bhava.ps1` (+ bash status/dry-run)  
8. Docs: inventory, support policy, push-button runbook, command reference, cleanup policy  
9. Ops retention manifest + archive layout under private MyPilotDropbox  

## Not done in this PR (gated)

- Merge to develop / staging deploy green confirmation (requires CI + workflow run)  
- Production deploy of modernization SHA (requires staging PASS + env approval)  
- CoWork UAT decision (human)  
- Story 010 / Story 011 / scheduler enablement (explicitly out of scope)  
- Local Docker image builds (Docker Desktop daemon unavailable on operator laptop during implementation)  

## Compatibility evidence

- Python 3.14.6: hashed API lock install OK; factory requirements install OK; `test_public_production_boundary` 6 passed  
- SQLite via Python: 3.50.4  
- Node 24: pinned in engines/Docker/CI; local laptop still on 22.23.1 until NVM upgrade — CI is source of truth for Node 24 proof  

## Follow-ups

1. After merge to develop: staging deploy must create/update `previous` when replacing staging current  
2. Next production deploy after this modernization should populate `/opt/bhava/releases/production/previous`  
3. Optional: pin official Actions to immutable commit SHAs  
4. Address Starlette TestClient `httpx2` deprecation warning when FastAPI updates guidance  
