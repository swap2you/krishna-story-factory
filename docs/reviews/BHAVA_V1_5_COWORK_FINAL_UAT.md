# Bhāva Portal V1.5 — CoWork Exhaustive Final UAT

**Branch:** `feature/bhava-portal-v1`
**Branch SHA:** `b51c0a877ee654207f146b3b19d8179f7a3ee620` (independently confirmed via `git rev-parse HEAD`)
**Tested product SHA:** `fe57b4661712845b12bf313ea46321d71723c1bb` (independently confirmed via `git rev-parse fe57b46`)
**Runtime instance:** `cursor-v15`, reused as instructed (http://127.0.0.1:3005 / :8003, production mode)
**Reviewer role:** Independent CoWork reviewer. No application code, stories, queue, scheduler, Drive, main/master/tags, or Factory/Knowledge Studio production actions were modified. No new stories were generated. No paid APIs were invoked.
**Evidence:** `docs/product/uat/v1.5/cowork-final/` (21 files + this report)

---

## Overall verdict: **FAIL**

The release is denied not because of a lack of progress — quite the opposite, this cycle resolves the single most persistent defect in the product's UAT history — but because a new, independently-confirmed, release-blocking defect (severe white-on-white contrast on the homepage's primary content section) was found this cycle, and the mission's own verdict rules (Section 22) explicitly require FAIL when "severe white-on-white or unreadable contrast affects a primary experience."

---

## Headline result 1: DEF-06 (audio playback) is genuinely fixed

DEF-06 was open and release-blocking across V1.2, V1.3, and V1.4. This cycle, independently and live, across all 8 released stories (001–008) in a real rendered Chromium browser:

- The player prefetches narration as a `Blob` on page load (`data-playback-path="blob_ready"`, `audio.currentSrc` already a `blob:` URL, `readyState: 4`, before Play is even pressed).
- Pressing Play transitions to `blob_playing`; `audio.currentTime` genuinely advances; Play/Pause/±15s all function correctly.
- No console errors during playback, any of the 8 stories.

This is confirmed, not merely trusted from Cursor's own documentation or the automated suite's claims. Full detail and Story 008 manifest/duration/filesize triangulation: `docs/product/uat/v1.5/cowork-final/09_AUDIO_001_008.md`.

**One disclosed gap:** the automated suite's `webkit-mobile` skip ("iOS WebKit autoplay policy") is a legitimate, intentionally-documented skip, but it means genuine WebKit/Safari audio behavior remains unexercised by both the automated suite and this review (Claude-in-Chrome is Chromium-based). Recommend a manual Safari/iOS spot check before final sign-off if WebKit users are material to the audience.

---

## Headline result 2: DEF-CONTRAST-01 — white-on-white homepage cards (release-blocking)

Independently confirmed via live `getComputedStyle` inspection of all 8 "CORE AREAS" cards on the homepage: white/near-white text (`rgb(255,255,255)` / `rgba(255,255,255,0.82)`) rendered directly on the page's plain cream background (`rgb(247,240,228)`), because the cards have `backgroundImage: none`, `backgroundColor: rgba(0,0,0,0)` (fully transparent), and no `<img>` child at all. This exactly matches the mission's explicitly-flagged operator hypothesis.

**Corroborated by a fresh, independent axe-core scan**: 99 `color-contrast` nodes flagged `incomplete` (serious impact) on the homepage, of which 12+ are directly the affected `.collection-card` title/description text, with axe's own failure summary ("background color could not be determined... obscured") consistent with the transparent-card-on-page-background finding.

**Proven isolated, not systemic:** `/library`'s own collection cards use a correct, different implementation (dark-navy panel over real artwork). The same axe scan on `/library` also flags `color-contrast` as incomplete, but for a different, benign reason (unresolvable CSS gradients over real images) — manually confirmed those cards have genuinely sufficient contrast. The homepage defect is isolated to one component, and the fix pattern already exists elsewhere in the same codebase.

| Field | Value |
|---|---|
| ID | DEF-CONTRAST-01 |
| Severity | P0/P1 — release-blocking |
| Route | `/` — "CORE AREAS" section |
| Browser | Chromium (reproduced); CSS-level defect, expected in all browsers |
| Viewport | Reproduced at desktop width; markup identical across breakpoints |
| Affected audience | All visitors — this is the homepage's primary content-discovery surface |
| Reproduction | Load `/`, scroll to "CORE AREAS", inspect any `.collection-card`'s computed text color vs. background |
| Expected | Photo/dark-panel background beneath white text, as on `/library` |
| Actual | Transparent background, no image, white text directly on cream page background |
| Evidence | `docs/product/uat/v1.5/cowork-final/04_VISUAL_CONTRAST_TYPOGRAPHY.md`, `17_ACCESSIBILITY.md` |
| Recommended correction | Apply `/library`'s working photo+scrim/dark-panel pattern to the homepage's `.collection-card` component |

Full detail: `docs/product/uat/v1.5/cowork-final/04_VISUAL_CONTRAST_TYPOGRAPHY.md`.

