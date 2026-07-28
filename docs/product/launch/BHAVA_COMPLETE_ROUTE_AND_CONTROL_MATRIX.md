# Bhāva — Complete Route and Control Matrix

**Scope:** Public and operator-facing routes under `apps/web/app`, primary navigation (`SiteHeader` / `SiteFooter`), sitemap / robots, and story controls through Stories **001–009**.  
**Inventory date:** 2026-07-28 (launch documentation pass).  
**Do not treat this as a deploy authorization.** See `docs/deployment/BHAVA_PUBLIC_DEPLOYMENT_READINESS.md`.

## Navigation sources of truth

| Surface | File | Links |
| --- | --- | --- |
| Primary header | `apps/web/components/site-header.tsx` | Home, Library, Knowledge; Learning dropdown (Children & Youth, Sunday School, Teachers, Preachers, Printables); Prabhupāda Vāṇī, About, Contact. Mobile: Menu toggle. |
| Footer | `apps/web/components/site-footer.tsx` | Explore, Learning, About & Contact (incl. FAQ), Trust & Policies (Sources & Permissions, Editorial Standards, Privacy, Accessibility). |
| Sitemap | `apps/web/app/sitemap.ts` | Static marketing/library/knowledge routes + SB cantos 1–12 + stories **001–007 only** (stale vs live 001–009; update before public SEO). Base `https://bhava.me`. |
| Robots | `apps/web/public/robots.txt` | `Allow: /`; `Disallow: /studio`; Sitemap → `https://bhava.me/sitemap.xml`. |
| Redirects | `apps/web/next.config.ts` | `/vanani`, `/vani` → `/prabhupada-vani`; `/blog` and `/blog/*` → `/knowledge` (+ path). |
| API rewrite | `apps/web/next.config.ts` | `/api/:path*` → `BHAVA_API_ORIGIN` / `BHAVA_API_URL` (default `http://127.0.0.1:8000`). |

**Launch status legend:** `live` = useful public experience today · `planned` = honest shell / partial content · `private` = loopback / denylist · `redirect` = not a destination.

---

## 1. Core marketing & trust

| Route | Purpose | Primary controls | Launch status | Notes |
| --- | --- | --- | --- | --- |
| `/` | Story-first homepage: audiences, core areas, featured/latest stories | CTAs: Open Krishna Book, Latest story, Explore Library; collection cards; story grid links | live | Core Areas use art + dark panel (DEF-CONTRAST-01 closed). Sunday School / Teachers / Preachers / Vāṇī may show Planned badges. |
| `/about` | Steward / product identity | In-page links to Contact, Library | live | Steward copy: Svarna Gauranga Das · Harrisburg. |
| `/contact` | Reach steward | mailto / copy affordances only | live | No server-side PII upload. |
| `/faq` | Common questions | Expandable / linked answers | live | Also mirrored in Knowledge Q&A seeds. |
| `/privacy` | Privacy policy | Policy reading | live | Notes/bookmarks = device `localStorage` only. |
| `/accessibility` | Accessibility statement | Policy reading | live | |
| `/source-permissions` | Provenance categories | Definitions + Contact link | live | `bhava_original`, `bbt_source_reference`, `third_party`, `pending_review`. |

---

## 2. Library

| Route | Purpose | Primary controls | Launch status | Notes |
| --- | --- | --- | --- | --- |
| `/library` | Collection hub | Collection cards → shelves | live | Cards: Krishna Book, SB, Gītā, Rāmāyaṇa, Rāma-kathā, Rāmacaritamānasa, Daśāvatāra, CC, CB, Prayers, Teacher resources. |
| `/library/krishna-book` | Published story timeline | `StoryGrid` → `/stories/NNN` | live | H1 range is catalog-dynamic (`Stories 001–009` when all published). DEF-V173-03 closed. |
| `/library/srimad-bhagavatam` | SB shelf | Links to cantos / planned copy | planned | Honest planned-state labeling. |
| `/library/srimad-bhagavatam/canto/[1-12]` | Per-canto shell | Prev/Next canto, back to SB | planned | In sitemap. |
| `/library/bhagavad-gita` | Gītā shelf | Collection intro / planned | planned | |
| `/library/ramayana` | Rāmāyaṇa shelf | Collection intro / planned | planned | |
| `/library/rama-katha` | Rāma-kathā shelf | Collection intro / planned | planned | |
| `/library/ramacaritamanasa` | Rāmacaritamānasa shelf | Collection intro / planned | planned | |
| `/library/dasavatara` | Daśāvatāra shelf | Collection intro / planned | planned | |
| `/library/caitanya-caritamrta` | Caitanya-caritāmṛta shelf | Collection intro / planned | planned | |
| `/library/caitanya-bhagavata` | Caitanya-bhāgavata shelf | Collection intro / planned | planned | |
| `/library/prayers-mantras` | Prayers & mantras learning space | Links back to Library | live / planned mix | Public space; deep verse libraries still curated carefully. |
| `/library/teacher-resources` | Teacher shelf entry | Links to Teachers / Printables | planned | |

