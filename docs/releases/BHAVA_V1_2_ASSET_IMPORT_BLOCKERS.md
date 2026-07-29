# Bhāva V1.2 Asset Import Blockers

**Date:** 2026-07-23  
**Status:** 8 of 122 assets not imported

## Missing Assets

All 8 missing assets are **Phase 5 Bhagavatam canto covers** (cantos 1–7 and 10). These are the "recreated" versions referenced by the manifest as coming from package `bhava-brand-assets-v1-phase5-recreated-complete.zip`.

| Manifest Filename | Canto | Phase/Batch |
|-------------------|-------|-------------|
| `BHAVA_P5B1_01_CANTO_1_RECREATED_1600x2000.png` | Canto 1 | Phase 5, Batch 1 |
| `BHAVA_P5B1_02_CANTO_4_RECREATED_1600x2000.png` | Canto 4 | Phase 5, Batch 1 |
| `BHAVA_P5B1_03_CANTO_10_RECREATED_1600x2000.png` | Canto 10 | Phase 5, Batch 1 |
| `BHAVA_P5B2_04_CANTO_2_RECREATED_1600x2000.png` | Canto 2 | Phase 5, Batch 2 |
| `BHAVA_P5B2_05_CANTO_3_RECREATED_1600x2000.png` | Canto 3 | Phase 5, Batch 2 |
| `BHAVA_P5B2_06_CANTO_5_RECREATED_1600x2000.png` | Canto 5 | Phase 5, Batch 2 |
| `BHAVA_P5B2_07_CANTO_6_RECREATED_1600x2000.png` | Canto 6 | Phase 5, Batch 2 |
| `BHAVA_P5B2_08_CANTO_7_RECREATED_1600x2000.png` | Canto 7 | Phase 5, Batch 2 |

## Root Cause

The source tree contains raw ChatGPT-generated images for these cantos under `bhava-brand-assets-v1-phase5-batch1/` and `batch2/`, but:

1. The files have their original generation names (e.g., `ChatGPT Image Jul 23, 2026, 01_58_17 PM (1).png`) — they were never renamed to canonical names.
2. The SHA-256 checksums do not match the manifest. The manifest references "RECREATED" versions (4+ MB each) from `bhava-brand-assets-v1-phase5-recreated-complete.zip`, while the local files are smaller originals (2.4–2.7 MB each).
3. The `bhava-brand-assets-v1-phase5-recreated-complete.zip` package is not extracted in the local source tree.

**Cantos 8, 9, 11, 12 (Batch 3) were imported successfully** — these files were properly named and their checksums match.

## Resolution Options

1. **Extract the recreated package:** Locate and extract `bhava-brand-assets-v1-phase5-recreated-complete.zip` into the source tree, then re-run `import_bhava_brand_assets.py`.
2. **Regenerate:** Create new recreated versions at 1600x2000 matching the manifest specifications.
3. **Use originals:** If the raw ChatGPT images are acceptable, rename them to canonical names and update the manifest checksums.

## Impact

- The 4 successfully imported cantos (8, 9, 11, 12) are available at `collections/collection-canto-{08,09,11,12}.webp`.
- Portal pages referencing cantos 1–7 and 10 will need fallback handling until these assets are resolved.
- All other 106 non-canto assets are fully imported and validated.

## Re-Import Instructions

After resolving the source files:

```powershell
.\.venv\Scripts\python.exe scripts\import_bhava_brand_assets.py
.\.venv\Scripts\python.exe scripts\optimize_bhava_brand_assets.py
.\.venv\Scripts\python.exe scripts\validate_bhava_brand_assets.py
```

The pipeline is idempotent — it will skip already-imported assets with matching checksums and only process the newly available cantos.
