# Bhāva Public Deployment Readiness (bhava.me)

**Status:** Planning / readiness checklist only.  
**Explicit non-goal:** Do **not** deploy, change DNS, provision SSL, or publish factory endpoints in this pass.

Companion docs:

- `docs/deployment/BHAVA_ME_DEPLOYMENT_GUIDE.md` (high-level hosting split)
- `docs/deployment/BHAVA_REQUIRED_ENVIRONMENT.md`
- `docs/deployment/BHAVA_PUBLIC_ROUTE_ALLOWLIST.md`
- `docs/deployment/BHAVA_PRIVATE_ROUTE_DENYLIST.md`
- `docs/architecture/BHAVA_ARCHITECTURE.md`

---

## 1. Intended public shape

| Host | Role | Allowed? |
| --- | --- | --- |
| `bhava.me` | Next.js public PWA (`apps/web`) | Yes (future) |
| `www.bhava.me` | Redirect → apex | Yes (future) |
| Optional `api.bhava.me` | Read-only catalog API (`apps/api` public routers only) | Optional |
| Any public host | `/studio`, `/dev/*`, `/api/v1/local/*`, factory actions | **Never** |

Local acceptance today remains:

- Web: `http://127.0.0.1:3000` (or instance port)
- API: `http://127.0.0.1:8000` bound for loopback studio safety

---

## 2. Pre-deploy product gates (must pass before any host cutover)

| Gate | Requirement | Owner check |
| --- | --- | --- |
| Stories lock | Stories **001–009** match `docs/releases/BHAVA_STORIES_LAUNCH_SAFETY_BASELINE.json` (72 files) | Hash guard / UAT |
| Unpublished | No `output/010_*` public package; `/stories/010` placeholder only + `noindex` | Catalog + page metadata |
| CoWork visual/a11y | DEF-CONTRAST-01, DEF-V173-01/02/03/04 closed | Visual audit doc |
| Automated matrix | Pytest + Playwright green on release SHA | CI / local scripts |
| Dependency security | Upgrade `next` (and related) out of known critical advisory range before public hosting | npm audit gate |
| Secrets | No `.env`, tokens, Drive credentials, or private PDFs in public repo/host env dumps | Repo scan |
| Sitemap | Stories list includes published max (today code still lists 001–007 — fix before SEO go-live) | `sitemap.ts` |
| Robots | Keep `Disallow: /studio` | `public/robots.txt` |

**This checklist being green still does not authorize deploy** until an explicit operator decision.

---

## 3. Studio / Factory loopback (hard boundary)

Public deployment must preserve the local-only factory control plane:

| Control | Default | Public requirement |
| --- | --- | --- |
| `BHAVA_ENFORCE_LOOPBACK` | `true` | Remain enforced on any API process that still mounts `/api/v1/local` |
| `BHAVA_FACTORY_ACTIONS_ENABLED` | `false` | Must stay `false` on public hosts |
| `BHAVA_AUTO_WEB_ASSETS` | `false` | Prefer off on public; rebuild via operator scripts |
| CORS `BHAVA_WEB_ORIGINS` / `BHAVA_WEB_URL` | Localhost ports | Exact `https://bhava.me` (and www if needed) — never `*` |
| Studio UI `/studio` | Local | Block at edge (403/404), omit from nav, robots Disallow |
| CSRF on mutating local routes | Required | Irrelevant if local router not mounted publicly — prefer omit router entirely |

**Preferred public API build:** ship a process that **does not include** `local_factory` router at all. Defense in depth: even if code is present, loopback + factory flag off + edge denylist.

Edge denylist must cover:

- `/studio`, `/studio/*`
- `/dev/*`
- `/api/studio/*`
- `/api/v1/local/*`

---

## 4. Security headers (recommended at CDN / reverse proxy)

Next config today does not emit a full header suite. For public hosting, set at the edge (example targets — tune to final asset hosts):

