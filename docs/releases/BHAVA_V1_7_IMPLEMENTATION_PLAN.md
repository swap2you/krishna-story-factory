# Bhāva V1.7 — Implementation Plan

## Scope

Repair the 2026-07-27 10:00 scheduler termination (`LastTaskResult=3221225786` / `0xC000013A`), harden process isolation and locks, safely validate the registered task, complete exactly one Story 009 production run, prove same-day no-op, and hand off CoWork UAT.

## Constraints

- Branch: `feature/bhava-portal-v1` only
- Preserve V1.6 tip ancestry and Stories 001–008 hashes
- No PR / merge / main / tags mutation
- Story 009 only; never Story 010
- Disable production task during repair

## Phases

| Phase | Deliverable | Commit |
|-------|-------------|--------|
| 0 | Safety baseline + task disable freeze | `test: freeze Bhava v1.7 scheduler incident baseline` |
| 1 | Forensic incident report + timeline + inventory | (with freeze or follow-up docs) |
| 2 | Story 009 state classification | docs |
| 3 | `.NET Process` launcher + heartbeat | `fix(factory): harden scheduled process isolation and termination evidence` |
| 4 | Ownership-safe locks + tests | `fix(factory): make scheduler locks ownership-safe and resumable` |
| 5 | Re-register resilient MWF task | `fix(operations): register resilient MWF production task` |
| 6 | Validate + SimulateProduction + temp task | ops evidence |
| 7–8 | One Story 009 prod + exact-eight publish | release docs |
| 9 | Registered production no-op proof | ops evidence |
| 10–12 | Portal UAT + full matrix + CoWork prompt | `test: complete Bhava v1.7 scheduler and Story 009 gates` |

## Safety gates before Story 009 prod

Root cause documented · launcher fixed · task XML fixed · simulation exit 0 · 001–008 hashes match · 009 next pending · no live lock · providers + cost guard + Drive present.
