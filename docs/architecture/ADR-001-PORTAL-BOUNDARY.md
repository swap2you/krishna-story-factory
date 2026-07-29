# ADR-001 — Portal Boundary Around Locked Factory

## Status

Accepted

## Context

The Krishna Story Factory already produces validated eight-file packages. The portal must present and operate around that system without rewriting generation, validation, Drive upload, or scheduling.

## Decision

Treat `krishna_story_factory/`, approved CLI scripts, `input/`, `tracking/`, `output/`, and `credentials/` as locked. The portal lives in `apps/`, `packages/`, and `data/catalog/`.

Factory interaction is allowed only through narrow adapters that:

- invoke documented entry points (`run_daily_story.py` / scheduled wrappers);
- never accept arbitrary shell commands or executable paths;
- default production actions to demo/disabled on the feature branch;
- never mutate Stories 001–007 packages during portal development.

## Consequences

- Faster, safer portal iteration.
- Duplicate business logic is forbidden; bugs in generation are fixed in the factory with minimal patches only when a portal test proves a compatibility defect.
- Portal tests must not call paid providers or Drive.
