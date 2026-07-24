# BHĀVA PORTAL V1.2+ — COWORK LIVE UAT

**Date:** 2026-07-23
**Reviewer:** Claude (Cowork), live browser testing via Claude-in-Chrome against the user's real Chrome on Windows
**Mode:** Review-only. No application code, story package, queue, scheduler, Drive, or paid-API state was modified during this review (verified by `git status --porcelain` against a clean plumbing index both before and after testing — zero working-tree changes from this session).

## 1. Git / branch / cleanliness

- Branch: `feature/bhava-portal-v1`
- HEAD at start of review: `1f224df` — "docs: freeze V1.2 CoWork prompt against verifiable branch tip"
- Working tree: clean. `git status --porcelain` run via a scratch index (to route around a pre-existing, unrelated stale `.git/index.lock` in this sandbox) returned no output — no modified or untracked files before this review began, and none were introduced by it.
- No tags, no `main`/`master` refs touched. No merge or PR opened.
- Prior V1.2 automated UAT claim cited by the user ("313 passed, uat_exit=0") was **not independently re-run** in this session — no test runner was executed. This review is a live, human-style browser walkthrough, not a re-execution of that automated suite. This is stated plainly rather than implied as re-verified.

## 2. Runtime

- Instance: `cursor-v12`, read from `.bhava/instances/cursor-v12/runtime.json`.
- Web: `http://127.0.0.1:3004` (preferred port 3002 was occupied — `collision: true`, so the instance auto-selected 3004; this is expected multi-instance behavior, not a defect).
- API: `http://127.0.0.1:8002`.
- Mode: `production`.
- The instance was already running; it was not started, restarted, or reconfigured by this review.
- One browser only: Chrome on Windows, via the Claude-in-Chrome extension. **No second browser engine (Firefox/WebKit) was exercised in this session** — any cross-browser claim below is explicitly scoped to Chrome only.

## 3. Pages tested live

Visited and visually inspected in this session: `/` (home), `/library`, `/library/srimad-bhagavatam`, `/library/srimad-bhagavatam/canto/[1]` (source-read, not clicked live), `/contact`, `/faq`, `/teachers`, `/sunday-school`, `/preachers`, `/prabhupada-vani`, `/blog`, `/printables`, `/about`, `/studio` (Factory Studio).

Not visited live this session (not re-tested; no claim is made about their current state beyond what Mission B already documented): the remaining `/library/*` collection stub pages (bhagavad-gita, ramayana, rama-katha, ramacaritamanasa, dasavatara, caitanya-caritamrta, caitanya-bhagavata, prayers-mantras, teacher-resources), and story routes 002–005.

## 4. Story routes tested

- **Story 001** (`/stories/001`, "The Earth Prays for Krishna to Come") — deep test: Listen, Read, Activities, Coloring, Source, Notes, Ślokās tabs all opened and inspected.
- **Story 006** (`/stories/006`, "The Birth of Lord Krishna") — audio-only re-test (fresh tab), to confirm the playback defect isn't story-001-specific.
- Stories 002, 003, 004, 005, 007 were **not** opened live in this session. No claim is made about them individually; Mission B's V1.1 findings (all seven stories structurally sound) are the last direct evidence on record for those routes, and this V1.2 session did not re-confirm them.

## 5. What is confirmed fixed / confirmed working

