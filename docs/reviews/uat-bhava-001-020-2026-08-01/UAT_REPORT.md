# Bhāva Stories 001–020 — Independent Local Product UAT

| | |
|---|---|
| **Date** | 2026-08-01 |
| **Scope** | Stories 001–020, all seven tabs each; global navigation; security boundary; API matrix |
| **Web** | http://127.0.0.1:3000 |
| **API** | http://127.0.0.1:8000 |
| **Repository** | `C:\Development\Workspace\DevotionalRepo\krishna-story-factory` |
| **Method** | Independent browser UAT (Chrome, DOM + rendered assertions), direct API probing, artefact inspection of the built packages |
| **Code changes** | None. Read-only pass. No mutating API call was executed. |
| **Final verdict** | **FAIL — P1 remains** |
| **Production approval** | **NOT APPROVED** |

---

## 1. Build identity

| Item | Expected | Observed | Result |
|---|---|---|---|
| Release commit | `develop` @ `7ac66ff28945b8d449429a61d6894b181aa151fb` | Working tree at `de79223acaadc911f89c4080d4d1ff3c9ad745aa`, branch `release/bhava-001-020-quality-completion-v2` | **MATCH** |
| Relationship | — | `7ac66ff` is the merge commit of PR #28; its second parent is exactly `de79223`. The tree under test is byte-identical to the release branch tip that landed on `develop`. | OK |
| Content tag | `bhava-content-001-020-v2` | → `0668f271cafb3278ed770d2bed9540d30d149b36`, an ancestor of the tree under test | OK |
| Working tree | clean | `git status --porcelain` empty | OK |
| Site mode | public | **LOCAL** — `BHAVA_PUBLIC_SITE` unset and `NODE_ENV != production`, so `isPublicSite()` is `false` | ⚠ see §5 |

---

## 2. Verdict summary

| Severity | Count | Blocking |
|---|---|---|
| **P0** — security / data loss / site unavailable | **0** | — |
| **P1** — story unusable, missing text/audio/PDF/source, wrong pastime | **1** | **Yes** |
| **P2** — impaired UX or content quality | **10** | No |
| **P3** — cosmetic | **4** | No |

**FAIL — P1 remains.**

The platform is in good shape on almost every axis: all 20 stories deliver narration, full text, a rendering activity PDF, a complete coloring set and reviewed source attribution, and every one of the 200 API checks passes. The single blocker is **D-01: the Ślokas tab renders an empty stub on all twenty stories** while the API returns curated, reviewed verse references, working Vedabase links and child-friendly explanations. A shipped tab that shows nothing on 100 % of the catalogue — and that silently discards content already signed off by a named reviewer — is not a cosmetic gap.

**D-02** (rights and copyright metadata missing on 11 of 20 stories) is filed P2 because the Source tab still carries permissions language and reviewed status. For BBT-derived material the release owner may reasonably choose to treat it as blocking; that judgement is theirs, not mine.

---

## 3. What passed

Verified across all 20 stories unless noted.

**Library** — 20 cards, correct 001→020 sequence, no 021. Every card shows story number, collection, unique title, "For 6-12", and a poster that loads (`naturalWidth` 1024) with descriptive alt text.

**Story shell** — correct poster, title, chapter line ("Krishna Book Chapter N") and age band. Story 001 has no previous link; story 020 has no next link and no route to 021. `/stories/021` returns 404.

**Listen** — all 8 controls present and correctly labelled (Play, −15s, +15s, Speed, Volume, Sleep, Bookmark, Download). Exercised live on story 019: play advances `currentTime`; +15 s stepped 10.34 → 25.34 s; −15 s returned to 10.73 s; clicking the waveform at 50 % seeked to 137.4 s of 273.7 s; volume applied; `preservesPitch` is `true`; the recommended pace is honoured — stories 011, 014, 016, 018, 019 and 020 declare `recommended_playback_rate: 0.75` and the player loads at 0.75× with a "Recommended story pace" chip. Full story text is visible in the Listen pane, there is **no** false "story.md unavailable" message, and no internal production block (Poster Visual Brief, Coloring Visual Brief, Activity Data, voice IDs) leaks into the reader payload for any story.

