# Bhāva Required Environment Variables

**Never commit secrets.** Use `.env` locally (gitignored). The tracked template is `.env.example` (factory) plus the Bhāva-specific variables below. Do not paste API keys, OAuth tokens, or cloud credentials into documentation, tickets, or commits.

---

## 1. Variable classes

| Class | Where used | Public `bhava.me` | Local operator |
| --- | --- | --- | --- |
| A. Bhāva portal runtime | `apps/api`, `apps/web` | Required (safe values) | Required |
| B. Factory generation / TTS / Drive | Krishna Story Factory CLI | **Must be absent or disabled** on public hosts | Optional / test-gated |
| C. Messaging (WhatsApp/Telegram/etc.) | Factory senders | **Disabled** | Disabled for pilot |
| D. CI / UAT only | Playwright, evidence scripts | N/A | Optional |

---

## 2. Class A — Bhāva portal (web + API)

### API (`apps/api/bhava_api/config.py`)

| Variable | Default | Local | Public | Notes |
| --- | --- | --- | --- | --- |
| `BHAVA_REPOSITORY_ROOT` | repo root (inferred) | Optional | Set explicitly if layout differs | Absolute path to monorepo root |
| `BHAVA_OUTPUT_ROOT` | `<root>/output` | Usual | Read-only package root / mount | Catalog source packages |
| `BHAVA_CATALOG_DB` | `data/catalog/bhava.sqlite` | Usual | Prefer managed Postgres later; path/DSN per adapter | Rebuildable index |
| `BHAVA_CATALOG_REFRESH_SEC` | `20` (clamped 15–30) | OK | Tune for load | Background refresh interval |
| `BHAVA_FACTORY_ACTIONS_ENABLED` | `false` | Keep false unless intentionally generating | **Must be `false`** | Gates generate/rebuild actions |
| `BHAVA_ENFORCE_LOOPBACK` | `true` | **Keep true** | **Keep true** if local router exists; better: omit router | `/api/v1/local/*` host check |
| `BHAVA_AUTO_WEB_ASSETS` | `false` | Optional operator convenience | Prefer `false` | Auto-build `data/web-assets` on index |
| `BHAVA_WEB_URL` | unset → localhost CORS set | e.g. `http://127.0.0.1:3000` | `https://bhava.me` | Drives CORS if origins unset |
| `BHAVA_WEB_ORIGINS` | unset → ports 3000–3003 localhost | Comma list if multiple | Exact public origins only | Overrides inferred CORS |

### Web (`apps/web` — Next)

| Variable | Default | Local | Public | Notes |
| --- | --- | --- | --- | --- |
| `BHAVA_API_ORIGIN` | `http://127.0.0.1:8000` | Usual | Public API origin or internal upstream | Used by `next.config.ts` rewrites |
| `BHAVA_API_URL` | `http://127.0.0.1:8000/api/v1` | Alternate | Same | If set, origin derived by stripping `/api/v1` |
| `BHAVA_WEB_URL` | `http://127.0.0.1:3000` | Playwright + helpers | Public site URL for e2e against staging | Not a secret |

**Public rule:** web may talk only to the read-only catalog API. It must not receive factory API keys.

---

## 3. Class B — Factory (local / CI test only)

Documented in `.env.example`. On any **public** host these must not enable paid or mutating providers:

| Variable group | Public posture |
| --- | --- |
| `OPENAI_*`, `ELEVENLABS_*` | Unset / disabled (`*_ENABLED=false`) |
| `GOOGLE_DRIVE_*` | `GOOGLE_DRIVE_UPLOAD_ENABLED=false`; no token files on public disk |
| `PACKAGE_PUBLISH_MODE` | Not used by public web |
| `ALLOW_PLACEHOLDER_AUDIO` | `false` |
| `AUDIO_REQUIRED` / provider mode | Irrelevant to public read path |

**Test mode must not call paid APIs** (project rule). Prefer `scripts/run_test.ps1` patterns locally.

---

## 4. Class C — Messaging (pilot off)

| Variable group | Required value |
| --- | --- |
| `WHATSAPP_SEND_ENABLED` | `false` |
| `TELEGRAM_SEND_ENABLED` | `false` |
| Cloud tokens / phone IDs | Unset on public; local only if explicitly testing |

---

## 5. Class D — UAT / Playwright (optional)

| Variable | Purpose |
| --- | --- |
| `BHAVA_WEB_URL` | Target web base for e2e |
| `BHAVA_API_URL` | Target API base for e2e helpers |
| `BHAVA_UAT_BROWSER_RESULTS` | JSON reporter output path |
| `CI` | Enables stricter Playwright retries/forbidOnly |

Never store UAT credentials in the repo.

---

## 6. Local minimum to run the portal

```text
# API process environment (illustrative — no secrets)
BHAVA_ENFORCE_LOOPBACK=true
BHAVA_FACTORY_ACTIONS_ENABLED=false
BHAVA_AUTO_WEB_ASSETS=false
BHAVA_WEB_URL=http://127.0.0.1:3000

# Web process environment
BHAVA_API_ORIGIN=http://127.0.0.1:8000
```

Then start API on `127.0.0.1:8000` and Next on `:3000` (or instance runner ports).

---

## 7. Public minimum (future — still do not deploy from this doc)

```text
# Public API
BHAVA_FACTORY_ACTIONS_ENABLED=false
BHAVA_ENFORCE_LOOPBACK=true
BHAVA_WEB_ORIGINS=https://bhava.me,https://www.bhava.me
BHAVA_CATALOG_DB=<managed>
BHAVA_OUTPUT_ROOT=<read-only package store>

# Public web
BHAVA_API_ORIGIN=https://api.bhava.me
```

Omit all Class B/C secrets from the public secret store. If a secret is not required for read-only serving, do not set it.

---

## 8. Secret handling checklist

- [ ] `.env` is gitignored and never staged
- [ ] `credentials/` and Drive token files stay local
- [ ] CI secrets use the host’s secret manager, not committed files
- [ ] Logs redact tokens (factory local routes already emphasize redaction)
- [ ] Public error pages never echo environment values
- [ ] Rotated keys invalidate old `.env` copies on disk

If a secret is accidentally committed: rotate immediately, purge from history with operator approval, and treat the key as burned.
