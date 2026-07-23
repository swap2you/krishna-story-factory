# Bhāva Portal V1 — CoWork UAT

Date: 2026-07-23 · Reviewer: Cowork agent (review-only cycle, no application code changed)

**Read this first:** this session's Linux review sandbox could not run the Next.js frontend
(`apps/web`) — see `docs/product/uat/00_METHODOLOGY_AND_LIMITATIONS.md` for exactly why and
exactly what that means for each finding below. The backend API was started and exercised for
real; the frontend was verified by reading the actual shipped source and cross-checking it
against live backend responses, not by rendering pixels. Findings are cited with file paths so
they can be independently re-checked or re-run natively.

## Executive verdict

**PASS WITH CONDITIONS**

The reviewed code is solid: Factory Studio safety is genuinely defense-in-depth and was verified
live (loopback + CSRF enforcement both return 403 on negative tests), no secrets are tracked, all
7 stories have complete asset sets, the audio player and notes system are well-built and
story-isolated, and placeholder content is handled honestly. Nothing found rises to P0 or P1. The
conditions are: (1) this session could not dynamically verify the live UI at all (no npm install
success in-sandbox — see methodology), so a native Windows pass through Phases 3–15/18 is still
owed before calling the UI itself fully verified; (2) five real, uncommitted code changes sit in
the working tree and should be committed or reverted; (3) a handful of P2 UX/testing-infrastructure
gaps (contact identity clarity, two toolkit actions that under-deliver on their label, zero
Playwright specs / no Firefox-WebKit / no axe automation) should be closed before wider release.

## Environment

- Branch: `feature/bhava-portal-v1`
- SHA tested: `a4276033951c62687660f9f26375057fe78e01ac` (local HEAD == `origin/feature/bhava-portal-v1`)
- Node: v22.22.3 / npm 10.9.8 (review sandbox, Linux — used only for the failed/attempted install; not the target runtime)
- Python: 3.10.12 (review-sandbox venv, used to execute tests); native workstation `.venv` is Python 3.13.5 (read from `.venv/pyvenv.cfg`, not executed this session)
- Windows: not directly exercised this session (sandbox is Linux); native workstation is the intended runtime for `scripts/*.ps1`
- Browsers: none rendered live this session (see methodology). Source review covered all routes.

## Scope tested

Fully, live: git/branch state, backend API (`apps/api`) via real `uvicorn` + `curl`, Python test
suites (`tests/portal` complete, `tests/` legacy suite 165/210 completed), repository secret and
hygiene scan, `.gitignore`/tracked-file audit.

By source-code review only (frontend could not run — see methodology): all 19 routes, the audio
player, notes/bookmark/localStorage behavior, PDF/coloring embed markup, Teacher Toolkit,
Factory Studio UI, contact/identity presentation, PWA manifest, accessibility CSS tokens,
Playwright/axe tooling configuration.

Not performed this session at all: live screenshots, live axe DOM scan, live console/network
capture, live responsive breakpoints, live cross-browser (Chromium/Firefox/WebKit) comparison,
real screen-reader spot check, Lighthouse/performance timing, PWA installability.

## Persona findings

Assessed from the actual page copy and component behavior in `apps/web/app/**` (see
`docs/product/uat/route_and_component_review.md`), not from a live click-through.

1. **Parent of a child age 5–7.** Tone is warm and calm ("Stories that bring little hearts closer
   to Krishna"); the homepage states plainly what's available (audio + PDF, local-only notes) and
   the hero meta strip sets honest expectations ("7 Stories ready"). The Notes tab's explicit
   "Bhāva does not upload child notes" line is exactly the reassurance this persona needs. Risk:
   notes require an explicit "Save" click with no autosave — a parent who assumes it saves like a
   phone app could lose what they typed if they navigate away first.
2. **Child age 5–7 with parent assistance.** Reading-mode toggles (larger text, sepia, dark,
   dyslexia-friendly spacing) and the ±15s / speed controls on audio are genuinely built, not
   decorative, and match what a young reader/listener needs. The coloring lightbox's missing
   Escape-to-close and focus handling is more likely to trip up a parent guiding a child by
   keyboard than the child themselves.
3. **Child age 8–13.** The Read tab's Markdown rendering, Source tab (chapter/scripture
   reference), and honestly-empty Ślokas tab avoid talking down to this age group or inventing
   content. Age range metadata (`age_range: "6-12"`) is present on every story from the API.
