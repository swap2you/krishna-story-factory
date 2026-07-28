# 04 — Accessibility & Screenshot Review

## Fresh axe scans (Section G) — ZERO critical/serious across all major routes

axe-core 4.9.1, `wcag2a`+`wcag2aa`, run fresh this session (live page for `/stories/009`; 1440×900 same-origin iframes for the rest):

| Route | Violations |
|---|---|
| `/` | 0 |
| `/rights` | 0 |
| `/library` | 0 |
| `/knowledge` | 0 |
| `/teachers` | 0 |
| `/preachers` | **0** (V1.7.3's `aria-required-children` critical — FIXED) |
| `/contact` | 0 |
| `/faq` | 0 |
| `/printables` | 0 |
| `/sunday-school` | 0 |
| `/prabhupada-vani` | 0 |
| `/about` | 0 |
| `/stories/001` | 0 |
| `/stories/009` | **0** (V1.7.3's Speed/Sleep select 1.33:1 contrast — FIXED; selects now `rgb(11,27,43)` on white, ~14.9:1) |

**Requirement "zero critical/serious findings": MET.**

## Committed screenshots (Section G)

- `docs/product/launch/screenshots/`: 26 PNGs × 6 viewports (390×844, 430×932, 768×1024, 1024×768, 1440×900, 1920×1080) = **156 files, all git-tracked**, matching `metadata.json.screenshot_png_count`.
- **Integrity: all 156 recomputed SHA-256 hashes match `screenshot-index-hash.json` exactly (156/156).**
- Rights screenshots: `rights.png` present in all 6 viewports (= evidence `rights_screenshot_count: 6`).
- Visual review performed on: `1440x900/rights.png` (full rights page — all seven sections legible, dark-navy footer with high-contrast gold/white links, no white-on-white anywhere), `390x844/story-009-listen.png` (full-page mobile capture, no horizontal clipping), plus live 1920 inspection of home/story/rights pages. Poster and coloring-page source PNGs visually reviewed for credit placement and sacred-subject unobstruction (see file 02).

## Layout probes (fresh, this session)

- 390×844 iframe probes on `/`, `/rights`, `/stories/009`, `/library`: **zero horizontal overflow**.
- 200% zoom proxy (720px-wide viewport ≈ 1440@200%): same four routes, **zero horizontal overflow**.
- Footer contrast: dark navy (#0B1B2B-family) background with white/gold text — visually high-contrast, corroborated by zero axe contrast violations on every scanned route.

## Keyboard/focus

Player documents its keyboard map on-page ("Space play/pause · ← −15s · → +15s (disabled while a dialog is open)"); modal keyboard-isolation and focus-return behavior was live-verified in the V1.5 cycle and the tab controls remain keyboard-reachable buttons (native `<button>`/`<select>` elements throughout the player — no div-button antipatterns observed).
