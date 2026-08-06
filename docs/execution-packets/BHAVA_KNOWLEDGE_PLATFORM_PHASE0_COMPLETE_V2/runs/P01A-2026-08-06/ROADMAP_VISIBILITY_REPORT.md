# Roadmap Visibility Report — P01A

## Counts (VERIFIED)

| Metric | Value |
|---|---|
| Path | `content/knowledge/roadmap/records.json` |
| Total | **348** (`TOP-0001` … `TOP-0348`) |
| `lifecycle=source_research` | 348 |
| `package_status=research_backlog` | 348 |
| `visibility=public` | 340 |
| `visibility=restricted_review` | 8 |
| `lifecycle` in `{approved, published}` | **0** |
| Public `listRoadmap(false)` publishable rows | **0** |

### Restricted IDs

`TOP-0108`, `TOP-0110`, `TOP-0112`, `TOP-0115`, `TOP-0119`, `TOP-0131`, `TOP-0132`, `TOP-0345`

## Why not public

1. Lifecycle gate: loader requires approved/published — none qualify.  
2. Bodies absent: metadata titles only; no reviewed Devanāgarī/IAST/translation packages.  
3. Product honesty: public Knowledge pages state content appears only after review.  
4. Governance: exposing raw roadmap would create empty/misleading public pages and bypass reviews/rights.

## Where they are visible today

| Surface | Behavior |
|---|---|
| `/studio/knowledge` | Cookie-gated; loads `listRoadmap(true)`; shows total 348, counts, filters; table first **200** rows; `noindex` |
| Public Knowledge UI | 0 roadmap rows |
| Public search (web loader) | published articles/questions only |
| API FTS `include_private` | header-gated; must stay non-public |

## P1-F08 / P1-F09 mapping

| Requirement | Current evidence | Gap |
|---|---|---|
| P1-F08 Studio shows all 348 + lifecycle counts | Partial: counts yes; table capped at 200 | Pagination / full list UX |
| P1-F09 no public leak of research/draft/paths | Runtime filter **PASS**; provenance strings in tracked JSON **risk**; header auth **weak** | Strip/redact private paths; strengthen auth for private preview |

## Prayer/śloka roadmap subset (metadata only)

- Pillar “Prayer and Sloka”: **44**  
- `content_type=prayer`: **23**  
- Candidates listed in `SOURCE_AVAILABILITY.md` — **not** publication-ready.
