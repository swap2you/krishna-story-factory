# Bhāva V1.7.3 — Release Candidate

## Identity

| Field | Value |
|-------|-------|
| Starting tip | `867182405ca376ccdde6be1b80ca5c36c2b64aca` |
| Product SHA | `aeb5104b8780b5a7a267db609060bfd870228a62` |
| Evidence / docs tip | fill after evidence commit |
| Branch | `feature/bhava-portal-v1` |

Resolve final tip live with `git rev-parse HEAD` / `origin/feature/bhava-portal-v1` (do not trust hard-coded obsolete tips).

## Why V1.7.3

Correct future Krishna Book Chapters 7–8 sequencing before Story 010 generation: cart-breaking becomes next; Tṛṇāvarta and both universal-form manifestations stay separate; Garga, crawling, and butter complaints are mapped. Non-skipping gate strengthened.

## Safety

| Item | State |
|------|-------|
| Stories 001–009 | Unchanged (`BHAVA_V1_7_3_SAFETY_BASELINE.json`) |
| Story 010 package | Absent |
| Next pending | `baby-krishna-breaks-the-cart` |
| Providers / Drive / scheduler | Not invoked |

## Tests (product SHA)

Evidence: `docs/product/uat/v1.7.3/runs/20260727-163324-aeb5104/`

| Suite | Result |
|-------|--------|
| pytest `-m "not slow"` | **434 passed**, 5 deselected, 0 failed |
| Playwright (5 projects) | **415 passed**, 10 skipped, 0 failed |
| lint / typecheck / unit / build | exit 0 |

## Verdict

**READY FOR FINAL COWORK UAT**
