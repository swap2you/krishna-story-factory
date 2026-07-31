# Bhāva release command reference

| Command | Purpose |
| --- | --- |
| `.\scripts\release-bhava.ps1 -Status` | Fetch refs; show main/develop SHAs; probe production version |
| `.\scripts\release-bhava.ps1 -ContentReleaseTag <tag> -DryRun` | Validate clean tree + content policy; print plan |
| `.\scripts\release-bhava.ps1 -ContentReleaseTag <tag>` | Dispatch staging deploy workflow |
| `.\scripts\release-bhava.ps1 -ContentReleaseTag <tag> -PromoteToProduction` | After staging PASS: open develop→main PR |
| `.\scripts\release-bhava.ps1 -Rollback -Environment staging -ConfirmRollback` | Dispatch staging rollback workflow |
| `.\scripts\release-bhava.ps1 -Rollback -Environment production -ConfirmRollback` | Dispatch production rollback (explicit confirm required) |
| `gh workflow run deploy-staging.yml -f content_release_tag=<tag>` | Direct staging deploy |
| `gh workflow run deploy-production.yml -f content_release_tag=<tag>` | Direct production deploy (env approval) |
| `gh workflow run rollback-staging.yml` | Staging rollback |
| `gh workflow run rollback-production.yml` | Production rollback |
| `bash deploy/ionos/scripts/tls-readiness.sh https://bhava.me` | TLS/ACME wait |
| `SKIP_TLS_READINESS=1 bash deploy/ionos/scripts/smoke-test.sh https://bhava.me <sha> production` | App smoke only |
| `bash deploy/ionos/scripts/smoke-test.sh https://staging.bhava.me <sha> staging` | Staging smoke (expects noindex) |

Default content tag for current public site: `bhava-content-001-009-v1`.
