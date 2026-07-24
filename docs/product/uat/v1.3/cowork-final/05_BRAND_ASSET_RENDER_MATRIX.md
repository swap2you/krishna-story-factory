# V1.3 Brand Asset Render Matrix

Manifest claim (`docs/brand/BHAVA_V1_3_CANONICAL_ASSET_INVENTORY.json`): 122 approved, 122 imported,
across 10 categories (logo_system 12, platform_icons 11, homepage_heroes 10, collection_covers 15,
canto_covers 12, section_banners 12, social_sharing 10, learning_icons 22, empty_states 11,
contact_faq 7). This matrix independently verifies *rendering*, not just presence, for each category.

| Category | Count | Rendered in live app? | Evidence |
|---|---:|---|---|
| logo_system | 12 | **1 of 12 wired** (`logo-small-header.webp`, header + favicon) | `apps/web/app/layout.tsx` lines 18/51; screenshot header on every page this session |
| platform_icons | 11 | Not independently re-verified this session (favicon/PWA icons load via manifest; not exhaustively checked) | — |
| homepage_heroes | 10 | 2 of 10 wired (unchanged from V1.2) | `apps/web/app/page.tsx` |
| collection_covers | 15 | **Now wired** — Library grid shows distinct art per collection | `apps/web/components/collection-card.tsx` → `collectionCoverPath()`; screenshot `ss_59990t1le` |
| canto_covers | 12 | **Now wired** — 12 covers confirmed via `cantoCoverPath()`; visually confirmed 5 distinct thumbnails without scrolling, plus 1 canto detail hero (canto 10) | `apps/web/app/library/srimad-bhagavatam/page.tsx`, `.../canto/[canto]/page.tsx`; screenshots `ss_7410r2h2p`, `ss_8554g7x5v` |
| section_banners | 12 | **Still 0 of 12 wired** | `grep -rn "/sections/section-" apps/web/app apps/web/components` → zero matches |
| social_sharing | 10 | **Still 0 of 10 wired** | `grep -rn "/social/" apps/web/app apps/web/components` → zero matches |
| learning_icons | 22 | **Still 0 of 22 wired** | `grep -rn "/icons/icon-" apps/web/app apps/web/components` → zero matches |
| empty_states | 11 | **Still 0 of 11 wired** | `grep -rn "/empty-states/" apps/web/app apps/web/components` → zero matches |
| contact_faq | 7 | **2 of 7 confirmed wired** (Contact hero, FAQ hero) | `apps/web/app/contact/page.tsx` line ~81 `heroSrc={brandSrc("hero-contact-page")}`; `apps/web/app/faq/page.tsx` line ~76; screenshots `ss_99547b5mt`, `ss_1086d7aue` |

## Notable code-level finding

`apps/web/lib/brand-assets.ts`'s `collectionCoverPath()` maps `"knowledge"` and `"bhakti-blog"` both to
the same underlying asset ID, `collection-bhakti-blog`. There is no distinct Knowledge-specific cover
in the approved asset library — the Knowledge collection card (where it appears, e.g. on `/library`
if referenced) reuses the old Bhakti Blog cover image. Minor, but worth noting since Knowledge is a
new, differently-scoped product surface from the old Blog.

## Visual judgment (desktop only — see Runtime section of the main report for the responsive-testing limitation)

- `/library`: clean, organized 4-column card grid at desktop width, each card showing distinct,
  correctly-matched cover art with a dark gradient scrim for text legibility. No longer looks like a
  placeholder.
- `/library/srimad-bhagavatam`: 5-column canto grid, each card showing a distinct golden/devotional
  illustration matching that canto's theme (e.g., a churning-ocean or cosmic-mandala motif for the
  cosmology-themed cantos). Reads as intentional, not generic stock art.
- `/library/srimad-bhagavatam/canto/10` ("The Summum Bonum"): large hero background depicting Kṛṣṇa
  with a flute, thematically appropriate for the canto describing Kṛṣṇa's pastimes.
- `/contact`, `/faq`: both now have a warm, on-brand hero image behind the page heading (a devotee
  figure for Contact, a father-with-children scene for FAQ) rather than the plain gradient background
  seen in the V1.2 UAT.

None of the above was checked at tablet or mobile width this session (see the Runtime section's note
on the `resize_window` tool not functioning against the real, maximized browser window in this
environment).