---

## 3. Stories 001–009 (and unpublished shell)

| Route | Purpose | Primary controls | Launch status | Notes |
| --- | --- | --- | --- | --- |
| `/stories/001` … `/stories/009` | Full Krishna Book bedtime experience | Sidebar: ← Krishna Book, poster. Tabs: **Listen**, **Read**, **Activities**, **Coloring**, **Source**, **Notes**, **Ślokas**. Persistent audio: Play/Pause, ±15s, waveform seek, Speed, Volume, Sleep, Bookmark, Download. Activities: open/download PDF. Coloring: simple + detailed + lightbox. Notes: save/export/print/clear (`localStorage`). Prev/Next story nav. | live | Packages byte-locked in launch safety baseline. Next Story Preview rewritten dynamically from `series_plan.csv` (DEF-V173-04 closed without mutating packages). |
| `/stories/010` (and higher unpublished) | Placeholder only | No narration/text leak; nav to last published / end | planned / soft-placeholder | `noindex` metadata when unpublished. HTTP 200 placeholder by design. |

### Story tab control detail (all live stories)

| Tab | Controls |
| --- | --- |
| Listen | Shared player + read-along text |
| Read | Full reader markdown (preview line from queue/plan) |
| Activities | Open full tab / Download PDF / Open to print → `activity_sheet.pdf` |
| Coloring | Simple + detailed images; lightbox Escape returns focus |
| Source | Manifest provenance, chapter reference, review fields |
| Notes | Device-local family notes + teaching reflections disclaimer |
| Ślokas | Honest empty/“not yet curated” until verses cleared — no invented verse text |

---

## 4. Printables

| Route | Purpose | Primary controls | Launch status | Notes |
| --- | --- | --- | --- | --- |
| `/printables` | Download hub for package assets | Per-story links: `story_poster.png`, `simple_coloring_page.png`, `coloring_page.png`, `activity_sheet.pdf`; Open story | live | Live for every catalog-published story (001–009). |
| Planned types on same page | Future worksheets | Cards labeled **Planned** only | planned | Word search, crossword, Sudoku, connect-the-dots, sequencing, matching, maze, memory, śloka cards, teacher packs, parent guides — no fabricated sheets. |

Asset URLs: `/api/v1/stories/{storyNo}/assets/{filename}` (proxied to API).

---

## 5. Learning & education

| Route | Purpose | Primary controls | Launch status | Notes |
| --- | --- | --- | --- | --- |
| `/learning/children-youth` | Age-band guidance | Links to Krishna Book / learning areas | live structure | Four age bands; content depth still growing. |
| `/sunday-school` | Weekly class planning structure | Plan table / age guidance | planned | Honest weekly-plan structure; not a full curriculum CMS. |
| `/teachers` | Class-pack composer | Interactive composer UI | live tool / planned content | Tool works; packs remain curated. |
| `/preachers` | Preacher outline workspace | Story selector (`role=list` + `listitem`), outline preview, export TXT, open story | live tool | DEF-V173-02 closed (`role="listitem"` wrappers). |
| `/prabhupada-vani` | Vāṇī learning shelf | Pathway / planned cards | planned | Honest source-tier language; no blanket BBT republication. |

---

## 6. Knowledge (public + planned depth)

