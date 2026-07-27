# Bhāva Stories 001–009 — Canonical Coverage Audit

**Releases:** V1.7.2 (Pūtanā repair) + V1.7.3 (Ch.7–8 future sequence)  
**Ledger:** `data/series/krishna_book_coverage.yaml`  
**Constraint:** Stories 001–009 packages were not modified in V1.7.3. Story 010 is **not generated**.

## Method

- Compared each public package’s manifest source fields to the coverage ledger.
- Verified Stories 001–009 SHA-256 hashes against `docs/releases/BHAVA_V1_7_3_SAFETY_BASELINE.json`.
- For Story 009, confirmed full Pūtanā coverage remains (no universe-in-mouth as Ch.6 event).
- Added future-sequence audit for Chapters 7–10 (planning only).

## Summary verdict (published packages)

| Story | Source chapter | Coverage vs ledger | Later-chapter leak | Verdict |
|------:|----------------|--------------------|--------------------|---------|
| 001 | KB Ch.1 | Major event `kb1-bhumi-brahma` | None observed | PASS (unchanged) |
| 002 | KB Ch.1 | Major event `kb1-wedding-voice` | None observed | PASS (unchanged) |
| 003 | KB Ch.1 | Major event `kb1-kirtiman` | None observed | PASS (unchanged) |
| 004 | KB Ch.1 | Major event `kb1-narada-imprisonment` | None observed | PASS (unchanged) |
| 005 | KB Ch.2 | Major event `kb2-demigod-prayers` | None observed | PASS (unchanged) |
| 006 | KB Ch.3 | Major event `kb3-birth` | None observed | PASS (unchanged) |
| 007 | KB Ch.4 | Major event `kb4-yogamaya-durga` | None observed | PASS (unchanged) |
| 008 | KB Ch.5 | Major event `kb5-nanda-vasudeva` | None observed | PASS (unchanged) |
| 009 | KB Ch.6 / SB 10.6 | Full Pūtanā event set `kb6-*` | None in main body | PASS (locked) |

**Story 010 package:** absent (`output/010_*` not present) — correct for V1.7.3.

## Future sequence (Chapters 7–10) — V1.7.3

| Story | Planned pastime | Source | Lifecycle |
|------:|-----------------|--------|-----------|
| 010 | Baby Kṛṣṇa Breaks the Cart | KB Ch.7 | pending (next) |
| 011 | The Salvation of Tṛṇāvarta | KB Ch.7 | pending |
| 012 | Yaśodā Sees the Universe While Kṛṣṇa Yawns (1st mouth vision) | KB Ch.7 | pending |
| 013 | Garga Muni Names Kṛṣṇa and Balarāma | KB Ch.8 | pending |
| 014 | Kṛṣṇa and Balarāma’s Crawling Adventures | KB Ch.8 | pending |
| 015 | The Gopīs Complain About Butter Theft | KB Ch.8 | pending |
| 016 | Kṛṣṇa Eats Dirt and Reveals the Universe (2nd vision) | KB Ch.8 | pending |
| 017 | Mother Yaśodā Binds Lord Kṛṣṇa | KB Ch.9 | planned |
| 018 | Nalakūvara and Maṇigrīva | KB Ch.10 | planned |

Confirmations:

- Story 010 is **cart-breaking**, not Tṛṇāvarta
- Tṛṇāvarta is mapped (011), not skipped
- Both universal-form manifestations mapped separately (012 vs 016)
- Chapter 8 majors (Garga, crawling, butter, dirt) each mapped
- Story 010 has **not** been generated

Boundary review: `docs/editorial/KRISHNA_BOOK_CHAPTERS_7_8_EVENT_BOUNDARY_REVIEW.md`  
Migration record: `docs/editorial/BHAVA_V1_7_3_FUTURE_SEQUENCE_MIGRATION.md`

## Per-story notes (001–009)

### 001–008
Hash-locked against the V1.7.3 safety baseline; not modified. Ledger mappings unchanged from prior published coverage.

### 009 — Pūtanā — Kṛṣṇa’s Astonishing Mercy (locked)
- **Folder:** `009_putana-krishnas-astonishing-mercy`
- **Sources:** Krishna Book Chapter 6; Śrīmad-Bhāgavatam 10.6
- **Verdict:** PASS — unchanged in V1.7.3

## Non-skipping guard

Publication and ledger integrity block incomplete Chapter 7–8 maps, recap/preview-only coverage, and queue jumps over uncovered majors. Regressions: `tests/test_coverage_non_skipping.py`.
