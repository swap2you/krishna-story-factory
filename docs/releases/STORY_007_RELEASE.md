# Story 007 Release — Kamsa Begins His Persecutions

**Release date:** 2026-07-22  
**Branch:** `main`  
**Story repair commit:** `f751b26` (*Add Story 007 content repair and review packet*)  
**Phase 7 ops:** Drive replace + hash verify + queue advance + MWF re-enable (no paid generation)

## Source boundary

- Krishna Book Chapter 4  
- Śrīmad-Bhāgavatam 10.4  

Locked content: `krishna_story_factory/content/story_007_locked.py` with Chapter 4 source guards.

## Reviewer verdicts

| Reviewer | Verdict |
|----------|---------|
| Human listen-through / visual inspection | Approved |
| Codex (source-boundary) | APPROVE |
| Claude Code (adversarial) | SAFE FOR RELEASE |
| CoWork (parent package) | APPROVE WITH NON-BLOCKING NOTES |

Non-blocking parent guidance: sober persecution theme may need extra facilitation for ages 6–8; activity sheet is text-heavy.

Review packet: [../reviews/STORY_007_REPAIR_REVIEW_PACKET.md](../reviews/STORY_007_REPAIR_REVIEW_PACKET.md)

## Exact eight-file SHA-256 (local = Drive)

| File | SHA-256 |
|------|---------|
| story.md | `5F6350DA7C09B67341E03D06BEA4E648D26F0FC1AF58B105226F7C57C3C897E7` |
| narration.mp3 | `F1812190DB9C6F057209D866AEF8E80389216A3698E160CD5124AD03F07897F5` |
| story_poster.png | `510060BF3A62493336023B79C5F6CA996E4EEA084F89F512C1F8CB8C12E4382D` |
| coloring_page.png | `75F85D86999C1109F64EC206BAC52AB65EEA7F3F86F5E11A4C132A31E701B1A0` |
| simple_coloring_page.png | `6108168BFC642E0D5CE20ECF4A652B7B513A86708DFAC910EB039BD8DD09AC53` |
| activity_sheet.pdf | `AC1CD03F012676221B98680E8071FC887F9F8004786743F37A6D7E29721AB70C` |
| whatsapp_caption.txt | `34DF151CA18D0CB6C5726B0324C1CB4F4E314CC0E105C4F1A8340D7F5992D970` |
| manifest.json | `039BA500C98E4F9E47B5203F6E5BE7EF08042E605B2C220852CF9C237385F681` |

## Audio metadata

| Field | Value |
|-------|--------|
| Provider | OpenAI |
| Voice | Marin |
| Duration | 282.9 seconds |
| Audio SHA-256 | `F1812190DB9C6F057209D866AEF8E80389216A3698E160CD5124AD03F07897F5` |
| audio_stale | false |
| publishable | true |
| quality.status | PASS |

## Drive

https://drive.google.com/drive/folders/12KjkBOc42AFvIlbUSFZHPZdCDUlZRW8v

Drive readback and all eight hash comparisons: **PASS**. Phase 7 used upload/readback only — **no paid generation APIs**.

## Queue transition

| Chapter | Status |
|---------|--------|
| 001–007 | done |
| 008 | pending (next) |

## Scheduler

| Field | Value |
|-------|--------|
| Task | Krishna Story Factory MWF |
| State | Enabled / Ready |
| Days | Monday, Wednesday, Friday |
| Time | 6:00 AM Eastern |
| StartWhenAvailable | true |
| MultipleInstances | IgnoreNew |
| Timeout | 60 minutes |
| Retries | 2 × 30 minutes |
| Drive | enabled |
| WhatsApp / Telegram | disabled |
| `--force` | not used |

## Stories 001–006

Unchanged. Pilot hash evidence remains PASS. Senior devotee sign-off remains **pending**.

Pilot tag `v1.0.0-pilot-stories-001-006` was not moved or recreated.

## Rollback note

- Code/config rollback: `git switch --detach v1.0.0-pilot-stories-001-006` (does not restore gitignored media).  
- Story 007 media rollback: restore from local archive under `output/_archive/` (operator local only) or re-download from Drive if the prior folder revision is retained by Drive history.  
- Do not regenerate Stories 001–006 without explicit approval.

## Next pending

**Story 008 — The Meeting of Nanda and Vasudeva**
