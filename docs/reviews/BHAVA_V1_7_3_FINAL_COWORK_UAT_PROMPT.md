# Bhāva V1.7.3 — Final CoWork UAT Prompt

## Role

Independent release reviewer for Bhāva Portal V1.7.3 on `feature/bhava-portal-v1`.

## Do not

- Modify Stories 001–009 or generate Story 010
- Mutate the queue, call paid providers, or modify Drive
- Create a PR or merge
- Treat summary-only test claims as sufficient without raw logs
- Hard-code an assumed final tip — resolve git SHAs live

## Resolve git state first

```powershell
git switch feature/bhava-portal-v1
git fetch origin
git pull --ff-only origin feature/bhava-portal-v1
git rev-parse HEAD
git rev-parse origin/feature/bhava-portal-v1
git status --short
```

Require local == origin. Compare against the product SHA recorded in the evidence `metadata.json` (expected product SHA at matrix time: `aeb5104b8780b5a7a267db609060bfd870228a62`). Docs-only commits after that SHA are allowed.

## Must verify

### Sequence correction

1. Story 009 remains full Pūtanā (`009_putana-krishnas-astonishing-mercy`); hashes match `docs/releases/BHAVA_V1_7_3_SAFETY_BASELINE.json`.
2. Stories 001–008 unchanged vs the same baseline.
3. No `output/010_*`.
4. Next pending plan is **Baby Kṛṣṇa Breaks the Cart** (`baby-krishna-breaks-the-cart`), not Tṛṇāvarta.
5. Chapter 7 ledger includes cart-breaking, Tṛṇāvarta, and first universal-mouth (yawn) as separate majors.
6. Chapter 8 ledger includes Garga Muni, crawling, butter complaints, and dirt-eating / second universal form as separate majors.
7. The two universal-form manifestations remain separately mapped (012 vs 016).
8. Non-skipping tests reject incomplete ledgers (`tests/test_coverage_non_skipping.py`).

### SHA-bound evidence

Folder under `docs/product/uat/v1.7.3/runs/` whose `metadata.json` product SHA equals the tested product commit.

Require complete raw:

- `pytest-full.txt`
- `playwright-full.txt`
- lint / typecheck / unit / build logs
- `safety-hashes.json` showing 001–009 unchanged and 010 absent

### Portal / website

Follow exhaustive link/control/screenshot expectations from the V1.7.2 CoWork UAT package style:

- Discover routes; visit public pages; test controls
- Screenshots at 390×844, 768×1024, 1440×900, 1920×1080 for primary families including Story 009
- Confirm Story 010 is not published
- No queue / provider / Drive mutation during UAT

## Verdict format

`READY FOR RELEASE` / `BLOCKED` with evidence citations.
