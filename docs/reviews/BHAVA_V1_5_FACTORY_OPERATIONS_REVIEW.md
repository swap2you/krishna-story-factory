# Factory Operations Review — V1.5

## Scheduler

- Root cause of 2026-07-24 10:00 failure: PowerShell `$ErrorActionPreference=Stop` + stderr Tee treated Python `logging.warning` as terminating; stale `.pipeline.lock`; 12:00 blocked.
- Repair: `Start-Process` runner; PID/stale lock reclaim; staging under `work/stories/`; stage state; atomic publish only after exact-eight.

## Story 008

- Reused `story.md` + `narration.mp3`
- Generated remaining six artifacts
- Exact-eight + publishable PASS
- Drive upload + caption/manifest verify PASS
- Queue: 008=done, next=009

## Post-fix validation (fe57b46)

- Playwright full matrix: **350 passed / 10 skipped / 0 failed**
- Pytest: **392 passed / 5 deselected**
- Stories 001–007 SHA-256 match safety baseline
- Evidence: `docs/product/uat/v1.5/runs/20260724-181701-fe57b46/`

## Verdict

**Operations gates closed for CoWork UAT.**
