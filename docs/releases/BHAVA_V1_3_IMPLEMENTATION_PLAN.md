# Bhāva Portal V1.3 — Implementation Plan

**Branch:** `feature/bhava-portal-v1`  
**Baseline tip:** `7c17c58` (CoWork V1.2+ live UAT already on origin)  
**Contract:** `MyPilotDropbox/bhava-v1.3-release/BHAVA_V1_3_CURSOR_MASTER_RELEASE_PROMPT.md`

## Goals

1. Repair DEF-06 media lifecycle (narration GET + play advances `currentTime`).
2. Isolate DEF-07 modal/media keyboard handling.
3. Complete approved brand wiring (Library, 12 cantos, Contact/FAQ heroes, required assets or explicit defer).
4. Implement Bhāva Knowledge Library per `bhava-knowledge-library-v1.0` (curated, no fabrication).
5. Full automated + live UAT; CoWork prompt; push feature branch only.

## Phase order

| Phase | Deliverable | Commit theme |
| --- | --- | --- |
| 0 | Safety baseline + plan | `test: establish Bhava v1.3 locked-factory safety baseline` |
| 1 | Discovery / reuse / asset audit docs | docs |
| 2 | Audio proxy + player lifecycle | `fix(audio): repair native media loading and reliable story playback` |
| 3 | Keyboard isolation | `fix(a11y): isolate modal and media keyboard interactions` |
| 4–5 | Canonical inventory + brand wiring | `feat(brand): wire the complete approved Bhava visual system` |
| 6–15 | Knowledge Library foundation → seed | `feat(knowledge): …` |
| 16–18 | Identity, a11y, security review | docs + fixes |
| 19–20 | Automated gates + live UAT `cursor-v13` | evidence |
| 21–24 | Reviews, CoWork prompt, Dropbox hygiene, push | docs |

## Non-negotiables

- Stories 001–007 locked; real 008 pending; no queue/scheduler/Drive/paid APIs/PR/merge.
- No fabricated scripture/mantra/quotations.
- READY only after live Play + narration request + 12 cantos + Knowledge + SHA match.
