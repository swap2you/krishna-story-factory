# Bhāva V1.6 — Implementation Plan

**Starting SHA:** `8b07b9f0018413495bfa9a8de183e4c507aee8a8` (V1.5 CoWork UAT evidence)  
**Branch:** `feature/bhava-portal-v1`  
**Contract:** `MyPilotDropbox/bhava-v1.6-stabilization/BHAVA_V1_6_CURSOR_MASTER_PROMPT.md`

## Phase order

| Phase | Commit message | Status |
|-------|----------------|--------|
| 0 | `test: establish Bhava v1.6 stabilization baseline` | in progress |
| 1 | `fix(home): restore accessible contrast on core area cards` | pending |
| 2 | `fix(design): complete page-by-page visual readability audit` | pending |
| 3 | Header/logo/typography (commit only if code changes) | pending |
| 4 | `test(story): complete Story 008 full-tab regression coverage` | pending |
| 5 | `test(audio): strengthen WebKit native playback evidence` | pending |
| 6 | `test(factory): prove registered scheduler safely without generating Story 009` | pending |
| 7 | `docs(factory): reconcile Story 008 recovery and Drive upload evidence` | pending |
| 8 | `docs: correct Bhava release evidence and SHA references` | pending |
| 9 | `perf(web): establish and address Bhava performance baseline` | pending |
| 10 | `test: complete Bhava v1.6 final stabilization gates` | pending |
| 11–13 | Live UAT, reviews, final push | pending |

## Hard constraints

- Preserve Stories 001–008, queue, Drive, paid providers
- Do not generate Story 009
- Scheduler: validation mode only
- No PR / merge / main / tags