| Header | Suggested posture |
| --- | --- |
| `Strict-Transport-Security` | `max-age=63072000; includeSubDomains; preload` (after HTTPS proven) |
| `X-Content-Type-Options` | `nosniff` |
| `Referrer-Policy` | `strict-origin-when-cross-origin` |
| `X-Frame-Options` / `frame-ancestors` | `DENY` or CSP `frame-ancestors 'none'` (unless a deliberate embed need appears) |
| `Permissions-Policy` | Disable unused powerful APIs (`camera=()`, `microphone=()`, `geolocation=()`) |
| `Cross-Origin-Opener-Policy` | `same-origin` (validate audio/player still OK) |

Do not weaken CORS to fix local Studio; Studio stays loopback-only.

---

## 5. Content-Security-Policy (CSP) notes

Bhāva pages use inline styles in places and Next.js hydration scripts. A strict nonce/hash CSP is desirable but must be rolled out carefully.

**Phase A (launch-safe starter):** report-only CSP collecting violations for 1–2 weeks.

Example report-only sketch (adjust before enforce):

```http
Content-Security-Policy-Report-Only:
  default-src 'self';
  script-src 'self' 'unsafe-inline' 'unsafe-eval';
  style-src 'self' 'unsafe-inline';
  img-src 'self' data: blob:;
  media-src 'self' blob:;
  connect-src 'self' https://api.bhava.me;
  font-src 'self';
  object-src 'none';
  base-uri 'self';
  frame-ancestors 'none';
  report-uri /csp-report
```

**Phase B (enforce):** replace `'unsafe-inline'` / `'unsafe-eval'` with nonces once Next header integration is validated; keep `media-src` allowing `blob:` for the story audio playback path; keep `connect-src` limited to same-origin and the public API host.

**Never** allow arbitrary third-party script CDNs without review.  
**Never** put factory/admin origins in `connect-src` for the public site.

---

## 6. Health & readiness probes

| Probe | URL | Expect |
| --- | --- | --- |
| API liveness | `GET /api/v1/health` | `200` `{"status":"ok","service":"bhava-api"}` |
| Web liveness | `GET /` | `200` HTML |
| Story smoke | `GET /stories/001` | `200` |
| Asset smoke | `GET /api/v1/stories/001/assets/narration.mp3` | `200` / `206` audio |
| Negative | `GET /api/v1/local/status` from public network | `403` / `404` / connection refused |
| Negative | `GET /studio` from public | Blocked |

Wire load balancer health to API health + web `/` (or a dedicated lightweight web health route if added later). Do not use Studio status as a public probe.

---

## 7. Data & runtime adapters before leaving localhost

| Local default | Public target |
| --- | --- |
| SQLite `data/catalog/bhava.sqlite` | PostgreSQL-ready repositories (Knowledge DDL already sketched) |
| Filesystem packages under `output/` | Object storage or read-only mounted package store |
| Next rewrite to `127.0.0.1:8000` | `BHAVA_API_ORIGIN=https://api.bhava.me` (or same-origin `/api` to internal upstream) |
| Dynamic instance ports | Fixed production ports behind TLS terminator |

---

## 8. Rollback plan (when a future deploy exists)

Documented for readiness; **do not execute** as part of this documentation task.

1. **Keep previous artifact:** prior web build + prior API image/tag + prior DB migration version.  
2. **DNS/CDN:** retain previous origin as instant swap target; avoid long TTL during first cutover.  
3. **Content rollback:** story packages are hash-locked — prefer reverting web/API code, not rewriting packages.  
4. **Feature flags:** ensure `BHAVA_FACTORY_ACTIONS_ENABLED=false` remains default on every environment.  
5. **Verify after rollback:** `/api/v1/health`, `/stories/001`, `/stories/009`, printables asset, confirm `/studio` and `/api/v1/local/*` still blocked.  
6. **Communication:** if public, post brief status on Contact/steward channel; do not hot-fix locked story binaries.

---

## 9. Operator “go / no-go” summary

| Question | Go only if |
| --- | --- |
| Deploy now? | **No** — this document is readiness only |
| Public factory? | **Never** |
| Stories 001–009 intact? | Hash baseline green |
| Headers/CSP planned? | Edge config drafted; CSP preferably report-only first |
| Rollback rehearsed on staging? | Yes (future staging env) |
| Secrets scanned? | Yes |

When an operator later authorizes deploy, update this file with the chosen host, TLS provider, and exact rollback tag — still without embedding secrets.
