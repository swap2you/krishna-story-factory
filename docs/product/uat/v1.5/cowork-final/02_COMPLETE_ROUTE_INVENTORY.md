# 02 — Complete Route Inventory

Routes independently visited and rendered live via Claude-in-Chrome against `http://127.0.0.1:3005` (cursor-v15 instance) this session, plus routes confirmed via full-fetch status checks:

## Core / marketing

| Route | Status | Notes |
|---|---|---|
| `/` | 200 | Homepage; DEF-CONTRAST-01 present (see file 04) |
| `/library` | 200 | Collection cards correct (dark-panel pattern) |
| `/about` | 200 | Steward identity correct |
| `/contact` | 200 | mailto identity correct, no upload of PII |
| `/faq` | 200 | |
| `/privacy` | 200 | Local-storage-only claims verified against page copy |
| `/accessibility` | 200 | |
| `/source-permissions` | 200 | |

## Knowledge

| Route | Status | Notes |
|---|---|---|
| `/knowledge` | 200 | Public landing; roadmap explicitly described as private until reviewed |
| `/knowledge/search?q=Krishna` | 200 | Real search works (see file 13) |
| `/knowledge/source-and-permissions` | 200 | |
| `/knowledge/what-is-bhava` | 200 | |
| `/knowledge/questions/what-is-bhava-faq` | 200 | |
| `/knowledge/questions/does-bhava-collect-child-data` | 200 | |
| `/knowledge/standards` | 200 | |

## Learning / education

| Route | Status | Notes |
|---|---|---|
| `/learning/children-youth` | 200 | Age-band structure, functional |
| `/sunday-school` | 200 | Structured weekly-plan content, not a stub |
| `/teachers` | 200 | Fully interactive class-pack composer tool |
| `/preachers` | 200 | Story selector lists all 8 released stories incl. #008 |
| `/printables` | 200 | Live assets for all 8 stories; honestly-labeled `PLANNED` placeholders for unbuilt worksheet types |
| `/prabhupada-vani` | 200 | |

## Stories

| Route | Status |
|---|---|
| `/stories/001` – `/stories/008` | 200, all 8 (see file 08 for tab-level matrix) |

## Prefetch anomaly (non-blocking, investigated)

Next.js RSC prefetch requests (`?_rsc=...` query suffix, issued automatically by link-hover/viewport prefetching) transiently returned `503` for `/`, `/library`, `/preachers`, `/printables` during the network capture window. Direct, non-prefetch `fetch()` calls to the same paths (run twice each) returned `200` consistently for all four routes. This is consistent with known Next.js dev/prod-server prefetch-cache behavior and does **not** indicate the pages themselves are broken — confirmed by real navigation succeeding and by repeated direct fetch checks. Logged for completeness; not treated as a defect.

## Verdict for this section

All inventoried routes render successfully (200) on direct/real navigation. No dead links or 404s found among in-app navigation targets tested.
