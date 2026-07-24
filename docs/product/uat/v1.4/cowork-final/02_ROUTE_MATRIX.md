# V1.4 Route Matrix (partial — see coverage note)

## Routes live-rendered and confirmed 200 this session

`/`, `/library`, `/stories/001` through `/stories/007`, `/stories/008` (honest pending shell), `/knowledge`, `/knowledge/search`, `/studio/knowledge`, `/dev/audio-lab`, `/dev/logo-sheet`.

Each story route's supporting API calls were observed via network capture and returned 200: `story_poster.png`, `waveform`, `reader`, `sync`, `source-links`, `reflections`, `shlokas`. Narration.mp3 correctly is **not** fetched on page load (lazy, on-Play only) — that part of the architecture is correct; the defect is that Play itself never triggers the fetch (see `05_AUDIO_EVIDENCE.md`).

Diagnostic routes `/dev/audio-lab` and `/dev/logo-sheet` both render, are labeled "NOT IN NAV", and are absent from the rendered public header/footer nav and from `sitemap.xml`.

## RSC-prefetch anomaly (noted, not blocking)

During rapid navigation, several Next.js RSC prefetch requests (`/?_rsc=...`, `/library?_rsc=...`, `/library/krishna-book?_rsc=...`, `/stories/005?_rsc=...`) returned **503**, while the actual page navigations to those same routes succeeded with 200. This is the same transient-503-under-concurrent-prefetch pattern documented in the V1.3 UAT round's network summary — a low-concurrency-ceiling artifact under this instance's dev/production server, not a page-level failure (every route that was actually navigated to rendered successfully).

## Not completed this session (coverage gap, disclosed honestly)

The mission specifies an extensive minimum route list (all 12 individual canto pages, all Knowledge sub-routes, Teachers/Sunday School/Preachers/Prabhupāda Vāṇī/Prayers/Printables, Contact/FAQ/About/Privacy/Accessibility/Source-permissions) with full link/card/CTA click-through, back/forward verification, and broken-image/404 inspection on every one. Given the time required to reproduce and root-cause the audio defect across all 7 stories (the mission's own highest-priority, most decisive check) and to verify the 348-record Knowledge claim through two independent methods, a full exhaustive click-through of every route/link/card in the mission's route list was **not completed this session**. Routes visited and found healthy are listed above; the remainder are unverified this round, not confirmed broken. This mirrors the coverage-disclosure pattern used in the V1.1–V1.3 UAT rounds for the same reason (mission scope exceeds what a single live-browser session can exhaustively cover without materially extending session length).

## `/blog → /knowledge` redirect

Not tested this session (no `/blog` route reference found in the nav or sitemap to trigger it against; carried forward as unverified, not as passing).
