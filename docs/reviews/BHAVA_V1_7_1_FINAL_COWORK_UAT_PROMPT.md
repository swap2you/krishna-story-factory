# Bhāva V1.7.1 — Final CoWork UAT Prompt

## Role

Independent release reviewer for Bhāva Portal V1.7.1 on `feature/bhava-portal-v1`.

## Do not

- Modify Stories 001–009 or generate Story 010
- Mutate the queue, call paid providers, or modify Drive
- Create a PR or merge
- Treat summary-only test claims as sufficient without raw logs

## Must verify

### Git hygiene

1. Actual branch tip vs claimed product SHA `86d43f1d64e2ac738e68b5d1c7f0182b8b5c41d5` and evidence SHA `f152490f1a1d78638d2bba5ebcd2ce470c6d50e4` (plus any later docs-only SHA-fill commits).
2. Docs-only delta after product SHA (`git diff --name-only 86d43f1d64e2ac738e68b5d1c7f0182b8b5c41d5..HEAD`).
3. `tracking/scheduler_health.json` is **untracked** and listed in `.gitignore`.
4. Local equals `origin/feature/bhava-portal-v1`.
5. `main` / tags unchanged.

### Scheduler reproducibility

1. `scripts/install_mwf_story_task.ps1` encodes PT4H, `StartWhenAvailable=true`, `StopOnIdleEnd=false`, IgnoreNew, MWF 10:00/12:00, WakeToRun=false.
2. `scripts/test_mwf_story_task.ps1` and `tests/test_scheduler_scripts.py` require `.NET System.Diagnostics.Process` and **reject** production `Start-Process` / `NoNewWindow`.
3. Validators inspect the **registered** task, not only source greps.
4. Final enabled XML: `docs/operations/SCHEDULER_V1_7_1_CONFIGURATION_FINAL_ENABLED.xml` — PT4H, StartWhenAvailable true, StopOnIdleEnd false, no `<Enabled>false</Enabled>`.
5. Safe validation docs: `SCHEDULER_V1_7_1_SAFE_VALIDATION.md`, `SCHEDULER_V1_7_1_REGISTERED_NOOP_PROOF.md` — ValidateScheduler / SimulateProduction exit 0; real no-op `LastTaskResult=0`.

### SHA-bound evidence

Folder: `docs/product/uat/v1.7.1/runs/20260727-130534-86d43f1/`

Require:

- `metadata.json` product SHA equals tested SHA
- Complete raw `pytest-full.txt` supporting **417 passed**
- Complete raw `playwright-full.txt` supporting **415 passed / 10 skipped / 0 failed**
- Summaries consistent with raw logs
- `skipped-tests.json` / `deselected-tests.json` present and justified

### Stories / portal

1. `output/009_baby-krishna-protects-gokula/` exact-eight; publishable true; quality PASS.
2. Stories 001–008 hashes unchanged vs safety baseline.
3. Story 010 pending/hidden (no public folder).
4. Catalog lists 001–009; Story 008 links to 009; Printables includes 009.
5. Audio/tabs on Story 009 work in Chromium; Safari/iOS skip limitation acknowledged.
6. No queue / provider / Drive mutation during UAT.

## Cost guard

Confirm the TTS budget guard is **advisory-only**, not a hard cap.

## Verdict format

`READY FOR RELEASE` / `BLOCKED` with evidence citations.