- **Contact/About identity** — correct in both places. `/contact` and `/about` both show "Svarna Gauranga Das," `svarnagaurangadas@gmail.com`, Harrisburg, Pennsylvania. No civil name found on either page.
- **Read tab** — section-nav chips (Scriptural Source, Recap, Main Story, Devotional Meaning, Five Lessons, Think About It, Five-Star Challenge, Bedtime Prayer, Next Story Preview, Parent/Teacher Note) and reading-mode toggles (Larger text/default/sepia/dark/Print/Download story text) all present and functioning as in V1.1.
- **Activities tab** — PDF activity sheet ("Prayer Petal Wheel") renders inline with Open full tab / Download PDF / Open to print controls.
- **Coloring tab** — Story poster, Simple coloring, and Detailed coloring thumbnails all render correctly for Story 001.
- **Source tab** — honest provenance model intact: primary-work citation (author, chapter, passage boundary, "excerpt-needs-review," reviewer name/date, "Open in Vedabase" link) separated from "Bhāva original elements" (own provenance/permissions line). Quality badge shows "PASS."
- **Notes tab** — family notes explicitly labeled "Notes stay in this browser only (localStorage). Bhāva does not upload child notes," separate from "Teaching reflections," which are labeled "Curated seeds from the package (may still need review)... These are never presented as Prabhupāda quotations."
- **Ślokās tab** — still honestly gated: "NOT YET CURATED," "Sanskrit placeholder — no verse text invented," with a "Reveal stubs" control rather than fabricated content.
- **Sunday School, For Teachers, For Preachers, Prabhupāda Vāṇī, Bhakti Blog, Printables** — all load cleanly, are populated with real structural content (age-group guidance, weekly class plans, class-pack composer, story selector, source-tier governance language, topic taxonomy, live per-story printable listings), and consistently use honest "planned"/"in preparation" language rather than fabricated content anywhere planned material is not yet ready.
- **Factory Studio safety** — "Actions enabled: NO (demo)," "Loopback enforced: true." All ten production-mutation buttons (7× "Rebuild web assets," "Preflight," "Generate next," "Drive readback") confirmed `disabled: true` via direct DOM query. Queue data shows chapters 001–007 = `done` (7), 008–093 = `pending` (86) — matches `data/catalog/locked_queue_state.csv` on disk exactly. Story 008 was not triggered.
- **Homepage brand imagery** — the two homepage hero images (`hero-desktop-wide.webp`, `hero-krishna-book-collection.webp`) are genuinely wired into `apps/web/app/page.tsx` and render live: a large Viṣṇu/demigods scene and a mother-child reading scene with peacock-feather motifs. This is real, applied, high-quality branding — not a placeholder.
- **Header logo** — `logo-icon-only.webp` (one of the twelve imported logo variants) is genuinely wired into the site header and favicon via `apps/web/app/layout.tsx`.

## 6. Brand-asset application verdict

**Verdict: PARTIALLY APPLIED — logo system and homepage heroes are real; most of the rest of the asset library is imported into the repo but not wired into any page.**

This verdict is based on three independent layers of evidence: the source asset manifest, a `grep` of actual component/page code for references to each asset folder, and live visual confirmation in the browser.

**What the master asset dump contains.** `MyPilotDropbox/bhava-brand-assets-v1/bhava-final/refs/final_inventory.md` records 122 total verified visual assets across 11 categories: logo_system (12), platform_icons (11), homepage_heroes (10), collection_covers (15 — one cover per Library collection, including Krishna Book, Śrīmad-Bhāgavatam, Bhagavad-gītā, etc.), canto_covers (12 — one per Śrīmad-Bhāgavatam canto), section_banners (12), social_sharing (10), learning_icons (22), empty_states (11), contact_faq (7, including dedicated Contact and FAQ hero images).

**What is physically present in the repo.** `apps/web/public/` now contains dedicated folders — `brand/`, `collections/`, `heroes/`, `sections/`, `icons/`, `empty-states/`, `social/` — holding processed `.webp` files (with responsive `640w`/`1280w`/`1920w` variants) for effectively the full 122-asset set, plus a `config/brand-assets.json` manifest (`assetCount: 114`) mapping each logical asset ID to its production path, dimensions, and approval state. **The import/processing pipeline has clearly run and is thorough** — this is real, non-trivial engineering work, correctly organized by category.

