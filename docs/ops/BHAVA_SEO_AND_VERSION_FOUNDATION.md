# Bhāva SEO and Version Foundation

Foundation for **version transparency**, **canonical URLs**, and **environment-aware indexing**. Complements [BHAVA_SEARCH_CONSOLE_OPERATOR_CHECKLIST.md](BHAVA_SEARCH_CONSOLE_OPERATOR_CHECKLIST.md).

**SEO limitation (explicit):** Bhāva implements technical SEO hygiene only. **No ranking guarantee**, traffic forecast, or Search Console outcome promise.

## Version footer format

Public footer uses build-time metadata from `apps/web/lib/release-meta.ts`:

```
Bhāva Web {webVersion} · Content {NNN NNN vN} · Build {shortSha}
```

Example shape (values come from env at build/deploy — do not hard-code in docs):

```
Bhāva Web 1.0.0 · Content 001 020 v3 · Build 30e720c
```

Implementation:

- `formatFooterReleaseLine()` strips `bhava-content-` prefix and hyphenates for display.  
- `shortSha` = first 7 chars of git SHA, or `dev` when unset.

## Environment variables

Set at **build** (Next.js) or via deploy workflow. Never commit secrets.

| Variable | Purpose | Example / default |
| --- | --- | --- |
| `NEXT_PUBLIC_BHAVA_WEB_VERSION` | Semver shown in footer | From release tag or CI |
| `BHAVA_WEB_VERSION` | Fallback if public var unset | Same |
| `NEXT_PUBLIC_BHAVA_CONTENT_RELEASE` | Content bundle label | `bhava-content-001-020-v3` |
| `BHAVA_CONTENT_RELEASE` | Fallback | Same |
| `NEXT_PUBLIC_BHAVA_GIT_SHA` | Full commit SHA | Deployed release SHA |
| `BHAVA_RELEASE_SHA` | Fallback | Same |
| `BHAVA_CANONICAL_ORIGIN` | Canonical host | `https://bhava.me` (default in `seo.ts`) |

API mirror: `/api/v1/version` returns `release_sha`, `environment`, `public_story_max`, content release fields for smoke tests.

Deploy reference: [BHAVA_REQUIRED_ENVIRONMENT.md](../deployment/BHAVA_REQUIRED_ENVIRONMENT.md), [BHAVA_PUSH_BUTTON_RELEASE_RUNBOOK.md](../deployment/BHAVA_PUSH_BUTTON_RELEASE_RUNBOOK.md).

## Canonical URLs

- Origin: `BHAVA_CANONICAL_ORIGIN` → default `https://bhava.me`.  
- Story pages: `https://bhava.me/stories/{NNN}` via `pageMetadata` / JSON-LD.  
- `www` → apex redirect expected (301) on production.  
- Unpublished placeholders (021+ before release): HTTP 200 placeholder OK by design; must send **`noindex`**.

Code: `apps/web/lib/seo.ts`, `apps/web/app/stories/[storyNo]/page.tsx`, `apps/web/app/sitemap.ts`, `apps/web/app/robots.ts`.

## Indexing: staging vs production

| Environment | robots / headers | Operator expectation |
| --- | --- | --- |
| **Staging** | `X-Robots-Tag: noindex` | Smoke fails if missing ([smoke-test.sh](../../deploy/ionos/scripts/smoke-test.sh)) |
| **Production** | Indexable stories; no global noindex | Release blocker if production sends site-wide noindex |

`robots.ts` disallows private paths (`/studio`, `/dev`, etc.); production must not disallow entire public catalog.

## Sitemap scope

- Generated from published catalog up to `public_story_max`.  
- v3 production: **20** URLs (001–020); **021 excluded** until published.  
- Submit only production sitemap URL to Search Console.

## Structured data (baseline)

Story pages emit schema.org JSON-LD (CreativeWork, breadcrumbs). Validate after template changes — see Search Console checklist.

## Content tags (reference)

| Tag | Role |
| --- | --- |
| `bhava-content-001-020-v2` | Prior published quality-completion |
| `bhava-content-001-020-v3` | Current production content (001–020) |
| `bhava-web-001-020-v3` | Matching web release tag |

Footer **Content** line should match deployed content tag. Mismatch between footer and `/api/v1/version` is a deploy defect.

## Operator quick check

```powershell
# Production (no auth)
curl -sS https://bhava.me/api/v1/version
curl -sI https://bhava.me/stories/001 | findstr /i "robots"
curl -sS https://bhava.me/sitemap.xml
```

```powershell
# Staging (Basic Auth when configured — use real credentials from secret store)
bash deploy/ionos/scripts/smoke-test.sh https://staging.bhava.me <expected-sha> staging
```

## Non-goals

- No SEO “playbook” promising traffic growth.  
- No staging URLs in sitemap or canonical tags.  
- No invented version strings in documentation — always read live `/api/v1/version` or deploy env.

## Related

- [BHAVA_SEARCH_CONSOLE_OPERATOR_CHECKLIST.md](BHAVA_SEARCH_CONSOLE_OPERATOR_CHECKLIST.md)  
- [BHAVA_POST_V3_SECURITY_REVIEW.md](../security/BHAVA_POST_V3_SECURITY_REVIEW.md)  
- [BHAVA_PRODUCTION_001_020_V3_FINAL_STATUS.md](../releases/BHAVA_PRODUCTION_001_020_V3_FINAL_STATUS.md)
