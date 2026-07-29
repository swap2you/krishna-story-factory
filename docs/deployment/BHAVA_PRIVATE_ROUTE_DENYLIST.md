# Bhāva Private Route Denylist

Routes, APIs, and surfaces that must **never** be reachable on public `bhava.me` (or must be blocked at the edge even if the app binary contains the code).

**Related:** `BHAVA_PUBLIC_ROUTE_ALLOWLIST.md`, `BHAVA_PUBLIC_DEPLOYMENT_READINESS.md`, `apps/web/public/robots.txt`.

---

## 1. Policy

```text
deny > robots Disallow > app-level loopback > feature flags
```

Defense in depth:

1. Edge / CDN returns **404 or 403** for denylisted paths.  
2. `robots.txt` Disallow for Studio (crawlers are not a security boundary).  
3. API `BHAVA_ENFORCE_LOOPBACK=true` on `/api/v1/local/*`.  
4. `BHAVA_FACTORY_ACTIONS_ENABLED=false` so even loopback cannot mutate without intent.  
5. Prefer **not mounting** `local_factory` router in the public API process.

---

## 2. Web UI denylist

| Pattern | Reason |
| --- | --- |
| `/studio` | Factory Studio control UI |
| `/studio/*` | Includes `/studio/knowledge` editorial stub |
| `/dev` | Dev-only tools root (if present) |
| `/dev/*` | `/dev/audio-lab`, `/dev/logo-sheet`, future labs |
| `/api/studio` | Studio session helper |
| `/api/studio/*` | Any studio API under web app |

**Nav rule:** these routes must not appear in `SiteHeader` or `SiteFooter` (current code already omits them).

**Robots (already present):**

```text
Disallow: /studio
```

Extend Disallow for `/dev` when publishing robots for production if those folders ship in the build.

---

## 3. Factory / local API denylist

| Pattern | Methods | Reason |
| --- | --- | --- |
| `/api/v1/local` | * | Prefix for factory gateway |
| `/api/v1/local/*` | GET/POST | status, queue, runs, scheduler, preflight, generate-next, drive/readback, rebuild, scheduler enable/disable |
| Any future `/api/v1/admin/*` | * | Not for public |
| Any shell/exec proxy | * | Forbidden by design |

Known local routes today (`apps/api/bhava_api/routes/local_factory.py`):

- `GET /api/v1/local/status`
- `GET /api/v1/local/queue`
- `GET /api/v1/local/runs`
- `GET /api/v1/local/scheduler`
- `POST /api/v1/local/preflight`
- `POST /api/v1/local/generate-next`
- `POST /api/v1/local/drive/readback`
- rebuild / scheduler enable|disable POSTs

Public expectation for these URLs: **not found** or **forbidden**, never `200` with CSRF tokens from the open internet.

---

## 4. Data & file denylist (host filesystem / URL mapping)

Do not expose via static file server or reverse-proxy alias:

| Path / pattern | Reason |
| --- | --- |
| `.env`, `.env.*` | Secrets |
| `credentials/**` | OAuth / Drive tokens |
| `tracking/queue_state.csv` write surfaces | Operator state |
| Raw `output/**` directory listing | Prefer catalog asset API with filename allowlist |
| Knowledge `roadmap/records.json` or draft MD not marked published | Editorial leakage |
| Internal UAT evidence dumps under `docs/product/uat/**` | Optional to publish as docs site; never as app routes |
| Full third-party books / encrypted PDFs | Copyright — reference only |

---

## 5. Behavioral denylist (features, not just paths)

| Behavior | Public posture |
| --- | --- |
| Enable factory generation | Denied (`BHAVA_FACTORY_ACTIONS_ENABLED=false`) |
| Call paid TTS/image APIs from web tier | Denied |
| WhatsApp / Telegram send | Denied (pilot off) |
| Accept public comments / open forum posts | Denied (Knowledge is curated) |
| Claim “used with permission” without documented rights | Denied (editorial) |
| Index unpublished story placeholders | `noindex` (soft deny for search) |

---

## 6. Verification commands (local / staging)

After any staging deploy (still not production cutover):

```text
# Must fail from a non-loopback client
GET https://<public-host>/studio
GET https://<public-host>/dev/audio-lab
GET https://<public-host>/api/v1/local/status
POST https://<public-host>/api/v1/local/generate-next

# Must succeed
GET https://<public-host>/
GET https://<public-host>/stories/001
GET https://<public-host>/api/v1/health
```

Record results in the release evidence pack; do not paste secrets or CSRF tokens into public docs.

---

## 7. Change control

Adding a route to the public site requires:

1. Entry in `BHAVA_PUBLIC_ROUTE_ALLOWLIST.md`  
2. Removal from this denylist (if previously listed)  
3. Explicit note in the launch/route matrix  
4. Confirmation it does not expose factory controls, drafts, or secrets
