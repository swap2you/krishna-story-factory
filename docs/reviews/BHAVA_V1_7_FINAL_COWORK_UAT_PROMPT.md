# Bhāva V1.7 — Final CoWork UAT Prompt

Independent review only. Do not modify Stories 001–008, generate Story 010, change the queue outside verification, or create a PR.

## Under test

- Branch: `feature/bhava-portal-v1`
- Confirm local SHA == origin
- Evidence: `docs/product/uat/v1.7/runs/**`, `docs/operations/SCHEDULER_20260727_*`, `docs/releases/STORY_009_RELEASE.md`

## Must verify

1. 2026-07-27 incident root cause classification for `0xC000013A`
2. Registered task: `PT4H`, no NoNewWindow child path, IgnoreNew, StartWhenAvailable
3. `-ValidateScheduler` and `-SimulateProduction` exit 0
4. Temp SimulateProduction task `LastTaskResult=0`
5. Real registered production no-op `LastTaskResult=0` without Story 010
6. Story 009 exact-eight, publishable PASS, Drive folder present
7. Story 010 pending/hidden
8. Catalog shows Stories 001–009
9. Story 009 tabs/audio
10. Stories 001–008 hashes unchanged
11. Homepage contrast regression still green

Write report to `docs/reviews/BHAVA_V1_7_COWORK_FINAL_UAT.md`.
