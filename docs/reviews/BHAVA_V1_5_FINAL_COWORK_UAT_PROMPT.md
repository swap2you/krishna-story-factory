# Bhāva V1.5 — Final CoWork UAT Prompt

Work only as independent reviewer. Do not modify application code, stories, queue, scheduler, Drive, or create a PR.

## Under test

- Branch: `feature/bhava-portal-v1`
- Confirm SHA equals `origin/feature/bhava-portal-v1` (matrix tested at `fe57b46`; include follow-up validation commit if present)
- Instance: `cursor-v15` (use `.bhava/instances/cursor-v15/runtime.json` URLs)
- Evidence: `docs/product/uat/v1.5/runs/20260724-181701-fe57b46/`

## Must verify

1. Full route/link click-through including Learning menu
2. All story tabs on 001–008
3. Story 008 exact-eight package + automatic catalog inclusion
4. Scheduler root cause accepted; backup no-op when day complete
5. Audio on all stories 001–008 with advancing `currentTime` (blob **or** native path acceptable)
6. Logo/typography: Tillana brand display; no unofficial Samarkan
7. Homepage platform positioning (not bedtime-only)
8. Knowledge readability + 348 private gate
9. Youth audiences + Learning pages
10. Responsive/accessibility
11. Immutable SHA-bound evidence under `docs/product/uat/v1.5/runs/`
12. Factory/Drive safety; Stories 001–007 unchanged

Write report to `docs/reviews/BHAVA_V1_5_COWORK_FINAL_UAT.md`.
