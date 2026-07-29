# 04 — Visual Contrast & Typography (White-on-White Defect)

## Summary

**A systemic, release-blocking white-on-white contrast defect was independently confirmed on the homepage's "CORE AREAS" section.** This exactly matches the mission's explicitly-flagged operator hypothesis.

## Live computed-style inspection

Navigated to `http://127.0.0.1:3005/` and inspected all 8 `.collection-card` elements under the "CORE AREAS / A complete devotional learning platform" heading (Krishna Book Stories, Knowledge Library, Prayers & Ślokas, Sunday School, Teacher Resources, Printables, Prabhupāda Vāṇī, Devotee Lives) via `getComputedStyle`.

Findings, for every one of the 8 cards:

- Title/description text color: `rgb(255,255,255)` / `rgba(255,255,255,0.82)` (white / near-white)
- Card `backgroundImage`: `none`
- Card `backgroundColor`: `rgba(0,0,0,0)` (fully transparent)
- No `<img>` child element present inside the card at all

Because the card itself has no background image and no opaque background color, the text renders directly against the page's plain cream body background, `rgb(247,240,228)`. White text at ~82–100% opacity on a cream (#F7F0E4-ish) background is far below WCAG AA contrast thresholds — effectively unreadable body copy on several cards, and low-contrast headings on all of them.

## Automated corroboration (axe-core)

Ran axe-core 4.9.1 (`wcag2a` + `wcag2aa` rule tags) live against the rendered homepage:

- `violations`: 0 (axe cannot assert a hard violation when it cannot programmatically resolve the effective background color)
- `incomplete` → `color-contrast`: **99 nodes, impact `serious`**, requiring manual verification

Filtering the 99 "incomplete" nodes for `.collection-card` targets returns exactly the affected cards, e.g.:

```
.collection-card[href$="knowledge"] > h3
.collection-card[href$="knowledge"] > p
.collection-card[href$="sunday-school"] > h3
.collection-card[href$="sunday-school"] > p
.collection-card[href$="teachers"] > h3
.collection-card[href$="teachers"] > p
.collection-card[href$="printables"] > h3
.collection-card[href$="printables"] > p
.collection-card[href$="prabhupada-vani"] > h3
.collection-card[href$="prabhupada-vani"] > p
```

axe's `failureSummary` for these nodes: *"Element's background color could not be determined because it's partially obscured by another element"* — consistent with a transparent card sitting directly on the page background with no resolvable backdrop, i.e. corroborating the manual finding rather than contradicting it.

## Isolation check — `/library` page is NOT affected

The `/library` page's own collection cards use a **different, correct implementation**: a dark-navy solid text panel rendered beneath real artwork/photography (a scrim/overlay-gradient technique). Running the same axe scan on `/library` also returns `color-contrast` as "incomplete" (80 nodes) — but inspecting those nodes shows the failure reason is *"background gradient"* (axe cannot resolve gradients automatically), not *"background color transparent / no image"*. Manual computed-style + visual inspection of the `/library` cards confirms genuinely sufficient contrast (dark panel, light text, real photographic backdrop).

**Conclusion: the defect is isolated to the homepage's `.collection-card` component and is not a global CSS regression.** The `/library` page proves the design system has a correct pattern available; the homepage component simply never received the background image/scrim that the design intends.

## Defect record

| Field | Value |
|---|---|
| ID | DEF-CONTRAST-01 |
| Severity | **P0/P1 — release-blocking** |
| Route | `/` (homepage), "CORE AREAS" section |
| Browser | Reproduced in Chromium; CSS-level defect, expected to reproduce in all browsers |
| Viewport | Reproduced at desktop width; card markup identical across breakpoints, so expected to persist across all responsive widths |
| Affected audience | All visitors landing on the homepage — this is the primary discovery surface for the entire site's content areas |
| Exact reproduction | Load `/`, scroll to "CORE AREAS", inspect any of the 8 `.collection-card` elements' text vs. background |
| Expected | Dark/photo background beneath white text (matching `/library`'s working pattern), sufficient contrast |
| Actual | `backgroundImage: none`, `backgroundColor: rgba(0,0,0,0)`, no `<img>` child — white text directly on cream page background |
| Evidence | Live `getComputedStyle` dump (this file) + axe-core `color-contrast` incomplete-node corroboration (99 nodes homepage-wide, 12+ specifically `.collection-card` targets) |
| Release-blocking | **Yes**, per mission Section 22: "severe white-on-white or unreadable contrast affects a primary experience" |
| Recommended correction | Apply the same photo + scrim/dark-panel pattern already used correctly on `/library`'s collection cards to the homepage's `.collection-card` component — either restore the missing background image or add an opaque/dark panel behind the text. |

## Typography

No separate typography defects found. Brand display font (Tillana) renders correctly; heading/body type stack is legible everywhere except where obscured by the contrast defect above.

## Verdict for this section

**FAIL** — DEF-CONTRAST-01 is confirmed, reproducible, and release-blocking per the mission's own verdict rules.
