# DEF-CONTRAST-01 — Before / After

## Defect

- **Route:** `/`
- **Section:** CORE AREAS / “A complete devotional learning platform”
- **Before:** `.collection-card` used white text (`#fff`) with **no background** and no media/scrim, so cards sat transparent on cream `rgb(247,240,228)`.
- **CoWork:** confirmed via `getComputedStyle` + axe incomplete contrast nodes.

## Fix

1. Homepage CORE AREAS now render `CollectionCard` (same Library pattern: approved cover art + dark navy scrim body).
2. Base `.collection-card` CSS defaults to a dark navy/indigo gradient — never transparent under white text.
3. `collection-card__body` scrim darkened for WCAG large/normal text contrast.
4. Focus ring: 3px gold outline.
5. Regression: `apps/web/e2e/contrast-home.spec.ts` fails on transparent cards, missing scrim, or white-on-light.

## Contrast (approximate against scrim `rgb(6,22,40)`)

| Pair | Ratio target |
|------|--------------|
| White title on navy scrim | ≥ 4.5:1 |
| Soft white body (`rgba(255,255,255,.92)`) on navy scrim | ≥ 4.5:1 |

## Viewports covered by regression

390×844, 768×1024, 1440×900, 1920×1080 (plus remaining required viewports in full matrix).

## Screenshots

Capture live after `cursor-v16` start into `docs/product/uat/v1.6/contrast/screenshots/`.
