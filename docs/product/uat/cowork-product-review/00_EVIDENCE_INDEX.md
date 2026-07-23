# Evidence Index — Bhāva Portal V1 CoWork Product/UX UAT

Companion evidence for `docs/reviews/BHAVA_V1_COWORK_PRODUCT_UX_UAT.md`. This review was performed
live against the already-running `cursor-uat` instance via the Claude-in-Chrome browser extension,
driving the user's real Chrome browser on Windows. Screenshot IDs below are internal tool
references captured during the session (not files written to this repo — the live browser was the
system under test, not a local build).

## Session identity

- HEAD tested: `73e1a8da7eb4a0d70aab8c2f6d6d1becd8805d85` (== `origin/feature/bhava-portal-v1`)
- Branch: `feature/bhava-portal-v1`
- `.bhava/instances/cursor-uat/runtime.json`: web `http://127.0.0.1:3000` (pid 37244), api
  `http://127.0.0.1:8000` (pid 11748), mode `production`
- Connected browser: one Chrome instance (`deviceId e7a1d952-c82f-41aa-9b3b-e972ba591760`,
  Windows, local) — no Firefox/WebKit instance was available to connect to live.

## Screens captured (screenshot IDs from this session)

| Screen / state | Screenshot ID(s) |
|---|---|
| Homepage hero | ss_98070s5pq |
| Homepage scrolled (shelves + latest stories) | ss_7252jk2u1 |
| `/library` | ss_1120f83od |
| `/stories/007` Coloring tab (gallery) | ss_3459gemvi |
| `/stories/007` Coloring lightbox open | ss_0907fq6re |
| `/stories/007` Coloring lightbox closed via Escape (focus returned) | ss_2902oz7ri |
| `/stories/007` Source tab | ss_8494ydjmz |
| `/stories/007` Notes tab | ss_5006urwpk |
| `/stories/007` Ślokas tab (honest placeholder) | ss_211906sl5 |
| `/source-permissions` | ss_7336n7gwe |
| `/about` | ss_2217qh3vi |
| `/contact` (identity leak evidence) | ss_3945ob7tl |
| Story 001 Read tab, scrolled to leaked internal content | ss_8808ewpki (from prior live session, same instance/branch) |

Additional screens (Listen tab player states, story 001 full walkthrough, `/library/krishna-book`)
were captured in the immediately preceding portion of this same review session against the same
HEAD and are referenced by ID in the main report where cited.

## Live checks performed via DOM/console/network inspection (not just screenshots)

- `read_page` (accessibility tree) on `/library` confirming only the Krishna Book shelf card has a
  real `href`; the other two shelf cards have no link/role, confirming DEF-03.
- `read_page` (accessibility tree) on the Coloring lightbox confirming a real `dialog` role exists,
  and a live Escape-key press confirming close-with-focus-return.
- `read_console_messages` across the full session: 52 messages captured, all from an unrelated
  third-party browser extension (`clipto-webext`), zero from the Bhāva application.
- Live click on the Activities tab's "Print" button confirmed it opens
  `/api/v1/stories/007/assets/activity_sheet.pdf` in a new tab (`tabs_context_mcp` showed the new
  tab's URL directly) rather than invoking `window.print()` — confirms DEF-04.
- `javascript_tool` reading `window.innerWidth`/`innerHeight` before and after multiple
  `resize_window` calls (targets: 390×844, 500×900) confirmed the live window never actually
  changed size (remained 2400×1068 CSS px throughout) — this is why the 7-viewport sweep is
  reported as a documented limitation rather than a completed pass in the main report.

## Filesystem / git checks (read-only)

```
git rev-parse HEAD                        -> 73e1a8da7eb4a0d70aab8c2f6d6d1becd8805d85
git rev-parse origin/feature/bhava-portal-v1 -> 73e1a8da7eb4a0d70aab8c2f6d6d1becd8805d85
git status --short                         -> ?? KrishnaBook.pdf   (only line)
git branch --show-current                  -> feature/bhava-portal-v1
```

`KrishnaBook.pdf` metadata (existence + metadata only — no text extracted, copied, or exposed):

```
pdfinfo KrishnaBook.pdf
Title:        Krsna, The Supreme Personality of Godhead
Author:       His Divine Grace A. C. Bhaktivedanta Swami Prabhupada
Pages:        863
Encrypted:    yes (RC4; print:no copy:yes change:no addNotes:no)
Producer:     Acrobat Distiller 4.0 for Macintosh
CreationDate: Fri Nov  8 2002
```

Confirmed via `grep -rn "KrishnaBook" apps/web` that the PDF itself is not referenced or served by
any application code path (the only match is the unrelated component name `KrishnaBookPage`).

`.gitignore` was checked for explicit coverage of root-level PDFs — no matching rule exists
(informs DEF-05).

CSS breakpoints in the codebase (`apps/web/app/globals.css`): `max-width: 960px` (line 194),
`max-width: 720px` (line 218), plus two `prefers-reduced-motion` blocks — read directly to support
§19/§21 of the main report given the live multi-viewport sweep limitation.

## Repository changes made by this review

Only the following paths were added by this UAT session — no application code, story package,
queue, or scheduler file was touched:

- `docs/reviews/BHAVA_V1_COWORK_PRODUCT_UX_UAT.md` (the report)
- `docs/product/uat/cowork-product-review/00_EVIDENCE_INDEX.md` (this file)
