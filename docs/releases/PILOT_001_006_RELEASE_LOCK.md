# Krishna Story Factory — Pilot Stories 001–006 Release Lock

## Purpose

Lock the Stories 001–006 pilot as the approved Krishna Book Bedtime package set under Story Format V2. No further content, audio, or Drive package changes for these stories without a new approved change request and senior devotee review.

## Release metadata

| Field | Value |
| --- | --- |
| Release date | 2026-07-21 |
| PR | [#9](https://github.com/swap2you/krishna-story-factory/pull/9) |
| Main SHA before merge | `947d453ef001b7a9b8577e6cdfacb9f9e837242c` |
| Story format standard | Story Format V2 |
| Golden structural reference | Story 006 — The Birth of Lord Krishna |
| Drive root | [Krishna Story Factory Drive root](https://drive.google.com/drive/folders/1vr5zYLVcPdAENwRDieGxxYuBgmHdkqei) |

## What was locked

- Stories **001–005** were migrated to the Story 006–approved Template V2 structure.
- Narration for each migrated story was regenerated from its matching hidden **Audio Narration** section.
- Repeated “Remember tonight…” closing filler was reduced to **at most one** occurrence per narration.
- Locked visual/PDF/caption assets were preserved byte-for-byte:
  - `story_poster.png`
  - `coloring_page.png`
  - `simple_coloring_page.png`
  - `activity_sheet.pdf`
  - `whatsapp_caption.txt`
- **Story 006** remained unchanged (all eight package file hashes locked).
- Drive packages for 001–005 were verified by readback after migration (prior to this cleanup PR).
- This cleanup PR archives one-time migration scaffolding locally and retains durable artifact regression tests only. It does **not** regenerate or re-upload packages.

## Exact eight-file package contract

Every story package directory must contain exactly:

1. `story.md`
2. `narration.mp3`
3. `story_poster.png`
4. `coloring_page.png`
5. `simple_coloring_page.png`
6. `activity_sheet.pdf`
7. `whatsapp_caption.txt`
8. `manifest.json`

## Audio generation summary (pilot)

| Story | Provider | Model | Voice | Approx. duration |
| --- | --- | --- | --- | --- |
| 001 | OpenAI | `gpt-4o-mini-tts-2025-12-15` | marin | ~243s |
| 002 | OpenAI | `gpt-4o-mini-tts-2025-12-15` | marin | ~222s |
| 003 | OpenAI | `gpt-4o-mini-tts-2025-12-15` | marin | ~211s |
| 004 | OpenAI | `gpt-4o-mini-tts-2025-12-15` | marin | ~207s |
| 005 | OpenAI | `gpt-4o-mini-tts-2025-12-15` | marin | ~217s |
| 006 | OpenAI | `gpt-4o-mini-tts-2025-12-15` | marin | ~293s |

ElevenLabs Renee was preferred in policy but unavailable/insufficient during generation; OpenAI Marin was used. Manifests must keep `generation_verified=true`, matching `narration_source_sha`, and `publishable=true` only when the publishable gate passes.

## Package folder links

| Story | Title | Drive folder |
| --- | --- | --- |
| 001 | The Earth Prays for Krishna to Come | [folder](https://drive.google.com/drive/folders/1_7R1uj_WtW0CfuhfMAz_d3FSF1zsHbo-?usp=sharing) |
| 002 | The Wedding and the Heavenly Voice | [folder](https://drive.google.com/drive/folders/1pr9ZMwnzE8bx7mgreAguduQFDzc8XC0V?usp=sharing) |
| 003 | Vasudeva Keeps His Word | [folder](https://drive.google.com/drive/folders/1wXrCGATPxzDpafBbQ9e_y_A3g4JkwcSn?usp=sharing) |
| 004 | Narada’s Warning and Kamsa’s Decision | [folder](https://drive.google.com/drive/folders/1ngcf6RZ2gxClVOt8_njKp-dorSEyaAs-?usp=sharing) |
| 005 | Prayers by the Demigods for Lord Krishna in the Womb | [folder](https://drive.google.com/drive/folders/1qqox6hHQzMR3HQU12TQv2xRb2IUlbXU3?usp=sharing) |
| 006 | The Birth of Lord Krishna | [folder](https://drive.google.com/drive/folders/10SatVqh_Sf1sgn3wr0xFLKlVYSX6Wa15?usp=sharing) |

## Queue and scheduler

- Stories **001–006**: `done`
- Next pending: **Story 007**
- Windows scheduled task `Krishna Story Factory Daily`: **Disabled**
- WhatsApp / Telegram sending: disabled for this pilot lock
- No automatic advancement of the queue as part of this release lock

## Review status

- **Senior devotee review**: pending
- No further content modification to Stories 001–006 without a new approved change request

## Rollback / archive procedure

1. Local package backups from migration swaps live under `output/_archive/swap_00x/` (local only; not committed).
2. Template V2 pre-migration baseline archive: `output/_archive/story_template_v2_migration_*` (local only).
3. Cleanup evidence freeze: `.local_release_archive/pilot_001_006_*` (gitignored; includes script copies and hash evidence).
4. To roll back a single story package, restore the corresponding pre-swap archive directory contents into `output/<chapter>_<slug>/` and replace Drive files only under an approved change request.
5. Do not force-push `main`. Revert via a new PR if needed after merge.

## Hash evidence

Committed non-media freeze: [PILOT_001_006_HASHES.json](PILOT_001_006_HASHES.json).

CI always validates that evidence structure (six stories, eight hashes each, Story 006 lock, narration/Drive fields) even when local `output/` packages are absent.

## Verification commands

```powershell
.\scripts\test_all.ps1
.\.venv\Scripts\python.exe -m pytest tests/test_pilot_release_hash_evidence.py tests/test_release_artifacts_001_006.py tests/test_post_pr7_release_blockers.py -q
Get-ScheduledTask -TaskName "Krishna Story Factory Daily" | Select-Object TaskName, State
```

Local `output/` artifact regressions skip gracefully if a package is absent. Committed hash-evidence tests never skip. Neither suite may call Drive or paid APIs.

## Release acceptance checklist

- [x] Stories 001–005 use Story Format V2 matching Story 006 structure
- [x] Narration matches Audio Narration (`narration_source_sha`)
- [x] Remember-line defect fixed (≤1 occurrence)
- [x] Locked assets unchanged for 001–005
- [x] Story 006 eight-file hash lock preserved
- [x] Drive readback passed for 001–005 (prior to cleanup)
- [x] Queue: 001–006 done; 007 pending
- [x] Scheduler disabled
- [x] One-time migration helpers removed from tracked tree
- [x] Durable release-artifact tests retained
- [ ] PR #9 reviewed and merged to `main`
- [ ] Senior devotee content sign-off recorded