---

## Other significant finding: scheduler — configuration correct, but no observed post-repair scheduled success

Independently re-implemented the product's own `test_mwf_story_task.ps1 -StaticOnly` assertions via direct `grep` checks against the current `run_daily_story_scheduled.ps1` / `install_mwf_story_task.ps1` — **all 16 checks pass**, confirming the fix (no `Tee-Object`, uses `Start-Process` + `RedirectStandardError`, safe args, correct 6-trigger MWF 10:00/12:00 schedule, no-overlap, retry policy) is genuinely present in source.

However, independent analysis of `tracking/run_history.csv` and `logs/scheduler/*.log` (today, 2026-07-24, is a real MWF trigger day) shows:

- **10:00** scheduled firing → FAILED, using the **old**, pre-fix script (`Tee-Object` error signature)
- **12:00** scheduled firing → FAILED, same pre-fix signature
- **12:44–12:47**, three manual attempts → the last one **succeeded** and produced Story 008, but with detail "Upload disabled by flag" and preceded by manual `--enable-production-recovery`-flag attempts — consistent with a direct/manual invocation, not a Task-Scheduler-triggered run of the fixed wrapper script.

**Conclusion:** the fix is source-verified-correct, and the scheduler's triggers are confirmed real and active (two genuine firings observed today) — but no log evidence shows the *current, fixed* script running via a real scheduled trigger and succeeding end-to-end. Story 008's release itself is fully verified safe and correctly gated (see below), so this is not a release blocker for the UAT itself, but it is a genuine open operational item: confirm one real scheduled success (next Mon/Wed/Fri trigger, or a manual `Start-ScheduledTask` + `Get-ScheduledTaskInfo` check) before trusting the pipeline unattended for Story 009 onward.

Full detail: `docs/product/uat/v1.5/cowork-final/11_SCHEDULER_OPERATIONS.md`.

Note: this section could not include live Windows Task Scheduler queries (`Get-ScheduledTask`, `Get-ScheduledTaskInfo`, `Export-ScheduledTask`) — this review runs in a Linux sandbox with no PowerShell/Task Scheduler access. All scheduler findings are independent source verification plus independent operational-log analysis, not a live task-registration query.

---

## Story 008 / catalog / safety baseline — all clean

- Exact-eight package, `publishable: true`, `quality.status: PASS`, manifest duration/filesize independently triangulated against live browser playback and on-disk file size — all consistent.
- Stories 001–007: independently recomputed SHA-256 for all 56 baseline-referenced files — **zero mismatches**.
- Live vs. frozen queue-state files correctly distinguished (`locked_queue_state.csv` is an intentionally-stale baseline snapshot; `tracking/queue_state.csv` is live and correctly shows 008 done / 009 pending).
- Quarantine/partial-recovery workspace confirmed not publicly reachable (404 on direct access and path traversal).
- Drive verification: evidence reviewed, not independently accessed (no Drive credentials/connectivity available to this sandbox). One reconciliation item flagged: the specific run that produced Story 008 recorded "Upload disabled by flag" in its own history entry, which the product owner should reconcile against the manifest's Drive-upload confirmation.

Full detail: `docs/product/uat/v1.5/cowork-final/10_STORY_008_FACTORY_CATALOG.md`.

---

## Knowledge, Learning, and trust pages — all clean

- 348-record roadmap independently parsed: 100% `research_backlog` lifecycle, 340 public / 8 restricted_review, and **zero** of the 348 records are reachable via any public route or API path tried — the "roadmap stays private until reviewed" claim on the public `/knowledge` page holds.
- Knowledge search initially appeared broken (0 results against a guessed API endpoint) but this was a false alarm from testing the wrong endpoint — the real product search, exercised through the actual UI, works correctly. Documented transparently in `13_KNOWLEDGE_PATHWAYS_SEARCH.md` as a correction to the review's own first attempt, not a product defect.
- `/teachers`, `/sunday-school`, `/preachers`, `/printables`, `/learning/children-youth` all render real, substantive, functional content; unbuilt items are honestly labeled `PLANNED` rather than fabricated.
- Identity (`/about`, `/contact`, `/privacy`) is consistent and correct: steward "Svarna Gauranga Das," mailto `svarnagaurangdas@gmail.com`, no placeholder content, no unintended PII leakage. `/contact` and `/teachers` playlist/notes features are confirmed client-side/`localStorage`-only, matching their own privacy claims.

Full detail: `docs/product/uat/v1.5/cowork-final/12_KNOWLEDGE_348_PUBLIC_GATE.md`, `13_KNOWLEDGE_PATHWAYS_SEARCH.md`, `14_LEARNING_EDUCATION_VANI.md`, `15_ABOUT_CONTACT_FAQ_TRUST.md`.

---

## Accessibility, responsive, console/network, performance, automated-evidence audit

