# V1.7.3 CoWork UAT — Screenshot & Visual Verification Index

## Tooling disclosure (read first)

Two hard tooling constraints, both reproduced and verified this session, prevented writing screenshot image files into the repository:

1. **`resize_window` does not change the real viewport** in this Claude-in-Chrome environment (reported success, but `window.innerWidth` remained 1920) — 7th consecutive UAT cycle reproducing this.
2. **The browser extension hard-blocks returning base64/image data** from `javascript_exec` (`[BLOCKED: Base64 encoded data]`), closing the only bridge for exporting rendered-image bytes to repository files. In-browser captures at all four required viewports were successfully produced with html2canvas inside correctly-sized same-origin iframes, but their bytes could not be exported.

**Substitute evidence provided instead, per row below:**

- **Programmatic viewport verification (all 4 required viewports)**: each route was loaded in a real same-origin iframe at exactly 390×844, 768×1024, 1440×900, and 1920×1080. Media queries genuinely fire at the iframe's viewport size. Measured: horizontal overflow (`scrollWidth` vs viewport), nav/header presence, H1 text, rendered text volume.
- **Reviewer visual inspection**: full-window screenshots (1920-wide) were captured and visually reviewed live by the reviewer for the pages marked "visually inspected"; findings recorded in the Findings column.

## Matrix — all rows verified at 390×844, 768×1024, 1440×900, 1920×1080

| Route | Family | Overflow-X (any viewport) | Verdict | Findings |
|---|---|---|---|---|
| `/` | Home | None | PASS | Visually inspected at 1920: hero (white on dark photo + scrim) correct; Core Areas cards use artwork + dark-navy text panel — V1.5's white-on-white defect confirmed FIXED; PLANNED badges honest |
| `/library` | Library | None | PASS | Card pattern correct |
| `/library/krishna-book` | Krishna Book | None | PASS with note | **DEF-V173-03**: H1 reads "Chapter timeline for Stories 001–007" — stale; 9 stories are published (cards correctly list 001–009) |
| `/library/srimad-bhagavatam` | Śrīmad-Bhāgavatam | None | PASS | Renders; planned-state labeling |
| `/knowledge` | Knowledge home | None | PASS | |
| `/knowledge/search` (q=Krishna) | Knowledge search | None | PASS | Search returns genuine results via real UI |
| `/learning/children-youth` | Children & Youth | None | PASS | 4 age bands render |
| `/sunday-school` | Sunday School | None | PASS | Weekly plan table renders |
| `/teachers` | Teachers | None | PASS | Class-pack composer functional |
| `/preachers` | Preachers | None | PASS with note | **DEF-V173-02**: axe `aria-required-children` (critical impact): `.scope-grid[role="list"]` contains `button[tabindex]` children not allowed under role=list |
| `/prabhupada-vani` | Prabhupāda Vāṇī | None | PASS | |
| `/printables` | Printables | None | PASS | Live assets 001–009; planned types honestly labeled |
| `/about` | About | None | PASS | Steward identity correct |
| `/contact` | Contact | None | PASS | mailto-only, no server upload |
| `/faq` | FAQ | None | PASS | |
| `/stories/001` | Story 001 | None | PASS with note | DEF-V173-01 (player selects contrast, below) |
| `/stories/009` | Story 009 | None | PASS with note | Visually inspected at 1920: title/PASS badge/waveform/tabs correct. **DEF-V173-01**: Speed + Sleep `<select>` controls #d5e0ec on #ffffff = 1.33:1 contrast (needs 4.5:1), axe serious — present on all story pages |

## Story 009 per-tab verification (each tab exercised live)

| Tab | Result | Evidence |
|---|---|---|
| Listen | PASS (with session-environment caveat) | Player renders, `data-playback-path="blob_ready"`, Play/±15s/Speed/Volume/Sleep/Bookmark/Download controls present; `preload="none"` by design. Live playback advance could NOT be demonstrated this session because the session browser's media pipeline is stalled for ALL audio (even a bare muted `new Audio()` on the direct URL goes `loadstart→stalled`, readyState 0 — including on Story 001, which is hash-unchanged since it passed live playback in the V1.5 UAT session). Asset independently verified: `narration.mp3` HTTP 200, 5,440,195 bytes, `audio/mpeg`, valid ID3 header |
| Read | PASS | Full Pūtanā narrative; poison/breast/fragrant-pyre/motherly-destination present; NO universe-in-mouth; Tṛṇāvarta appears ONLY in the Next Story Preview line (see DEF-V173-04) |
| Activities | PASS | Activity sheet: Open full tab / Download PDF / Open to print; PDF serves 200 |
| Coloring | PASS | Simple + detailed coloring images both load (naturalWidth > 0), serve 200 |
| Source | PASS | "Krishna Book — Chapter 6: Pūtanā Killed", author attribution, passage boundaries, provenance `bbt-source-derived`, `excerpt-needs-review`, reviewed-by present |
| Notes | PASS | localStorage-only family notes; Save/Export/Print/Clear controls |
| Teaching Reflections | PASS | Present within Notes tab; explicitly "never presented as Prabhupāda quotations" |
| Ślokas | PASS | Honest "not yet curated" placeholder; "no verse text invented"; Reveal-stubs control |

## Interaction checks

- Browser Back: `/stories/009` → `/stories/001` (correct). Forward: back to `/stories/009` (correct).
- `/stories/010`: renders unpublished-placeholder shell only ("A story in preparation"; no story text, no narration, no next-title leak); nav shows "← Story 009 / End of the currently published stories". Story 010 NOT published. (Note: returns HTTP 200 placeholder rather than 404 — content-safe; soft-404 by design.)
- Route inventory: 69 discovered public routes, all HTTP 200 on direct fetch; transient Next.js RSC-prefetch 503s investigated and confirmed benign (direct fetches consistently 200).
- Console: no application errors (only reviewer-injected axe preload warnings and an unrelated third-party extension logger).
