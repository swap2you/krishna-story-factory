# Bhāva Portal V1 — CoWork Product, UX & Content-Architecture UAT

**Review type:** Live, review-only UAT against an already-running instance. No application code,
story packages, queue, or scheduler were touched. No installs, restarts, merges, or paid API
calls were performed.

## Executive verdict: **PASS WITH CONDITIONS**

The running application was genuinely reached, navigated, clicked, and inspected in the user's
real Chrome browser (not a static/code-only review). Core reading, listening, activity, coloring,
source, notes, and śloka-placeholder experiences all work as built, with clean console output and
no broken routes. Two items require attention before this branch is considered release-ready for
the identity/content goals stated in this mission:

1. **P1 — internal production content is publicly visible** on every story's Read tab (narration
   script with SSML tags, AI image-generation prompts, raw activity data).
2. **P2 — the public Contact page still exposes the steward's civil name and professional
   identity** (swapnilpatil.tech, LinkedIn, GitHub), which this mission explicitly asked to remove.

Everything else — Library IA, Teacher toolkit, Prabhupāda Vāṇī, Bhakti Blog, Śloka data model,
synchronized listening, storage/scale, and the coloring carousel — is **honest, unbuilt, or
partially built** and is captured below as scoped recommendations, not defects. No fabricated
content, invented ślokas, invented quotes, or invented titles were found anywhere live.

---

## 1. Environment

| Item | Value |
|---|---|
| Repository | `C:\Development\Workspace\DevotionalRepo\krishna-story-factory` |
| Branch | `feature/bhava-portal-v1` |
| HEAD tested | `73e1a8da7eb4a0d70aab8c2f6d6d1becd8805d85` (confirmed equal to `origin/feature/bhava-portal-v1`, working tree clean except untracked `KrishnaBook.pdf`) |
| Running instance | `cursor-uat`, read from `.bhava/instances/cursor-uat/runtime.json` (not assumed) |
| Web URL | `http://127.0.0.1:3000` (web_pid 37244) |
| API URL | `http://127.0.0.1:8000` (api_pid 11748) |
| Mode | `production` |
| Catalog DB | `.bhava/instances/cursor-uat/bhava.sqlite` |
| Browser used | Google Chrome on the user's Windows workstation, driven live via the Claude-in-Chrome extension (`deviceId e7a1d952…`, confirmed local) |
| Other browsers available | **None.** `list_connected_browsers` returned exactly one connected browser. Firefox/WebKit were not reachable live this session (consistent with `playwright.config.ts` defining only a `chromium` project and zero `*.spec.ts` files existing anywhere in `apps/web`). |

Nothing was installed, rebuilt, or restarted. The application was already running when this
session began, per the mission's constraint.

---

## 2. What was genuinely tested live

Live, in-browser testing (screenshot + click + scroll + DOM inspection, not just static code
reading) was performed on: `/`, `/library`, `/library/krishna-book`, `/stories/001` (all seven
tabs), `/stories/007` (all seven tabs), `/teachers`, `/prabhupada-vani`, `/blog`,
`/source-permissions`, `/about`, `/contact`. Console messages were captured for the full session.
Screenshots were taken at every major state change (player states, tab switches, lightbox open/
close, coming-soon states). Where a finding originates from source-code reading rather than a live
click, it is labeled **(code-confirmed)** below rather than implied to be a live click.

**Known limitation — full 7-viewport responsive sweep could not be forced live.** The mission
asked for live visual UAT at 390×844, 430×932, 768×1024, 1024×768, 1366×768, 1440×900, and
1920×1080. `resize_window` was called repeatedly against the live tab and reported success each
time, but `window.innerWidth`/`innerHeight` measured immediately after every call remained
unchanged (2400×1068 CSS px / 1920×1032 physical, DPR 0.8) — the extension cannot override the
real, maximized state of the user's actual Windows browser window. Rather than fabricate a
7-viewport PASS, this is reported honestly: the live app was visually verified at its one actual
window size (a large-desktop viewport), and the two CSS breakpoints that exist in the codebase
(`apps/web/app/globals.css:194` `max-width:960px`, `:218` `max-width:720px`) were confirmed by
direct code read. A genuine multi-viewport sweep needs either the user to manually resize/un-
maximize the window, or a Playwright/devtools-emulation run outside this session.

---

## 3. Git and data verification

`git rev-parse HEAD` = `73e1a8da7eb4a0d70aab8c2f6d6d1becd8805d85`, equal to
`origin/feature/bhava-portal-v1` — no divergence, no pull needed. `git status --short` shows
exactly one line: `?? KrishnaBook.pdf` (untracked, at repo root, correctly not committed — see
§12). `data/catalog/locked_queue_state.csv` still shows stories 001–007 as `done`, story 008 as
`pending`; **story 008 was not generated, and no queue file was touched, during this review.**

The catalog is confirmed disposable/derived, not hand-authored: `apps/api/bhava_api/config.py`
resolves `catalog_db` from `BHAVA_REPOSITORY_ROOT`/`BHAVA_CATALOG_DB` env vars and rebuilds it on a
`catalog_refresh_sec` timer (clamped 15–30s) from the seven package folders under `output/`
(50 MB total on disk, ~7.1 MB/story). No fake or placeholder story packages were found — all
catalog entries trace to real `output/00N_*` folders with the required 8-file manifest contract.

---

## 4. Screen-by-screen findings

