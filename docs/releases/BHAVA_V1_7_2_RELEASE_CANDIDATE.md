# Bhāva V1.7.2 — Release Candidate

## Identity

| Field | Value |
|-------|-------|
| Starting branch SHA | `208841458a0605a7af762e9421c76571bd2303d5` |
| Product SHA | `a1d277b0a55ab85b28c6e8a8a8f330a966b1b085` |
| Evidence / docs tip | 7035fcd69c9dcf6c5490c14fe581b3e9fef601c2 |
| Branch | `feature/bhava-portal-v1` |

## Why V1.7.2

Public Story 009 claimed *Krishna Book* Chapter 6 but narrated later material (universe-in-mouth) and treated Pūtanā as already past. V1.7.2 replaces Story 009 with the full Pūtanā pastime and adds a hard non-skipping coverage ledger/gate so major pastimes cannot be skipped, reduced to recap, or replaced by later-chapter events.

## Stories

| Item | State |
|------|-------|
| 001–008 | Unchanged (SHA-locked vs `BHAVA_V1_7_2_SAFETY_BASELINE.json`) |
| 009 | Repaired exact-eight Pūtanā package; publishable true; quality PASS |
| 010 | Tṛṇāvarta remains pending / hidden (not generated) |
| Queue | 009 `done`, 010 `pending` |

## Canonical guardrails

- Ledger: `data/series/krishna_book_coverage.yaml` (Chapters 1–10)  
- Gate + regressions: coverage module + `tests/test_coverage_non_skipping.py`  
- Audit: `docs/editorial/BHAVA_STORIES_001_009_CANONICAL_COVERAGE_AUDIT.md`

## Drive / portal

- Public folder: `009_putana-krishnas-astonishing-mercy`  
- Drive folder id: `1tz3RjfAY3HRLNng_Gbd43_nbPTTDkKVj` (exact-eight uploaded)  
- Catalog: 001–009; instance `cursor-v172` at `http://127.0.0.1:3003`

## Testing (exact product SHA)

Evidence: `docs/product/uat/v1.7.2/runs/20260727-152549-a1d277b/`

| Suite | Result |
|-------|--------|
| pytest `-m "not slow"` | **424 passed**, 5 deselected, 0 failed |
| Playwright (5 projects) | **415 passed**, 10 skipped, 0 failed |
| lint / typecheck / unit / build | exit 0 |

## Verdict

**READY FOR FINAL COWORK UAT**
