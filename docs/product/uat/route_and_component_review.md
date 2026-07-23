# Route & Component Source Review — Bhāva Portal V1

Static review method (see `00_METHODOLOGY_AND_LIMITATIONS.md`). Every route in Phase 5's list
maps to a real, non-trivial page file — no structural 404 risk was found:

| Route | Source file |
|---|---|
| `/` | `apps/web/app/page.tsx` |
| `/library` | `apps/web/app/library/page.tsx` |
| `/library/krishna-book` | `apps/web/app/library/krishna-book/page.tsx` |
| `/stories/001`…`/stories/007` | `apps/web/app/stories/[storyNo]/page.tsx` (dynamic) |
| `/teachers` | `apps/web/app/teachers/page.tsx` |
| `/vanani` | `apps/web/app/vanani/page.tsx` |
| `/blog` | `apps/web/app/blog/page.tsx` |
| `/about` | `apps/web/app/about/page.tsx` |
| `/contact` | `apps/web/app/contact/page.tsx` |
| `/privacy` | `apps/web/app/privacy/page.tsx` |
| `/accessibility` | `apps/web/app/accessibility/page.tsx` |
| `/source-permissions` | `apps/web/app/source-permissions/page.tsx` |
| `/studio` | `apps/web/app/studio/page.tsx` |

`/blog` and `/vanani` are honest "coming soon" states with explicit "we will not invent"
copy — not empty or broken-looking. `lib/catalog.ts` fails gracefully (4s fetch timeout + abort
controller, returns `[]`/`null` on any API error) so pages render informative empty states
("Start the local API…") instead of crashing or showing blank areas when the backend is down.

## `/vanani` naming — explicit recommendation (Phase 5)

The nav entry and page heading both read **"Prabhupāda Vāṇī"** (`apps/web/app/layout.tsx` nav
array; `apps/web/app/vanani/page.tsx` `PageIntro`), but the URL slug is `/vanani` — it drops
"prabhupada" entirely and reads as a doubled/garbled "vani". This looks like an unintentional
transliteration typo rather than a deliberate short slug.

**Recommendation: rename the route to `/prabhupada-vani`** (matches the full nav label exactly,
clearest for SEO and for anyone sharing the link) with **`/vani`** as an acceptable shorter
fallback if brevity is preferred. If `/vanani` has already been shared or indexed anywhere,
add a redirect from `/vanani` → the new slug rather than a hard cut-over. Not changed during
this UAT per the review-only mandate.

## Contact / public identity (Phase 10)

`apps/web/config/contact.json`:
```json
{
  "steward_name": "Svarna Gauranga Das",
  "website": "https://swapnilpatil.tech",
  "contact_url": "https://swapnilpatil.tech/contact",
  "linkedin_url": "https://linkedin.com/in/swapnil-patil-ai-architect",
  "github_url": "https://github.com/swap2you",
  "public_email": ""
}
```
`public_email` is an empty string; `contact/page.tsx` only renders the email `<a>` when
`contact.public_email` is truthy, so **no blank or invented email is ever displayed** — this
requirement is met cleanly.

Identity clarity: the Contact page's only heading is **"Svarna Gauranga Das"** (the devotional
steward name), and its call-to-action button reads "Contact Svarna Gauranga Das" — but that
button, the Website link, LinkedIn, and GitHub all point to **Swapnil Patil's** personal/
professional identity (`swapnilpatil.tech`, `linkedin.com/in/swapnil-patil-ai-architect`,
`github.com/swap2you`). Nothing on the page states the relationship between the two names. A
first-time visitor (public visitor or parent persona) has no way to know these are the same
person. This is a real, evidence-backed instance of Known Item #2 — see Defects.

## Factory Studio UI (Phase 11)

`apps/web/app/studio/page.tsx`: page opens with a fixed banner — *"Local Factory Studio —
loopback only · never expose publicly"*. Shows live `factory_actions_enabled` state fetched from
`/api/v1/local/status`. All three action buttons (`Preflight`, `Generate next`, `Drive readback`)
are `disabled={!enabled}` (HTML-disabled, not just styled to look disabled) whenever
`factory_actions_enabled` is false — i.e., by default. `post()` additionally re-checks `enabled`
client-side before firing a request. No queue-mutation control exists in the UI at all (queue
panel is read-only `<pre>{JSON.stringify(queue)}</pre>`). This matches and reinforces the
server-side enforcement captured live in `api_health_and_safety_evidence.md`.

## Audio player (Phase 6)

