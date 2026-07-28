# Launch CoWork Final UAT — Evidence Index

**Branch tip (live-resolved):** `f8caa61f7c4b4f2a0e8c86c5b143cb668ce9d4cd` (local == origin, post-fetch)
**Tested product SHA:** `77640c3205d9caddd96789c76aeb32b743674450` (from evidence `metadata.json`; exactly one docs-only evidence commit after it)
**Runtime:** `bhava-final`, http://127.0.0.1:3000 (web) / :8000 (API), production — the single active instance
**Date:** 2026-07-28
**Verdict:** see `docs/reviews/BHAVA_STORIES_PRODUCTION_LAUNCH_COWORK_FINAL_REPORT.md`

| File | Contents |
|---|---|
| `01_COPYRIGHT_MATRIX.md` | Identity config, rights-accuracy checks, per-surface notices |
| `02_STORY_PACKAGE_MATRIX.md` | All 9 stories: archives, hashes, exact-eight, rights, media metadata, PDF footers |
| `03_ROUTE_CONTROL_MATRIX.md` | Route sweep, controls, tabs, Back/Forward, sitemap, private boundary |
| `04_ACCESSIBILITY_SCREENSHOTS.md` | Fresh axe results, committed-PNG verification, visual review, overflow/zoom |
| `05_SECURITY_RUNTIME_SAFETY.md` | npm audit, versions, single-runtime proof, queue/scheduler/Drive safety |

Prior-cycle defect closure verified this session: V1.7.3's DEF-V173-01 (player select contrast) FIXED; DEF-V173-02 (/preachers list ARIA) FIXED; DEF-V173-03 (stale 001–007 heading) FIXED (heading now reads "Chapter timeline for Stories 001–009" per live check); DEF-V173-05 (Story 009 audio coverage) FIXED via catalog-driven audio-advance spec passing on 4 engines.