4. **Bal Gopal teacher.** The Teacher Toolkit's "Bal Gopal" mode gives age-appropriate guidance
   text ("shorter listen, simple coloring, one gentle activity"), and the answer key is hidden by
   default with an explicit "do not invent answers" guard — good for a teacher who needs to trust
   the material. The "Save to classroom playlist" button gives no visible confirmation and nothing
   later displays what was saved — a teacher would reasonably conclude it's broken.
5. **Dāmodara teacher.** Guidance text correctly differentiates ("full narration, detailed
   coloring, activity with discussion prompts") for the older-child mode. Same playlist-visibility
   gap applies.
6. **Public visitor.** First impression from `layout.tsx`/`page.tsx` is coherent and on-brand. The
   Contact page is where trust could wobble: it introduces "Svarna Gauranga Das" as steward but
   every actionable link (Contact button, Website, LinkedIn, GitHub) resolves to "Swapnil Patil"
   with no on-page bridge between the two names — see DEF-05.
7. **Local project operator.** `/studio` is the persona this app is clearly most careful about:
   a fixed "loopback only · never expose publicly" banner, live-fetched enabled/disabled state,
   HTML-disabled action buttons by default, and a read-only queue view. This matches what an
   operator needs to trust the console won't do something by accident.

## Functional findings

- All 19 Phase-5 routes map to real, non-trivial page files — no structural 404 risk (source
  inventory in `route_and_component_review.md`).
- All 7 story packages (001–007) are complete on disk (8 files each, all non-empty) and are
  returned by the live API in correct numeric order with `quality_status: "PASS"` — the
  uncommitted `_chapter_sort_key` fix (see below) is what makes the numeric ordering correct.
- Audio player: play/pause, ±15s, 0.75–2× speed, volume, resume-per-story, bookmark-per-story,
  sleep timer, keyboard shortcuts, Media Session integration, download — all implemented, and
  story-scoped via `localStorage` keys namespaced by `storyNo`, so one story's audio state cannot
  bleed into another (Phase 6's explicit concern) — confirmed at the code level.
- Notes: story-isolated, localStorage-only, never sent to the API (no fetch/POST touches notes
  content anywhere reviewed), working Export (.txt) and Print.
- PDF: embedded via `<iframe>`, plus "Open full tab" and "Download". The dedicated "Print" button
  under Activities does not call `window.print()` — see DEF-09.
- Teacher Toolkit: age modes, class-pack composer, and answer-key reveal all function; classroom
  playlist and print/export preview under-deliver on their labels — see DEF-10, DEF-11.
- Factory Studio: verified live that Story 008 cannot be generated, the queue is read-only, no
  Drive write path exists, and no shell/command execution path exists in `factory_adapter.py`.

## UX findings

- Empty-state handling is graceful everywhere reviewed (`lib/catalog.ts` fails soft with a 4s
  timeout and informative "Start the local API…" copy) rather than blank screens or crashes.
- Placeholder sections (`/vanani`, `/blog`, the Ślokas tab) are labeled honestly as
  not-yet-available with an explicit "we will not invent" promise — a real strength, not a gap.
- `/vanani`'s URL does not match its own nav label ("Prabhupāda Vāṇī") — see DEF-06.
- Contact identity presentation needs a bridging sentence — see DEF-05.
- Two Teacher Toolkit actions look complete but under-deliver — see DEF-10, DEF-11.
- One mislabeled control (Activities "Print") — see DEF-09.

## Accessibility findings

Static/code-level only — **not** a WCAG 2.2 AA pass claim (per the mission's own instruction, and
because no axe/live pass was possible this session).

Real, verified-in-code strengths: `:focus-visible` outlines (3px, offset) in the shared UI
package; `min-height: 44px` touch targets on nav, buttons, tabs, and audio controls; two
independent `prefers-reduced-motion: reduce` blocks; a dyslexia-friendly reading-mode CSS rule;
`aria-label`s on the primary nav, brand link, and every audio-player control; `sr-only` label on
the library search input.

Gaps found in code: `alt=""` on two meaningful poster images (home hero, story sidebar) vs.
correct descriptive `alt` text on the Coloring gallery — DEF-07. Coloring lightbox modal has no
`role="dialog"`, no `aria-modal`, no focus trap, and no Escape-key handler — DEF-08. No
`axe-core`/`@axe-core/playwright` dependency exists anywhere in `apps/web` — automated
accessibility scanning is not wired up at all (Known Item #4, confirmed true).

No live axe run, no live screen-reader spot check, and no live 200%-zoom/reflow check were
possible this session.

## Responsive findings

**Not performed live this session** — the frontend could not be started (see methodology). No
representative screenshots at 390×844 / 430×932 / 768×1024 / 1024×768 / 1366×768 / 1440×900 /
1920×1080 exist from this session. CSS was spot-checked for a mobile breakpoint on the story
sidebar (`@media` rule collapsing `story-sidebar` to a `110px 1fr` grid) confirming responsive
rules exist, but this is not a substitute for a rendered pass.

## Cross-browser findings

**Not performed live this session.** Independent of the sandbox limitation, the repository itself
currently has a real gap: `apps/web/playwright.config.ts` defines only a `chromium` project (no
`firefox`/`webkit`), and `apps/web/e2e/` does not exist — there are zero Playwright specs to run
on any browser today. Confirms Known Items #3, #6, and #7 (only #7 partially — story *content*
completeness was verified for all 7 via the API/filesystem check above; story *UI* functional
testing across all 7 was not performed live).

## Performance/PWA findings

`manifest.webmanifest` is present and well-formed with 192/512 icons and correct `start_url`/
`display`. No offline service worker was found (consistent with the mission's note that offline
audio is not required unless already implemented — it isn't). Raw `<img>` tags (not
`next/image`) are used for the hero poster, story sidebar poster, and coloring gallery/lightbox
images (each has an `eslint-disable-next-line @next/next/no-img-element` comment acknowledging
this), which means no built-in lazy-loading/responsive-srcset optimization for what are, on disk,
1–1.6 MB poster PNGs. Lighthouse/real network-waterfall/layout-shift measurement was not possible
this session.

## Security/privacy findings

- Factory Studio: loopback host+origin enforcement (live 403 confirmed on bad `Host` header),
  CSRF via `secrets.compare_digest` constant-time comparison (live 403 confirmed without token),
  `factory_actions_enabled` defaults `False`, `generate-next`/`preflight`/`drive-readback` all
  route through an adapter that never invokes a shell and returns `"disabled"`/`"demo"` only,
  `scheduler/enable`+`disable` are hardcoded to "not implemented" regardless of any flag. No path
  found by which Story 008 could be generated, the queue mutated, or Drive written to.
- CORS is an explicit localhost/127.0.0.1 allow-list, not a wildcard.
- Path traversal on the asset route was tested live and correctly returns 404.
- Notes/child data: localStorage-only, never transmitted to the API in any code path reviewed;
  privacy statement is visible on the Notes tab and on `/privacy`.
- `.env` and `credentials/` are git-ignored and not tracked; only `.env.example` (blank/`false`
  placeholders) is tracked. The real, populated `.env` on this workstation currently has
  `OPENAI_TEXT_ENABLED`, `OPENAI_IMAGE_ENABLED`, `ELEVENLABS_ENABLED`, and
  `GOOGLE_DRIVE_UPLOAD_ENABLED` all set to `true` with live-looking keys present locally — this
  UAT did not call any of those providers (no story regenerated, nothing uploaded), but it is
  worth flagging that this local `.env` is *not* in a "paid APIs off" state; only the default
  code-level gates (`BHAVA_FACTORY_ACTIONS_ENABLED=false`, which was never touched) are what
  actually prevented any spend during this review, not the `.env` flags themselves.

## Public-repository findings

`output/` (story media) is correctly git-ignored and not shipped in the repo. No secrets, tokens,
or credential files are tracked. `portal-bootstrap/` (21 MB, 25 files of one-time
Cursor-bootstrap scaffolding) *is* tracked and should be a deliberate keep/remove decision before
merging to `main`. The 21 MB `bhava_portal_cursor_bootstrap_v1.zip` sitting in the working tree is
correctly git-ignored (untracked). Full detail in
`docs/product/uat/repo_state_and_public_repo_review.md`.

## Content/source presentation findings

Every story's Source tab surfaces `source_reference` and `scripture_reference` from the package
manifest plus an explicit boundary statement ("does not republish unlicensed full BBT books").
The Ślokas tab and `/vanani`/`/blog` all explicitly refuse to invent content ahead of real
curated material. This is a consistent, deliberate pattern across the app and is called out
below as a confirmed strength, not filed as a defect.

## Defects

### DEF-01 — `npm install` fails out of the box on non-Windows systems
- **Severity:** P2
- **Route:** N/A (build tooling)
- **Persona affected:** Local project operator / any non-Windows contributor or CI runner
- **Repro:** From a clean clone on Linux (or macOS/x64 without the exact win32 package), run
  `npm install` at the repo root exactly as Phase 2 instructs.
- **Expected:** Dependency install succeeds or degrades gracefully for platform-specific packages.
- **Actual:** Fails immediately: `npm error code EBADPLATFORM … Unsupported platform for
  @next/swc-win32-x64-msvc@15.3.5`. Root `package.json` lists this and
  `@rollup/rollup-win32-x64-msvc` directly under `dependencies` rather than letting npm's normal
  per-platform optional-dependency mechanism handle them.
- **Screenshot:** none (terminal output only) — see `docs/product/uat/pytest_results.md` for the
  exact captured error text.
- **Console/network evidence:** `npm error code EBADPLATFORM` (captured live this session).
- **Recommended direction:** Remove the two win32-specific packages from `dependencies`; let Next/
  Rollup's own optional-platform-dependency mechanism install the correct native binary per
  platform automatically (this is how these packages are designed to be consumed).

### DEF-02 — CI only exercises the Python suite; the entire frontend has zero CI coverage
- **Severity:** P2
- **Route:** N/A (`.github/workflows/ci.yml`)
- **Persona affected:** Local project operator
- **Repro:** Read `.github/workflows/ci.yml`.
- **Expected:** CI gates whatever the local test pack (`scripts/test_bhava.ps1`) is meant to gate.
- **Actual:** CI runs only `python -m pip install -r requirements.txt` + `pytest -q` on
  windows-latest/ubuntu-latest. No `npm install`, no `lint`, no `typecheck`, no `vitest`, no
  `next build`, no Playwright e2e ever runs in CI.
- **Screenshot:** none — see workflow file directly.
- **Recommended direction:** Add a frontend CI job (after fixing DEF-01) running
  `npm run lint:web && npm run typecheck:web && npm run test:web && npm run build:web` at minimum.

### DEF-03 — Playwright is configured but has zero test specs; no Firefox/WebKit; no axe
- **Severity:** P2
- **Route:** N/A (`apps/web/playwright.config.ts`, `apps/web/e2e/`)
- **Persona affected:** Local project operator
- **Repro:** Inspect `apps/web/playwright.config.ts` (`projects: [{ name: "chromium" }]` only,
  `testDir: "./e2e"`) and look for `apps/web/e2e/` on disk.
- **Expected:** End-to-end coverage across the browsers named in the mission (Chromium, Firefox,
  WebKit) for the routes named in Phase 14.
- **Actual:** `apps/web/e2e/` does not exist; there are no `*.spec.ts` files anywhere under
  `apps/web`. `npm run test:e2e` currently has nothing to execute, on any browser. No
  `axe-core`/`@axe-core/playwright` dependency is present either.
- **Screenshot:** none — confirmed by direct file inspection (file does not exist).
- **Recommended direction:** Add real Playwright specs under `apps/web/e2e/` covering at least the
  10 routes named in Phase 14, add `firefox`/`webkit` projects to `playwright.config.ts`, and wire
  in `@axe-core/playwright` per route.

### DEF-04 — Working tree has real uncommitted changes on a shared review branch
- **Severity:** P2
- **Route:** N/A (repository state)
- **Persona affected:** Local project operator
- **Repro:** `git diff --ignore-all-space --name-only` on `feature/bhava-portal-v1`.
- **Expected:** Clean working tree at the SHA under review (Phase 1 precondition).
- **Actual:** 5 files carry real, uncommitted work: `apps/api/bhava_api/catalog/filesystem.py`
  (numeric chapter sort fix), `apps/api/bhava_api/routes/media.py` (content-type fallback fix),
  and 3 portal test files with matching new assertions. (The other 116 "modified" files reported
  by plain `git status` are CRLF/LF churn from this review sandbox lacking `.gitattributes` /
  `core.autocrlf` — not real changes; see `docs/product/uat/repo_state_and_public_repo_review.md`.)
- **Screenshot:** none — see the diff excerpt in `repo_state_and_public_repo_review.md`.
- **Recommended direction:** Commit these 5 files (they are real, tested bug fixes — the portal
  test suite passes 8/8 with them in place) or explicitly revert them; don't leave real code
  changes uncommitted on a branch being reviewed for merge readiness.

### DEF-05 — Contact page identity (Svarna Gauranga Das vs. Swapnil Patil) is unexplained
- **Severity:** P2
- **Route:** `/contact` (also `/about`, `/privacy`, `/source-permissions` footer references)
- **Persona affected:** Public visitor, parent evaluating trust
- **Repro:** Open `/contact`. Read the heading ("Svarna Gauranga Das") and click "Contact Svarna
  Gauranga Das".
- **Expected:** A visitor understands who they're reaching and why the name on the button differs
  from the destination, if it does.
- **Actual:** The Contact/Website/LinkedIn/GitHub links all resolve to Swapnil Patil's personal
  identity (`swapnilpatil.tech`, `linkedin.com/in/swapnil-patil-ai-architect`,
  `github.com/swap2you`) with no on-page sentence connecting the devotional steward name to that
  identity. Source: `apps/web/config/contact.json` + `apps/web/app/contact/page.tsx`.
- **Screenshot:** none — see `docs/product/uat/route_and_component_review.md` for the exact JSON
  and JSX cited.
- **Recommended direction:** Add one clarifying line, e.g. "Svarna Gauranga Das is the devotional
  name of Swapnil Patil, who builds and stewards Bhāva," near the steward heading or footer.

### DEF-06 — `/vanani` route slug doesn't match its own nav label
- **Severity:** P3
- **Route:** `/vanani`
- **Persona affected:** Public visitor, Dāmodara teacher
- **Repro:** Compare the nav label/page heading ("Prabhupāda Vāṇī") to the URL (`/vanani`).
- **Expected:** URL slug recognizably matches the displayed name.
- **Actual:** `/vanani` reads as a garbled/duplicated "vani", dropping "prabhupada" entirely.
- **Recommended direction:** Rename to `/prabhupada-vani` (matches the nav label exactly) with
  `/vani` as an acceptable shorter alternative; add a redirect from `/vanani` if already shared.
  Not changed during this review-only UAT.

### DEF-07 — Empty `alt=""` on meaningful poster images (inconsistent with Coloring gallery)
- **Severity:** P3
- **Route:** `/` (hero), `/stories/[storyNo]` (sidebar)
- **Persona affected:** Screen-reader users across all personas
- **Repro:** Read `apps/web/app/page.tsx:38` and `apps/web/app/stories/[storyNo]/page.tsx:24`.
- **Expected:** Meaningful content images get descriptive `alt` text, as the Coloring gallery
  correctly does (`story-experience.tsx:164`, `alt={item.label}`).
- **Actual:** Both the homepage hero poster and the story-sidebar poster use `alt=""`, making them
  invisible to assistive technology despite carrying real content (which story is featured).
- **Recommended direction:** Use a descriptive alt (e.g. `` `${title} story poster` ``) or, if
  truly decorative, wrap consistently with `aria-hidden="true"` (the current
  `aria-hidden={!featured?.poster_url}` on the homepage is backwards — it hides the wrapper only
  when there is *no* poster).

### DEF-08 — Coloring lightbox modal lacks dialog semantics and Escape-to-close
- **Severity:** P3
- **Route:** `/stories/[storyNo]` → Coloring tab
- **Persona affected:** Keyboard/screen-reader users, parent assisting a 5–7-year-old
- **Repro:** Read `apps/web/components/story-experience.tsx:169-181`.
- **Expected:** A modal announces itself to assistive tech and can be closed with `Escape`.
- **Actual:** No `role="dialog"`, no `aria-modal="true"`, no focus trap, no `keydown` handler for
  `Escape`; only clicking the backdrop or an on-screen "Close" button dismisses it.
- **Recommended direction:** Add dialog semantics, trap focus while open, and close on `Escape`.

### DEF-09 — Activities "Print" button doesn't print; duplicates "Open full tab"
- **Severity:** P3
- **Route:** `/stories/[storyNo]` → Activities tab
- **Persona affected:** Parent, Bal Gopal/Dāmodara teacher printing worksheets
- **Repro:** Open a story's Activities tab, click "Print".
- **Expected:** Browser print dialog opens for the activity PDF (as the Coloring lightbox's own
  "Print" button correctly does via `window.print()`).
- **Actual:** `story-experience.tsx:144` calls `window.open(activity_pdf_url, "_blank")` — the
  same action as the adjacent "Open full tab" button. No print dialog is triggered.
- **Recommended direction:** Either call `window.print()` on the opened PDF context, or relabel
  the button to match what it actually does (e.g. remove the duplicate control).

### DEF-10 — "Save to classroom playlist" appears to do nothing
- **Severity:** P2
- **Route:** `/teachers`
- **Persona affected:** Bal Gopal teacher, Dāmodara teacher
- **Repro:** On `/teachers`, choose pack items and click "Save to classroom playlist".
- **Expected:** Visible confirmation, and a way to later view/manage what was saved (matching the
  "classroom playlist" name).
- **Actual:** `apps/web/app/teachers/page.tsx:111-120` does write a real entry to
  `localStorage["bhava:classroom-playlist"]`, but shows no toast/confirmation (unlike "Save
  notes", which does), and no page or component anywhere in the reviewed source ever reads that
  key back. A teacher clicking it has no way to know it worked, and no way to ever see it again.
- **Recommended direction:** Add a save confirmation and a simple "My classroom playlist" view
  that lists saved entries (even a read-only list on the same page would close this gap).

### DEF-11 — "Print / export preview" doesn't produce an exportable class-pack document
- **Severity:** P3
- **Route:** `/teachers`
- **Persona affected:** Bal Gopal teacher, Dāmodara teacher
- **Repro:** On `/teachers`, click "Print / export preview".
- **Expected:** A printable/exportable class-pack summary (title implies both print *and* export).
- **Actual:** `apps/web/app/teachers/page.tsx:101-110` saves a plan string to
  `localStorage["bhava:class-pack"]` and calls `window.print()` on the live interactive builder
  page itself — there is no dedicated print layout and the saved plan text is never displayed or
  offered as a download anywhere.
- **Recommended direction:** Render the saved plan as a clean printable summary (separate from the
  interactive controls) and/or offer it as a text/PDF download.

### DEF-12 — `portal-bootstrap/` (21 MB, 25 files) is committed to the public repo
- **Severity:** P3
- **Route:** N/A (repository)
- **Persona affected:** Local project operator / open-source visitor
- **Repro:** `git ls-files portal-bootstrap | wc -l` → 25 files, `du -sh portal-bootstrap` → 21 MB.
- **Expected:** Only shipped-product source is tracked in the public repo.
- **Actual:** One-time Cursor-bootstrap scaffolding (config, prompts, scripts, specs, UX-prototype
  assets) is tracked, inflating clone size with material unrelated to the running product.
- **Recommended direction:** Archive `portal-bootstrap/` outside the repo (or squash it out of
  history before the eventual merge to `main`) — a deliberate decision, not urgent. Not deleted
  during this review-only UAT.

### DEF-13 — Several legacy factory tests run long enough to be worth profiling
- **Severity:** P4
- **Route:** N/A (`tests/test_daily_idempotency.py` and slow portions of several others)
- **Persona affected:** Local project operator (CI/dev-loop speed)
- **Repro:** Run `pytest tests/test_daily_idempotency.py` — did not produce a second passing
  result within 40s on two separate attempts in this sandbox.
- **Expected:** Reasonably fast unit-test runtime.
- **Actual:** Unknown exact runtime (exceeded this session's execution windows); not confirmed to
  be an application defect, may simply be a slow test or sandbox I/O artifact.
- **Recommended direction:** Time this test natively; if genuinely slow, mark it `@pytest.mark.slow`
  or optimize it so `scripts/test_all.ps1` stays fast for day-to-day use.

## Confirmed non-defects

- Factory Studio safety: loopback host+origin enforcement, CSRF (constant-time compare), the
  `factory_actions_enabled` default-off gate, the shell-free `factory_adapter.perform()`
  allowlist, and the hardcoded "not implemented" scheduler endpoints were all read in source
  **and** verified live (403s on negative tests) — this is a genuine strength, not merely an
  absence of defects.
- No secrets, tokens, or credential files are tracked by git; the one secret-shaped regex hit in
  the codebase is a unit test that asserts redaction works.
- `output/` story media is deliberately git-ignored, not an oversight (Known Item #10 resolved).
- All 7 stories have complete, correctly-ordered, non-empty asset sets, confirmed both via the
  live API and directly on disk.
- Audio resume/bookmark state is correctly namespaced per story — cannot leak between stories.
- Notes are never transmitted to the API in any code path reviewed, and the privacy statement is
  visible in-product, not just in a policy page.
- Placeholder content (`/vanani`, `/blog`, Ślokas tab) is handled with honest "coming soon / we
  will not invent" messaging rather than looking broken or fabricated.
- `public_email` correctly renders nothing (not a blank/invented address) when unset.
- Real accessibility CSS infrastructure (focus-visible, 44px targets, reduced-motion, dyslexia
  mode) backs the `/accessibility` page's claims at the code level.
- PWA manifest and icons are present and well-formed.

## Proposed consolidated upgrade scope

1. **Release blockers:** none identified at P0/P1 in this session's findings.
2. **Functional completion:** fix DEF-09 (Activities Print), DEF-10 (classroom playlist
   visibility), DEF-11 (class-pack export).
3. **UX polish:** DEF-05 (contact identity bridge sentence), DEF-06 (`/vanani` →
   `/prabhupada-vani` rename with redirect).
4. **Accessibility:** DEF-07 (alt text on poster images), DEF-08 (lightbox dialog semantics +
   Escape), then a real `@axe-core/playwright` pass per route once e2e exists (DEF-03).
5. **Cross-browser:** DEF-03 — add Firefox/WebKit projects and real specs under `apps/web/e2e/`.
6. **Performance:** consider `next/image` for the hero/sidebar/coloring/lightbox images (currently
   raw `<img>`, 1–1.6 MB PNGs, no built-in lazy-loading/responsive srcset).
7. **Public-deployment readiness:** DEF-01 (fix `npm install` on non-Windows), DEF-02 (add a
   frontend CI job).
8. **Repository cleanup:** DEF-12 (`portal-bootstrap/` decision), delete the local untracked
   21 MB `bhava_portal_cursor_bootstrap_v1.zip` (already git-ignored, just local clutter).
9. **Future roadmap:** DEF-13 (profile slow tests), a curated Ślokas dataset when available, and
   — most importantly — **a native Windows re-run of Phases 3–15 and 18** (via
   `scripts\test_bhava.ps1` / `scripts\start_bhava_local.ps1`) to supply the live screenshots,
   axe report, responsive matrix, and real cross-browser pass this sandbox could not produce.

## Final recommendation

No production/application code was changed. Commit the 5 real uncommitted fixes (DEF-04) or
revert them, then schedule one native Windows UAT pass to close the visual/dynamic verification
gap this session left open, alongside the P2/P3 items above. Nothing found blocks continued local
use of the app in its current state.
