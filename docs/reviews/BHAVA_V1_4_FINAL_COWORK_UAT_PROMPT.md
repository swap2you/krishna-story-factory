# Bhāva V1.4 — Final CoWork Live UAT Prompt

## Binding

- Repository: `krishna-story-factory`
- Branch only: `feature/bhava-portal-v1`
- Final SHA to test: run `git fetch` then `git rev-parse origin/feature/bhava-portal-v1` (must equal local HEAD). Authoritative tip at READY: 3f67db7f9d5eeb3b0ae04300f616acfc3ba318d5
- Do **not** create a PR or merge. Evidence-only commits allowed after this prompt.

## Runtime

```powershell
.\scripts\run_bhava_uat.ps1 `
  -InstanceName cursor-v14 `
  -PreferredWebPort 3000 `
  -PreferredApiPort 8000 `
  -KeepRunning
```

Expected (if already running):

- Web: http://127.0.0.1:3000
- API: http://127.0.0.1:8000
- Stop: `.\scripts\stop_bhava_local.ps1 -InstanceName cursor-v14`

## Must prove live

1. **Audio (all seven stories):** Play produces a narration media request (or verified blob fallback), `currentSrc` non-empty, `readyState >= 2`, `currentTime` advances. Deep Network + state captures on 001/006/007.
2. **Keyboard:** With audio playing and Coloring modal open, arrows only affect carousel; Space does not toggle audio; Escape closes; focus returns.
3. **Logo:** Desktop shows true-aspect `/brand/logo-small-header.webp` (not a 44×44 crop). Mobile shows icon-only + live `bhāva`. Footer shows dark logo. Favicon/PWA icon-only.
4. **Brand surfaces:** Library covers, 12 canto covers, Contact/FAQ heroes, Knowledge cover — no broken images.
5. **Knowledge:** `/knowledge` hierarchical UX; `/blog` redirects; public shows published only; studio at `/studio/knowledge` shows exact **348** roadmap records; search; standards; ask/corrections/report-link private.
6. **Story 007:** No link to Story 008; truthful end-of-release message.
7. **Identity:** Only Svarna Gauranga Das · svarnagaurangdas@gmail.com · Harrisburg, Pennsylvania.
8. **Factory:** Stories 001–007 unchanged; 008 pending; queue untouched; no paid APIs.
9. **Matrix:** Confirm post-fix Playwright was 346 passed / 9 skipped / 0 failed (re-run if code changes).

## Evidence location

`docs/product/uat/v1.4/**`

## Verdict language

Return **READY** or **BLOCKED** with defects. Do not rubber-stamp.