**Read** — complete text, correct headings and paragraphs, Lessons, Think About It, Five-Star Challenge, Bedtime Prayer and Parent/Teacher Note on all 20. No HTML or Markdown corruption. IAST Unicode (ā ī ū ṛ ṇ ṭ ḍ ś ṣ ṁ ḥ) renders correctly throughout.

**Activities** — PDF.js loads on every story with a real page canvas (3.2 %–5.2 % ink coverage sampled across the full canvas — not a blank grey area). Page counts match the source PDFs exactly (001:3, 002:4, 003:3, 004:4, 005:4, 006:4, 007:4, 008:3, 009:4, 010–020:2). Next/Previous work and disable at the boundaries, zoom in/out works, fit-width rescales the canvas (459 px → 1075 px), the viewer is a focusable `role="region"` with an aria-label and ←/→ change pages. "Open full tab" opens the raw PDF in a new tab, "Download PDF" appends `?download=1`, "Open to print" is wired.

**Coloring** — poster, simple coloring and detailed coloring all load on all 20, with correct labels and alt text. Line art is clean, high-contrast and printable. Illustrations match the specific pastime on 19 of 20 — see D-10 for story 009.

**Source** — Krishna Book chapter mapping is correct end to end (1,1,1,1,2,3,4,5,6,7,7,7,8,8,8,8,9,10,11,12). Author is credited as "His Divine Grace A.C. Bhaktivedanta Swami Prabhupāda" on all 20, review status is "reviewed" with a named reviewer and date, permissions language is present, and every Vedabase link resolves to the correct chapter.

**Ślokas — honesty** — no verse text is invented anywhere. Sanskrit and transliteration fields are `null` rather than fabricated, and stories with no selected verse say so in the data. That part of the design is sound; the rendering is not (D-01).

**Notes** — typing autosaves ("Saved on this device"), the note survives a full page reload, Clear removes it from `localStorage`, and Export is wired to a Blob download. Confirmed **zero network requests** while typing — `fetch`, `XMLHttpRequest` and `sendBeacon` were all instrumented and none fired. Note text is stored only under `bhava:notes:NNN` in `localStorage`, matching the stated policy.

**Global** — Home, Library, Krishna Book, Learning dropdown (Children & Youth, Sunday School, For Teachers, For Preachers, Printables), Knowledge, Prabhupāda Vāṇī, About, Contact, FAQ and every footer link return 200 with an H1. `/blog` and `/vani` redirect correctly. `sitemap.xml` lists 63 URLs including stories 001–020 only — no 021, no `/studio`, no `/dev`. `robots.txt` disallows the private surface. No horizontal overflow at 1905 px on home, library or story pages. A "Skip to content" link is present, focus outlines are a solid 2 px, and two `prefers-reduced-motion: reduce` blocks exist.

**API matrix** — 20 stories × 8 endpoints = 160 requests, **all 200** with non-trivial payloads. Narration range requests return **206** with a correct `Content-Range` and `audio/mpeg` on all 20. Activity PDFs return **200 `application/pdf`** on all 20. Reflections are story-specific and meaningful (6 per story).

**Security** — `/stories/021` 404. `/api/v1/factory` and `/api/v1/scheduler` do not exist (404). `/api/v1/queue` and `/api/studio/*` 404. Mutating calls are denied: `POST /api/v1/local/scheduler/enable` and `POST /api/v1/local/generate-next` both return **403 `{"detail":"CSRF token required"}`**. No API keys, tokens or passwords appear in any public payload. No Windows or POSIX filesystem paths are exposed to public users in any story payload or rendered page.

---

## 4. Defect log

Full detail, evidence and suggested fixes are in the **Defect Log** sheet of the workbook. Summary:

| ID | Sev | Area | Stories | Defect |
|---|---|---|---|---|
| **D-01** | **P1** | Ślokas tab | **001–020** | Panel renders no reference, no Vedabase link and no child explanation on any story — only `Transliteration: —  Word-for-word: —  Translation: —`. The API returns all three fields. |
| D-02 | P2 | Rights metadata | 010–020 | No "Rights and Credits" section in `story.md` / Read tab; `web_manifest.rights` is `{}`; coloring pages carry no copyright footer. 001–009 have all three. |
| D-03 | P2 | Source tab | 001, 005, 006 | No Śrīmad-Bhāgavatam companion reference, although 17 of 20 stories have one and 001's own text cites SB Canto 10 Ch. 1. |
| D-04 | P2 | Ślokas provenance | 001, 005, 006 | Badge reads "REVIEWED" although `review_status` is `not_applicable` and no verse was selected. |
| D-05 | P2 | Ślokas granularity | 007–020 | References are chapter-only (SB 10.4 … SB 10.12) where 002–004 carry exact verse ranges. Flagged per brief. |
| D-06 | P2 | Story shell | 001–020 | Internal factory quality-gate value printed to public users as a green "PASS" chip beside the title. |
| D-07 | P2 | A11y — tabs | 001–020 | `role="tab"` without `aria-controls`, no panel `id`/`aria-labelledby`, Arrow keys do not move focus between tabs. |
| D-08 | P2 | A11y — audio seek | 001–020 | Waveform seeking is mouse-only: `<canvas role="img">` with no `tabindex` and no slider semantics. |
| D-09 | P2 | Follow-along sync | 001–020 | `/sync` returns `cues: []`, `status: needs_alignment` catalogue-wide. Honestly surfaced in the UI as "Follow-along cues pending review". |
| D-10 | P2 | Illustration match | 009 | Poster and both coloring pages for the Pūtanā story show a peaceful garden scene; the named pastime is not depicted. Reads as a deliberate child-safe substitution. |
| D-11 | P2 | Privacy | 001–009 | Public `/web-manifest` exposes a personal `contact_email` inside the rights dossier. |
| D-12 | P3 | Poster typography | 019; 001–006, 008 | 019's baked-in title clips ("and Bakasura" cut by the artwork); title type scale is inconsistent across the poster set. |
| D-13 | P3 | PDF viewer | 001–020 | "Fit width" rescales correctly but the zoom percentage readout keeps its previous value. |
| D-14 | P3 | Transliteration | 004, 006, 007, 017–020 | IAST applied inconsistently — Pūtanā/Kṛṣṇa/Yaśodā in 009–016 vs Yasoda/Nalakuvara/Aghasura in 017–020. |
| D-15 | P3 | robots.txt | site-wide | `/api/v1/local` is not disallowed, although it is reachable and returns operational state. |

### D-01 in detail (the blocker)

`GET /api/v1/stories/020/shlokas` returns:

```json
{ "shlokas": [ { "reference": "SB 10.12 — Aghāsura",
                 "url": "https://vedabase.io/en/library/sb/10/12/",
                 "sanskrit": null, "transliteration": null,
                 "child_explanation": "The serpent-demon Aghāsura opens a cave-like mouth to swallow the boys. Kṛṣṇa enters and protects everyone in a gentle, child-safe way.",
                 "review_status": "reviewed", "reviewer": "…" } ],
  "status": "…", "note": "…" }
```

The rendered panel shows only `REVIEWED — Transliteration: —  Word-for-word: —  Translation: —`.

Root cause is in `apps/web/components/story-experience.tsx` (≈ L826-853). The verse map renders exactly four fields — `sanskrit`, `transliteration`, `word_for_word`, `translation` — and never reads `reference`, `url` or `child_explanation`. Because the Sanskrit fields are deliberately `null` (correct — nothing invented), every branch resolves to an em-dash and the panel is empty on every story.

