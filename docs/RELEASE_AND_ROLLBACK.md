# Release and Rollback

## Current release posture

- Stories **001–020** complete/public (exact-eight). Story **021** next pending/private — not generated.  
- Content tag **`bhava-content-001-020-v2`** exists.  
- Staging candidate: quality-completion **v3** content (`bhava-content-001-020-v3` being prepared).  
- **Production** remains on older web/content until later approval — do not promote v3 without explicit approval.  
- Scheduler **Disabled**. WhatsApp/Telegram sending disabled; Drive after local PASS.  
- Stack: Node **24**, Python **3.14**.  
- Push-button ops: [deployment/BHAVA_PUSH_BUTTON_RELEASE_RUNBOOK.md](deployment/BHAVA_PUSH_BUTTON_RELEASE_RUNBOOK.md), [deployment/BHAVA_RELEASE_COMMAND_REFERENCE.md](deployment/BHAVA_RELEASE_COMMAND_REFERENCE.md).

## Pilot lock (001–006 baseline)

- Stories **001–006** locked under Story Format V2.  
- Evidence: [releases/PILOT_001_006_RELEASE_LOCK.md](releases/PILOT_001_006_RELEASE_LOCK.md), [releases/PILOT_001_006_HASHES.json](releases/PILOT_001_006_HASHES.json).  
- Senior devotee review: **pending**.  
- Annotated tag: **`v1.0.0-pilot-stories-001-006`**.

Generated packages and runtime queue files are **not** Git-tracked. Tags are **code/configuration** rollback points; Drive folders + hash/content-bundle evidence preserve media.

## Staging / production content release

```powershell
.\scripts\release-bhava.ps1 -Status
.\scripts\release-bhava.ps1 -ContentReleaseTag bhava-content-001-020-v3 -PublicStoryMax 20 -DryRun
.\scripts\release-bhava.ps1 -ContentReleaseTag bhava-content-001-020-v3 -PublicStoryMax 20
# After staging PASS and explicit approval only:
.\scripts\release-bhava.ps1 -ContentReleaseTag bhava-content-001-020-v3 -PublicStoryMax 20 -PromoteToProduction
```

`PublicStoryMax` is **20** (blocks Story 021+). Do not force-push; do not enable scheduler during release.

## Roll back working tree to the pilot tag

```powershell
git fetch --tags
git switch --detach v1.0.0-pilot-stories-001-006
```

You are in detached HEAD on the locked code baseline. Do not regenerate 001–006 from this point without approval.

## Return to main

```powershell
git switch main
git pull --ff-only
```

## Package / Drive / deploy rollback notes

- Local package backups (if any) live under `output/_archive/` (local only).  
- To restore one story’s local package, copy the archived eight files back into `output/<chapter>_<slug>/`.  
- Replace Drive files only under an approved change request.  
- App/content rollback: `.\scripts\release-bhava.ps1 -Rollback -Environment staging|production -ConfirmRollback`.  
- Do not force-push `main`. Prefer a new revert PR/commit if code must be undone after merge.

## Verify after rollback

```powershell
.\scripts\test_all.ps1
.\.venv\Scripts\python.exe -m pytest tests/test_pilot_release_hash_evidence.py -q
```
