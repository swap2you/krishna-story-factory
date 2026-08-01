# Bhāva Search Console Operator Checklist

Practical recurring checks for **bhava.me** (production). Staging (`staging.bhava.me`) is **noindex** — do not expect meaningful Search Console data there.

**No invented tokens:** Record only values you obtain from Google Search Console, PageSpeed Insights, or live HTTP headers. Placeholders below are field labels, not secrets.

## Prerequisites

| Item | Action |
| --- | --- |
| Google account | Use org-controlled account with property owner access |
| Domain property | Verify **Domain** property for `bhava.me` (DNS TXT), not URL-prefix only |
| Production only | Confirm you are inspecting `https://bhava.me`, not staging |

## 1. Domain property setup

- [ ] Search Console → **Add property** → **Domain** → `bhava.me`  
- [ ] Add DNS TXT record at registrar (Google-supplied verification string — store in password manager, not git)  
- [ ] Wait for verification; confirm **Ownership verified**  
- [ ] Add delegated users if needed (least privilege)

## 2. Sitemap

- [ ] Confirm live sitemap: `https://bhava.me/sitemap.xml`  
- [ ] Expect **20** story URLs for current public max (001–020); Story 021+ absent until published  
- [ ] Search Console → **Sitemaps** → submit `https://bhava.me/sitemap.xml`  
- [ ] Review **Last read** and **Discovered URLs** — investigate sharp drops after deploys  
- [ ] Cross-check `apps/web/app/sitemap.ts` and `PublicStoryMax` / content release tag

Post-v3 baseline: sitemap includes 001 and 020; excludes 021 ([BHAVA_PRODUCTION_001_020_V3_FINAL_STATUS.md](../releases/BHAVA_PRODUCTION_001_020_V3_FINAL_STATUS.md)).

## 3. Indexing posture

| Environment | Expected |
| --- | --- |
| Production | Indexable story pages; `robots.txt` without global `Disallow: /` |
| Staging | `X-Robots-Tag: noindex` (smoke-tested in `deploy/ionos/scripts/smoke-test.sh`) |

Checks:

- [ ] **URL Inspection** on `/`, `/stories/001`, `/stories/020` → “URL is on Google” or valid reason if new  
- [ ] `/stories/021` → 404 (must not appear in sitemap)  
- [ ] `/studio`, `/dev/*`, `/api/*` → not indexed (404 or blocked)  
- [ ] Confirm canonical URLs use `https://bhava.me/stories/…` (see `apps/web/lib/seo.ts`)

## 4. Core Web Vitals (CWV)

- [ ] Search Console → **Experience** → **Core Web Vitals** (mobile + desktop)  
- [ ] Supplement with [PageSpeed Insights](https://pagespeed.web.dev/) on `/`, `/library`, `/stories/006`  
- [ ] Record LCP, INP, CLS — compare month-over-month, not single-run absolutes  
- [ ] File perf defects against web bundle/images; **no ranking guarantee** from fixes alone

## 5. Structured data monitoring

Bhāva emits JSON-LD on story pages (CreativeWork / BreadcrumbList via `apps/web/app/stories/[storyNo]/page.tsx`).

- [ ] Search Console → **Enhancements** (or Rich results report) — note errors/warnings  
- [ ] [Rich Results Test](https://search.google.com/test/rich-results) on one story URL after material template changes  
- [ ] Validate required fields present: name, description, url, author/publisher where configured  
- [ ] Fix breaking schema changes before next production promote

## 6. Manual actions and security

- [ ] **Security & Manual Actions** → confirm no manual actions or security issues  
- [ ] If issues appear, cross-check TLS cert, malware scan, and recent deploy diff

## 7. Post-deploy routine (within 72h of production promote)

1. URL-inspect homepage + one early + one late story (e.g. 001, 020).  
2. Confirm sitemap last-read updated.  
3. Spot-check CWV report for regressions.  
4. Log release SHA from `/api/v1/version` alongside Search Console notes.

## 8. What not to do

- Do not submit staging URLs to Search Console as canonical.  
- Do not paste verification tokens or API keys into docs, tickets, or commits.  
- Do not claim SEO outcomes (“#1 ranking”) — monitoring only.  
- Do not enable global noindex on production (release blocker per [BHAVA_PUSH_BUTTON_RELEASE_RUNBOOK.md](../deployment/BHAVA_PUSH_BUTTON_RELEASE_RUNBOOK.md)).

## Related

- [BHAVA_SEO_AND_VERSION_FOUNDATION.md](BHAVA_SEO_AND_VERSION_FOUNDATION.md)  
- [BHAVA_PUBLIC_ROUTE_ALLOWLIST.md](../deployment/BHAVA_PUBLIC_ROUTE_ALLOWLIST.md)  
- [BHAVA_PUSH_BUTTON_RELEASE_RUNBOOK.md](../deployment/BHAVA_PUSH_BUTTON_RELEASE_RUNBOOK.md)
