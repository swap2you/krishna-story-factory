# Source and Reuse Inventory — P01A

**Run:** `P01A-2026-08-06`  
Specialists: routes/schema, UX, content/source, tests/export/security (read-only).

## Reuse now (VERIFIED)

| Capability | Location | Phase 1 use |
|---|---|---|
| Site shell / pillars nav | `apps/web/components/site-header.tsx`, `layout.tsx` | Keep; private preview pages must not break IA |
| PageIntro / CollectionCard | `apps/web/components/*` | Page chrome |
| Design tokens / UI kit | `packages/ui/src/styles.css`, `packages/ui/src/index.tsx` | Visual system base |
| Knowledge loader + public filters | `apps/web/lib/knowledge/loader.ts`, `governance.ts` | Extend for prayer records; do not bypass filters |
| Studio Knowledge workbench | `apps/web/app/studio/knowledge/` | Show 348 roadmap + future private preview |
| Middleware + Caddy private deny | `apps/web/middleware.ts`, `deploy/ionos/Caddyfile` | Harden for private preview |
| Story śloka panel pattern | `story-experience.tsx`, `shloka.schema.json` | Closest Sanskrit/IAST/translation UI precedent |
| Activity PDF (reportlab) + pdf.js viewer | `krishna_story_factory/pdf/`, `pdf-js-viewer.tsx` | Pattern/fonts only — not Knowledge export |
| FTS / publication gates | `apps/api/bhava_api/knowledge/` | Studio search / gate evaluation |
| Contracts schemas | `packages/contracts/schemas/prayer_item.schema.json`, `shloka.schema.json` | Starting point for record shape |
| Axe Playwright + jsx-a11y | `apps/web/e2e/accessibility.spec.ts` | Expand matrix |
| Privacy boundary tests | `tests/test_public_production_boundary.py`, e2e studio-safety | Extend to Knowledge preview |
| `bhava-library` candidate export | `data/exports/bhava-candidates/` (553 metadata/briefs, 0 binaries) | Provenance-aware intake only |
| Publishing-studio schemas | `bhava-publishing-studio/schemas/` | Rights/dossier vocabulary reference |

## Build (absent today — VERIFIED gaps)

| Need | Status |
|---|---|
| Stanza content-block components | absent |
| Age depth lenses / focus mode | absent (marketing age pathways ≠ lenses) |
| Loaded Devanāgarī font (Noto named in CSS only) | absent |
| Knowledge PDF export | absent |
| Knowledge DOCX export / dependency | absent |
| Canonical prayer record packages (`source_dossier.json`, `rights.json`, …) under `content/knowledge/` | absent |
| Published prayer/śloka bodies | **0** |
| Production-grade Studio auth (beyond bootstrap cookie + forgeable header) | insufficient |

## Placeholders / dead / planned (VERIFIED)

- `/knowledge/prayers`, `/knowledge/slokas` — honest empty stubs  
- Most Library collections + `/prabhupada-vani` — planned  
- No `/learning` index (dropdown-only)  
- `app/blog/page.tsx` orphaned behind redirect  
- 12 pathway shells still `proposed`

## Competing configs to reconcile before build

| Topic | Values |
|---|---|
| Public story max | release **22** vs web/API default **20** vs AGENTS **020** |
| Node | pin **24** vs local **22.23.1** |
| Lifecycle vocabulary | roadmap `lifecycle` vs article `review_state` vs Studio labels |
| `content_type` enums | roadmap vs `CONTENT_TYPES` in loader |

## Private-path hygiene

**VERIFIED risk:** tracked `content/knowledge/roadmap/records.json` embeds `MyPilotDropbox\…\topic_backlog.csv` provenance strings (340+ rows). Not absolute disk paths, but private layout leak in public repo data. Runtime public list remains empty.
