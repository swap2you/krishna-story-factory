# Bhāva Stories 001–020 — Story / Audio Equivalence Audit

**Branch:** `feat/bhava-version-seo-canonical-story-foundation`  
**Scope:** Published packages **001–020** only.  
**Regeneration:** **None performed** in this audit phase. No paid TTS calls. No package rebuilds.

## Canonical rule (021+)

From Story **021** onward, the **visible + hidden narrative body in `story.md`** is the single source of truth for text and for TTS input derivation. Audio must bind to `narration_source_sha` computed from the hidden **Audio Narration** block. See [BHAVA_CANONICAL_STORY_AND_TTS_CONTRACT.md](BHAVA_CANONICAL_STORY_AND_TTS_CONTRACT.md).

Stories **001–020** remain **as published** under content tag `bhava-content-001-020-v3`. This audit documents equivalence posture only; it does not authorize retroactive narration regen.

## What “equivalence” means

| Class | Definition |
| --- | --- |
| **EQUIVALENT_VERIFIED** | Operator confirmed spoken audio matches the hidden Audio Narration text (listen-through or archived TTS request transcript). |
| **HASH_BOUND_ONLY** | `manifest.json` `narration_source_sha` matches SHA of hidden Audio Narration in `story.md`; audio bytes present; **no** archived provider transcript to confirm spoken output. |
| **DRIFT_SUSPECTED** | Hash mismatch, stale audio flag, or listen-through differs materially from narration text. |
| **TRANSCRIPT_UNAVAILABLE** | No archived TTS request/transcript and no operator listen-through on record; hash-only check not yet run. |

Honest default for legacy packages: **TRANSCRIPT_UNAVAILABLE** until an operator runs the classification steps below.

## Operator classification (no regen)

1. Open `output/<NNN>_<slug>/story.md`. Extract hidden **Audio Narration** (HTML comment block).  
2. Compute SHA: `krishna_story_factory.audio.drift.narration_source_sha(text)` (uppercase hex).  
3. Compare to `manifest.json` → `audio.narration_source_sha` (or top-level field per manifest schema).  
4. If SHA matches → reclassify **HASH_BOUND_ONLY**.  
5. Optional: listen to `narration.mp3` against Audio Narration; if aligned → **EQUIVALENT_VERIFIED**.  
6. If SHA mismatch or audible drift → **DRIFT_SUSPECTED**; open defect; **do not** regen without explicit approval.  
7. Record evidence path (local note, ticket, or ops evidence folder); update **Reviewed** column.

**Not acceptable:** guessing equivalence from main-story prose alone (Read tab text ≠ TTS source).

## Audit table (initial classification)

Titles from `input/series_plan.csv`. **No live package inspection in this doc commit** — all rows start **TRANSCRIPT_UNAVAILABLE** pending operator hash/listen pass.

| Story | Title | Initial class | `narration_source_sha` in manifest | Archived TTS transcript | Notes |
| ---: | --- | --- | --- | --- | --- |
| 001 | The Earth Prays for Kṛṣṇa to Come | TRANSCRIPT_UNAVAILABLE | pending operator | No | Pilot-era OpenAI Marin; see `docs/releases/PILOT_001_006_HASHES.json` for historical hash sample only |
| 002 | The Wedding and the Heavenly Voice | TRANSCRIPT_UNAVAILABLE | pending operator | No | |
| 003 | Vasudeva Keeps His Word | TRANSCRIPT_UNAVAILABLE | pending operator | No | |
| 004 | Nārada's Warning and Kaṁsa's Decision | TRANSCRIPT_UNAVAILABLE | pending operator | No | |
| 005 | Prayers by the Demigods for Lord Kṛṣṇa in the Womb | TRANSCRIPT_UNAVAILABLE | pending operator | No | |
| 006 | The Birth of Lord Kṛṣṇa | TRANSCRIPT_UNAVAILABLE | pending operator | No | Golden structural reference story |
| 007 | Kaṁsa Begins His Persecutions | TRANSCRIPT_UNAVAILABLE | pending operator | No | |
| 008 | The Meeting of Nanda and Vasudeva | TRANSCRIPT_UNAVAILABLE | pending operator | No | Story 008 package evidence exists (`docs/product/uat/story-008/`) |
| 009 | Pūtanā — Kṛṣṇa's Astonishing Mercy | TRANSCRIPT_UNAVAILABLE | pending operator | No | Locked; senior review pending |
| 010 | Baby Kṛṣṇa Breaks the Cart | TRANSCRIPT_UNAVAILABLE | pending operator | No | |
| 011 | The Salvation of Tṛṇāvarta | TRANSCRIPT_UNAVAILABLE | pending operator | No | |
| 012 | Yaśodā Sees the Universe While Kṛṣṇa Yawns | TRANSCRIPT_UNAVAILABLE | pending operator | No | |
| 013 | Garga Muni Names Kṛṣṇa and Balarāma | TRANSCRIPT_UNAVAILABLE | pending operator | No | |
| 014 | Kṛṣṇa and Balarāma's Crawling Adventures | TRANSCRIPT_UNAVAILABLE | pending operator | No | |
| 015 | The Gopīs Complain About Butter Theft | TRANSCRIPT_UNAVAILABLE | pending operator | No | |
| 016 | Kṛṣṇa Eats Dirt and Reveals the Universe | TRANSCRIPT_UNAVAILABLE | pending operator | No | |
| 017 | Mother Yaśodā Binds Lord Kṛṣṇa | TRANSCRIPT_UNAVAILABLE | pending operator | No | |
| 018 | The Deliverance of Nalakūvara and Maṇigrīva | TRANSCRIPT_UNAVAILABLE | pending operator | No | |
| 019 | Kṛṣṇa Protects the Calves from Vatsāsura and Bakāsura | TRANSCRIPT_UNAVAILABLE | pending operator | No | |
| 020 | Kṛṣṇa Protects Everyone from the Aghāsura Demon | TRANSCRIPT_UNAVAILABLE | pending operator | No | |

## Summary (initial)

| Class | Count |
| --- | ---: |
| EQUIVALENT_VERIFIED | 0 |
| HASH_BOUND_ONLY | 0 |
| DRIFT_SUSPECTED | 0 |
| TRANSCRIPT_UNAVAILABLE | 20 |

Update this table after operator pass. Do not bump counts without evidence.

## Related artifacts

- Content release: `bhava-content-001-020-v3` — [BHAVA_PRODUCTION_001_020_V3_FINAL_STATUS.md](../releases/BHAVA_PRODUCTION_001_020_V3_FINAL_STATUS.md)  
- Sample-first gate (021+): `krishna_story_factory/audio/sample_first_gate.py`  
- Follow-along / alignment backlog: [FOLLOW_ALONG_ALIGNMENT.md](../backlog/FOLLOW_ALONG_ALIGNMENT.md) (no paid transcription APIs in v3 candidate)

## Non-goals

- No regeneration of Stories **001–020** narration for this audit.  
- No modification of locked **001–006** without explicit approval.  
- No claim that hash equality proves perceptual audio match without listen-through (021+ still requires sample-first PASS).