**What is actually referenced in application code.** A repo-wide `grep` for each folder's usage inside `apps/web/app` and `apps/web/components` found:
- `/brand/logo-icon-only.webp` — used (header + favicon). This is the *only* one of the twelve logo variants referenced anywhere in the code.
- `/heroes/hero-desktop-wide.webp` and `/heroes/hero-krishna-book-collection.webp` — used, both only in the homepage (`apps/web/app/page.tsx`).
- `/collections/*` (15 assets) — **zero references** anywhere in `apps/web/app` or `apps/web/components`.
- `/sections/*`, `/icons/icon-*` (the new 22-icon learning set), `/empty-states/*`, `/social/*` — **zero references**.
- `/brand/hero-contact-page*.webp` and `/brand/hero-faq-page*.webp` — present on disk with full responsive variants, but **zero references** in `apps/web/app/contact/page.tsx` or `apps/web/app/faq/page.tsx`.

**Live visual confirmation.** Screenshots taken this session confirm the code finding exactly: `/library` renders its ten collection cards as flat CSS `linear-gradient` blocks (`.collection-card.krishna { background: linear-gradient(...) }`, defined in `apps/web/app/globals.css`) with a decorative circular "orb" — no cover art. `/library/srimad-bhagavatam` and its canto detail page render plain white cards with numbered badges — none of the 12 canto covers appear. `/contact` and `/faq` both render on a plain warm gradient background with no hero image, despite `hero-contact-page.webp`/`hero-faq-page.webp` existing in `public/brand/` for exactly this purpose.

**Direct answer to the user's stated concern** ("many brand asset folders exist... but the app still appears not to be fully using them, especially in Library / Śrīmad-Bhāgavatam / collection presentation"): **confirmed accurate.** The Library and Śrīmad-Bhāgavatam collection pages are the most visible gap — they still look generic/placeholder (flat color-gradient cards) even though matching cover art for every one of those exact collections was generated, processed, and sits unused in the repository. This is not a missing-asset problem; it is a missing-integration problem. The asset pipeline and the page components were evidently built in separate passes that were never wired together.

## 7. Knowledge-library readiness verdict

**Verdict: NOT IMPLEMENTED — planning/architecture package only, no code exists yet. Current live app still uses "Bhakti Blog," not "Knowledge."**

`MyPilotDropbox/bhava-knowledge-library-v1.0/` contains a substantial, well-structured *planning* package: a blueprint, a Cursor master prompt, and a nested `Bhava_Knowledge_Library_Research_and_Cursor_Prompt_Library_v1.0/` bundle with `00_EXECUTIVE_DECISIONS.md`, architecture docs, a content model, editorial governance and copyright policy, JSON schemas for content/navigation/assets, 17 numbered implementation prompts (repository discovery through release handoff), templates, and one seed MDX example. **This is documentation and prompts for a future Cursor implementation pass — it is not application code, and none of it has been merged into `apps/web`.**

Per `00_EXECUTIVE_DECISIONS.md`, the intended direction matches what the user described: public navigation label **"Knowledge,"** page title **"Bhava Knowledge Library,"** explicitly replacing/retiring the current limited "Bhakti Blog" tab, structured as a curated documentation system (articles, structured reference records, prayer/śloka experiences, learning paths, canonical questions, teacher resources) with no open public contributor portal — only private question/correction/broken-link/rating submissions, none of which appear publicly without editorial action. A source-authority tier system (A1 governing primary sources through D discovery-only) and explicit rules on confidential content (what may vs. may not be published about initiation, mantra, and restricted procedures) are specified in detail.

**Live confirmation that none of this exists yet in the app:** the site nav still shows "Bhakti Blog" linking to `/blog`; there is no `/knowledge` route, no "Knowledge" nav item, and no mega-menu. `/blog` itself still renders the old structure documented in Mission B — five topic categories (Family practice, Teaching notes, Festival reflections, Behind the stories, Śloka study) and a "Planned articles" section stating plainly "These five articles are in preparation. No article bodies or fabricated quotations exist yet." This is honest, but it is the V1.1-era Bhakti Blog, not the Knowledge Library.

