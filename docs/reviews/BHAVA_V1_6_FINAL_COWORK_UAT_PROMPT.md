# Bhāva V1.6 — Final CoWork UAT Prompt

Independent review only. Do not modify code, stories, queue, scheduler generation mode, Drive, or create a PR.

## Under test

- Branch: `feature/bhava-portal-v1`
- Confirm local SHA == origin
- Instance: `cursor-v16` (`.bhava/instances/cursor-v16/runtime.json`)
- Evidence: `docs/product/uat/v1.6/runs/**`

## Must verify

1. DEF-CONTRAST-01 closed on `/` CORE AREAS at required viewports
2. Page-by-page visual scan per `PAGE_SECTION_AUDIT.md`
3. Story 008 all tabs
4. Scheduler registration + safe validation (no Story 009)
5. Drive reconciliation honesty
6. WebKit evidence + Safari checklist boundary
7. Lighthouse baseline
8. Full SHA-bound tests
9. Stories 001–008 unchanged; Story 009 hidden

Write report to `docs/reviews/BHAVA_V1_6_COWORK_FINAL_UAT.md`.
