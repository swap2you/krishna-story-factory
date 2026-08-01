# Bhāva release command reference

| Command | Purpose |
| --- | --- |
| `.\scripts\release-bhava.ps1 -Status` | Fetch refs; show main/develop SHAs; probe production version |
| `.\scripts\release-bhava.ps1 -ContentReleaseTag <tag> -PublicStoryMax 20 -DryRun` | Validate clean tree + content policy; print plan |
| `.\scripts\release-bhava.ps1 -ContentReleaseTag <tag> -PublicStoryMax 20` | Dispatch staging deploy workflow |
| `.\scripts\release-bhava.ps1 -ContentReleaseTag <tag> -PublicStoryMax 20 -PromoteToProduction` | After staging PASS + approval: open develop→main PR |
| `.\scripts\release-bhava.ps1 -Rollback -Environment staging -ConfirmRollback` | Dispatch staging rollback workflow |
| `.\scripts\release-bhava.ps1 -Rollback -Environment production -ConfirmRollback` | Dispatch production rollback (explicit confirm required) |
| `.\scripts\create-next-bhava-story.ps1` | Generate exactly one next pending story (governed create-next) |
| `gh workflow run deploy-staging.yml -f content_release_tag=<tag>` | Direct staging deploy |
| `gh workflow run deploy-production.yml -f content_release_tag=<tag>` | Direct production deploy (env approval) |
| `gh workflow run rollback-staging.yml` | Staging rollback |
| `gh workflow run rollback-production.yml` | Production rollback |
| `bash deploy/ionos/scripts/tls-readiness.sh https://bhava.me` | TLS/ACME wait |
| `SKIP_TLS_READINESS=1 bash deploy/ionos/scripts/smoke-test.sh https://bhava.me <sha> production` | App smoke only |
| `bash deploy/ionos/scripts/smoke-test.sh https://staging.bhava.me <sha> staging` | Staging smoke (expects noindex) |

## Content tag defaults

| Tag | Role |
| --- | --- |
| `bhava-content-001-020-v2` | Exists (quality-completion v2) |
| `bhava-content-001-020-v3` | Staging candidate being prepared — prefer this for new staging dry-runs/deploys |

`PublicStoryMax` is **20**. Production remains on older web/content until later approval.

Example staging candidate:

```powershell
.\scripts\release-bhava.ps1 -ContentReleaseTag bhava-content-001-020-v3 -PublicStoryMax 20 -DryRun
.\scripts\release-bhava.ps1 -ContentReleaseTag bhava-content-001-020-v3 -PublicStoryMax 20
```

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