**Readiness assessment:** the current Blog/Vāṇī/Teachers structure is a reasonable **placeholder foundation** — its honesty discipline (no fabricated content, explicit "planned" states) is exactly the posture the Knowledge Library blueprint also calls for, so the team has already internalized the right editorial values. But structurally it is not "ready for integration" in the sense of reusable components: the current Blog page has no article/FAQ/prayer/śloka template components, no source-tier UI, no mega-menu navigation, and no taxonomy data model, all of which the Knowledge Library blueprint specifies from scratch. This reads as **ready for the next implementation phase to begin** (the planning is thorough and specific enough to hand to an implementer), but **not**, itself, an in-progress or partially-built feature.

## 8. Defects

| ID | Title | Severity | Page | Repro | Actual | Expected | Blocker? |
|---|---|---|---|---|---|---|---|
| DEF-06 | Audio narration never buffers/plays | **P1** | `/stories/{001,006,...}`, Listen tab | Open a story, click Play (or call `audio.load()` directly via console). Wait 4+ seconds. | `<audio>` element stays at `readyState: 0` (HAVE_NOTHING), `networkState: 2`, `currentTime: 0` indefinitely. Network log shows **no HTTP request is ever issued** for `/api/v1/stories/{n}/assets/narration.mp3`, even after an explicit manual `audio.load()`. A direct `HEAD` fetch to the same URL confirms the server-side file is healthy (200, `audio/mpeg`, correct `content-length`, `accept-ranges: bytes`) — this rules out a server/file problem. UI sometimes shows "Pause" (optimistic state) while the element is objectively not loading. Reproduced 3 times this session (2× story 001, 1× story 006 in a fresh tab) with an identical failure signature each time. | Clicking Play loads and plays the narration audio. | **Yes.** This was flagged P1 in the prior V1.1 UAT with a commit (`0448251 fix(audio): restore reliable cross-browser story playback`) that appeared to target it — but live testing in V1.2 shows the underlying symptom is unchanged. Given that a manual `audio.load()` call (not subject to autoplay-gesture policy) also never progresses past `readyState 0`, this looks like a genuine client-side bug in the load pipeline, not merely an automation-gesture artifact. |
| DEF-08 | Collection/canto cover art generated but not wired into Library pages | **P2** | `/library`, `/library/srimad-bhagavatam`, `/library/srimad-bhagavatam/canto/[n]` | Visit `/library` or any Śrīmad-Bhāgavatam canto page. | Collection and canto cards render as flat CSS-gradient blocks with a decorative "orb," despite 15 collection covers and 12 canto covers existing, fully processed, in `apps/web/public/collections/`. `grep` confirms zero references to that folder anywhere in `apps/web/app` or `apps/web/components`. | Each Library collection card and each Śrīmad-Bhāgavatam canto card shows its matching cover art. | No — cosmetic/branding gap, not a functional break. But directly matches the user's stated concern and is a visible quality gap on the most-trafficked browsing page. |
| DEF-09 | Contact/FAQ hero images imported but unused | **P3** | `/contact`, `/faq` | Visit either page. | Plain gradient background; no hero image, despite `hero-contact-page.webp`/`hero-faq-page.webp` (with 640/1280/1920w variants) existing in `apps/web/public/brand/` and being listed in `config/brand-assets.json`. | Contact and FAQ pages show their dedicated hero imagery, matching the homepage treatment. | No. |
| DEF-10 | 11 of 12 logo variants, all 22 learning icons, all 11 empty-state illustrations, all 10 social-sharing assets, and all 12 section banners are imported but entirely unreferenced in code | **P3** | Sitewide | `grep` for each asset folder across `apps/web/app` and `apps/web/components`. | Only `logo-icon-only.webp` (of 12 logo variants) and the 2 homepage heroes (of 10) are wired in. Everything else in `sections/`, `icons/` (the new icon set), `empty-states/`, `social/` has 0 references. | These asset categories were generated for a reason (e.g., dark-background logo for footer/print contexts, empty-state illustrations for zero-result states, social cards for share buttons) and should either be wired in or explicitly deferred with a written plan. | No — but worth flagging as scope: `brand-assets.json` reports `assetCount: 114` as "approved," which could read as "applied" to someone skimming the config rather than the rendered pages. |
| DEF-07 | Coloring-carousel arrow keys leak into global audio ±15s skip shortcut | P4 | Story pages, Coloring lightbox | Open Coloring lightbox, press ArrowRight/ArrowLeft to navigate images. | Same keypress can also trigger the page-level audio player's −15s/+15s skip handler (not re-verified live this session; carried forward from V1.1 findings as an open, low-severity item). | Carousel keyboard nav should be scoped so it doesn't leak to background shortcuts. | No. |

