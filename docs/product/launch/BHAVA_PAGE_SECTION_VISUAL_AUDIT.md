# Bhāva — Page Section Visual Audit

**Purpose:** Launch-oriented visual hierarchy, contrast, CTA clarity, and mobile notes for major page families.  
**Evidence baseline:** V1.6 page/section audit, V1.7.3 CoWork screenshot index, and current `apps/web` shell (header/footer, globals).  
**Viewports of record:** 390×844, 768×1024, 1440×900, 1920×1080 (V1.7.3: zero horizontal overflow across primary families).

## Classification

| Tag | Meaning |
| --- | --- |
| `pass` | Hierarchy/contrast/CTA acceptable for launch |
| `closed` | Prior CoWork defect fixed in product code |
| `watch` | Non-blocking residual; monitor in next UAT |
| `planned_honest` | Empty/planned UI is intentional and labeled |

---

## Closed CoWork visual / a11y defects

| ID | Family | Finding (historical) | Resolution | Status |
| --- | --- | --- | --- | --- |
| DEF-CONTRAST-01 | Home CORE AREAS | White/light text on transparent cream cards | Collection-card pattern: artwork + solid dark-navy text panel (`apps/web/app/page.tsx` comment + `CollectionCard`) | **closed** (confirmed V1.6 / V1.7.3) |
| Footer steward hint | Global shell | Muted text on navy | Cream-on-navy `.hint` enhancement | **closed** (V1.6) |
| DEF-V173-01 | Story player | Speed/Sleep `<select>` light text on light OS surface (~1.33:1) | `.audio-controls select` forced dark text `#0b1b2b` on white (`globals.css`) | **closed** |
| DEF-V173-02 | Preachers | `role="list"` with bare `button` children | Wrapper `role="listitem"` around each button (`preachers-workspace.tsx`) | **closed** |
| DEF-V173-03 | Krishna Book | Stale H1 “Stories 001–007” | Dynamic `publishedRangeLabel()` from catalog | **closed** |
| DEF-V173-04 | Story Read tab | Frozen package preview contradicted sequence | Dynamic Next Story Preview from `series_plan.csv` at read time (packages untouched) | **closed** |
| DEF-06 (audio) | Story Listen | Player never advanced / no media request | Blob/ready playback path restored in V1.5+ | **closed** (Chromium); WebKit autoplay policy remains a disclosed test gap |
| DEF-01 / DEF-02 | Stories / identity | Public reader / identity leaks | Fixed in V1.1 CoWork closure | **closed** |

Open test-coverage note (not a visual defect): DEF-V173-05 (ensure Story **009** remains in automated audio matrix) — coverage hygiene, not a section layout issue.

---

## Global shell

### Visual hierarchy
- Brand lockup (icon + **Bhāva** wordmark + “Devotional learning”) is the first header signal.
- Primary nav: Home / Library / Knowledge / Learning menu / Vāṇī / About / Contact.
- Footer: brand column + four link groups; gold links on navy.

### Contrast
- Header cream glass over page background — pass at audited viewports.
- Footer links gold-on-navy — pass.
- Steward hint — **closed** cream-on-navy.

### CTA clarity
- Header is navigation, not competing CTAs.
- Mobile: single **Menu** toggle; Learning submenu closes on route change / Escape / outside click.

### Mobile notes
- Nav collapses behind Menu; ensure focus returns when closing.
- Footer stacks into readable columns; no overflow at 390.

---

## Home (`/`)

| Section | Hierarchy | Contrast | CTA | Mobile | Status |
| --- | --- | --- | --- | --- | --- |
| Hero | Brand-forward photo + scrim; one primary headline region | White on dark photo + scrim | Primary: Krishna Book; secondary: latest story | Full-bleed hero holds at 390 | pass |
| Who Bhāva serves | Audience cards (ages) | Dark text on light panels | Informational | Stacks cleanly | pass |
| CORE AREAS | Collection cards | Art + dark panel text | Card = destination | Grid → single column | **closed** DEF-CONTRAST-01 |
| Featured / latest | Story emphasis | Chip + cream main | Accent button → story | Cards stack | pass |

**CTA clarity:** One primary path (Krishna Book / latest story); Library is quiet secondary. Planned badges on unfinished areas stay honest (`planned_honest`).

---

## Library family (`/library`, shelves)

| Concern | Notes | Status |
| --- | --- | --- |
| Hierarchy | PageIntro → collection grid / shelf body | pass |
| Contrast | Same dark-panel collection cards as home fix | pass |
| CTA | Each card one destination; Krishna Book is launch spine | pass |
| Mobile | Cards stack; canto prev/next remain tappable | pass |
| Planned shelves | SB/Gītā/Rāmāyaṇa/etc. labeled planned | planned_honest |

**Krishna Book (`/library/krishna-book`):** Dynamic H1 range; story cards list published packages — **closed** DEF-V173-03.

---

