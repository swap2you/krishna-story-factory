# Bhāva V1.7.2 — Final CoWork UAT Prompt

## Role

Independent release reviewer for Bhāva Portal V1.7.2 on `feature/bhava-portal-v1`.

## Do not

- Modify Stories 001–009 or generate Story 010  
- Mutate the queue, call paid providers, or modify Drive  
- Create a PR or merge  
- Treat summary-only test claims as sufficient without raw logs  

## Must verify

### Git hygiene

1. Actual branch tip vs claimed product SHA `a1d277b0a55ab85b28c6e8a8a8f330a966b1b085` and the later evidence/docs commit(s).  
2. Docs-only delta after product SHA (`git diff --name-only a1d277b0a55ab85b28c6e8a8a8f330a966b1b085..HEAD`).  
3. Local equals `origin/feature/bhava-portal-v1`.  
4. `main` / tags unchanged.

### Defect closure

1. Retired incorrect Story 009 (`009_baby-krishna-protects-gokula` / universe-in-mouth framing) is not public.  
2. Public Story 009 is `009_putana-krishnas-astonishing-mercy` with title **Pūtanā — Kṛṣṇa’s Astonishing Mercy**.  
3. Exact-eight files present; `publishable=true`; quality PASS.  
4. Stories 001–008 hashes unchanged vs `docs/releases/BHAVA_V1_7_2_SAFETY_BASELINE.json`.  
5. Story 010 pending/hidden (no `output/010_*`).

### Scriptural fidelity (Story 009)

Compare against *Krishna Book* Ch.6 and SB 10.6. Require full Pūtanā coverage in story **and** narration. FAIL if universe-in-mouth / Tṛṇāvarta appear as Chapter 6 events, or if Pūtanā is only “already defeated.”

### Non-skipping guard

1. Ledger `data/series/krishna_book_coverage.yaml` maps Ch.6→009 and Ch.7→010.  
2. Recap/preview cannot count as major-event coverage.  
3. `tests/test_coverage_non_skipping.py` rejects the old defective 009 patterns.

### SHA-bound evidence

Folder: `docs/product/uat/v1.7.2/runs/20260727-152549-a1d277b/`

Require:

- `metadata.json` product SHA equals tested SHA  
- Complete raw `pytest-full.txt` supporting **424 passed**  
- Complete raw `playwright-full.txt` supporting **415 passed / 10 skipped / 0 failed**  
- Summaries consistent with raw logs  
- `skipped-tests.json` / `deselected-tests.json` present and justified  

### Stories / portal

1. Catalog lists 001–009; Story 008 links to corrected 009; Printables includes 009.  
2. Live instance: `cursor-v172` — web `http://127.0.0.1:3003`, API `http://127.0.0.1:8000`.  
3. All Story 009 tabs; genuine audio advancement in Chromium; Safari/iOS skip limitation acknowledged.  
4. No queue / provider / Drive mutation during UAT.

### Exhaustive visual UAT

Follow `MyPilotDropbox/bhava-v1.7.2-putana-repair/BHAVA_V1_7_2_COWORK_UAT.md` for full-site discovery, screenshots, axe, and report packaging under `docs/product/uat/v1.7.2/cowork-final/`.

## Verdict format

`READY FOR RELEASE` / `BLOCKED` with evidence citations.
