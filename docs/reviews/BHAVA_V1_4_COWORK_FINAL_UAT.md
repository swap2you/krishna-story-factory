# Bhāva Portal V1.4 — Final Exhaustive Independent CoWork UAT

**Reviewer role:** Independent senior UAT lead / release auditor (review and evidence only — no application code modified, no branch created, no PR/merge, no story/queue/scheduler/Drive/paid-API action taken).
**Repository:** `krishna-story-factory`, branch `feature/bhava-portal-v1`
**SHA under test:** `19afe6fd7548ff938dd9375c268acccc093947cf` — confirmed to equal `origin/feature/bhava-portal-v1` and to be the mission's expected release SHA.
**Instance:** `cursor-v14` (existing, reused), `http://127.0.0.1:3000` / `http://127.0.0.1:8000`, mode `production`.
**Evidence:** `docs/product/uat/v1.4/cowork-final/00_EVIDENCE_INDEX.md` through `16_FACTORY_SAFETY.md`.

## Git and runtime

Branch and SHA are correct and match origin exactly. `main`/`master`/tags unchanged. No secret or private source tracked. One disclosed exception: two live-telemetry files (`docs/product/uat/live/runtime.json`, `docs/product/uat/live/uat-summary.json`) show uncommitted drift, root-caused to the running instance overwriting its own status files on restart — not an application-code change. Critically, that drift includes an uncommitted, unexplained flip of `playwright_exit_code` from the committed value `1` to a local, never-committed `0` — see the Automated Matrix finding below. Full detail: `01_GIT_RUNTIME.md`.

## Coverage

This round concentrated verification effort on the two most decisive, release-determining checks the mission specifies (live audio across all 7 stories; genuineness of the "346/9/0" automated-matrix claim) and on independently re-checking the single largest open finding carried from V1.3 (the 348-record Knowledge Library import). Both audio and automated-matrix authenticity were tested exhaustively and are release-blocking. The 348-record claim, logo fix, and Editorial Studio auth were each verified two independent ways and hold up. Several mission sections — full route/link sweep, all 7 stories' Activities/Coloring/Source/Notes/Ślokās tabs, Education areas, fresh axe scans, genuine multi-viewport screenshots, and Lighthouse/performance capture — were **not exhaustively covered this round**; each evidence file states plainly what was tested and what was not. Nothing untested is reported as passing.

## Audio

