# Story 021 Governed Completion Evidence (current approved package)

**Status:** APPROVED PRIVATE PACKAGE — listening accepted 2026-08-04  
**Production visibility:** Stories 021/022 remain private (`public_story_max=20`)

## Current approved audio (authoritative)

| Field | Value |
| --- | --- |
| narration.mp3 SHA-256 | `96173B03F9E168FB577E42E2CC9230665671F48D46DD2FF916755541AECBF05C` |
| duration_seconds | `377.4` |
| measured_wpm | `145.3` |
| model_id | `gpt-4o-mini-tts-2025-12-15` |
| voice | `marin` |
| speed | `0.88` |
| narration_source_sha | `7FEC37EA8C6D8B8CE83AA4B579E70F01ED7197067C1265A60A35A598484A3C55` |
| human_listening_status | `USER_LISTENED_AND_ACCEPTED_ON_2026-08-04` |
| human approval binding | Tied to the complete narration.mp3 SHA-256 above |

## Locked non-audio assets (must not drift without explicit approval)

| File | SHA-256 |
| --- | --- |
| story.md | `8310320EE3D83E2FC91EB36AE870D6B9195B4DE5EDCC116A8528DFA33470C037` |
| story_poster.png | `244985FDBA253171FAE0CAB5E91C93C36D21DD21283CD11DC35E0584DDADAAD8` |
| coloring_page.png | `105138ED3E530E9E56446DDA9B6F8C66D6C33CE010C1CD728564F225AB4F6D03` |
| simple_coloring_page.png | `C49261BE77ED90E47BB133BF55C80008F97732ECB3AAC110A5E711FAF10EBB14` |
| whatsapp_caption.txt | `D32DCFF22A2137762E0F5CE654DA00FC0C20AE1E774F243E93BF95A398DD2BF4` |

Source of truth ledger: `deploy/content/PRIVATE_STORY_LOCK_021_022.json`

## Package

| Field | Value |
| --- | --- |
| title | The Stealing of the Boys and Calves by Brahma |
| source boundary | Krishna Book Chapter 13 / SB 10.13 (chapter-framed) |
| package path | `output/021_the-stealing-of-the-boys-and-calves-by-brahma` |
| exact-eight | PASS |
| production `/stories/021` | HTTP 404 |
| production `public_story_max` | 20 |

## Gates (current contract)

| Gate | Result |
| --- | --- |
| canonical Main Story ↔ TTS | exact-canonical PASS (fuzzy coverage is fail-closed) |
| bedtime WPM band | PASS (~145.3) |
| visuals | owner-approved poster + coloring pages locked |
| activity | STORY_SEQUENCE from ActivityStoryMap |
| web-assets | `data/web-assets/021` |
| ślokas / sources | reviewed chapter-framed companions |

## Historical note

Earlier completion drafts recorded a different intermediate duration (~356s) and fuzzy ~62% story/TTS coverage. Those values are superseded by the approved shipped package hashes above. Do not regenerate narration to “match” stale notes.
