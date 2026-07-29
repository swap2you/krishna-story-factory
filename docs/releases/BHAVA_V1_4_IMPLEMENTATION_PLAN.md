# Bhāva V1.4 — Implementation Plan

**Branch:** `feature/bhava-portal-v1`  
**Contract:** `MyPilotDropbox/bhava-v1.4-repair/BHAVA_V1_4_CURSOR_MASTER_PROMPT.md`  
**Starting SHA:** `018740bbe46dea6360169197dbd77fd3c3fb8d1a` (local = origin; CoWork commit preserved)

## Scope

Final repair release: live audio proof, approved logo lock, complete brand wiring, full Knowledge Library package (348-resource roadmap, types, search, governance, Editorial Studio), full post-fix matrix, native UAT.

## Factory protection (non-negotiable)

- Stories 001–007 locked (SHA-256 in `BHAVA_V1_4_SAFETY_BASELINE.json`)
- Story 008 remains pending; no real generation
- Queue / scheduler / Drive / paid APIs untouched
- No PR, merge, or main/master/tag changes

## Phase map

| Phase | Deliverable |
|------|-------------|
| 0 | Safety baseline + this plan |
| 1 | Defect / brand / knowledge requirement matrices |
| 2 | Audio laboratory + verified native/blob playback |
| 3 | Keyboard isolation + released-story nav |
| 4 | Approved logo lock |
| 5 | Complete brand asset wiring |
| 6–7 | Consume package + import 348 roadmap |
| 8–9 | Public Knowledge UX + content types |
| 10 | SQLite FTS + PostgreSQL-ready search |
| 11 | Editorial Studio workflow |
| 12–13 | Safe engagement + governance gates |
| 14–15 | Platform unify + public identity |
| 16–17 | Full post-fix matrix + live UAT |
| 18–20 | Reviews, CoWork prompt, cleanup, push |

## Authoritative open findings (from V1.3 CoWork)

1. DEF-06: media element issues no narration request; `fetch()` succeeds — root-cause via lab then blob-resilient player
2. Logo rejected — reconcile against brand package approval precedence
3. Brand assets imported ≠ rendered — audit and wire
4. Knowledge: replace 20 placeholders with governed 348-topic import
5. Full post-fix matrix required (not targeted audio recheck alone)

## Inputs

- Brand: `MyPilotDropbox/bhava-brand-assets-v1`
- Knowledge: `MyPilotDropbox/bhava-knowledge-library-v1.0` (`data/topic_backlog.csv` = 348)
