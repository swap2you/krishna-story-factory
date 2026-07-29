# Bhāva V1.7.3 — Future Sequence Migration

## Why

Before generating Story 010, the pending Krishna Book sequence incorrectly treated:

| Old story | Old mapping |
|----------:|-------------|
| 010 | Entire Chapter 7 as Tṛṇāvarta only |
| 011 | Entire Chapter 8 as one universal-form story |
| 012+ | Chapter 9+ (Damodara onward) |

That would skip cart-breaking, the first (yawning) universal-mouth vision, Garga Muni, crawling adventures, and butter-theft complaints as full stories.

## Locked (unchanged)

- Stories **001–009** packages, hashes, and queue `done` status
- Story **009** = Pūtanā — Kṛṣṇa’s Astonishing Mercy
- No `output/010_*` created
- No provider / Drive / scheduler execution

## Corrected pending map (Chapters 7–8)

| Story | Slug | Title | Source |
|------:|------|-------|--------|
| 010 | `baby-krishna-breaks-the-cart` | Baby Kṛṣṇa Breaks the Cart | KB Ch.7 |
| 011 | `the-salvation-of-trinavarta` | The Salvation of Tṛṇāvarta | KB Ch.7 |
| 012 | `yasoda-sees-the-universe-while-krishna-yawns` | Yaśodā Sees the Universe While Kṛṣṇa Yawns | KB Ch.7 |
| 013 | `garga-muni-names-krishna-and-balarama` | Garga Muni Names Kṛṣṇa and Balarāma | KB Ch.8 |
| 014 | `krishna-and-balaramas-crawling-adventures` | Kṛṣṇa and Balarāma’s Crawling Adventures | KB Ch.8 |
| 015 | `the-gopis-complain-about-butter-theft` | The Gopīs Complain About Butter Theft | KB Ch.8 |
| 016 | `krishna-eats-dirt-and-reveals-the-universe` | Kṛṣṇa Eats Dirt and Reveals the Universe | KB Ch.8 |

## Shift of later pending rows

Former pending Damodara+ episodes (old 012–093) renumbered to **017–098** (+5). Status remains `pending` / ledger `planned` as appropriate. Series length: 93 → 98.

| Old # | Old title (abbrev.) | New # |
|------:|---------------------|------:|
| 012 | Mother Yaśodā Binds… | 017 |
| 013 | Nalakūvara / Maṇigrīva | 018 |
| … | … | … |
| 093 | Summary description… | 098 |

## Files updated

- `input/series_plan.csv`
- `input/krishna_book_master_plan.csv`
- `tracking/queue_state.csv` (pending rewrite; 001–009 done preserved)
- `data/series/krishna_book_coverage.yaml`

## Selection check

`read_next_pending()` → **010** `baby-krishna-breaks-the-cart` (not Tṛṇāvarta).
