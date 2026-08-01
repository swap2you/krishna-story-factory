# Push-button Bhāva release runbook

## Operator entry point

```powershell
cd C:\Development\Workspace\DevotionalRepo\krishna-story-factory
.\scripts\release-bhava.ps1 -Status
.\scripts\release-bhava.ps1 -ContentReleaseTag bhava-content-001-020-v3 -PublicStoryMax 20 -DryRun
.\scripts\release-bhava.ps1 -ContentReleaseTag bhava-content-001-020-v3 -PublicStoryMax 20
```

Bash companion (status/dry-run only):

```bash
./scripts/release-bhava.sh status
./scripts/release-bhava.sh dry-run
```

## Content tags

| Tag | Role |
| --- | --- |
| `bhava-content-001-020-v2` | Exists (published quality-completion v2) |
| `bhava-content-001-020-v3` | Staging candidate being prepared (quality-completion / v3) |

Production remains on older web/content until later approval. Do not `-PromoteToProduction` for v3 without explicit approval.

## Gates

1. Clean working tree  
2. Content tag + checksum (`deploy/content/RELEASE_CONTENT.json`)  
3. `PublicStoryMax` must be **20** for Stories 001–020 (blocks Story 021+)  
4. CI green on develop  
5. Staging deploy + TLS readiness + environment-aware smoke  
6. Staging rollback exercise (when a `previous` pointer exists)  
7. Explicit `-PromoteToProduction` before develop→main PR  
8. Protected `production` environment approval  
9. Production TLS readiness **before** app smoke  
10. Rollback only on **application** smoke failure (not ACME wait timeout)  
11. Confirm `/opt/bhava/releases/production/previous` after second+ deploy  

## Forbidden

- force-push  
- bypass CI  
- enable scheduler  
- paid generation during release gates  
- print secrets  
- duplicate concurrent production deploys (`concurrency: bhava-production`)  
- one-click production rollback without `-ConfirmRollback`

## Smoke indexing policy

- Staging: must send `X-Robots-Tag: noindex`  
- Production: must **not** be globally noindex  

## TLS readiness

`deploy/ionos/scripts/tls-readiness.sh` waits with backoff for DNS, TCP 443, HTTPS, and certificate hostname match. Exit code **3** = ACME/TLS provisioning problem — do not treat as automatic application rollback.

## Operator command library (Stories release)

| Alias | Mapped command |
| --- | --- |
| BHAVA STATUS | `.\scripts\release-bhava.ps1 -Status` |
| BHAVA RELEASE `<CONTENT_TAG>` | `.\scripts\release-bhava.ps1 -ContentReleaseTag <CONTENT_TAG> -PublicStoryMax 20` |
| BHAVA RELEASE V3 STAGING | `.\scripts\release-bhava.ps1 -ContentReleaseTag bhava-content-001-020-v3 -PublicStoryMax 20` |
| BHAVA UAT HANDOFF | Update `MyPilotDropbox/bhava-production-ops/reports/BHAVA_PRODUCTION_COWORK_UAT_HANDOFF.md` after smoke PASS |
| BHAVA ROLLBACK STAGING | `.\scripts\release-bhava.ps1 -Rollback -Environment staging -ConfirmRollback` |
| BHAVA ROLLBACK PRODUCTION | `.\scripts\release-bhava.ps1 -Rollback -Environment production -ConfirmRollback` |
| BHAVA CREATE NEXT | `.\scripts\create-next-bhava-story.ps1` |
