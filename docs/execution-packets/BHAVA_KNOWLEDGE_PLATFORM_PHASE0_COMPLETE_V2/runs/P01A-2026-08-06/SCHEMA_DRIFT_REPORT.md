# Schema Drift Report — P01A

## Competing schemas (VERIFIED)

| Layer | Artifact | Identity / state fields | Role today |
|---|---|---|---|
| Roadmap JSON | `content/knowledge/roadmap/records.json` | `id` TOP-*, `lifecycle`, `package_status`, `visibility` | research backlog metadata |
| KnowledgeMeta | `apps/web/lib/knowledge/loader.ts` | `slug`, `review_state`, `visibility` | published filesystem docs |
| ResourceDraft / TYPE_TEMPLATES | `types.ts` + loader | 13 content types; field stubs | preliminary templates |
| Prayer/śloka contracts | `packages/contracts/schemas/*.json` | prayer_item, shloka (+ `word_meanings`) | factory/story oriented |
| FastAPI story schemas | `apps/api/bhava_api/schemas.py` | Story*/Collection*/ShlokaResponse | story catalog |
| Knowledge FTS / gates | `knowledge/search.py`, `governance.py` | dict payloads; FTS rows from roadmap | search + publication eval |
| SQLite FTS5 | runtime `data/catalog/knowledge_fts.sqlite` | | current search store |
| PostgreSQL DDL | string in `search.py` + `migrations/001_*.sql` | | **not** proven deployed |
| Phase 0 canonical package | dossier/claims/rights/assets/reviews/manifest | | **PROPOSED** only |
| Age presentation profile | Phase 0 UX doc | lenses / min_age / max_age | **PROPOSED**; no TS types |

## Concrete mismatches

1. **Lifecycle vocabulary:** roadmap uses `source_research`; public filter expects `approved|published`; articles use `review_state: published`.  
2. **content_type enums:** roadmap (`concept`, `guide`, `faq`, `restricted_guide`, …) ≠ loader `CONTENT_TYPES` (article, prayer, arati, sloka, …). Questions use `"question"` special-cased.  
3. **UAT docs** sometimes call lifecycle `research_backlog` — that value is actually `package_status` (**REPORTED** outdated wording).  
4. **No single canonical prayer page schema** binding Devanāgarī, IAST, translation, word meanings, lenses, assets, rights, and export hashes.

## Phase 1 implication (PROPOSED consolidation direction)

Introduce one governed record package for pilot pages (private preview) that:

- keeps roadmap TOP-* as planning IDs until promotion;  
- stores canonical scripture strings once;  
- references dossiers/rights/reviews as separate artifacts;  
- maps to web render + PDF/DOCX from the same version hash.

Do **not** migrate PostgreSQL or replace Next/FastAPI in Phase 1.