`apps/web/components/audio-player.tsx`: play/pause, ±15s skip, speed selector
(`0.75 / 1 / 1.25 / 1.5 / 2×` — exactly the set requested), volume slider, resume position
(`localStorage["bhava:resume:${storyNo}"]`), bookmark save/jump
(`localStorage["bhava:bookmark:${storyNo}"]`), sleep timer (5/15/30 min), keyboard shortcuts
(Space play/pause, ←/→ ±15s, guarded so they don't fire while a text field has focus), Media
Session API wiring for OS-level lock-screen controls, waveform canvas, download link. Both
`resumeKey` and `bookmarkKey` are namespaced by `storyNo`, so one story's saved position/bookmark
cannot leak into another story's player — confirms the "one story's audio never loads for
another" requirement at the code level. No dedicated multi-story "playlist" UI was found next to
the player itself (see Teacher Toolkit note below for the only playlist-shaped feature found).

## Story experience tabs (Phases 6–8)

`apps/web/components/story-experience.tsx` implements Listen / Read / Activities / Coloring /
Source / Notes / Ślokas as tabs:

- **Notes**: `localStorage["bhava:notes:${storyNo}"]` — isolated per story, requires an explicit
  "Save notes" click (no autosave), has a working "Export" (downloads a `.txt` blob) and "Print
  notes" (`window.print()`), and a visible privacy line: *"Notes stay in this browser only
  (localStorage). Bhāva does not upload child notes."* No `fetch`/`POST` call touches notes
  content anywhere in this file or `audio-player.tsx`.
- **Activities (PDF)**: embedded via `<iframe src={activity_pdf_url}>`, plus "Open full tab" and
  "Download PDF" links. The **"Print" button here calls `window.open(url, "_blank")`** — identical
  to "Open full tab" — it does **not** call `window.print()`. Contrast with the Coloring
  lightbox's Print button (below), which does call `window.print()` correctly. See Defects.
- **Coloring**: gallery tiles use real, descriptive `alt` text (`alt={item.label}`, e.g. "Story
  poster", "Detailed coloring", "Simple coloring") and open a lightbox on click. The lightbox has
  no `role="dialog"`/`aria-modal`, no focus trap, and no `Escape`-to-close handler — closing
  requires locating the on-screen "Close" button. See Defects.
- **Source**: shows `source_reference`, `scripture_reference`, `quality_status`, and an explicit
  boundary statement: *"Bhāva shows reviewed package facts and boundaries. It does not republish
  unlicensed full BBT books."*
- **Ślokas**: explicitly placeholder — *"Not yet curated… Placeholders only until reviewed ślokas
  are supplied. We will not invent verses."* Honest, not a defect.

Two instances of a meaningful poster image rendered with **`alt=""`** (effectively invisible to
screen readers) were found: `apps/web/app/page.tsx:38` (homepage hero) and
`apps/web/app/stories/[storyNo]/page.tsx:24` (story sidebar poster). Contrast with the Coloring
gallery's correct use of descriptive alt text above. See Defects.

## Teacher Toolkit (Phase 9)

`apps/web/app/teachers/page.tsx`: age modes (Bal Gopal / Dāmodara / Mixed) each show tailored
guidance text that updates live; a class-pack builder toggles 5 pack items with a live "Selected:"
summary; an answer-key panel defaults hidden behind "Reveal answer key" and explicitly warns
*"Do not invent answers for missing keys."* — all functional, not decorative.

Two items only partially deliver on their label:

- **"Save to classroom playlist"** writes a real entry to
  `localStorage["bhava:classroom-playlist"]` (JSON array with mode/minutes/selected/timestamp) —
  but no confirmation is shown (unlike "Save notes", which shows a toast), and **no page or
  component anywhere in the reviewed source reads that key back** — the data is captured but
  never surfaced to the teacher. From the UI, clicking it looks like it does nothing.
- **"Print / export preview"** saves a plan string to `localStorage["bhava:class-pack"]` and calls
  `window.print()` of the live interactive builder page — there is no dedicated print-friendly
  class-pack layout, and the saved plan text is never displayed or offered as a download, so
  "export" doesn't fully deliver on its label; only the page-print half works.

## PWA (Phase 15)

`apps/web/public/manifest.webmanifest` is present and valid: `name`, `short_name`,
`start_url: "/"`, `display: "standalone"`, `background_color`, `theme_color`, and two icons
(`192×192`, `512×512`) at `public/icons/`. Linked from `app/layout.tsx` metadata
(`manifest: "/manifest.webmanifest"`). No offline service worker was found — that is consistent
with the mission's note not to require offline audio unless explicitly implemented; installability
itself was **not verified live** (would need a running server + Lighthouse/Chrome, not available
in this sandbox).

## Accessibility infrastructure actually present in code (Phase 13)

`packages/ui/src/styles.css` and `apps/web/app/globals.css` were checked directly (not just the
`/accessibility` marketing copy) and do contain real backing for the claims made on that page:
`button:focus-visible, a:focus-visible, [tabindex]:focus-visible { outline: 3px solid ...; }`,
`min-height: 44px` on nav links/buttons/tabs/audio controls, two separate
`@media (prefers-reduced-motion: reduce)` blocks, and a `.reading-mode-dyslexia` rule (increased
letter/word spacing and line-height). This is **static confirmation that the tokens exist in the
stylesheet**, not a live-rendered, live-computed-contrast, or screen-reader-verified pass — per
the mission's own instruction, this is **not** claimed as a WCAG 2.2 AA PASS.

## Cross-browser / e2e test coverage (Phases 13–14, Known Items #3, #4, #6)

- `apps/web/playwright.config.ts` defines **one** project: `chromium`
  (`projects: [{ name: "chromium", use: { ...devices["Desktop Chrome"] } }]`). No `firefox` or
  `webkit` projects are configured.
- `testDir: "./e2e"` — **`apps/web/e2e/` does not exist anywhere in the repository**, and no
  `*.spec.ts` files exist under `apps/web` at all. There are currently **zero** Playwright specs
  to run, on any browser.
- No `axe-core`/`@axe-core/playwright` dependency exists in `apps/web/package.json`, and no test
  file references `axe`. Automated accessibility scanning is not wired up at all yet, on any
  browser, confirming Known Item #4.