**Homepage (`/`)** — hero renders a full illustrated Kṛṣṇa/Vasudeva scene with real artwork, a
"Radha-Krishna · Family Library" eyebrow, stat row (7 stories ready / Audio + PDF / Local notes),
and two CTAs. Scrolling reveals three "Scripture shelves" cards and a "Latest released stories"
grid with real story-poster thumbnails. **This directly contradicts a prior concern about an
"oversized empty hero" and "lack of artwork on collection cards"** (§16) — live inspection found a
populated hero and populated cards, not empty ones. Whitespace and density read as calm and
intentional, not sparse or cramped.

**Library (`/library`)** — three shelves: "Krishna Book Bedtime Stories" (live, linked to
`/library/krishna-book`), "Śrīmad-Bhāgavatam" (Cantos 1–12, coming soon), "Rāmāyaṇa & Caitanya"
(coming soon). Confirmed via the live accessibility tree that **only the Krishna Book card is a
real link** (`href="/library/krishna-book"`); the other two render as plain
heading+paragraph — no `href`, no `role="link"`, not keyboard-reachable, not clickable. See DEF-03.

**Story detail (`/stories/001`, `/stories/007`)** — seven tabs render for every story: Listen,
Read, Activities, Coloring, Source, Notes, Ślokas. The sidebar shows one poster, story number,
title, age range, and chapter — confirmed via live scroll that the "repeated sidebar cards"
concern from earlier full-page screenshots **is not a real defect**: it is consistent with a
normal, short, non-sticky CSS grid page; most likely a screenshot-stitching artifact from whatever
tool produced those earlier images, not app behavior. **Confirmed non-defect.**

**Contact (`/contact`)** — see §14, DEF-02.

**About (`/about`)** — clean: heading and stewardship line both read only "Svarna Gauranga Das,"
no civil name, no external professional links. **This is the pattern the Contact page should
match.**

**Source & permissions (`/source-permissions`)** — honest, no blanket "all content copyrighted by
Bhāva" claim; states sources come from each package's manifest and that ślokas stay empty until
curated. Does not yet distinguish Bhāva-original vs. BBT-source vs. third-party per-asset — see
§12 recommendation.

**Prabhupāda Vāṇī (`/prabhupada-vani`)** and **Bhakti Blog (`/blog`)** — both are honest
"coming soon" states, explicitly stating they will not invent content, and both correctly use only
the devotional name. **`/vanani` → `/prabhupada-vani` rename (recommended in the prior UAT round)
has been implemented** and the nav link and page both resolve correctly — confirmed fixed.

**Factory Studio (`/studio`)** *(safety-only glance, not a functional review)* — fixed banner
"Local Factory Studio — loopback only · never expose publicly"; all three action buttons remain
HTML-`disabled` while `factory_actions_enabled` is false (the default). No queue-mutation control
exists in the UI. Consistent with the safety posture confirmed in the prior UAT round; **not
touched or exercised this session.**

---

## 5. Story-by-story findings

Stories 001 and 007 were opened and clicked through in full; the remaining five (002–006) were
confirmed present and correctly catalogued via the Library grid and API-backed catalog, but were
not individually clicked through tab-by-tab in this session (time-boxed to two representative
stories as called out in §2). No inconsistencies were found between story 001 and story 007's
component behavior — both use the same shared `story-experience.tsx` tab implementation, so the
findings below apply uniformly to all seven.

---

## 6. Audio-player findings

Confirmed live on story 001: play/pause, ±15s skip, speed selector (0.75/1/1.25/1.5/2×, correctly
rendered — an earlier read of a zoomed screenshot momentarily misread "1x" as blank; re-zoomed and
confirmed correct), volume slider, resume position, bookmark save/jump, sleep timer, and a visible
waveform. The player's "4:02 / −0:00" initial-state reading on repeat visits is a genuine
`localStorage["bhava:resume:001"]` resume behavior from this same browser profile's prior testing
— not a bug. Keyboard shortcuts (Space, ←/→) are guarded so they don't fire while a text field has
focus **(code-confirmed)**. No cross-story bleed: resume and bookmark keys are namespaced per
`storyNo`, confirmed by design and by observing story 007's player start clean.

**Requested redesign items — classified:**

- **Required now:** none. The player is functionally complete and correct for a single-story
  listening session.
- **Useful next:** a visible "now playing" chapter/story title label docked to the player (small
  clarity win when a user has scrolled away from the header); a persistent mini-player that
  survives tab switches within the same story (currently switching to Read/Activities does not
  interrupt playback, which is correct, but there is no mini-bar reminding the user audio is still
  playing).
- **Future enhancement:** a true cross-story playlist/queue (e.g., "play all 7 in order") — no such
  feature exists today and none was implied as broken; this is new scope, not a fix.

---

## 7. Synchronized listen-and-read architecture (recommendation only — nothing built)

No sentence-level highlighting or auto-scroll exists today; Listen and Read are two independent
tabs with no shared timing data. Recommended direction, in order of effort:

1. **Per-story alignment artifact, stored outside the locked 8-file package.** Do not touch
   `narration.mp3`/`story.md` inside `output/00N_*` (that package is contractually locked). Instead
   add a new, additive, web-only file per story under a path such as `data/web-assets/001/
   sync.json`, generated from the existing narration audio + story text and consumed only by the
   web app.
