# Release and Rollback

## Pilot lock

- Stories **001–006** locked under Story Format V2.  
- Evidence: [releases/PILOT_001_006_RELEASE_LOCK.md](releases/PILOT_001_006_RELEASE_LOCK.md), [releases/PILOT_001_006_HASHES.json](releases/PILOT_001_006_HASHES.json).  
- Senior devotee review: **pending**.  
- Planned annotated tag: **`v1.0.0-pilot-stories-001-006`**.

Generated packages and runtime queue files are **not** Git-tracked. The tag is the **code/configuration** rollback point; Drive folders + hash evidence preserve pilot media.

## Create / push tag (operators only, after main is verified)

```powershell
git fetch origin
git rev-parse HEAD
git rev-parse origin/main
# Require equality, then:
git tag -a v1.0.0-pilot-stories-001-006 -m "Krishna Story Factory pilot lock: Stories 001-006, Story Format V2"
git push origin v1.0.0-pilot-stories-001-006
```

## Roll back working tree to the tag

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

## Package / Drive rollback notes

- Local package backups (if any) live under `output/_archive/` (local only).  
- To restore one story’s local package, copy the archived eight files back into `output/<chapter>_<slug>/`.  
- Replace Drive files only under an approved change request.  
- Do not force-push `main`. Prefer a new revert PR/commit if code must be undone after merge.

## Verify after rollback

```powershell
.\scripts\test_all.ps1
.\.venv\Scripts\python.exe -m pytest tests/test_pilot_release_hash_evidence.py -q
```
