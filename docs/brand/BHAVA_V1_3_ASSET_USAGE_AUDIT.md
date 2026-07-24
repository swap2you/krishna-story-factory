# Bhāva V1.3 Asset Usage Audit

## Counts

| Measure | Value |
| --- | ---: |
| Canonical approved (manifest) | 122 |
| Imported / registry | 122 |
| Canto covers on disk | 12 |
| Missing required files | 0 |

## Wiring (required)

| Surface | Status |
| --- | --- |
| Header logo (`logo-small-header`) | Wired |
| Library collection covers | Wired via `CollectionCard` |
| All 12 canto covers | Wired on Bhāgavatam index + detail heroes |
| Contact hero | Wired |
| FAQ hero | Wired |
| Knowledge cover | Wired on `/knowledge` |
| Homepage heroes | Already wired (V1.2) |

## Deferred (approved but not every route)

Section banners, learning icons, empty-states, and social OG variants remain available in `public/` and registry; used where product surfaces exist. Marked `approved_deferred` only when a dedicated UI slot is absent — not omitted silently from inventory.

## Provenance note

Eight Phase-5 canto masters were normalized from local Phase-5 batch drafts to 1600×2000 because `bhava-brand-assets-v1-phase5-recreated-complete.zip` was not present in Dropbox. Checksums updated in consolidated manifest; QA batch approval remains the authority for visual intent.
