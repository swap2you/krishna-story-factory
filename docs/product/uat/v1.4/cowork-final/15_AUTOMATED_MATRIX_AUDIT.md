# V1.4 Automated Matrix Audit — the "346 passed / 9 skipped / 0 failed" claim is not verifiable release evidence

## Summary

The release repeatedly claims a clean post-fix Playwright run: **"346 passed · 9 skipped · 0 failed"** in `docs/releases/BHAVA_V1_4_RELEASE_CANDIDATE.md`, `docs/reviews/BHAVA_V1_4_CODEX_TECHNICAL_REVIEW.md` ("full matrix 346/0"), and `docs/product/uat/v1.4/00_EVIDENCE_INDEX.md`. Independent audit of the git history shows this claim rests entirely on a file that **is not tracked by git and cannot be attributed to the frozen release SHA**, while the automated-test evidence that **is** committed to that SHA shows a failing run with dozens of individually-documented test failures.

## The untracked evidence

`docs/product/uat/v1.4/playwright-final.log` (50,833 bytes, 355 listed tests, ending `9 skipped` / `346 passed (6.3m)`) is:
- **Not tracked**: absent from `git ls-files docs/product/uat/v1.4/` (only `00_EVIDENCE_INDEX.md`, `04_AUDIO_EVIDENCE.json`, `runtime.json` are tracked there).
- **Gitignored**: `git check-ignore -v docs/product/uat/v1.4/playwright-final.log` → matched by `.gitignore:20:*.log`.
- Has no commit history at all (`git log --follow -- .../playwright-final.log` returns empty).

This means the file exists on disk in the working tree but was never part of any commit, is not reachable from the `19afe6f` SHA under review, and cannot be verified as having been produced by an actual Playwright run against this codebase at this SHA rather than hand-authored, copied from elsewhere, or produced at any other time. The tracked `00_EVIDENCE_INDEX.md` restates its headline number as fact without qualification, and `04_AUDIO_EVIDENCE.json` (also tracked, also unverifiable as to provenance) restates `readyState: 4` audio claims that this session's live testing directly contradicts (see `05_AUDIO_EVIDENCE.md`).

Per the mission's own standard — "Source inspection, Cursor reports, prior screenshots, and existing automated results alone are insufficient" and "Do not accept Cursor's JSON file as proof when the live browser disagrees" — an untracked, gitignored log matching exactly the mission template's own stated hoped-for figures is not admissible as release evidence.

## The committed, git-authenticated evidence says the opposite

`docs/product/uat/live/uat-summary.json`, as committed at HEAD (`git show HEAD:docs/product/uat/live/uat-summary.json`):
```json
{
  "instance_name": "cursor-v14",
  "mode": "production",
  "playwright_exit_code": 1,
  "started_at": "2026-07-24T03:42:57.88778Z",
  "completed_at": "2026-07-24T03:50:27.3734429Z",
  "notes": "Factory generation, scheduler, and Drive were not invoked."
}
```
`playwright_exit_code: 1` = a failing run. This file was committed in `484634349` (2026-07-23 09:54:11, "test: complete Bhava live browser UAT and dynamic runtime validation") and again in `22ff772` (2026-07-23 23:59:39, "docs: add Bhava v1.4 final CoWork UAT prompt and live evidence") — i.e. re-committed with the same failing result nearly 14 hours later, the same evening the release docs were frozen.

Backing this up, `docs/product/uat/live/traces/` (committed in `484634349`) contains dozens of Playwright failure-artifact folders (`error-context.md` + `test-failed-1.png` + `trace.zip` — Playwright's convention for **failed** tests only), including:
- `navigation-navigation-loads-*` failures across chromium-desktop/firefox-desktop/webkit-desktop for routes `/`, `/about`, `/accessibility`, `/contact`, `/knowledge`, `/library`, `/library/krishna-book`, `/prabhupada-vani`, `/privacy`, `/source-permissions`, `/studio`, `/teachers`.
- `responsive-responsive-*-has-no-horizontal-overflow` failures at multiple viewport widths (768/1024/1366/1440/1920) across chromium-desktop/chromium-mobile/firefox-desktop/webkit-desktop/webkit-mobile.
- Two `v14-audio-all-stories-v1-4-*-play-advances-currentTime-chromium-mobile` failures — an automated test with exactly the name "play advances currentTime" failing on chromium-mobile, directly corroborating this session's independent live finding of DEF-06 (see `05_AUDIO_EVIDENCE.md`).
- Two `v12-audio-routes-v1-2-audi-*` failures on the same "play advances currentTime on story 001" assertion.

**The uncommitted, working-tree-only drift on this exact field is itself telling**: `git diff` on `docs/product/uat/live/uat-summary.json` shows `playwright_exit_code: 1 → 0` locally (uncommitted), i.e. someone/something changed this file's `exit_code` to `0` on disk after the release was pinned, without ever committing that change. This working-tree file was **not** relied on as evidence in this review — only the committed HEAD value was used, per the mission's git-authority rules.

## What this means

There is no git-verifiable evidence that a full 355-test Playwright suite passed cleanly at the frozen release SHA. The only evidence that *is* committed and attributable to the SHA shows a failing run (`exit_code: 1`) with specific, named test failures spanning navigation, responsive layout, and audio — the same defect category (audio) independently reproduced live in this session. Per the mission's Section 18 verdict rule ("Return FAIL when: … complete post-fix matrix has a failure" and "Do not report a clean full-matrix PASS based only on targeted audio tests"), this is independently release-blocking, separate from and corroborating the live audio finding.

## Not completed this session

- A byte-for-byte diff of every individual test name in `playwright-final.log` against the failure list in `traces/` was not performed (the untracked log's per-test pass/fail markers are not present in its "list reporter" format — only start-of-test lines were captured, so it cannot even be internally verified against itself without re-running the suite).
- The suite was not re-run this session (mission prohibits modifying/triggering test-affecting application state beyond evidence-only docs; re-running the full suite was judged out of scope for a review-only mandate, and would not change the git-authority finding above regardless of outcome).
