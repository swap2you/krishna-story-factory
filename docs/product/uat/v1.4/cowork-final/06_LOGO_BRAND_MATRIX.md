# V1.4 Logo and Brand Matrix

## Logo — genuinely fixed (positive finding, verified live)

V1.3 finding being re-checked: `logo-small-header.webp` (approved wide wordmark, 3600×520) was forced into a 44×44 `object-fit: cover` crop, destroying the mark.

Live DOM inspection of the rendered homepage header (desktop viewport):
```json
{"src":".../logo-small-header.webp","alt":"bhāva","naturalWidth":3600,"naturalHeight":520,
 "renderedWidth":221.48,"renderedHeight":31.99,"objectFit":"contain","borderRadius":"0px"}
```
Rendered aspect ratio 221.48/31.99 = 6.92 — **matches the native aspect ratio 3600/520 = 6.92 exactly**. `objectFit: contain` (not `cover`), `borderRadius: 0` (not rounded/cropped). Alt text `"bhāva"` — correct spelling, macron present. **This is a genuine, verified fix**, not merely a documentation claim.

Header markup confirms the documented mapping in `BHAVA_V1_4_LOGO_LOCK.md`:
```html
<a class="brand-lockup" aria-label="Bhāva home" href="/">
  <img class="brand-logo-header" src="/brand/logo-small-header.webp" alt="bhāva" width="220" height="32">
  <img class="brand-mark-mobile" src="/brand/logo-icon-only.webp" alt="" width="40" height="40" aria-hidden="true">
  <span class="brand-text-mobile"><span class="wordmark">bh<span>ā</span>va</span><span class="brand-sub">Devotional learning</span></span>
</a>
```
- Desktop: `.brand-logo-header` (true-aspect wide wordmark) — confirmed rendered, `renderedWidth/Height` non-zero.
- Mobile fallback: `.brand-mark-mobile` (icon, `aria-hidden`) + `.brand-text-mobile` (live HTML wordmark with macron `<span>ā</span>` preserved, not a raster crop) — present in the DOM with correct markup and macron; **not independently confirmed at a genuine mobile viewport** because `resize_window` again failed to change `window.innerWidth` from the real maximized-window size (2400×1138) — the fourth consecutive session (V1.1, V1.2, V1.3, V1.4) in which this tool limitation is confirmed. The architecture is correct by inspection; the actual mobile-breakpoint rendering was not visually verified.
- Footer: `logo-dark-bg.webp`, natural 4200×1600, `objectFit: contain` — no distortion (container box is wider than the image's own aspect, so `contain` letterboxes it centered; this is not a crop or stretch).
- Favicon: not independently re-verified this session (carried forward as unchanged from prior rounds; no defect suspected).

## `/dev/logo-sheet`

Exists, labeled "BRAND LABORATORY · NOT IN NAV", shows primary horizontal, compact horizontal, and small variants with the canonical flute-and-lotus mark and correct "bhāva" macron spelling throughout. Not present in `sitemap.xml`. Confirmed absent from the rendered public nav (Home/Library/For Teachers/Prabhupāda Vāṇī/Knowledge/About/Contact only).

## Asset counts (per `docs/brand/BHAVA_V1_4_ASSET_USAGE_REPORT.md`, not independently re-tallied against the full 122-asset MyPilotDropbox inventory this session)

| Asset | Imported | Rendered live |
|---|---|---|
| logo-small-header | yes | **yes — verified live, true aspect** |
| logo-icon-only | yes | yes (mobile DOM node present; viewport not verified) |
| logo-dark-bg | yes | yes (footer, verified live) |
| logo-primary-horizontal / compact-horizontal | yes | comparison sheet only |
| logo-mono-* | yes | partial (print/sheet only) |
| Ceremonial gold logo | yes | explicitly deferred (documented, accepted non-blocking) |

## Not completed this session

- Collection/canto cover art, hero images, Contact/FAQ heroes, learning icons, empty states, and OG/social image were not individually re-screenshotted and dimension-checked this round (carried forward as unchanged from V1.3, where they were found live and correctly wired — no regression suspected, not re-verified).
- No genuine tablet/mobile viewport screenshot was captured (see resize_window limitation above).