DEF-01 (public reader/content leak) and DEF-02 (public civil-identity leak), both confirmed fixed in the V1.1 review, were **not re-verified live in this V1.2 session** — no regression is suspected (contact/about identity was re-checked and remains correct, per §5), but the specific reader-leak marker search from V1.1 was not repeated here.

## 9. Safety validation

- Git working tree: clean before and after this review (verified via scratch-index `git status --porcelain`).
- No story/queue/scheduler/Drive files were modified. `data/catalog/locked_queue_state.csv` matches the live Factory Studio queue view exactly: 001–007 `done`, 008–093 `pending`.
- Factory Studio (`/studio`): "Actions enabled: NO (demo)," "Loopback enforced: true," all ten production-mutation buttons confirmed `disabled: true` via direct DOM query.
- No paid API was called. No Story 008 was generated. No branch, tag, `main`, or `master` ref was touched. No PR was opened or merged.
- The already-running `cursor-v12` instance was used as-is; it was not restarted, and this review does not stop it on completion (per instruction to only restart if genuinely unavailable — it was available throughout).

## 10. Final verdict

**PASS WITH CONDITIONS.**

Contact/identity correctness, the Read/Activities/Coloring/Source/Notes/Ślokās tab set, the education areas (Teachers/Sunday School/Preachers/Vāṇī), and Factory Studio safety are all confirmed solid in this live V1.2 pass. The homepage's new brand imagery is genuinely and attractively applied.

Two conditions before this can be called release-ready:

1. **DEF-06 (audio playback, P1)** — the single highest-priority item the user asked about is still broken live, by the same objective measure (network request for the narration file never fires) used in the prior UAT round, despite an intervening commit that looked like it targeted this exact issue. This needs engineering attention with the network-layer evidence in this report as a starting point, not another "should be fixed now" pass.
2. **Brand-asset integration (DEF-08/DEF-09/DEF-10, P2/P3)** — a full, well-organized 122-asset library has been produced and imported into the repo, but only 3 of those assets are actually wired into any page. The Library and Śrīmad-Bhāgavatam pages the user specifically flagged as looking unfinished are confirmed to still be unfinished, for exactly the reason suspected: the assets exist but were never connected to the components.

The Knowledge Library is confirmed **not yet implemented** — this is not a defect, it is accurately represented in the current app (still "Bhakti Blog," honestly labeled as planned), and the research/blueprint package is thorough enough to be handed to an implementation phase whenever the team is ready to prioritize it.

---

## Note on this review session

This report was written directly to `docs/reviews/BHAVA_V1_2_COWORK_LIVE_UAT.md` in the repository. **I created a local git commit containing only this file** (using a git-plumbing workaround for a pre-existing, unrelated stale `.git/index.lock` in this sandbox — the same technique used successfully in the two prior UAT sessions). **I then attempted `git push origin feature/bhava-portal-v1` and it failed**, exactly as in every prior session: `fatal: could not read Username for 'https://github.com': No such device or address`. This sandbox has no GitHub credentials configured (no `~/.git-credentials`, no SSH key). The commit exists locally on this machine's checkout only and has **not** reached `origin`. I am not reporting this as a success — the push did not succeed, and reaching GitHub will require credentials to be supplied outside this session (e.g., pushing from a machine that already has `git` authenticated, or configuring a credential helper here).