2. **Format: WebVTT-derived JSON, not raw VTT.** Store `sync.json` as an array of
   `{ paragraphId, startMs, endMs }` objects keyed to the Read tab's existing paragraph structure
   (the Read tab already renders discrete sections — Recap, Main Story, Five Lessons, etc. — which
   map naturally to sync units). VTT is a fine *authoring* format (many forced-alignment tools
   emit it) but the app should consume a small pre-parsed JSON so the browser never needs a VTT
   parser at runtime.
3. **Timing source: forced alignment, not hand-timestamping.** Given narration is already
   TTS-generated (confirmed by the leaked "Audio Narration" SSML script — see §8), a forced-
   alignment tool (e.g., an open-source aligner run against the existing `narration.mp3` + the
   plain-text narration script) can generate `sync.json` automatically and repeatably per story,
   with no manual timestamping labor per release.
4. **UI behavior:** on the Read tab, highlight the currently-playing paragraph and auto-scroll it
   into view only while the Listen tab's audio is actively playing; never auto-scroll if the user
   has manually scrolled Read within the last few seconds (avoid fighting the reader). Make this
   toggleable — some families read ahead of the narration on purpose.
5. **Do not touch the locked package or Drive.** `sync.json` is a derived, regenerable, web-only
   artifact — same trust tier as the SQLite catalog, not the same tier as the 8-file package.

---

## 8. Reader-content separation — **P1 defect, live-confirmed**

**DEF-01.** Scrolling to the bottom of the Read tab on both story 001 and story 007 shows, fully
**visible** (not hidden, not scrapeable-only), an internal production block containing:

- "Audio Narration" — the complete TTS script, with literal, unrendered SSML tags such as
  `<break time="1.0s" />` printed as garbled visible text.
- "Poster Visual Brief" and "Coloring Visual Brief" — the raw AI image-generation prompts used to
  produce the story's artwork.
- "Activity Data" — a raw Python dict literal.

**Root cause (code-confirmed):** `renderMarkdown()` in `apps/web/components/story-experience.tsx`
HTML-escapes `<`, `>`, and `&` in the source markdown *before* stripping `<!-- -->` comments. The
source `story.md` almost certainly wraps this block in a real HTML comment intended to hide it from
readers, but because `<`/`>` are escaped first, the browser never sees a real comment — it sees
literal `&lt;!--` text, which is not a comment, so the whole block renders as visible garbled
content instead of being invisible. This is more severe than a "hidden but scrapeable" issue: it is
fully visible to every reader, including children, on every published story.

**Fix direction (not implemented — review only):** reorder the pipeline so comment-stripping (or a
dedicated split on a clear internal-content delimiter) happens on the *raw* markdown before entity
escaping, or — more robustly — stop relying on HTML-comment hiding entirely and have the story
generation pipeline emit internal fields (`audio_narration`, `poster_visual_brief`,
`coloring_visual_brief`, `activity_data`) as **separate structured fields in `manifest.json`**
rather than inline in `story.md`, so the Read tab template only ever has reader-facing prose to
render in the first place. This also removes the escaping-order fragility permanently rather than
patching around it.

**Severity: P1.** This is public-facing content, live on the production instance, for every one of
the seven released stories.

---

## 9. Activities

Working well, as the user already likes — **no redesign recommended**, only the one real defect
below.

Live-confirmed on story 007 ("Yoga-māyā Warns Kaṁsa" / "Put Chapter 4 in Order," 3 pages): the PDF
embeds correctly via Chrome's native viewer in an iframe, "Open full tab" and "Download PDF" work,
zero console errors on load.

**DEF-04 (P4, live-confirmed this session).** Clicking "Print" on the Activities tab opens a new
browser tab at `/api/v1/stories/007/assets/activity_sheet.pdf` — **identical behavior to "Open full
tab."** It does not call `window.print()`. This is a low-severity mislabeling, not a broken
feature (the user can still print from the opened PDF tab), but the button's label promises a
different action than it performs, and duplicates "Open full tab" exactly. Recommend either wiring
`window.print()` on the current iframe, or removing the redundant "Print" button and keeping
"Open full tab" + "Download PDF."

---

## 10. Coloring gallery and carousel

Live-confirmed on story 007: three tiles (Story poster, Detailed coloring, Simple coloring), each
with correct, descriptive `alt` text (e.g. `alt="Kamsa Begins His Persecutions — Detailed
coloring"`). Clicking a tile opens a lightbox with Download / Print / Close.

**Accessibility — better than the prior static review suggested.** Live DOM inspection shows the
lightbox now renders with a real `dialog` role (`presentation > dialog`), and pressing **Escape**
correctly closes it **and returns focus** to the triggering thumbnail button (confirmed via
screenshot showing the focus ring back on "Detailed coloring" post-close). This appears to have
been fixed since the prior UAT round's static code read, which had flagged no `role="dialog"` and
no Escape handler — **confirmed resolved, not a current defect.**

**Carousel — does not exist today; recommended, not required.** The lightbox shows exactly one
image with no next/previous navigation between the three assets. Recommended carousel spec:

