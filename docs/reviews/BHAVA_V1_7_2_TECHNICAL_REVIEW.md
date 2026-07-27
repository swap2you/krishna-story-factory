# Bhāva V1.7.2 — Technical Review

## Product SHA

`a1d277b0a55ab85b28c6e8a8a8f330a966b1b085`

Includes:

- `data/series/krishna_book_coverage.yaml` chapter-event ledger  
- Non-skipping publication gate + `tests/test_coverage_non_skipping.py`  
- Preferred `_pack_009` activity pack  
- Reviewed Vedabase sources for 008–009 + test expectation through 009  

## Publication / ops

| Gate | Result |
|------|--------|
| Local exact-eight for repaired 009 | PASS |
| Atomic public replace | `output/009_putana-krishnas-astonishing-mercy/` |
| Incorrect package | Privately archived; removed from public output |
| Drive folder | `1tz3RjfAY3HRLNng_Gbd43_nbPTTDkKVj` (8 files UPLOADED) |
| Queue 009 / 010 | `done` / `pending` |
| Stories 001–008 hashes | Unchanged vs V1.7.2 safety baseline |
| Story 010 package | Absent |
| Catalog index | 9 stories; 009 title is Pūtanā |
| Web assets | Rebuilt for 001–009 |

## Test matrix (product SHA)

Evidence: `docs/product/uat/v1.7.2/runs/20260727-152549-a1d277b/`

| Suite | Result |
|-------|--------|
| pytest `-m "not slow"` | **424 passed**, 5 deselected, 0 failed |
| Playwright (5 projects) | **415 passed**, 10 skipped, 0 failed |
| lint / typecheck / unit / build | exit 0 |

## Known limitations

- Safari/iOS WebKit autoplay → intentional Playwright skips  
- Old Drive folder for retired slug may still exist; public catalog uses new slug folder  
- Cost / TTS budget remains advisory-only  

## Verdict

**PASS** for technical release candidate readiness.
