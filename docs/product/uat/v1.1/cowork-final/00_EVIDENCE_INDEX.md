# Evidence Index — Bhāva Portal V1.1 Final CoWork UAT

Companion evidence for `docs/reviews/BHAVA_V1_1_COWORK_FINAL_UAT.md`. All testing was performed
live against the already-running `cursor-v11` instance via the Claude-in-Chrome browser extension,
driving the user's real Chrome browser on Windows.

## Session identity

- SHA tested: `70722981ee19550c8c6ce19137d33c4bdccae9f8` (== `origin/feature/bhava-portal-v1`)
- Branch: `feature/bhava-portal-v1`
- `.bhava/instances/cursor-v11/runtime.json`: web `http://127.0.0.1:3001`, api
  `http://127.0.0.1:8000`, mode `production`, `collision: true` (preferred port 3000 was occupied,
  confirming this instance was not restarted or reconfigured by this review)
- Connected browser: one Chrome instance, Windows, local. No second browser engine was available.

## Key live checks and their direct evidence

**DEF-01 (reader leak) — fixed.** `document.body.innerText` marker search (`Audio Narration`,
`break time`, `Visual Brief`, `Activity Data`, `SSML`, `<break`, `poster_visual_brief`,
`coloring_visual_brief`) returned zero hits on Stories 001–007. Direct fetch of
`http://127.0.0.1:3001/api/v1/stories/007/reader.txt` returned clean prose ending at
"Parent/Teacher Note" with no internal fields — full text captured and inspected.

**DEF-02 (identity leak) — fixed.** Live accessibility-tree read of `/contact` shows:
`link "Email Svarna Gauranga Das" href="mailto:swarnagaurangadas@gmail.com"`,
`link "swarnagaurangadas@gmail.com" href="mailto:swarnagaurangadas@gmail.com"`, and a footer
`contentinfo` block listing only Sunday School / For Preachers / Privacy / Accessibility / Source &
permissions (no Factory Studio link, no civil-name links). Homepage `<meta>` dump: `og:description`
= "Devotional learning for children, parents, and teachers — stewarded by Svarna Gauranga Das." —
no civil name.

**DEF-06 (audio playback) — new finding, reproduced 4 times.** JS state captures across four
independent trials (stories 001, 006, 007 twice — once on a pre-existing tab, once on a freshly
created tab):
```
Trial 1 (story 001, click+wait 3s):  {"paused":false,"currentTime":0,"readyState":0,"networkState":2}
Trial 2 (story 001, reload+click):   {"paused":true, "currentTime":0,"readyState":0,"networkState":2}
Trial 3 (story 006, fresh nav, 5x polling over 3s): all 5 samples {"t":0,"rs":0,"ns":2,"paused":true}
Trial 4 (story 007, brand-new tab, click+wait 3s):  {"paused":true,"currentTime":0,"readyState":0,"networkState":2}
Trial 4 continued (8 more seconds of waiting):       {"paused":true,"currentTime":0,"readyState":0,"networkState":2}
```
Direct `fetch('/api/v1/stories/001/assets/narration.mp3', {method:'HEAD'})` confirmed the file
itself is healthy: `{"status":200,"contentType":"audio/mpeg","contentLength":"3885356","acceptRanges":"bytes"}`.
`read_network_requests` on a fresh page load additionally showed the same URL fetched via `GET`
with `200 OK` within 2 seconds of page load (this is the app's own waveform-loading `fetch()`, not
the `<audio>` element's playback request) — confirming server-side and network-layer health while
the `<audio>` element itself never left `readyState 0`. Root-cause hypothesis (not confirmed, flagged
for the team) recorded against `apps/web/components/audio-player.tsx` lines 42–78 (waveform loader)
and line 138 (`await audio.play()`).

**Coloring carousel — fully built.** Live accessibility-tree captures before/after navigating
Previous → Next confirmed: `dialog` role, `"Showing Detailed coloring, image 3 of 3"` /
`"Showing Simple coloring, image 2 of 3"` live text, per-image `Download` href changing from
`.../coloring_page.png` to `.../simple_coloring_page.png`, keyboard ArrowRight/ArrowLeft
navigation, and Escape-to-close with focus returned to the originating thumbnail (screenshot
evidence: lightbox open state, lightbox after Escape showing focus ring on "Simple coloring").
Print button confirmed to call the browser's native `window.print()` (the automated click blocked
on the native print dialog exactly as expected, requiring a follow-up navigation to clear it —
consistent with genuine `window.print()` behavior, not a new-tab-opening shortcut).

**Factory Studio safety.** `document.querySelectorAll('button')` filtered to the ten
production-action buttons (7× "Rebuild web assets" + Preflight + Generate next + Drive readback)
all returned `disabled: true`. Overview panel text: `"Actions enabled: NO (demo)"`,
`"Loopback enforced: true"`. Full queue JSON dump confirmed chapters 001–007 = `done`, 008–093 =
`pending`, `next_pending.chapter_no = "008"` — matching `data/catalog/locked_queue_state.csv` on
disk exactly.

**KrishnaBook.pdf.** `git status --short` returned no output for this file this session (previously
showed as untracked `??`) because `.gitignore` line 52 now has an explicit `/KrishnaBook.pdf` rule
— confirmed by direct `grep`. `grep -rn "KrishnaBook" apps/web` still returns only the unrelated
`KrishnaBookPage` component name.

**Responsive limitation.** `resize_window({width:390,height:844})` and `({width:500,height:900})`
both reported success; `window.innerWidth/innerHeight` measured immediately after, in both cases,
remained `2400×1068` (the real maximized window). No fabricated multi-viewport pass is claimed.

## Screens captured (screenshot IDs from this session)

| Screen / state | Screenshot ID |
|---|---|
| Homepage (`/`) | ss_0316noki3 |
| `/contact` | ss_433842laj |
| `/about` (text-only capture) | — |
| `/library` full shelf grid | ss_5817xjupz, ss_9514nke8j |
| `/library/srimad-bhagavatam` | ss_5129ln45o |
| `/sunday-school` | ss_81983p729 |
| `/preachers` | ss_7027v4u5j |
| `/studio` overview + queue | ss_1515lauhw |
| Story 001 Listen tab (before/after Play click) | ss_4413e0xsk, ss_6494153dt |
| Story 007 Coloring gallery | ss_7528cxtg3 |
| Story 007 Coloring lightbox open (Simple coloring) | ss_755509n9m |
| Story 007 Coloring lightbox after Next (Detailed coloring) | ss_7764l2291 |
| Story 007 Coloring lightbox after Escape (focus returned) | ss_4894evvdf |
| Story 007 Notes + Teaching reflections | ss_65036zpuh |
| `/blog` topics + planned articles | ss_2019n49f8 |

## Repository changes made by this review

Only the following paths were added by this UAT session:

- `docs/reviews/BHAVA_V1_1_COWORK_FINAL_UAT.md` (the report)
- `docs/product/uat/v1.1/cowork-final/00_EVIDENCE_INDEX.md` (this file)

No application code, story package, queue file, or scheduler file was touched. No cowork-local
instance was started this session (the already-running `cursor-v11` was healthy and used as-is),
so no instance stop was required at the end of this review.