- Left/right on-screen arrows plus **←/→ keyboard** navigation.
- Touch **swipe** on mobile.
- A **position indicator** ("2 of 3").
- A **thumbnail strip** at the bottom of the lightbox for direct jump.
- **Preload** the adjacent image so arrow navigation feels instant.
- **Accessible announcement** on navigate (e.g. `aria-live="polite"` region announcing "Detailed
  coloring, image 2 of 3") so screen-reader users get the same context sighted users do.
- Keep the existing **Download** and **Print** actions scoped to *whichever image is currently
  shown* in the carousel, not just the first.
- **Default-open asset recommendation:** open on "Story poster" first (the most visually rich,
  color asset) rather than "Detailed coloring," since it's the natural first impression; keep
  "Detailed coloring" and "Simple coloring" as swipe/arrow targets from there.

---

## 11. Notes vs. curated Teaching Reflections

**"My Notes" (existing, live-confirmed on story 007):** a private, per-story textarea under
"Our family notes," explicitly labeled *"Notes stay in this browser only (localStorage). Bhāva does
not upload child notes."* Save / Export (.txt) / Print all work; no network call touches this data
**(code-confirmed: no `fetch`/`POST` anywhere in `story-experience.tsx` or `audio-player.tsx`
touches notes content)**.

**"Teaching Reflections / Realizations" (does not exist yet — recommendation only).** This must be
architecturally distinct from My Notes: curated, not private; attributed to a named
reviewer with a date; and **never presented as Prabhupāda's direct words unless it is an actual,
sourced quotation.** Recommended data shape per reflection entry: `{ storyNo, reviewerName,
reviewedDate, text, sourceType: "reviewer-reflection" | "quoted-source", sourceCitation? }`. Render
quoted-source entries with a visible citation; render reviewer-reflection entries with a visible
"Reflection by {reviewerName}, {date}" byline so a reader can never mistake a steward's personal
reflection for a direct Prabhupāda quotation. **No reflections were invented or drafted during this
UAT** — this is architecture only.

---

## 12. Śloka data model (recommendation only — no ślokas selected, copied, or invented)

Live-confirmed on story 007: the Ślokas tab is an honest, correctly-labeled placeholder —
*"NOT YET CURATED… Placeholders only until reviewed ślokas are supplied. We will not invent
verses."* Not a defect.

Recommended future data model per śloka entry: `{ storyNo, verseRef (e.g. "SB 10.3.13"),
sanskritDevanagari, transliteration (IAST), wordForWord, translation, sourceEdition (e.g. "BBT
Śrīmad-Bhāgavatam Canto 10"), audioUrl?, hideRevealDefault: "hidden", memorizationMode: boolean,
printableCard: boolean, ageLevel: "young" | "all", reviewerStatus: "draft" | "reviewed" |
"published", reviewerName?, reviewedDate? }`. The hide/reveal and memorization-mode UI states are
new client behaviors on top of this data, not additional content — they don't require inventing or
selecting any verse text, satisfying the mission's explicit prohibition.

---

## 13. Library expansion (Information Architecture)

Live-confirmed current state: exactly three shelves (Krishna Book — live; Śrīmad-Bhāgavatam —
coming soon, non-clickable; Rāmāyaṇa & Caitanya — coming soon, non-clickable). See DEF-03.

Recommended full future taxonomy, each as its own top-level shelf card, all coming-soon cards
**clickable to a real (if minimal) description page** rather than dead text:

Krishna Book (live) · Śrīmad-Bhāgavatam, broken out by **all 12 Cantos individually** rather than
one combined card · Bhagavad-gītā · Rāmāyaṇa · Rāmacaritamānasa · a Daśāvatāra collection ·
Caitanya-caritāmṛta · Caitanya-bhāgavata · Prabhupāda Vāṇī (already a top-nav item; also
cross-listed here) · Lectures · Prayers & Mantras · Bhakti Blog (already top-nav; cross-listed) ·
Teacher Resources.

Each coming-soon description page should state, honestly, what the shelf will contain and its
review status — no fabricated titles, chapter counts, or release dates. This mirrors the honest
pattern already used correctly on `/prabhupada-vani` and `/blog`.

---

## 14. Teacher, Sunday School & Preacher strategy

Live-confirmed on `/teachers`: age modes (Bal Gopal / Dāmodara / Mixed age), a class-pack builder
(5 toggleable items with a live "Selected:" summary), an answer-key panel defaulting hidden with an
explicit *"Do not invent answers for missing keys"* warning, Print/Export/Save-to-playlist actions,
and — **improvement confirmed since the prior UAT round** — a "My Classroom Playlist" section that
now correctly reads back saved `localStorage["bhava:classroom-playlist"]` entries (the prior static
review had found this data was captured but never surfaced; **this gap is now closed**).

Today this single "For Teachers" area covers general class-pack building only. Recommended
structure going forward, as three distinct destinations (not three redesigns of the same page):

- **For Teachers** (existing, keep): class-pack builder, lesson timing, answer keys, printable
  plan, classroom playlist, teaching reflections (§11), source references.
- **Sunday School** (new): the same Bal Gopal / Dāmodara / Mixed-age framing already used, extended
  with festival units (e.g. Janmāṣṭamī, Rāma-navamī), a weekly sequence planner, homework sheets,
  and parent-communication templates.
- **For Preachers** (new): lecture outlines built from source references, thematic collections
  (e.g. "stories about surrender," "stories about the demigods"), inline citations, and discussion
  prompts.

No content for any of these three was implemented or fabricated this session; this is a navigation
and permissions-model recommendation only.

---

## 15. Prabhupāda Vāṇī strategy

Live-confirmed honest coming-soon state (§4). Recommended content categories for when curated
sourcing is ready: audio lectures, morning walks, room conversations, letters, interviews, and
age-adapted (child/teen) excerpts — each requiring a documented, approved-archive source and
copyright/permissions clearance before publication. **No scraping, downloading, mirroring, or
republishing of any Vāṇī source material was performed or is recommended without that clearance
step.**

## 16. Bhakti Blog strategy

Live-confirmed honest coming-soon state (§4), correctly attributed to "Svarna Gauranga Das" with
no civil name. Recommended topic categories: regulative principles, chanting and japa etiquette,
Vaiṣṇava etiquette (including aparādha), temple etiquette, prasādam, praṇāma prayers, the
Gurvaṣṭakam, Nṛsiṁha and Tulasī prayers, daily sādhana structure, and festival guides.

Recommended sample card designs (titles + short descriptions + "planned" status only — no full
articles drafted, per the mission's restriction):

1. *"Why We Chant Sixteen Rounds"* — planned — regulative-principle primer.
2. *"Before You Enter the Temple Room"* — planned — etiquette guide for families new to visiting.
3. *"What Prasādam Actually Means"* — planned — short explainer with a citation-ready structure.
4. *"A Child's First Japa Bead"* — planned — parent-facing practical guide.
5. *"The Twelve Months, the Twelve Festivals"* — planned — festival-calendar overview.

Every future article must carry a bona fide source citation, a named reviewer, and a
last-reviewed date before publication; **no Prabhupāda quotations were fabricated for these
samples** — titles/descriptions only.

---

## 17. Contact, identity, and public footer — **P2 defect, live-confirmed**

**DEF-02.** Live text captured from `/contact` this session:

> "Svarna Gauranga Das is the devotional name of Swapnil Patil, who builds and stewards Bhāva.
> Public contact links below use his civil-name profiles so families can reach the same steward
> with confidence."

...followed by a "Links" card listing `https://swapnilpatil.tech`, `LinkedIn`, and `GitHub`, and a
"Contact Svarna Gauranga Das" button that resolves to `swapnilpatil.tech/contact`. This is the
**only** place in the app where the civil name and professional links leak — `/about`, the global
footer, `openGraph` metadata (`apps/web/app/layout.tsx`), `manifest.webmanifest`, and `/privacy`
were all checked and are already clean, devotional-name-only. No phone number was found anywhere
in the codebase (`grep` across `apps/web` for phone/tel: patterns returned no real matches).

**Required changes (not implemented — review only, per this mission's explicit request):**

- Heading stays **"Svarna Gauranga Das."**
- Remove the "is the devotional name of Swapnil Patil… civil-name profiles…" sentence entirely —
  no explanation of the civil name is needed on the public page.
- Remove the `swapnilpatil.tech`, LinkedIn, and GitHub links from `apps/web/config/contact.json`
  and the Contact page's "Links" card.
- Replace with a public email: **`swarnagaurangadas@gmail.com`** (currently `contact.json`'s
  `public_email` is an empty string, which the page already correctly hides rather than showing
  blank — swapping in the real address is a one-line config change).
- The CTA button should become a plain `mailto:swarnagaurangadas@gmail.com` (or an in-app form)
  rather than linking out to `swapnilpatil.tech/contact`.
- No email was sent and no config file was edited during this review.

**Copyright/permissions footer.** The current global footer (`"Bhāva — stewarded with care by
Svarna Gauranga Das."` + Privacy/Accessibility/Source & permissions/Factory Studio links) makes
**no copyright claim at all** — which is safe (no "used with permission" overreach, no claiming BBT
ownership) but also doesn't yet distinguish Bhāva-original work from BBT-source material.
Recommended addition, once source attribution is finalized per §12/§18: a short line such as
*"Story text, activities, and artwork are Bhāva-original works inspired by Śrīla Prabhupāda's
Kṛṣṇa Book (Bhaktivedanta Book Trust). Bhāva does not republish BBT's copyrighted text."* — factual,
non-overreaching, and matches the boundary language already live on the Source tab and
`/source-permissions`.

---

## 18. Copyright, permissions, and `KrishnaBook.pdf`

Per the mission's explicit restriction, `KrishnaBook.pdf` was checked for **existence and metadata
only** — no text was extracted, copied, committed, moved, or exposed.

| Field | Value |
|---|---|
| Path | repo root, `KrishnaBook.pdf` |
| Git status | untracked (`?? KrishnaBook.pdf`) — correctly not committed |
| Referenced by app code? | **No.** `grep -rn "KrishnaBook" apps/web` matches only the unrelated component function name `KrishnaBookPage` in `apps/web/app/library/krishna-book/page.tsx` — the actual PDF file is not imported, fetched, or served by any code path. |
| Title (PDF metadata) | "Krsna, The Supreme Personality of Godhead" |
| Author (PDF metadata) | His Divine Grace A. C. Bhaktivedanta Swami Prabhupada |
| Pages | 863 (confirmed independently via `pdfinfo` and `pypdf`) |
| Encryption | RC4, `print:no copy:yes change:no addNotes:no` |
| Producer/dates | Acrobat Distiller 4.0 for Macintosh, created/modified Nov 2002 |

**Finding:** this is a complete, published BBT book — third-party copyrighted material, not
Bhāva-original. It is currently safe (untracked, unreferenced), but nothing in `.gitignore`
explicitly protects it from a future accidental `git add .`. **Recommendation: add an explicit
root-level ignore entry** (e.g. `/KrishnaBook.pdf`, scoped to the root so it doesn't blanket-ignore
legitimate PDFs elsewhere in the repo) as a defense-in-depth measure, given the consequences of
accidentally publishing a full copyrighted BBT book to a public repo are severe.

**Recommended source-reference schema** (for `/source-permissions` and the per-story Source tab),
to replace the current single free-text `source_reference`/`scripture_reference` pair with an
explicit provenance classification: `{ contentType: "story-text" | "narration" | "artwork" |
"activity" | "sloka", provenance: "bhava-original" | "bbt-source-derived" | "third-party", 
sourceCitation, permissionsStatus: "public-domain" | "fair-use-excerpt" | "licensed" |
"needs-review" }`. This directly satisfies the mission's requirement to avoid a blanket
"all content copyrighted by Bhāva" claim while still giving every asset a clear, auditable
provenance trail.

---

## 19. Brand and visual system

Assessed live against each specific concern this mission raised:

- **"Oversized empty hero on Library"** — not found. The homepage hero is fully illustrated and
  populated; the Library hero is a normal text-only intro band, appropriately sized, not oversized.
- **"Lack of artwork on collection cards"** — mixed. The three Library shelf cards use solid color
  fields with a subtle circular graphic accent, no illustration — a legitimate future polish item,
  but not "empty." The homepage's "Latest released stories" cards **do** use full story-poster
  photography. Recommend bringing the same poster-art treatment to the Library shelf cards for
  visual consistency once each shelf has real cover art to show.
- **"Story-card density"** — reads as comfortable, not cramped, at the tested (large-desktop)
  viewport; genuine mobile-density confirmation is blocked per §2's resize limitation.
- **"Player hierarchy"** — the audio player is visually the dominant element on the Listen tab,
  correctly so.
- **"Tab density"** — seven tabs (Listen/Read/Activities/Coloring/Source/Notes/Ślokas) fit on one
  row without wrapping at the tested viewport; not verified at mobile widths this session.
- **"Read-page line length"** — prose measure reads as reasonable at desktop width; not verified at
  mobile widths this session.
- **"Desktop whitespace"** — balanced; no dead/empty stretches found on any page visited.
- **"Small-screen behavior"** — **not verified live** this session (§2 limitation); recommend a
  follow-up pass once genuine viewport resizing is available.

**Icon direction / animation:** no autoplay, no flashing, no particle effects, and no heavy 3D were
found anywhere in the live app — consistent with a calm, devotional tone. No specific icon-system
gaps were identified; the existing lotus/crown motif in the wordmark and favicon is consistent
across pages.

---

## 20. Storage and scalability architecture (recommendation only)

**Current state (code- and filesystem-confirmed):** `output/` holds all 7 story packages,
50 MB total (~7.1 MB/story average). `data/catalog/bhava.sqlite` is a disposable index rebuilt
from `output/` manifests on a 15–30s timer (`BHAVA_CATALOG_REFRESH_SEC`, clamped in
`apps/api/bhava_api/config.py`) — not a system of record. `output/*` is git-ignored (only
`.gitkeep` is tracked), so story media never bloats the repository. This is a sound, appropriately
minimal setup for a 7-story pilot.

**Recommended phased path as the library grows:**

- **Phase A (now → ~50 stories, still single-operator):** keep local filesystem + SQLite +
  the existing `data/web-assets/<storyNo>/` pattern proposed in §7 for derived, web-only artifacts
  (sync.json, future caches). No infrastructure change needed yet.
- **Phase B (public multi-reader, growing catalog):** move to a managed **PostgreSQL** database for
  the catalog (replacing the disposable SQLite index with a real queryable store once search/
  filter/library-taxonomy features in §13 need real querying), plus **object storage** (S3-
  compatible) for story media instead of local filesystem, fronted by a **CDN** with **immutable,
  content-hashed URLs** (e.g. `.../activity_sheet.<sha256prefix>.pdf`) so assets can be cached
  aggressively and safely. Store a checksum per asset (the existing
  `locked_story_hashes.json` pattern already does this for integrity — extend the same idea to the
  object-storage layer) and define a lifecycle policy (e.g. move superseded/re-generated assets to
  cold storage rather than deleting immediately, to protect against a bad regeneration).
- **Phase C (scale/media-heavy):** add generated thumbnails for coloring/poster assets (for the
  carousel in §10 and any future gallery/search UI) and streaming-friendly delivery for narration
  audio (HTTP range-request support, which most object-storage + CDN combinations provide by
  default) rather than serving full MP3s from the API process.

**What git should/shouldn't retain:** git should keep source code, docs, manifests/config, and
small structural JSON (like a future `data/web-assets/*/sync.json`). It should **never** retain
story media binaries (already correctly excluded) or the full `KrishnaBook.pdf`-class source
documents (§18). **Migration triggers:** move to Phase B when either (a) the catalog exceeds
roughly 50–100 stories, (b) more than one person needs to publish concurrently, or (c) the app is
exposed beyond localhost — whichever comes first.

---

## 21. Accessibility

Live-confirmed this session: the Coloring lightbox's `role="dialog"` and Escape-to-close-with-
focus-return (§10) — an improvement over the prior static review. Alt text is descriptive and
correct on Coloring tiles. **Not re-verified live this session** (carried from the prior UAT
round's code-level confirmation, still believed accurate): `focus-visible` outlines and 44px
minimum touch targets exist in `packages/ui/src/styles.css`/`apps/web/app/globals.css`, two
`prefers-reduced-motion` blocks exist, and a `.reading-mode-dyslexia` CSS rule exists — though the
user's stated preference is that the dyslexia-mode *toggle* be removed from the visible reading
controls; whether that toggle is still exposed in the Read tab's UI controls was not re-clicked
live this session and should be confirmed before removal is called complete. No `axe-core`
dependency exists in `apps/web/package.json` — automated a11y scanning is still not wired up, on
any browser.

---

## 22. Performance

Not independently re-measured this session (no Lighthouse/performance-trace tooling was run
against the live instance). Page loads felt fast and interactions (tab switches, lightbox open/
close) were immediate with no visible jank during live use. PWA manifest is present and valid
**(code-confirmed, carried from prior round)**; no offline service worker exists, consistent with
the product not yet requiring offline audio.

---

## 23. Console and network findings

52 console messages were captured across the full session. **All 52 originate from an unrelated
third-party Chrome extension already installed in the user's browser ("clipto-webext" — a
clipboard-history extension), not from the Bhāva application.** Zero console errors, zero console
warnings, and zero application-originated log lines were produced by the app itself across every
page and interaction tested this session, including PDF loads, lightbox open/close, tab switches,
and the Activities "Print" button's new-tab-open action.

---

## 24. Defects

| ID | Title | Severity | Route | Evidence | Steps | Expected | Actual | Recommendation |
|---|---|---|---|---|---|---|---|---|
| DEF-01 | Internal production content visible on public Read tab | **P1** | `/stories/001`, `/stories/007` (all stories) | ss_8808ewpki (story 001, scrolled to bottom) | Open a story, click Read, scroll to the bottom | Only reader-facing prose (Recap → Bedtime Prayer → Next Story Preview) is shown | Audio Narration script (with literal SSML tags), Poster/Coloring Visual Briefs, and raw Activity Data dict all render as visible text | Move internal fields into structured `manifest.json` fields instead of an in-markdown HTML comment; stop relying on comment-hiding after HTML-entity escaping (§8) |
| DEF-02 | Contact page exposes civil name and professional identity | **P2** | `/contact` | ss_3945ob7tl | Open `/contact` | Only devotional name + a devotional-domain contact method | "Svarna Gauranga Das is the devotional name of Swapnil Patil…" plus swapnilpatil.tech/LinkedIn/GitHub links | Remove the explanatory sentence and civil-identity links; add `swarnagaurangadas@gmail.com` (§17) |
| DEF-03 | Coming-soon Library shelf cards are not clickable | **P3** | `/library` | live accessibility-tree read | Tab/click "Śrīmad-Bhāgavatam" or "Rāmāyaṇa & Caitanya" card | Navigates to a description page | No `href`, not focusable, no navigation occurs | Make every shelf card a real link to a polished (even if minimal) description page (§13) |
| DEF-04 | Activities "Print" button duplicates "Open full tab" instead of printing | **P4** | `/stories/007` Activities tab | live tab-open confirmed → `activity_sheet.pdf` in new tab | Click "Print" on the Activities tab | Triggers the browser print dialog for the current PDF | Opens a new tab at the raw PDF URL, identical to "Open full tab" | Wire `window.print()`, or remove the redundant button (§9) |
| DEF-05 | `.gitignore` does not explicitly protect root-level copyrighted source PDFs | **P4** | repo root | `git status --short` + `.gitignore` read | Inspect `.gitignore` for `KrishnaBook.pdf`/root `*.pdf` coverage | An explicit rule prevents accidental commit | No such rule exists; file is safe today only because no one has `git add`-ed it | Add a scoped root-level ignore entry (§18) |

**Confirmed non-defects / resolved-since-prior-round:**

- Repeated Story-001 sidebar cards in earlier full-page screenshots — confirmed via live scroll to
  be a screenshot-stitching artifact, not real rendering behavior (§4).
- Coloring lightbox missing `role="dialog"` / Escape-to-close — **fixed since the prior UAT round**;
  both now work correctly, including focus return (§10).
- Classroom playlist saved-but-never-displayed — **fixed since the prior UAT round**; "My
  Classroom Playlist" now correctly reads back saved entries (§14).
- `/vanani` slug typo — **fixed since the prior UAT round**; route is now `/prabhupada-vani` and
  resolves correctly (§4).
- Homepage "oversized empty hero" / "empty collection cards" — **not found live**; hero and
  homepage story cards are populated with real artwork (§4, §19).

---

## 25. Requested upgrades — mapped to priority

**Required now:**
- Fix DEF-01 (internal content leak) — public-facing content-safety issue.
- Fix DEF-02 (Contact identity) — explicit, direct user requirement for this mission.

**Useful next:**
- DEF-03 (clickable coming-soon cards), DEF-04 (Activities Print button), DEF-05 (.gitignore
  hardening).
- Copyright/provenance schema on Source tab and `/source-permissions` (§12, §18).
- Coloring carousel (§10).
- Teaching Reflections data model + UI (§11).
- Classroom-playlist visibility polish now that the base wiring works (§14).

**Later research:**
- Synchronized listen-and-read (§7) — needs a forced-alignment pass per story before any UI work.
- Śloka data model population (§12) — blocked on actual curated verse sourcing.
- Library IA expansion beyond the current three shelves (§13).
- Sunday School / For Preachers areas (§14).
- Prabhupāda Vāṇī and Bhakti Blog real content (§15, §16) — both blocked on sourcing/permissions.
- Storage Phase B/C migration (§20) — triggered by scale, not needed today.

**Rejected / unsafe to do automatically:**
- Any auto-generated śloka text, Vāṇī excerpt, or Bhakti Blog article — all explicitly prohibited
  without a named reviewer and a real source citation.
- Any blanket copyright claim over BBT-derived material.
- Deleting or exposing `KrishnaBook.pdf` in any served route.

---

## 26. Consolidated Cursor implementation scope

One recommended direction, phased. No application code was written during this review.

**Phase 1 — Content safety (required now)**
- Goal: stop internal content from rendering on the public Read tab.
- Files affected: `apps/web/components/story-experience.tsx` (`renderMarkdown()`), story
  generation pipeline output shape (likely `manifest.json` schema + whatever script currently
  emits `story.md`'s trailing internal block).
- Data model change: add structured fields to `manifest.json` (`audio_narration_script`,
  `poster_visual_brief`, `coloring_visual_brief`, `activity_data`) instead of an in-markdown
  comment block.
- Migration: regenerate/backfill `manifest.json` for stories 001–007 to move the existing trailing
  block's content into the new fields, then strip it from `story.md`.
- Tests: a unit test asserting the Read tab's rendered HTML never contains the strings
  `<break time=`, `Visual Brief`, or `Activity Data`.
- Acceptance criteria: scrolling to the bottom of every story's Read tab shows only reader-facing
  prose ending at "Next Story Preview"/"Parent/Teacher Note."
- Rollback: revert the template change; no data is destroyed since the source fields are additive.

**Phase 2 — Identity correction (required now)**
- Goal: Contact page shows only the devotional identity.
- Files affected: `apps/web/config/contact.json`, `apps/web/app/contact/page.tsx`.
- Data model change: `contact.json` — remove `website`/`linkedin_url`/`github_url`, set
  `public_email` to `swarnagaurangadas@gmail.com`.
- Migration: none needed (config-only change).
- Tests: a snapshot/regression test asserting the rendered Contact page never contains "Swapnil,"
  "swapnilpatil," "linkedin," or "github.com/swap2".
- Acceptance criteria: `/contact` shows heading "Svarna Gauranga Das," no civil-name sentence, one
  `mailto:swarnagaurangadas@gmail.com` link, no LinkedIn/GitHub/personal-site links.
- Rollback: restore prior `contact.json` values from git history.

**Phase 3 — Navigation polish (useful next)**
- Goal: coming-soon Library cards become real links; Activities Print behaves correctly.
- Files affected: `apps/web/app/library/page.tsx` (or its shelf-card component),
  `apps/web/components/story-experience.tsx` (Activities panel).
- Tests: link-presence assertions for every shelf card; a click-triggers-`window.print`
  assertion for the Activities Print button.
- Acceptance criteria: every Library shelf card navigates somewhere; Activities Print opens the
  browser print dialog instead of a new tab.
- Rollback: trivial, isolated UI changes.

**Phase 4 — Provenance and carousel (useful next)**
- Goal: implement the source-provenance schema (§18) and the Coloring carousel (§10).
- Files affected: manifest schema (provenance fields), `/source-permissions` page,
  story-experience Source tab, Coloring tab component.
- Data model change: per-asset `provenance`/`permissionsStatus` fields as specified in §18.
- Tests: provenance-field-required lint/test on manifest ingestion; carousel keyboard/swipe/focus
  tests.
- Acceptance criteria: Source tab and `/source-permissions` show explicit per-asset provenance;
  Coloring tab supports arrow/keyboard/swipe navigation with an accessible live-region
  announcement.
- Rollback: additive schema fields, safe to roll back independently of Phase 1–3.

**Phase 5+ — Later research** (synchronized reading, Śloka population, Library IA expansion,
Sunday School/Preacher areas, Vāṇī/Blog real content, storage Phase B/C) are intentionally left
unscoped here — each depends on a sourcing, curation, or scale decision outside engineering's
control, per §7, §12, §13, §14, §15, §16, §20.

---

## 27. Final recommendation

**PASS WITH CONDITIONS.** The running application is functionally solid — every tested feature
(Listen, Read, Activities, Coloring, Source, Notes, Ślokas, Teacher toolkit, honest coming-soon
states) works as built, with a clean console and no fabricated content anywhere. Before this
branch is considered complete against this mission's explicit goals, **Phase 1 (content safety)
and Phase 2 (identity correction) should be treated as required, near-term fixes** — the former is
a real content-safety issue on a children's product, the latter is a direct, explicit user
requirement that current production output does not yet satisfy. Everything else in this report is
scoped, honest, non-fabricated recommendation work for a future implementation pass — not a
blocker to continued use of the current branch.

---

## Compliance summary

- Application code modified: **NO**
- Story packages modified: **NO**
- Queue modified: **NO** (`locked_queue_state.csv` unchanged; story 008 not generated)
- Scheduler triggered: **NO**
- Drive modified/uploaded to: **NO**
- Paid APIs called: **NO**
- Factory Studio actions enabled/used: **NO**
- `main`/`master`/tags modified: **NO**
- Dependencies installed / app restarted: **NO** — tested entirely against the already-running
  `cursor-uat` instance per this mission's explicit constraint.
