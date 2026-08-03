# Bhāva Post-V3 Security Review

**Context:** Production Stories **001–020** on `bhava-content-001-020-v3` ([BHAVA_PRODUCTION_001_020_V3_FINAL_STATUS.md](../releases/BHAVA_PRODUCTION_001_020_V3_FINAL_STATUS.md)).  
**Posture:** Honest assessment of **tested controls** and **residual risk**. This site is **not** claimed hack-proof.

## Tested controls (evidence-backed)

| Control | Status | Notes |
| --- | --- | --- |
| **npm audit (prod)** | **0 vulnerabilities** | `npm audit --omit=dev` — requirement from launch UAT ([05_SECURITY_RUNTIME_SAFETY.md](../product/launch/cowork-final/05_SECURITY_RUNTIME_SAFETY.md)) |
| **Public route boundary** | PASS | `/studio`, `/dev`, `/api/v1/local`, `/api/v1/factory`, `/api/v1/scheduler`, `/api/v1/queue` → 404 on production spot-check |
| **Private denylist** | Documented | [BHAVA_PRIVATE_ROUTE_DENYLIST.md](../deployment/BHAVA_PRIVATE_ROUTE_DENYLIST.md) |
| **TLS / HTTPS** | Ready | Production smoke + `tls-readiness.sh`; HTTP 200 on `https://bhava.me` |
| **Staging Basic Auth** | When configured | `STAGING_BASIC_AUTH_USER` + `STAGING_BASIC_AUTH_PASSWORD` used by smoke/TLS scripts |
| **Production Basic Auth** | **None** | Public read-only site; no Basic Auth on `bhava.me` |
| **Factory mutation on public** | Blocked | `BHAVA_FACTORY_ACTIONS_ENABLED=false` on public hosts |
| **Content checksum gate** | PASS | Release workflow verifies content tag SHA |
| **Secrets in git** | Policy clean | `.env`, credentials, outputs gitignored; docs pattern-scan clean in launch review |
| **Path traversal / `.env` probe** | 404 | Launch adversarial checks |
| **Scheduler** | Disabled | No unattended paid generation from production host |

## Staging vs production

| Item | Staging | Production |
| --- | --- | --- |
| Indexing | `noindex` required | Must be indexable (no global noindex) |
| Basic Auth | Expected when env set | Not used |
| Smoke script | `smoke-test.sh … staging` | `… production` |
| Purpose | Pre-promote validation | Public catalog |

## Rollback

| Layer | Mechanism |
| --- | --- |
| Application | `.\scripts\release-bhava.ps1 -Rollback -Environment production -ConfirmRollback` |
| Pointer | `/opt/bhava/releases/production/previous` on server |
| Known good SHA | Documented per release (v3 prior main: `660831db…` in FINAL_STATUS) |
| Content | Content tag pin in `deploy/content/RELEASE_CONTENT.json` |

Rollback rehearsed on staging when `previous` pointer exists ([BHAVA_PUSH_BUTTON_RELEASE_RUNBOOK.md](../deployment/BHAVA_PUSH_BUTTON_RELEASE_RUNBOOK.md)).

**Not automatic:** TLS/ACME wait timeout (exit 3) is not an app rollback trigger.

## Residual risks (accepted / open)

| Risk | Mitigation today | Gap |
| --- | --- | --- |
| Dependency drift | CI `npm audit`, lockfile pin | DevDependency highs in full audit (eslint cluster) — not prod runtime |
| DDoS / volumetric attack | Host/provider defaults | No dedicated WAF documented in-repo |
| Account compromise (GitHub, IONOS, DNS) | Manual approval on `production` env | Out-of-band credential rotation runbook |
| Zero-day in Next/React | Upgrade path via CI | Requires active patching discipline |
| Insider publish | Protected environment + review | Social/process risk remains |
| Catalog data exposure | Read-only API | Internal fields may still appear in JSON (known v3 deferral) |

## Operator verification (lightweight)

After each production promote:

1. `curl -sS https://bhava.me/api/v1/version` — note `release_sha`, `public_story_max`.  
2. Confirm factory/local routes 404 (sample list above).  
3. Re-run `npm audit --omit=dev` on release SHA if web deps changed.  
4. Staging smoke with Basic Auth before next promote.

## Non-claims

- No “fully secure,” “unhackable,” or “zero risk” language.  
- No substitute for periodic host-level patching and backup verification.  
- Security review does not replace legal/compliance counsel.

## Related

- [BHAVA_REQUIRED_ENVIRONMENT.md](../deployment/BHAVA_REQUIRED_ENVIRONMENT.md)  
- [RELEASE_AND_ROLLBACK.md](../RELEASE_AND_ROLLBACK.md)  
- [BHAVA_PUBLIC_DEPLOYMENT_READINESS.md](../deployment/BHAVA_PUBLIC_DEPLOYMENT_READINESS.md)