## Story experience (`/stories/[storyNo]`)

| Region | Hierarchy | Contrast | CTA / controls | Mobile | Status |
| --- | --- | --- | --- | --- | --- |
| Sidebar | Poster, story #, title, source | Light text on dark sidebar | ← Krishna Book | Sidebar stacks above main on narrow | pass |
| Top bar | H1 + quality chip | Dark on cream | Status chip informational | Wrap OK | pass |
| Persistent player | Above tabs | Dark gradient player; select text fixed | Play, seek, Speed, Sleep, Download | Controls wrap; 44px min targets | **closed** DEF-V173-01 |
| Tabs | Listen → Ślokas | Active tab clear | One job per tab | Horizontal tab scroll/wrap — watch overflow | pass / watch |
| Coloring lightbox | Modal focus trap | — | Escape closes | Full viewport | pass |
| Unpublished shell | Clear “in preparation” | No content leak | Nav to published end | — | planned_honest |

---

## Printables (`/printables`)

| Concern | Notes | Status |
| --- | --- | --- |
| Hierarchy | Intro → Live package assets → Planned types | pass |
| Contrast | Scope cards on cream | pass |
| CTA | Filename download links + Open story — unambiguous | pass |
| Mobile | Cards stack; long link lists remain readable | pass |
| Planned types | Explicit Planned badges | planned_honest |

---

## Knowledge family (`/knowledge` + children)

| Concern | Notes | Status |
| --- | --- | --- |
| Hierarchy | PageIntro → search → mega columns → published lists | pass |
| Contrast | Soft mega-col panels can read quieter (V1.6 deferred P2) | watch |
| CTA | Search button primary; pathway links secondary | pass |
| Mobile | Mega columns stack; search full width | pass |
| Planned depth | Empty prayers/ślokas / roadmap private | planned_honest |

Seeded articles and Q&A should remain the only “complete article” surfaces until rights clearance expands the corpus.

---

## Learning family

### Children & Youth (`/learning/children-youth`)
- Hierarchy: intro → age bands → story/library CTAs — **pass**.
- CTA: quiet buttons to Stories / Library — clear, not competing with home hero.
- Mobile: bands stack — **pass**.

### Sunday School (`/sunday-school`)
- Weekly plan table is the primary artifact — **planned_honest**.
- Ensure table scrolls horizontally only inside table container if needed — **watch** on 390 (V1.7.3 reported no page-level overflow).

### Teachers (`/teachers`)
- Composer is the interaction — cards OK as interactive containers.
- CTA: generate/compose actions must remain labeled; empty states honest — **pass** / **planned_honest**.

### Preachers (`/preachers`)
- Selector grid + outline preview + export — **pass**.
- List semantics — **closed** DEF-V173-02.
- Mobile: selector cards full width; export remains reachable — **pass**.

### Prabhupāda Vāṇī (`/prabhupada-vani`)
- Source-tier / planned cards — **planned_honest**.
- Avoid implying full lecture republication — copy discipline, not layout.

---

## Trust & utility pages

`/about`, `/contact`, `/faq`, `/privacy`, `/accessibility`, `/source-permissions`

| Concern | Status |
| --- | --- |
| Single-column readable prose (~760px content) | pass |
| Primary CTA usually Contact / mailto | pass |
| No hero clutter | pass |
| Mobile: comfortable line length | pass |

---

## Brand / motion notes (launch)

- Prefer established Bhāva tokens (navy, saffron/gold, cream) — do not introduce generic purple/glow themes.
- Motion should reinforce hierarchy (nav open, tab change, lightbox), not decorate every card.
- Incomplete PageIntro hero photos may still produce axe “incomplete” contrast flags on busy imagery — treat as **watch**, not reopen DEF-CONTRAST-01.

---

## Launch visual gate (checklist)

- [x] Home CORE AREAS readable (DEF-CONTRAST-01 closed)
- [x] Story player selects meet contrast on light OS surfaces (DEF-V173-01 closed)
- [x] Preachers list semantics (DEF-V173-02 closed)
- [x] Krishna Book H1 matches published count (DEF-V173-03 closed)
- [ ] Fresh axe scan on `/`, `/library`, `/stories/009`, `/preachers`, `/printables` after launch CSS freeze
- [ ] Spot-check Learning menu + story tabs at 390 width
- [ ] Confirm Planned badges remain visible where content is incomplete

---

## Related evidence

- `docs/product/uat/v1.6/design/PAGE_SECTION_AUDIT.md`
- `docs/product/uat/v1.6/contrast/DEF_CONTRAST_01_BEFORE_AFTER.md`
- `docs/product/uat/v1.7.3/cowork-final/SCREENSHOT_INDEX.md`
- `docs/product/uat/v1.7.3/cowork-final/ACCESSIBILITY_AXE_RESULTS.md`
- `docs/product/launch/BHAVA_COMPLETE_ROUTE_AND_CONTROL_MATRIX.md`
