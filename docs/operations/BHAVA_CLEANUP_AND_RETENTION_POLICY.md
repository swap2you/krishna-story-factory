# Bhāva cleanup and retention policy

## Classification labels

| Label | Meaning |
| --- | --- |
| KEEP_ACTIVE | Needed for current operations |
| KEEP_RECOVERY | Needed to recover from incident |
| KEEP_AUDIT | Evidence for audits / CoWork |
| ARCHIVE | Move under dated archive; retain ≥ 1 year |
| DELETE_SAFE | Confirmed disposable |
| SECRET_ACTIVE | Live secret — never commit; rotate on schedule |
| SECRET_ROTATE | Still present but should be rotated |
| SECRET_EXPIRED | Superseded secret material — destroy after rotation confirmation |

## Active layout

```
MyPilotDropbox/bhava-production-ops/
  .secrets/           # SECRET_ACTIVE (gitignored)
  evidence/current-release/
  recovery/current/
  reports/current/
  archive/2026-07-initial-launch/
  BHAVA_OPS_RETENTION_MANIFEST.md
  README.md
```

## Never delete without retention decision

- Active r4 deploy key paths / known-hosts references  
- `operator.env` / `runtime.env`  
- Final production & staging reports  
- CoWork UAT handoff  
- DNS cutover + TLS recovery evidence  
- Exact release SHAs  

## Repository hygiene

- Delete only fully merged local branches after verifying commits are reachable  
- Remove obsolete worktrees after evidence preserved  
- Do not delete `backup/*` branches until commits are tagged or merged  
- Keep `main`, `develop`, `feature/story-010` until Story 010 release completes  
