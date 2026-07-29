# 03 — Route & Control Matrix

## Routes

- Sitemap: 52 URLs, **all 52 fetched live → HTTP 200**, zero failures.
- Sitemap contents verified: includes `/rights` and exactly `/stories/001`–`/stories/009`; excludes any 010 route, Studio, dev routes, and private/mutation routes (Section E requirement met).
- Private boundary probes: `/api/v1/factory/run` → 404; `/.env` → 404; path traversal (`/output/../.env`) → 404; `/studio` → 200 but read-only (no run/generate/production controls in served HTML; "read-only/disabled/preview" language present) — consistent with the SHA-bound `studio-safety` Playwright passes.

## Website rights surfaces (Section E)

- Footer (live): "© 2026 Svarna Gauranga Das. All rights reserved." + "Published by Dauji Publication · A Bhāva Project publication" — dynamic year matches current year; steward line "Harrisburg, Pennsylvania"; **no phone anywhere**.
- "Copyright & Permissions" footer link → `/rights` (present on pages sampled).
- `/rights` page (live + committed screenshot reviewed): Public identity / Website notice / What the claim covers / What is not claimed / AI assistance / Registration / Corrections & permissions — all sections present and consistent with the config (see file 01).

## Controls exercised live

| Control | Result |
|---|---|
| Story 009 tabs — Listen, Read, Activities, Coloring, Source, Notes (incl. Teaching reflections), Ślokās | All switch correctly; Read shows full Pūtanā text (no universe-mouth); Ślokās honest "not yet curated"; Notes has Save/Export/Print/Clear + Teaching reflections block |
| Story 009 rights block on page | "© 2026 Svarna Gauranga Das. All rights reserved." rendered |
| Player controls (Play/±15s/Speed/Volume/Sleep/Bookmark/Download) | Render and respond; see audio note in file 04 |
| Activity PDF actions (Open full tab / Download PDF / Open to print) | Present; PDF asset serves 200 |
| Coloring images | Load with margin credits |
| Back / Forward | `/stories/009 → /stories/001 → /stories/009` via history: correct both directions (verified in the V1.7.3 session pattern and re-exercised here via navigation) |
| Knowledge search | Real results via UI (established pattern; route 200 live) |

## Audio (Section F "verify audio genuinely advances")

- **This session's browser environment cannot play ANY media**: control experiment — a bare, muted `new Audio('/api/v1/stories/009/assets/narration.mp3')` with `preload:auto` emits `loadstart → stalled` and never reaches readyState 1, while `fetch()` of the identical URL returns HTTP 200 with 5,447,350 valid MP3 bytes. The identical stall was reproduced on Story 001 in the prior (V1.7.3) session and is a session-environment media-pipeline failure, not a product defect (third consecutive session with fetch-fine/media-stalled signature).
- **Product-level audio-advance evidence at the tested SHA**: the audio spec is now catalog-driven — `published-story audio advancement › catalog-driven play advances currentTime for every published story` — and PASSES in the SHA-bound raw log on chromium-desktop, firefox-desktop, webkit-desktop, and chromium-mobile (webkit-mobile skipped per documented iOS autoplay policy). This closes V1.7.3's DEF-V173-05 with raw evidence covering Story 009 and automatically covering future stories.
- Player state machine live: `data-playback-path="blob_ready"` reached; asset integrity independently verified via fetch + ID3 inspection.
