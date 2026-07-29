# Story 009 Content Defect (V1.7.2)

## Classification

**Canonical mismatch / chapter leakage** — not a missing package.

## Claimed identity

| Field | Incorrect package |
|-------|-------------------|
| Folder | `output/009_baby-krishna-protects-gokula/` |
| Title | Baby Krishna Protects Gokula |
| `source_reference` | Krishna Book Chapter 6 |
| `scripture_reference` | Complete Krishna Book Chapter 6 |
| `publishable` | was `true` (unpublished for repair) |

## Actual narrative

- Treats **Pūtanā as already defeated** (“after Putana's defeat”) without narrating Chapter 6.
- Centers **universe shining in baby Kṛṣṇa’s mouth** (Krishna Book Chapter 8 / SB 10.8 territory).
- Next preview jumps to **The Salvation of Trinavarta** (Chapter 7) while skipping the real Chapter 6 pastime.

## Required identity (repair target)

| Field | Value |
|-------|-------|
| Number | `009` |
| Title | Pūtanā — Kṛṣṇa’s Astonishing Mercy |
| Slug | `putana-krishnas-astonishing-mercy` |
| Primary source | Krishna Book Chapter 6, “Pūtanā Killed” |
| Supporting | Śrīmad-Bhāgavatam 10.6 |
| Story 010 | Tṛṇāvarta remains pending/hidden |

## Safety actions taken (Phase 0)

1. Hashes frozen in `docs/releases/BHAVA_V1_7_2_SAFETY_BASELINE.json`.
2. Incorrect package privately archived under `work/stories/009/v172-incorrect-archive-*` (gitignored).
3. `manifest.publishable` set to `false` so the catalog gate removes public 009 until the corrected package is published.
4. Queue **not** advanced; 009 stays `done`, 010 stays `pending`.