- Fresh live axe-core scans (not a rerun of an old report): 0 hard violations homepage and `/library`; homepage's `color-contrast` "incomplete" flag independently resolved to the real DEF-CONTRAST-01 defect; `/library`'s equivalent flag resolved to a benign gradient-detection limitation.
- `resize_window` tooling limitation reconfirmed for a sixth consecutive UAT cycle — reports success but does not actually change the real viewport. Responsive correctness this cycle relies on the automated Playwright suite's genuine 7-width coverage (390–1920, all passing).
- Console clean of application errors; network clean aside from benign Next.js RSC-prefetch 503s (confirmed transient/harmless via repeated direct-fetch checks).
- Lighthouse could not run — the live app is reachable only via the user's own browser (Claude-in-Chrome), not this sandbox's network. Documented per the mission's own non-blocking allowance; lightweight Performance-API proxy metrics (domContentLoaded 101ms, load 577ms) showed no red flag.
- The official automated evidence run (`docs/product/uat/v1.5/runs/20260724-181701-fe57b46/`) is genuinely git-tracked and internally consistent — every checkable claim in it was independently corroborated by this review's separate methods.

Full detail: `docs/product/uat/v1.5/cowork-final/16_RESPONSIVE_SCREENSHOT_MATRIX.md` through `20_AUTOMATED_EVIDENCE_AUDIT.md`.

---

## Minor, non-blocking documentation items

1. `docs/releases/BHAVA_V1_5_RELEASE_CANDIDATE.md` states an incorrect full 40-character SHA (`fe57b46fbb273b9689cadb59c663fd0992d9a983`, which does not exist in the repo); the correct SHA is `fe57b4661712845b12bf313ea46321d71723c1bb`. Cosmetic/documentation only.
2. The Story 008 run-history entry that produced the final success recorded "Upload disabled by flag," which the product owner should reconcile against the manifest's Drive-upload confirmation.

---

## Scope disclosures (honesty, not evasion)

- The full six-tab-per-story (Listen/Read/Activities/Coloring/Source/Notes) live deep-dive performed exhaustively in V1.1–V1.4 was not repeated in full manual form this cycle for tabs other than Audio, given the size of the V1.5 mission. This review relies on the automated matrix plus the cryptographic unchanged-guarantee for Stories 001–007; **Story 008's non-audio tabs specifically were not independently live-verified this session** and are recommended as a follow-up before final sign-off.
- Live Windows Task Scheduler queries were not possible from this sandbox (no PowerShell access); scheduler findings are source + log analysis only, clearly labeled as such throughout.
- Independent full Playwright/pytest matrix rerun and Lighthouse were not possible from this sandbox (no network path to the app's host); live manual browser testing was substituted as the independent verification layer instead.
- Factory Studio live-mutation re-test and a direct source-PDF-exposure probe were not independently re-exercised this specific session (time constraints); flagged as follow-ups, not failures, given consistent claims elsewhere in the evidence and no observed contradiction.

---

## Verdict rationale (per mission Section 22)

- Audio: PASS on all 8 stories (Chromium) — the historically release-blocking condition is resolved.
- Contrast: **FAIL** — "severe white-on-white or unreadable contrast affects a primary experience" is explicitly triggered by DEF-CONTRAST-01 on the homepage.
- Story 008 / catalog / hashes / private-roadmap / identity / safety: all clean, no other FAIL-triggering condition found.
- Scheduler: configuration correct, real triggers confirmed, but no observed post-repair scheduled success — a genuine open item, not independently rising to a mission-defined FAIL condition on its own, but worth the product owner's prompt attention.

**Because DEF-CONTRAST-01 alone is sufficient to trigger a mandatory FAIL under the mission's own rules, the overall verdict is FAIL, notwithstanding the genuine and significant progress represented by the DEF-06 audio fix and the otherwise clean safety/integrity results.**

---

## Recommended next steps

1. Fix DEF-CONTRAST-01: apply `/library`'s working card pattern (photo + dark panel/scrim) to the homepage's `.collection-card` component.
2. Confirm one genuine end-to-end scheduled success of the current (fixed) `run_daily_story_scheduled.ps1` via the real Windows Task Scheduler before relying on it unattended for Story 009+.
3. Reconcile the "Upload disabled by flag" detail on the Story 008 success run against the manifest's Drive-upload confirmation.
4. Correct the SHA typo in `BHAVA_V1_5_RELEASE_CANDIDATE.md`.
5. Before final production sign-off: a manual Safari/iOS WebKit audio spot check, and a full six-tab live pass on Story 008 specifically (the one story not covered by the cryptographic unchanged-guarantee).

---

## Commit / push

Per mission Section 23, this review will commit only:

```text
docs/reviews/BHAVA_V1_5_COWORK_FINAL_UAT.md
docs/product/uat/v1.5/cowork-final/**
```

No application code, stories, queue, scheduler config, or Drive state was modified. If `git push` fails in this sandbox (no GitHub credentials configured here, consistent with every prior UAT cycle in this series), the local commit will be preserved and the exact error reported honestly — this review will not claim remote publication without independent confirmation.
