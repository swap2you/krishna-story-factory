# Bhāva Portal V1.1 — Implementation Plan

Phased release plan for `feature/bhava-portal-v1`. Preserve Stories **001–007**, keep Story **008** pending, never trigger the scheduler, never modify Drive, and never call paid APIs. Factory Studio real actions stay disabled by default.

## Phase overview

| Phase | Theme | Outcome |
|------:|-------|---------|
| 1 | Safety baseline | Record branch/main/tag SHAs, package hashes for 001–007, queue fingerprint; guard tests |
| 2 | Content leak | Backend story parser; web-only reader assets; no public internal production sections |
| 3 | Identity | Public contact is Svarna Gauranga Das only; remove civil/professional identity leakage |
| 4 | Provenance | Per-asset provenance/permissions model; honest Source & Permissions pages |
| 5 | Story V2 | Premium spoken-story player (seek, speed, sleep, bookmark, sticky, a11y) |
| 6 | Sync | Offline sentence alignment → `sync.json`; follow-along UI without package mutation |
| 7 | Reader V2 | Clean reader themes/print; download TXT; no raw `story.md` |
| 8 | Assets | Truthful PDF print; accessible coloring carousel |
| 9 | Sources | Reviewed chapter boundaries + verified Vedabase links; PDF stays private |
| 10 | Notes | Private local notes + curated public teaching reflections |
| 11 | Ślokas | Verse curation/memorization framework; publish only reviewed content |
| 12 | Library | Multi-scripture collection pages, filters, coming-soon polished cards |
| 13 | Education | Teachers class-pack, Sunday School, Preachers workspaces |
| 14 | Vāṇī | Source-governed Prabhupāda Vāṇī categories and planned cards only |
| 15 | Blog | Bhakti blog/prayers taxonomy; planned cards; no fabricated quotations |
| 16 | Brand | Original mark, icons, PWA assets, subtle reduced-motion polish |
| 17 | Storage | Keep local FS + SQLite; document future scale interfaces/ADRs |
| 18 | Enrichment | Auto web enrichment for future factory stories (fixture-safe for 008) |
| 19 | Studio | Read-only enrichment status + allowlisted local maintenance flags |
| 20 | Testing | Full factory/portal/web/Playwright/axe/CI gates on feature branch |
| 21 | UAT | Isolated live browser UAT across viewports with evidence under `docs/product/uat/v1.1/` |
| 22 | Reviews | Technical, adversarial, parent/teacher reviews + release candidate record |
| 23 | Final safety | Re-verify locks, push branch only; no PR/merge; READY only after real browser UAT |

## Non-negotiables

- Exact **eight-file** package contract remains locked; derived web assets live under `data/web-assets/` only.
- `KrishnaBook.pdf` is never committed, served, uploaded, or mirrored.
- `BHAVA_FACTORY_ACTIONS_ENABLED` defaults false; Studio must not expose arbitrary shell/path actions.
- `main` / tags remain unchanged; work stays on `feature/bhava-portal-v1`.

## Phase 1 deliverables

- [BHAVA_V1_1_IMPLEMENTATION_PLAN.md](BHAVA_V1_1_IMPLEMENTATION_PLAN.md) (this file)
- [BHAVA_V1_1_SAFETY_BASELINE.json](BHAVA_V1_1_SAFETY_BASELINE.json)
- `tests/portal/test_v11_safety_baseline.py`
