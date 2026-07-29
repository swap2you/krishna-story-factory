# 20 — Automated Evidence Audit

## Official run folder — authenticity check

`docs/product/uat/v1.5/runs/20260724-181701-fe57b46/` contains `SUMMARY.md`, `playwright.log`, `pytest.log`, `run-metadata.json`.

- **Git-tracked:** confirmed via `git ls-files` — this entire folder is committed, not a local-only/untracked artifact. This is a genuine improvement over V1.4, where the sole clean-result evidence was an untracked, gitignored file.
- **Internal consistency:** `playwright.log`'s tail genuinely reads `10 skipped / 350 passed (6.6m)`, and `pytest.log`'s tail genuinely reads `392 passed, 5 deselected, 1 warning in 41.17s (0:00:41)` — both match `run-metadata.json`'s claimed counts (`playwright.skipped: 10, passed: 350`; `pytest.deselected: 5, passed: 392`) exactly. No discrepancy between the summary metadata and the raw log tails.
- **`run-metadata.json` fields cross-checked:** `tested_sha: fe57b4661712845b12bf313ea46321d71723c1bb` (matches independently-verified git SHA, file 01), `dirty_tree_at_capture: false`, `stories_001_007_hash_match: true` (matches this review's own independent 56-file SHA-256 re-verification, file 10), instance fields (`cursor-v15`, ports 3005/8003, pids 3352/123980) matching `.bhava/instances/cursor-v15/runtime.json` exactly.

## The "10 skipped" — verified legitimate, not hidden failures

Grepped `apps/web/e2e/v14-audio-all-stories.spec.ts` and `v12-audio-routes.spec.ts` directly. All skip conditions found are explicit, reasoned `test.skip(...)` calls tied to `webkit-mobile` + "iOS WebKit autoplay policy", or a conditional guard (`if (!card.count())`) — not a blanket or unexplained skip. This accounts for exactly the 10 skipped tests in the official run. See file 09 for the audio-coverage implication of this (WebKit playback remains genuinely un-exercised by both the automated suite and this manual review).

## Scratch/dev logs (untracked, gitignored) — not a red flag

Separate untracked files (`playwright-latest.log`, `playwright-audio-retry.log`, `playwright-audio-retry2.log`, `playwright-full-latest.log`, `pytest-latest.log`) exist with earlier timestamps than the official run folder. These are consistent with normal local iterative dev/test cycles preceding the final official capture, and are correctly excluded from the committed evidence set rather than being presented as the release evidence.

## Independent full-matrix rerun — not performed (reachability, disclosed)

This review's Playwright/pytest tooling in the sandbox has no network path to the live app running on the user's Windows machine (same reachability constraint as Lighthouse, file 19). An independent rerun of the full automated matrix from this sandbox was therefore not attempted. In its place, this review substituted **genuine live manual browser interaction** via Claude-in-Chrome (audio across all 8 stories, contrast inspection, knowledge/learning route sweep, axe scans) as the independent verification layer — per the mission's own framing that "existing Cursor documents and automated logs are claims to verify, not substitutes for testing." Multiple of the automated suite's claims were independently corroborated this way (audio fix, Stories 001–007 hash match, WebKit skip legitimacy); one was found to need correction on first attempt but resolved (Knowledge search — file 13).

## Verdict for this section

**PASS.** The official evidence run is genuine, git-tracked, and internally consistent, with every checkable claim independently corroborated by this review's own separate methods (hashing, log reads, live interaction). No fabricated or inconsistent automated evidence found.
