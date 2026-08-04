# Story 021 Governed Completion Evidence

**Verdict target:** PASS — STORY 021 COMPLETE AND PRIVATE; SCHEDULER SAFELY RESTORED; NO DEPLOYMENT

## Baseline

| Item | Value |
| --- | --- |
| starting `origin/main` | `c25973d29c200e7a4911c61b4c8d6b652cda0076` |
| starting `origin/develop` | `45041557cb06886edeb2aebc39186b34163cc900` |
| branch | `feature/bhava-story-021-governed-completion` |
| worktree | `C:\Development\Workspace\DevotionalRepo\krishna-story-factory-wt-021` |
| prior failed run | `logs/scheduler/daily_20260803_100003.log` (missing `audio_sample_pass.json`) |
| reused story run | `work/stories/021/20260803-100015-d7bfea` |

## Story 021 package

| Field | Value |
| --- | --- |
| title | The Stealing of the Boys and Calves by Brahma |
| source boundary | Krishna Book Chapter 13 (chapter-framed; no invented exact verse range) |
| package path | `output/021_the-stealing-of-the-boys-and-calves-by-brahma` |
| exact-eight | PASS |
| Drive folder ID | `1MQiEIux35WbGq8PiUcbVpi4lEDfLgzso` |
| Drive upload | UPLOADED / readback via pipeline success |
| queue | 021=done; next pending=022 |
| `public_story_max` | 20 (unchanged) |
| public `/stories/021` | HTTP 404 |
| production release_sha | `c25973d…` unchanged |

## Audio (sample-first)

| Field | Value |
| --- | --- |
| provider | openai (ElevenLabs unavailable / insufficient at run time) |
| initial wrong settings | `tts-1-hd` + `nova` @ `1.0` → ~261.7 s (too fast vs series template) |
| repaired settings | `gpt-4o-mini-tts-2025-12-15` + `marin` @ `0.92` (series OpenAI template) |
| settings_hash (repair) | `1EA485E1F314D085E0D6C5240E0692B137C5C995C8948A4AE9462BC8B468CDB4` |
| narration_source_sha | `FF2BFDF42FBEA0F04F7C75252EECA4A9AD2489DB1AB1DF0DA59C931309214E3B` |
| sample duration (repair) | 58.658 s (retry once after first sample >60s) |
| sample QA | objective PASS |
| sample retry count | 1 |
| full narration duration | 356.21 s |
| objective full audio QA | PASS |
| Drive narration repair | UPLOADED (narration.mp3 + manifest.json) |
| human listening status | HUMAN_REVIEW_PENDING (later accepted USER_LISTENED_AND_ACCEPTED_ON_2026-08-04) |

## Gates

| Gate | Result |
| --- | --- |
| story/TTS equivalence | Historical note: earlier completion accepted fuzzy ~62% coverage; permanent gates in PR #47 now require exact-canonical Main Story ↔ TTS (fuzzy is fail-closed / legacy opt-in only) |
| pronunciation coverage | PASS |
| source_boundary.json | PASS (chapter-framed) |
| editorial_review.json | automated PASS; human senior devotee review PENDING |
| visuals | poster_score=92, coloring_score=92 |
| activity | deterministic pack after LLM STORY_MAP malform; package accepted |
| web-assets | rebuilt for 021 under `data/web-assets/021` (ślokas reviewed SB 10.13 companion; narration refreshed) |
| ślokas tab | reviewed chapter-framed companion (not “not yet curated”) |

## Scheduler

| Field | Value |
| --- | --- |
| task | Krishna Story Factory MWF |
| state | Ready (Enabled) |
| schedule | Mon/Wed/Fri 10:00 only |
| StartWhenAvailable | false |
| RestartCount | 0 |
| noon backup | removed |
| validate-scheduler | provider_calls=0 |
| next run | 2026-08-05 10:00:00 (local) |
| Story 022 generated | no |
| live lock | none |

## Remaining human gate

- Human senior devotee listening / editorial review for Story 021 (private).
- After PR merge to `develop`, reinstall the MWF task from the primary checkout so the scheduled WorkingDirectory is not the temporary worktree.