| Route | Purpose | Primary controls | Launch status | Notes |
| --- | --- | --- | --- | --- |
| `/knowledge` | Knowledge home | Search form → `/knowledge/search`; mega-columns; published guides list | live | Curated docs only — not an open forum. |
| `/knowledge/search` | Search published knowledge | `q` input + results | live | Local/in-memory + API FTS path as configured. |
| `/knowledge/topics` | Topics & pathways index | Links into pathways | live / planned | |
| `/knowledge/learning-paths` | Learning paths index | Path links | planned depth | |
| `/knowledge/pathways/[slug]` | Pathway detail | Pathway steps + Library/Printables links | live for seeded slugs | e.g. `new-to-bhakti`, `daily-practice`, `deity-worship`, `families-children`. |
| `/knowledge/scriptures` | Scripture orientation | Links to Library shelves | live shell | |
| `/knowledge/prayers` | Knowledge prayers | Lists / planned empty states | planned | Complements `/library/prayers-mantras`. |
| `/knowledge/slokas` | Śloka index shell | Lists / honest empty | planned | No invented verses. |
| `/knowledge/questions` | Q&A index | Question links | live (seeded) | |
| `/knowledge/questions/[slug]` | Q&A article | Answer body | live (seeded) | e.g. what-is-bhava-faq, child-data, official-bbt. |
| `/knowledge/ask` | Private ask | mailto / copy | live | No public comments. |
| `/knowledge/corrections` | Suggest correction | mailto / copy | live | |
| `/knowledge/standards` | Editorial standards | Policy reading | live | Also in footer Trust group. |
| `/knowledge/index` | Alphabetical index | Letter / title links | live | |
| `/knowledge/recent` | Recently updated | Chronological list | live | |
| `/knowledge/report-link` | Report a problem link | Form / mailto | live | |
| `/knowledge/[slug]` | Published article | Article body | live (seeded) | e.g. `what-is-bhava`, `source-and-permissions`, `printing-and-classroom-use`. |
| Knowledge roadmap / 348 research records | Editorial backlog | Studio / private data only | planned / private | Public pages must not expose draft lifecycle records. |

`/blog` → redirect to Knowledge (not a public destination).

---

## 7. Private / operator (not public launch surface)

| Route | Purpose | Primary controls | Launch status | Notes |
| --- | --- | --- | --- | --- |
| `/studio` | Factory Studio status | Loopback status, queue view, enrichment readbacks | private | Disallowed in `robots.txt`; absent from header/footer. |
| `/studio/knowledge` | Knowledge editorial stub | Status shell only | private | Explicitly not a public CMS. |
| `/dev/audio-lab` | Audio engineering lab | Dev player controls | private | Local QA only. |
| `/dev/logo-sheet` | Brand asset sheet | Visual grid | private | Local QA only. |
| `/api/studio/session` | Studio session helper | Session bootstrap | private | |
| `/api/v1/local/*` | Factory gateway | Status, queue, CSRF-gated actions | private | Loopback + `BHAVA_ENFORCE_LOOPBACK` + factory flag off by default. |

See `docs/deployment/BHAVA_PRIVATE_ROUTE_DENYLIST.md`.

---

## 8. Public API surfaces (via web rewrite)

| Route pattern | Purpose | Launch status | Notes |
| --- | --- | --- | --- |
| `/api/v1/health` | Liveness | live (local) | `{"status":"ok","service":"bhava-api"}` |
| `/api/v1/stories`, `/api/v1/stories/{n}` | Catalog read | live | |
| `/api/v1/stories/{n}/assets/{file}` | Media | live | Path-safe filenames only. |
| `/api/v1/stories/{n}/waveform` | Waveform peaks | live | |
| `/api/v1/collections*` | Collections | live | |
| Knowledge API under `/api/v1/...` | Search/helpers | live / optional | Must remain read-only publicly. |

Allowlist: `docs/deployment/BHAVA_PUBLIC_ROUTE_ALLOWLIST.md`.

---

## Sitemap gaps / follow-ups before public SEO

1. Extend `sitemap.ts` stories from `length: 7` to published max (**009**).  
2. Add missing live static routes if desired: `/learning/children-youth`, `/knowledge/standards`, `/knowledge/index`, `/knowledge/recent`, `/knowledge/ask`, `/knowledge/corrections`, `/knowledge/learning-paths`, `/knowledge/scriptures`, `/knowledge/report-link`, article/question/pathway URLs.  
3. Keep `/studio`, `/dev/*`, unpublished story placeholders out of sitemap (or `noindex`).

---

## Control matrix summary (launch-critical)

| Area | Must work for launch | Honest planned OK |
| --- | --- | --- |
| Header/footer navigation | Yes | — |
| Home → Krishna Book → Stories 001–009 | Yes | — |
| Story audio + tabs + printables downloads | Yes | Ślokas empty |
| Printables live package types | Yes | Worksheet types |
| Knowledge search + seeded articles/Q&A | Yes | Full 348 publish |
| Sunday School / Vāṇī deep libraries | Structure | Full curricula |
| Studio / factory actions | Never public | Local only |
