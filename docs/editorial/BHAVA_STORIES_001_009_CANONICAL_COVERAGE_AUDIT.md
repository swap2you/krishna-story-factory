# Bhāva Stories 001–009 — Canonical Coverage Audit (V1.7.2)

**Release:** V1.7.2 Pūtanā repair  
**Product SHA (gates + activity pack + reviewed-sources test):** `a1d277b0a55ab85b28c6e8a8a8f330a966b1b085`  
**Ledger:** `data/series/krishna_book_coverage.yaml`  
**Constraint:** Stories 001–008 were not modified. Story 010 remains pending/hidden.

## Method

- Compared each public package’s manifest source fields to the coverage ledger.
- Verified Stories 001–008 SHA-256 hashes against `docs/releases/BHAVA_V1_7_2_SAFETY_BASELINE.json` (all match).
- For Story 009, checked main-story body (excluding Next Story Preview) for prohibited later-chapter leakage and required Pūtanā markers.
- Did not rewrite Stories 001–008 even if future editorial depth improvements are desirable.

## Summary verdict

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
| 009 | KB Ch.6 / SB 10.6 | Full Pūtanā event set `kb6-*` | None in main body (Tṛṇāvarta only in Next Preview) | PASS (repaired) |

**Blockers found for V1.7.2 scope:** none.  
**Story 010:** Tṛṇāvarta (KB Ch.7) remains `pending` with no public `output/010_*` package — correct.

## Per-story notes

### 001 — The Earth Prays for Krishna to Come
- **Folder:** `001_the-earth-prays-for-krishna`
- **Covered units:** Mother Earth / Brahmā / Ocean of Milk opening (`kb1-bhumi-brahma`)
- **Omissions:** Remaining Ch.1 majors correctly deferred to 002–004
- **Verdict:** PASS — hash-locked; not modified

### 002 — The Wedding and the Heavenly Voice
- **Covered units:** Wedding + heavenly voice (`kb1-wedding-voice`)
- **Verdict:** PASS — hash-locked; not modified

### 003 — Vasudeva Keeps His Word
- **Covered units:** First son / word kept (`kb1-kirtiman`)
- **Verdict:** PASS — hash-locked; not modified

### 004 — Narada’s Warning and Kamsa’s Decision
- **Covered units:** Nārada warning / imprisonment (`kb1-narada-imprisonment`)
- **Verdict:** PASS — hash-locked; not modified

### 005 — Prayers by the Demigods for Lord Krishna in the Womb
- **Covered units:** Demigod prayers (`kb2-demigod-prayers`)
- **Verdict:** PASS — hash-locked; not modified

### 006 — The Birth of Lord Krishna
- **Covered units:** Birth appearance (`kb3-birth`)
- **Verdict:** PASS — hash-locked; not modified

### 007 — Kamsa Begins His Persecutions
- **Covered units:** Yoga-māyā / Durgā / persecution (`kb4-yogamaya-durga`)
- **Verdict:** PASS — hash-locked; not modified

### 008 — The Meeting of Nanda and Vasudeva
- **Covered units:** Mathurā meeting (`kb5-nanda-vasudeva`)
- **Next link:** Portal should surface repaired Story 009 (Pūtanā), not the retired wrong package
- **Verdict:** PASS — hash-locked; not modified

### 009 — Pūtanā — Kṛṣṇa’s Astonishing Mercy (repaired)
- **Folder:** `009_putana-krishnas-astonishing-mercy` (replaces retired `009_baby-krishna-protects-gokula`)
- **Sources:** Krishna Book Chapter 6 “Pūtanā Killed”; Śrīmad-Bhāgavatam 10.6
- **Covered units (main story + narration):** Nanda’s shelter; Kaṁsa sends Pūtanā; beautiful form; lap / poison breast; life air drawn; gigantic fall; gopī protection; fragrant pyre; motherly destination; hearing brings favor of Govinda
- **Prohibited content check:** No universe-in-mouth as Ch.6 event; no Tṛṇāvarta/whirlwind in main body; Pūtanā is the present pastime (not “already defeated”)
- **Preview:** May announce Tṛṇāvarta only after the full Pūtanā narration
- **Artifacts:** Exact-eight rebuilt and publishable=`true`, quality=`PASS`
- **Verdict:** PASS (V1.7.2 repair)

## Defect closed by this audit

Previous Story 009 claimed Chapter 6 while narrating post-Pūtanā / universe-in-mouth material and treating Pūtanā as already past. That package is privately archived and unpublished; public 009 is now the full Pūtanā pastime.

## Non-skipping guard

Publication is blocked when major events are omitted, only mentioned in recap/preview, or replaced by later-chapter material. Regression coverage: `tests/test_coverage_non_skipping.py`.