**Still broken on all 7 released stories.** Genuine pointer-click Play was tested on every story (001–007), deep-tested with full state capture on 001/006/007. On every story: `readyState` stayed `0`, `currentTime` never advanced past `0`, `duration` stayed `null`, and **no `narration.mp3` network request was ever issued** by the audio element — while a manual `fetch()` to the identical URL succeeded instantly with correct headers (200/206, `audio/mpeg`, `accept-ranges: bytes`). The defect was further isolated using `/dev/audio-lab`: a bare, isolated native `<audio>` element (not the app's custom player) exhibited the identical failure, while the lab's own manual HEAD/Range/Blob probes to the same URL all succeeded — proving the backend and the byte stream are healthy and the failure is specifically in native `<audio>`-element request issuance in this render environment. This directly contradicts `BHAVA_V1_4_RELEASE_CANDIDATE.md`'s claim ("Live audio: Stories 001/006/007 — narration requests + readyState 4 + advancing currentTime") and `docs/product/uat/v1.4/04_AUDIO_EVIDENCE.json`. This is the fourth consecutive independently-tested release (V1.2, V1.3, V1.4) exhibiting this exact signature. Full detail, per-story table, and raw state captures: `05_AUDIO_EVIDENCE.md`.

## Logo and brand

**Genuinely fixed, verified live.** The V1.3 defect (approved wide wordmark `logo-small-header.webp`, 3600×520, forced into a 44×44 `object-fit: cover` crop) is corrected: live DOM inspection confirms `objectFit: contain`, `borderRadius: 0`, and a rendered aspect ratio (221.48/31.99 = 6.92) matching the asset's native aspect ratio exactly. Header markup confirms the documented desktop/mobile/footer mapping, including a live HTML wordmark with the macron preserved (`bh<span>ā</span>va`) for the mobile fallback. `/dev/logo-sheet` exists, is correctly excluded from public nav/sitemap, and shows the canonical reference marks with correct "bhāva" spelling throughout. Genuine mobile-viewport rendering could not be visually confirmed this session (see Quality section — `resize_window` limitation, fourth consecutive session). Full detail: `06_LOGO_BRAND_MATRIX.md`.

## Knowledge Library

**The 348-record governed roadmap import is genuine — a real, verified fix of V1.3's largest finding.** Confirmed two independent ways: (1) the on-disk `content/knowledge/roadmap/records.json` contains exactly 348 records, all `lifecycle: "source_research"`, with real titles/pillars/provenance back-referencing the source CSV's checksum; (2) live, authenticated sign-in to `/studio/knowledge` (role `steward`) shows the identical count and lifecycle breakdown rendered from the running API, with working lifecycle/pillar filters. The public gate holds: search and direct API access both correctly exclude all 348 private records, verified live with zero leakage. The Editorial Studio itself is now a genuine authenticated, role-aware console (9 documented roles, full 9-stage workflow displayed) — a real upgrade from V1.3's static disclosure stub, though per-role mutation enforcement was not exercised this session. Published public seed content remains the same thin set as V1.3 (3 articles + 3 questions) — not re-expanded, not re-tested for regressions. Full detail: `08_KNOWLEDGE_348_RECORD_AUDIT.md`, `10_EDITORIAL_STUDIO_GOVERNANCE.md`, `07_KNOWLEDGE_REQUIREMENT_TRACEABILITY.md`.

## Education

Teachers, Sunday School, Preachers, Prabhupāda Vāṇī, Prayers & Mantras, and Printables were **not re-opened this session** — confirmed present in navigation and in the (disputed) automated test-name list only. No pass or fail is claimed. Full detail: `11_EDUCATION_PRINTABLES.md`.

## Quality (accessibility, responsive, console, network, performance)

No console errors observed on any page visited. Network traffic was clean apart from a known, previously-documented transient RSC-prefetch 503 pattern. No fresh accessibility scan was run and no genuine mobile/tablet viewport was captured — `resize_window` again failed to change the real window's `innerWidth` from its maximized size, the fourth consecutive UAT round (V1.1–V1.4) this exact limitation has been confirmed. No performance/Lighthouse figures are reported, per the mission's instruction not to invent them. Notably, the committed (not this session's) Playwright evidence in `docs/product/uat/live/traces/` independently shows the automated suite's own responsive-overflow tests failing at several viewport widths — real signal this session could not visually confirm or refute. Full detail: `13_ACCESSIBILITY_RESPONSIVE.md`, `14_CONSOLE_NETWORK_PERFORMANCE.md`.

## Factory safety

All checks pass: story hashes/queue/scheduler/Drive/paid-APIs untouched, Story 008 not generated (404, honest pending UI, no link from Story 007), no secret tracked, `main`/`master`/tags unchanged, no production-mutation action attempted in either Factory or Knowledge Studio. Full detail: `16_FACTORY_SAFETY.md`.

## Defects

### DEF-06 (recurring, 4th consecutive release) — Audio playback non-functional on all released stories
- **Severity:** P0 (release-blocking)
- **Route:** `/stories/001` through `/stories/007` (all 7)
- **Affected user:** Every visitor attempting to listen to any story — the core "Listen" experience is non-functional
- **Reproduction:** Open any story page, click Play. Observe via DevTools/JS: `readyState` stays 0, `currentTime` stays 0, no `narration.mp3` request is issued.
- **Expected:** Narration loads and plays; `currentTime` advances.
- **Actual:** Silent failure; UI shows the Play button (never switches to a "loading"/"error" state); no user-facing feedback that anything is wrong.
- **Evidence:** `docs/product/uat/v1.4/cowork-final/05_AUDIO_EVIDENCE.md`
- **Blocker:** Yes.
- **Recommended direction:** Root-cause is isolated to native `<audio>`-element request issuance failing in this environment while `fetch()` succeeds — this points toward a genuine Blob-fallback player (fetch bytes via JS, assign a Blob URL to the `<audio>` element) as the fix, since the commit claiming exactly this (`d6867e3`) does not appear to actually be reaching a working fallback path in the deployed build. Recommend instrumenting the player to log which code path (native vs. Blob) is attempted and why the fallback isn't engaging.

### Automated-matrix evidence is unverifiable / contradicted by committed evidence
- **Severity:** P1 (release-blocking per mission Section 18: "complete post-fix matrix has a failure")
- **Evidence:** `docs/product/uat/v1.4/cowork-final/15_AUTOMATED_MATRIX_AUDIT.md`
- **Blocker:** Yes.
- **Recommended direction:** Commit the actual Playwright output (not a gitignored `.log` file) as part of the release evidence trail, and re-run the full suite after DEF-06 is genuinely fixed before re-pinning a release SHA.

### Minor / non-blocking observations
- Direct navigation to `/stories/008` returns HTTP 200 with an honest "pending" placeholder rather than a hard 404 — not a leak (no fabricated content, all backing APIs 404), but softer than the mission's literal "require 404/unpublished" phrasing. Not treated as blocking since no content is fabricated or exposed.
- A stray HEAD request to `narration.mp3` was logged as 503 by the network monitor while the identical `fetch()` reported 200 in the same call — an unexplained monitor/proxy artifact, consistent with a similar anomaly noted in V1.3, not identified as the cause of DEF-06.

## Report

Written to `docs/reviews/BHAVA_V1_4_COWORK_FINAL_UAT.md` (this file) plus 16 evidence files under `docs/product/uat/v1.4/cowork-final/`.

## Final verdict

# FAIL

Two independent, release-blocking findings, each sufficient on its own per the mission's Section 18 rules: (1) live audio fails on all 7 released stories, reproduced and root-cause-isolated via genuine rendered-browser testing; (2) the release's own committed automated-test evidence (`playwright_exit_code: 1`, dozens of named failures including on the exact audio assertion this session reproduced) contradicts the "346 passed / 0 failed" claim, whose only support is an untracked, gitignored file not attributable to the frozen SHA. These are corroborating, not redundant: the committed automated failures and this session's independent live testing point at the same underlying defect through two unrelated methods.

Genuine, verified progress was made elsewhere in this release and should be recognized: the logo defect is fixed, the 348-record Knowledge Library import is real and correctly gated from public exposure, and the Editorial Studio is now a functioning authenticated console. None of this offsets a non-functional core Listen experience or an unverifiable automated-test claim, both of which are explicit release-blocking conditions under this mission's own verdict rules.
