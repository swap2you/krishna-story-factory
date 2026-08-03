# BHAVA_PRODUCTION_001_020_V3_FINAL_STATUS

## Verdict

**PASS — PRODUCTION V3 LIVE**

Production is approved for Stories 001–020 on content `bhava-content-001-020-v3`.

## Identity

| Item | Value |
|---|---|
| Starting develop SHA (RELEASE_DEVELOP_SHA) | `a9d787b6a40123349ed7c742e6c699a5e733d291` |
| Release PR | https://github.com/swap2you/krishna-story-factory/pull/32 |
| Merge method | merge commit |
| Merged / PRODUCTION_MAIN_SHA | `30e720cd22cb333e087b3d5e48faeac0056dcde3` |
| Merge timestamp | 2026-08-01T16:11:26Z |
| Prior main / rollback target | `660831dbdaad97d934917bbb367d84424850b64a` |
| Content tag | `bhava-content-001-020-v3` |
| Content SHA-256 | `35c40da62e6695f7caca9f1eff30da493382c95b1b7a4d7fbbb706d1ffb64f93` |
| Public stories | 001–020 |
| Story 021 | private / pending / not generated |
| Scheduler | Disabled |
| Web tag | `bhava-web-001-020-v3` |
| GitHub Release | https://github.com/swap2you/krishna-story-factory/releases/tag/bhava-web-001-020-v3 |

## Release PR checks

All required CI checks on PR #32 succeeded (source-unit, portal-fixture, web-checks, content-release, production-security, production-gate, browser Chromium/Firefox/WebKit desktop + mobile, studio).

Copilot threads on sample-first / web-assets fail-closed gates were replied as intentional create-next posture and resolved before merge.

## Production workflow

| Item | Value |
|---|---|
| Run | https://github.com/swap2you/krishna-story-factory/actions/runs/30707599632 |
| Approval | Protected `production` environment approved for exact SHA `30e720c` + content v3 |
| Checkout SHA | `30e720cd22cb333e087b3d5e48faeac0056dcde3` |
| Content | `bhava-content-001-020-v3` (checksum verified by workflow) |
| TLS | Ready (HTTP 200) |
| Smoke | Passed (`public_max=20`) |
| Rollback pointer | Ready (`previous=660831d…`) |

## Live technical UAT (post-deploy)

| Check | Result |
|---|---|
| https://bhava.me | 200 |
| www → apex | 301 then 200 |
| `/api/v1/version` | `release_sha=30e720c…`, `environment=production`, `public_story_max=20` |
| `/api/v1/health` | ok |
| robots.txt | No global noindex; private routes Disallow |
| sitemap.xml | 20 story URLs; excludes 021; includes 001 and 020 |
| Stories 001/009/020 HTML | 200; indexable; canonical `https://bhava.me/stories/…` |
| Story 021 | 404 |
| `/studio`, `/dev`, `/api/studio`, `/api/v1/local`, `/api/v1/factory`, `/api/v1/scheduler`, `/api/v1/queue` | 404 |
| Narration Range | 206 `audio/mpeg` |
| Rights on spot stories | No `contact_email`; no unsupported “used with permission” |
| Ślokas API | Present for spot stories 001/005/006/009/011/019/020 |

## Known accepted deferrals

- Some chapter-framed Śloka references
- Follow-along alignment backlog (`docs/backlog/FOLLOW_ALONG_ALIGNMENT.md`)
- Temporary recommended slower rates for selected narration
- Catalog JSON may still expose internal `quality_status` fields; public UI PASS badge was removed in v3 UX work

## Residual security limitations (honest)

Tested controls include public-route blocking, TLS, Basic Auth on staging only, content checksum, rollback pointer, and production smoke. This does **not** claim the site is hack-proof.

## Branch synchronization

- Trees of `origin/main` and `origin/develop` match (`8c0c256…`)
- Sync PR main→develop: https://github.com/swap2you/krishna-story-factory/pull/33 (merge commit ancestry)

## Permanent remote branches

- `main`
- `develop`

## Paid spend

TTS $0 · Image generation $0 · Story 021 not generated
