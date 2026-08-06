# Route / Component / Data Map — P01A

## Public pillars

| Pillar | Primary routes | Page modules | Data source |
|---|---|---|---|
| Home | `/` | `apps/web/app/page.tsx` | marketing + age pathways |
| Knowledge | `/knowledge` + children | `apps/web/app/knowledge/**` | `content/knowledge/**` via `loader.ts` |
| Library | `/library` + collections | `apps/web/app/library/**` | `collection-readiness.ts` + static pages |
| Learning | `/learning/children-youth`, `/sunday-school`, `/teachers`, `/preachers`, `/printables` | respective `app/**` | mostly static; **no `/learning` index** |
| Prabhupāda Vāṇī | `/prabhupada-vani` | `app/prabhupada-vani/page.tsx` | planned cards |
| About / Contact | `/about`, `/contact` | matching pages | `config/contact.json` |

## Redirects (VERIFIED)

| From | To |
|---|---|
| `/blog`, `/blog/*` | `/knowledge`, `/knowledge/*` |
| `/vani`, `/vanani` | `/prabhupada-vani` |

## Knowledge subroutes

| Route | Behavior |
|---|---|
| `/knowledge` | hub + search form + lists |
| `/knowledge/[slug]` | article: `PageIntro` + `<pre>{body_md}</pre>` |
| `/knowledge/questions/[slug]` | FAQ: plain paragraph answer |
| `/knowledge/pathways/[slug]` | pathway shell |
| `/knowledge/prayers`, `/slokas` | empty stubs |
| `/knowledge/search` | SSR substring over published articles/questions |
| `/knowledge/ask`, `/corrections`, `/standards`, … | forms/static |

## Private surfaces

| Route / API | Guard |
|---|---|
| `/studio`, `/studio/knowledge` | middleware 404 if public; cookie bootstrap |
| `/dev/*` | middleware |
| `/api/studio/session` | bootstrap token |
| `/api/v1/local/*`, factory/scheduler/queue | local/non-public + loopback |
| `/api/v1/knowledge/search?include_private=` | requires `X-Bhava-Studio: 1` (**forgeable**) |

## Sitemap / robots

| Artifact | Includes | Excludes |
|---|---|---|
| `app/sitemap.ts` | hubs, SB cantos, stories ≤ `PUBLIC_STORY_MAX` | article slugs, pathways, studio, `/learning/children-youth` |
| `app/robots.ts` | disallows studio/dev/factory; `/stories/021` | incomplete for 022+ private stories |

## Component reuse map (Phase 1 golden page)

| UI need | Existing | Gap |
|---|---|---|
| Page chrome | `PageIntro`, layout landmarks | — |
| Stanza stack (Deva/IAST/EN) | story `.sanskrit` pattern only | new Knowledge blocks |
| Lens switcher | none | new |
| Focus mode | none | new |
| Source/review panel | Studio table only | new public-preview-safe panel |
| Export buttons | story print/TXT; activity PDF | new PDF/DOCX |
| Related content | pathway related lists | must not link dead planned items |

## Data flow (current)

```text
content/knowledge/roadmap/records.json ──► Studio listRoadmap(true)
                                         ╳ public listRoadmap(false) → 0 rows
content/knowledge/articles|questions ──► public Knowledge pages
FastAPI knowledge_fts ◄── rebuild from roadmap JSON
Story packages ──► /stories/[n] + API catalog (separate from Knowledge)
```
