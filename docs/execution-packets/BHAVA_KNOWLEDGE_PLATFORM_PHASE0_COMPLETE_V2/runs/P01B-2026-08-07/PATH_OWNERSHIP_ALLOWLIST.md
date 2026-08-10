# Path Ownership Allowlist — Future P01C

One application-code writer on the feature branch. Specialists read-only unless non-overlapping assigned artifacts.

| Path / pattern | Owner | Allowed change |
|---|---|---|
| `packages/contracts/schemas/knowledge_record*.json` (new) | Schema | Add canonical schema |
| `content/knowledge/packages/**` | Content | Pilot packages only |
| `apps/web/lib/knowledge/**` | Web | Loader/adapters/governance |
| `apps/web/app/studio/knowledge/**` | Web | Pagination + preview entry |
| `apps/web/app/studio/**/preview/**` | Web | Private preview pages |
| `apps/web/components/knowledge/**` (new as needed) | Web | Stanza/lens/focus/source |
| `apps/web/middleware.ts`, `app/robots.ts`, `app/sitemap.ts` | Web | Privacy/SEO |
| `apps/api/bhava_api/knowledge/**` | API | Search/gates/auth bind |
| `packages/ui/src/**` | UI | Tokens/fonts only as approved |
| Export module (TBD under api or factory knowledge export) | Export | After OD-02 |
| `tests/**`, `apps/web/e2e/**` | QA | Boundary/a11y/export |
| `docs/execution-packets/.../runs/P01*/**` | Docs | Evidence only |

## Not allowlisted

`krishna_story_factory` story pipeline, `deploy/content/RELEASE_CONTENT.json`, scheduler scripts, `output/`, `.env`, public prayer publication, Stories 001–022 packages, Postgres cutover.
