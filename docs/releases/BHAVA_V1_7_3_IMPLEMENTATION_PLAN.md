# Bhāva V1.7.3 — Implementation Plan

## Mission

Correct the future Krishna Book sequence for Chapters 7–8 **before** Story 010 is generated. Story 009 (Pūtanā) remains locked. No paid providers, Drive, scheduler trigger, or package regeneration.

## Starting tip

Resolved dynamically at kickoff: `867182405ca376ccdde6be1b80ca5c36c2b64aca` (= `origin/feature/bhava-portal-v1`).

## Defect

Coverage ledger + queue still map:

- Chapter 7 → only Tṛṇāvarta as Story 010
- Chapter 8 → only one universal-mouth story as Story 011

That would skip cart-breaking, the first (yawning) universal-mouth manifestation, Garga Muni / name-giving, crawling adventures, and butter-theft complaints as full stories.

## Phases

| Phase | Deliverable |
|------:|-------------|
| 0 | Safety baseline + this plan |
| 1 | `docs/editorial/KRISHNA_BOOK_CHAPTERS_7_8_EVENT_BOUNDARY_REVIEW.md` |
| 2 | Expanded `data/series/krishna_book_coverage.yaml` |
| 3 | Pending queue/plan migration; `BHAVA_V1_7_3_FUTURE_SEQUENCE_MIGRATION.md` |
| 4 | Hardened non-skipping gate + regressions |
| 5 | Updated 001–009 audit + future Ch.7–10 section |
| 6 | SHA-bound safe test matrix under `docs/product/uat/v1.7.3/runs/` |
| 7 | `docs/reviews/BHAVA_V1_7_3_FINAL_COWORK_UAT_PROMPT.md` (no hard-coded obsolete tip) |

## Provisional story map (pending only)

| Story | Pastime | Source |
|------:|---------|--------|
| 010 | Baby Kṛṣṇa Breaks the Cart | KB Ch.7 / SB 10.7 |
| 011 | The Salvation of Tṛṇāvarta | KB Ch.7 / SB 10.7 |
| 012 | Yaśodā Sees the Universe While Kṛṣṇa Yawns | KB Ch.7 / SB 10.7 |
| 013 | Garga Muni Names Kṛṣṇa and Balarāma | KB Ch.8 / SB 10.8 |
| 014 | Kṛṣṇa and Balarāma’s Crawling Adventures | KB Ch.8 / SB 10.8 |
| 015 | The Gopīs Complain About Butter Theft | KB Ch.8 / SB 10.8 |
| 016 | Kṛṣṇa Eats Dirt and Reveals the Universe | KB Ch.8 / SB 10.8 |

Former pending Damodara+ stories shift forward (+5 episode numbers). All remain `pending`/`planned`. No `output/010_*`.

## Hard constraints

- Do not modify Stories 001–009 packages or regenerate 009
- Do not generate Story 010
- Do not call providers / mutate Drive / trigger scheduler
- Do not create PR / merge / touch main or tags
