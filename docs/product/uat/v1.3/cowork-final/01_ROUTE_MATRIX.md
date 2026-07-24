# V1.3 Route Matrix

Source of truth: `find apps/web/app -name "page.tsx"`, 39 routes. "Visited" = navigated live this
session and observed a rendered response (not just a source-code read).

| Route | Visited live | Result |
|---|---|---|
| `/` | Yes | 200, renders |
| `/about` | Yes | 200, renders, identity correct |
| `/accessibility` | Yes | 200, renders |
| `/blog` | Yes (via fetch) | 308 → `/knowledge`, confirmed real redirect |
| `/contact` | Yes | 200, renders, hero image now present |
| `/faq` | Yes | 200, renders, hero image now present |
| `/knowledge` | Yes | 200, renders, full pathway grid |
| `/knowledge/[slug]` (e.g. `what-is-bhava`) | Yes (1 of unknown total slugs) | 200, renders |
| `/knowledge/ask` | Yes | 200, mailto form |
| `/knowledge/corrections` | Yes | 200, mailto form |
| `/knowledge/learning-paths` | Yes | 200, pathway shell list |
| `/knowledge/prayers` | Yes | 200, honest empty state |
| `/knowledge/questions` | Yes | 200, 3 questions |
| `/knowledge/questions/[slug]` (`what-is-bhava-faq`) | Yes (1 of 3) | 200, renders |
| `/knowledge/recent` | Yes | 200, 3 items |
| `/knowledge/scriptures` | Yes | 200, 3 index links |
| `/knowledge/search` | Yes | 200, functional (tested 3 queries) |
| `/knowledge/slokas` | Yes | 200, honest empty state |
| `/knowledge/topics` | Yes | 200, same 16-pathway list |
| `/library` | Yes | 200, collection covers rendered |
| `/library/bhagavad-gita` | No | Not visited this session |
| `/library/caitanya-bhagavata` | No | Not visited this session |
| `/library/caitanya-caritamrta` | No | Not visited this session |
| `/library/dasavatara` | No | Not visited this session |
| `/library/krishna-book` | No | Not visited this session (implied healthy via story pages under it) |
| `/library/prayers-mantras` | No | Not visited this session |
| `/library/rama-katha` | No | Not visited this session |
| `/library/ramacaritamanasa` | No | Not visited this session |
| `/library/ramayana` | No | Not visited this session |
| `/library/srimad-bhagavatam` | Yes | 200, canto covers rendered |
| `/library/srimad-bhagavatam/canto/[canto]` | Yes (canto 10 only, of 12) | 200, renders, per-canto hero |
| `/library/teacher-resources` | No | Not visited this session |
| `/prabhupada-vani` | Yes | 200, renders |
| `/preachers` | Yes | 200, renders |
| `/printables` | Yes | 200, renders |
| `/privacy` | Yes | 200, renders |
| `/source-permissions` | Yes | 200, renders |
| `/stories/[storyNo]` | Yes (all 7: 001–007) | 200, renders; audio broken on all 7 (see 04) |
| `/studio` | No (not re-opened this session; confirmed in prior V1.2 UAT round) | — |
| `/studio/knowledge` | Yes | 200, honest "status shell" disclosure |
| `/sunday-school` | Yes | 200, renders |
| `/teachers` | Yes | 200, renders |

**Totals:** 39 routes discovered from source. 28 route patterns rendered live this session (27 via
direct navigation returning 200, plus `/blog` confirmed via a redirect-following fetch). 11 route
patterns were not visited this session: `/library/bhagavad-gita`, `/library/caitanya-bhagavata`,
`/library/caitanya-caritamrta`, `/library/dasavatara`, `/library/krishna-book`,
`/library/prayers-mantras`, `/library/rama-katha`, `/library/ramacaritamanasa`, `/library/ramayana`,
`/library/teacher-resources`, and `/studio` (this last one was confirmed healthy and safe in the
prior V1.2 UAT round but not re-opened fresh this session). Additionally, for the two dynamic routes
with multiple possible instances, only a sample was checked: 1 of 12 canto pages (canto 10), 1 of
3 Knowledge articles (`what-is-bhava`), and 1 of 3 Knowledge questions (`what-is-bhava-faq`).

No 404s, 500s, or blank pages were encountered on any route that was actually visited.
