# Final Activity Engine V2 Report

## Branch

`fix/activity-engine-v2-production-lock`

## Summary

* Activity Engine V2 with `ActivityPack` model, dynamic multi-page PDF renderer, prompt bank, diversity rules, QA repair loop
* Low-credit ElevenLabs narration path (420–560 words) without placeholder audio
* Story 003 production completed with seven-file package and Drive upload
* Test mode no longer mutates runtime queue
* Windows scheduler installed **disabled** by default

## Tests

```
79 passed (pytest -q)
.\scripts\run_test.ps1 --force  → SUCCESS (queue unchanged)
```

## Story 003 production

| Field | Value |
|-------|-------|
| Status | SUCCESS |
| Output | `output/003_vasudeva-keeps-his-word/` |
| Drive | https://drive.google.com/drive/folders/1wXrCGATPxzDpafBbQ9e_y_A3g4JkwcSn?usp=sharing |
| Audio | 241s (~4.0 min), 3.86 MB, source `elevenlabs` |
| Poster QA | 91 |
| Coloring QA | 92 |
| Activity type | STORY_SEQUENCE — Truthfulness Story Path |
| Activity pages | 2 |
| Activity QA | 97 |
| Final files | 7 (local + Drive) |

## Next pending story

`004` — `narada-warns-kamsa`

## Scheduler

* Task: Krishna Story Factory Daily
* Time: 5:30 AM local
* Command: `.\scripts\run_prod.ps1` (no `--force`)
* State: **Disabled** (enable manually after review)
* Validation: `scripts/test_daily_story_task.ps1` PASS

## Known limitations

* Preferred packs for stories 001–003 are deterministic overrides; LLM planner used when OpenAI text is enabled for later episodes
* Activity vision QA skipped in test mode (returns 90)
* Low-credit audio window allows 2.5–6 minutes only when ElevenLabs quota retry activates
* Runtime queue / activity history CSVs remain local and gitignored

## Rollback

1. Disable scheduled task: `Disable-ScheduledTask -TaskName "Krishna Story Factory Daily"`
2. Revert merge of this branch on `main`
3. Restore prior activity planner/PDF modules if needed
4. Story 003 Drive folder remains; do not delete unless intentionally rebuilding
