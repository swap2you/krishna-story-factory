# Bhāva Canonical Story and TTS Contract

**Effective:** Story **021+** create-next path.  
**Legacy:** Stories **001–020** remain published as-is; equivalence tracked separately in [BHAVA_001_020_STORY_AUDIO_EQUIVALENCE_AUDIT.md](BHAVA_001_020_STORY_AUDIO_EQUIVALENCE_AUDIT.md).

## Source of truth

| Layer | Authority |
| --- | --- |
| Narrative (parent/child visible) | `story.md` sections per [CONTENT_STANDARD.md](../CONTENT_STANDARD.md) Story Format V2 |
| TTS input | Hidden **Audio Narration** block inside `story.md` (HTML comment; SSML allowed) |
| Runtime binding | `manifest.json` → `narration_source_sha`, audio file SHA, provider metadata |
| Queue / plan | `input/series_plan.csv` + `tracking/queue_state.csv` |

**Rule:** The main-story body is canonical for meaning and editorial review. Audio Narration is a **controlled derivative** for speech — not a second competing story. From 021+, edits to meaning flow: main story → Audio Narration → TTS; never the reverse without editorial pass.

## Canonical narrative structure

Required visible order (no YAML frontmatter on distributed `story.md`):

1. Greeting  
2. Series — Krishna Book Bedtime  
3. Story number and title  
4. Scriptural Source  
5. Recap  
6. Main Story (~700–950 words prod)  
7. Devotional Meaning  
8. Five Lessons (exactly five)  
9. Think About It (3–5 questions; no printed answers)  
10. Five-Star Challenge (exactly five tasks)  
11. Bedtime Prayer (include Hare Kṛṣṇa mahā-mantra)  
12. Next Story Preview  
13. Parent/Teacher Note  

Hidden in HTML comment only: Audio Narration (~650–850 spoken words), poster/coloring visual briefs, activity data.

Golden structural reference: Story **006**.

## Permitted TTS transforms

Applied **only** to the Audio Narration block:

| Transform | Allowed |
| --- | --- |
| SSML breaks, emphasis, rate within provider limits | Yes |
| Spoken contractions / gentle oral phrasing | Yes, if meaning unchanged |
| Sanskrit name pronunciation hints via SSML | Yes |
| Trimming redundant stage directions not in main story | Yes, if recap/preview boundaries preserved |
| Provider voice rendering (ElevenLabs Renee primary, OpenAI Marin fallback) | Yes, after sample-first PASS |

## Forbidden transforms

| Transform | Forbidden |
| --- | --- |
| New plot events, quotes, or morals not in main story | Yes |
| must_avoid leakage from future episodes | Yes |
| Replacing main story text from audio transcript (“fix prose from TTS”) | Yes |
| Publishing when `narration_source_sha` ≠ current Audio Narration hash | Yes |
| Full narration before sample-first PASS (021+ default) | Yes |
| Paid TTS in test mode | Yes (project rule) |

## Durable hashes

| Hash | Computed from | Stored in |
| --- | --- | --- |
| `narration_source_sha` | Normalized Audio Narration text (SSML stripped per drift module) | `manifest.json`, `audio_sample_pass.json` |
| `settings_hash` | Stable JSON of provider/model/voice/settings | `audio_sample_pass.json` |
| Package file SHA-256 | Each of exact eight finals | `manifest.json` / release evidence |
| Content release checksum | Tagged content bundle | `deploy/content/RELEASE_CONTENT.json` |

Changing Audio Narration, voice, model, or material settings **invalidates** sample pass and blocks full TTS until re-sample PASS.

Implementation: `krishna_story_factory/audio/drift.py`, `sample_first_gate.py`.

## Sample-first gate order (021+ create-next)

Fail-closed default: `AUDIO_SAMPLE_FIRST_REQUIRED` unset or true.

| Step | Gate | Fail action |
| ---: | --- | --- |
| 1 | Story Format V2 + source guards PASS | Stop before images/audio spend |
| 2 | Extract Audio Narration; compute `narration_source_sha` | Stop if missing/empty |
| 3 | Generate **45–60s sample** with intended provider/voice/model/settings | Stop if provider unavailable |
| 4 | Human/sample QA PASS | No full narration |
| 5 | Write `audio_sample_pass.json` binding provider, model, voice, `settings_hash`, `narration_source_sha` | — |
| 6 | Full narration synthesis | Blocked if pass missing or stale |
| 7 | Verify audio SHA + manifest fields | `publishable=false` until PASS |
| 8 | Exact-eight package + local PASS | Queue stays pending on failure |
| 9 | Drive upload (if enabled) | Optional post-PASS |

Legacy rebuild tools may set `AUDIO_SAMPLE_FIRST_REQUIRED=0` — not for routine 021+ prod.

## Web / portal contract

- Public Read tab: visible sections only (`apps/api/bhava_api/web_assets/story_parser.py`).  
- Listen tab: serves `narration.mp3`; must not expose SSML or internal briefs.  
- Internal fields belong in structured manifest/catalog fields, not visible markdown.

## Related docs

- [CONTENT_STANDARD.md](../CONTENT_STANDARD.md)  
- [PROJECT_SNAPSHOT_V1.md](../PROJECT_SNAPSHOT_V1.md)  
- [BHAVA_001_020_STORY_AUDIO_EQUIVALENCE_AUDIT.md](BHAVA_001_020_STORY_AUDIO_EQUIVALENCE_AUDIT.md)
