# Testing and Release Gates

## Full suite

```powershell
cd C:\Development\Workspace\DevotionalRepo\krishna-story-factory
.\scripts\test_all.ps1
```

Runs `.venv` Python `pytest -q`. Prefer this over a global pytest.

Optional structural dry run:

```powershell
.\scripts\run_test.ps1 --force
```

Test mode must not call paid APIs and is never publishable.

## Publishable gate

`manifest.publishable` is true only when all hold:

- `mode` is prod  
- quality status `PASS` and empty quality errors  
- audio `generation_verified` with a real provider (not preserved/unknown)  
- `narration_source_sha` and audio SHA present  
- not `AUDIO_STALE`  
- exact eight-file package on disk  

Otherwise `publishable` must be false. Do not hand-edit manifests to force true.

## Hash / release evidence (Stories 001–006)

Committed evidence: `docs/releases/PILOT_001_006_HASHES.json`  
Lock narrative: `docs/releases/PILOT_001_006_RELEASE_LOCK.md`

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_pilot_release_hash_evidence.py tests/test_release_artifacts_001_006.py tests/test_post_pr7_release_blockers.py -q
```

- Hash-evidence tests **always run** (even without local `output/`).  
- Local artifact regressions **skip gracefully** if a package folder is missing.  
- Neither suite may call Drive or paid APIs.

## Other gates operators care about

- Exact eight filenames (`krishna_story_factory/outputs.py`).  
- Story Format V2 section order.  
- Source guards / paid-call protection in unit tests.  
- MWF scheduler static checks: `.\scripts\test_mwf_story_task.ps1 -StaticOnly` (or full after install).

Do not claim release-ready unless `test_all` passes and 001–006 evidence tests are green.
