# Bhāva V1.4 — Final CoWork UAT Evidence Index

**SHA under test:** `19afe6fd7548ff938dd9375c268acccc093947cf` (branch `feature/bhava-portal-v1`, confirmed = origin HEAD)
**Instance:** `cursor-v14`, `http://127.0.0.1:3000` / `http://127.0.0.1:8000`, mode `production` (reused existing running instance)
**Verdict: FAIL** — see main report `docs/reviews/BHAVA_V1_4_COWORK_FINAL_UAT.md`

## Two release-blocking, independently-verified findings

1. **Live audio (DEF-06) still broken on all 7 released stories**, reproduced via genuine rendered-browser Play clicks, and root-cause-isolated to native `<audio>`-element request issuance (not the app's player logic — a bare isolated `<audio>` tag in `/dev/audio-lab` fails identically) while `fetch()` to the same URL succeeds every time. Fourth consecutive release (V1.2, V1.3, V1.4) with this exact defect. → `05_AUDIO_EVIDENCE.md`
2. **The "346 passed / 9 skipped / 0 failed" automated-matrix claim is not verifiable release evidence.** Its only source, `docs/product/uat/v1.4/playwright-final.log`, is untracked and gitignored — not attributable to the frozen SHA. The evidence that *is* committed to the SHA (`docs/product/uat/live/uat-summary.json`, `playwright_exit_code: 1`, plus dozens of named Playwright failure artifacts in `docs/product/uat/live/traces/`) shows a failing run, including a failure on the exact same audio-currentTime assertion this session reproduced live. → `15_AUTOMATED_MATRIX_AUDIT.md`

## Genuine, verified improvements over V1.3 (positive findings)

- Logo defect fixed: header logo now renders true-aspect (`object-fit: contain`, no crop), verified via live DOM inspection, not just documentation. → `06_LOGO_BRAND_MATRIX.md`
- Knowledge Library 348-record governed roadmap import is genuine and exact (348 records, `source_research` lifecycle, verified two independent ways: static file + live authenticated Studio UI), correcting V1.3's finding of only 20 synthetic placeholders. → `08_KNOWLEDGE_348_RECORD_AUDIT.md`
- Public search/API gate correctly excludes all 348 private roadmap records — verified live, no leakage. → `08_KNOWLEDGE_348_RECORD_AUDIT.md`
- Editorial Studio is now a real authenticated, role-aware console with live data (was a static disclosure page in V1.3). → `10_EDITORIAL_STUDIO_GOVERNANCE.md`
- Story 008 safety gate holds: 404 on direct API access, honest "pending" UI shell, no link from Story 007. → `05_AUDIO_EVIDENCE.md`, `16_FACTORY_SAFETY.md`

## Files in this evidence set

1. `01_GIT_RUNTIME.md` — git/release authority, commit history interpretation, working-tree drift explanation
2. `02_ROUTE_MATRIX.md` — routes rendered and confirmed (partial coverage, disclosed)
3. `03_LINK_REDIRECT_MATRIX.md` — link/redirect spot checks
4. `04_STORY_TAB_MATRIX.md` — Listen deep-tested all 7 stories; other tabs not re-verified this session
5. `05_AUDIO_EVIDENCE.md` — the decisive DEF-06 finding, all 7 stories + `/dev/audio-lab` isolation
6. `06_LOGO_BRAND_MATRIX.md` — logo fix verification (positive)
7. `07_KNOWLEDGE_REQUIREMENT_TRACEABILITY.md` — V1.3→V1.4 Knowledge requirement diff
8. `08_KNOWLEDGE_348_RECORD_AUDIT.md` — the 348-record import verification (positive)
9. `09_KNOWLEDGE_SEARCH_CONTENT_TYPES.md` — search engine and content-type coverage (partial)
10. `10_EDITORIAL_STUDIO_GOVERNANCE.md` — Studio auth/role/workflow live test (positive, partial)
11. `11_EDUCATION_PRINTABLES.md` — not re-tested this session (disclosed)
12. `12_IDENTITY_PRIVACY_SECURITY.md` — identity/security spot checks
13. `13_ACCESSIBILITY_RESPONSIVE.md` — resize_window limitation (4th consecutive session), no fresh axe scan
14. `14_CONSOLE_NETWORK_PERFORMANCE.md` — console/network clean; no performance data (not fabricated)
15. `15_AUTOMATED_MATRIX_AUDIT.md` — the decisive automated-evidence authenticity finding
16. `16_FACTORY_SAFETY.md` — all factory-safety checks pass

## Coverage disclosure

This session prioritized the mission's two most decisive, release-determining checks (live audio across all 7 stories; automated-matrix evidence authenticity) and the largest open item from V1.3 (the 348-record Knowledge claim), verifying each thoroughly and independently. Given the mission's very large scope (19 sections, hundreds of individual checklist items), several sections were not exhaustively covered this round — each affected file states plainly what was and was not tested. No untested item is reported as passing.