**Fix:** render `verse.reference` as the panel heading, `verse.child_explanation` as body copy, and `verse.url` as a "Read on Vedabase" link. Keep the em-dash stubs only for the Sanskrit fields that are genuinely absent.

Evidence: `evidence/04-story001-slokas-empty-P1.jpg`.

---

## 5. Not verified — public-mode security gating

The instance under test is running in **LOCAL** mode. `apps/web/middleware.ts` gates `/studio`, `/dev`, `/api/studio`, `/api/v1/factory`, `/api/v1/scheduler` and `/api/v1/queue` behind `isPublicSite()`, which returns `false` unless `BHAVA_PUBLIC_SITE` is truthy or `NODE_ENV === "production"`. Neither holds here.

Consequently:

| Check | Required | Observed here | Status |
|---|---|---|---|
| `/studio` unavailable in public mode | 404 | **200** (local mode — intended) | **NOT VERIFIED** |
| `/dev` unavailable in public mode | 404 | **200** (local mode — intended) | **NOT VERIFIED** |
| `/api/v1/local/*` not public | n/a | 200 GET; `loopback_only: true`, `factory_actions_enabled: false`; mutations 403 | **NOT VERIFIED** |
| Content-Security-Policy header | set | absent (middleware only sets CSP in public mode) | **NOT VERIFIED** |

Static review of the middleware shows the gating logic is present and also returns 405 for non-GET `/api/*` in public mode. One point deserves attention: **`/api/v1/local` is not in `PRIVATE_PREFIXES`.** In public mode it would therefore not be 404'd by the middleware; it is protected instead by the API's own loopback-only binding and CSRF requirement. Confirm that is the intended defence and that it holds behind a reverse proxy.

**These four rows can only be closed by re-running against an instance started with `BHAVA_PUBLIC_SITE=1`.** I did not restart the server, per the no-modification constraint.

Other limitations: the automation browser window could not be resized (`innerWidth` stayed 1920), so small-viewport mobile **layout** was not rendered — mobile nav toggle behaviour and the presence of 640–960 px breakpoints were verified instead. Audio was verified functionally, not listened to. No physical print was produced and no full WCAG contrast sweep was run.

---

## 6. Recommended path to approval

1. Fix **D-01** and retest the Ślokas tab on all 20 stories.
2. Decide on **D-02** — regenerate the rights dossier for 010–020, or record an explicit exception. Add a publish gate that fails when `web_manifest.rights` is empty.
3. Re-run the security block with `BHAVA_PUBLIC_SITE=1` to close the four NOT VERIFIED rows, and confirm the intended handling of `/api/v1/local` in public mode.
4. Run a real small-viewport mobile pass.
5. Treat D-03 through D-15 as a post-release backlog unless the release owner decides otherwise.

---

## 7. Evidence pack

| File | Contents |
|---|---|
| `BHAVA_UAT_001-020_Evidence_Matrix.xlsx` | Story Matrix (one row per story, 18 columns) · API Matrix · Defect Log · Global & Security · Verdict · Limitations |
| `evidence/01-library-krishna-book.jpg` | Library grid, cards 001–004 |
| `evidence/02-story001-shell-player.jpg` | Story 001 shell — poster, title, tabs, player, no previous link |
| `evidence/03-story001-activities-pdfjs.jpg` | PDF.js rendering real activity-sheet content |
| `evidence/04-story001-slokas-empty-P1.jpg` | **D-01** — empty Ślokas panel |
| `evidence/05-home.jpg` | Home page |
| `evidence/06-story019-recommended-pace.jpg` | Recommended 0.75× pace applied; prev + next present; "PASS" chip (D-06) |
| `evidence/posters_contact_sheet.png` | All 20 posters — pastime match review |
| `evidence/coloring_contact_sheet.png` | All 20 detailed coloring pages — pastime match and print quality |
| `evidence/poster_headers.png` | **D-12** — 019 title clipping, 001/002 title scale |
