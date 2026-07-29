# Bhāva V1.2 Implementation Plan

Branch: `feature/bhava-portal-v1`  
Baseline SHA: `b0ba09a`  
Prior tested RC: `7072298`

## Goals

1. Integrate approved brand asset system from `MyPilotDropbox/bhava-brand-assets-v1` using Phase 13 consolidated manifest (122 approved visual assets).
2. Fix DEF-06 audio playback and DEF-07 modal/keyboard collision.
3. Complete Preachers outline selection/export.
4. Contact/About/FAQ with Harrisburg stewardship and encoded mailto workflow.
5. Prayers & Mantras destination and Printables hub.
6. Preserve automatic future-story integration with isolated fixtures.
7. Security/privacy/copyright review, full test gates, live UAT, CoWork prompt.

## Constraints

- Stories 001–007 immutable; real Story 008 pending.
- No queue/scheduler/Drive/paid API/production Studio actions.
- Do not commit MyPilotDropbox, KrishnaBook.pdf, keys, or unoptimized masters.

## Execution order

Phases 0 → 18 as defined in `BHAVA_V1_2_CURSOR_MASTER_RELEASE_PROMPT.md`.

## Brand import strategy

Authoritative inventory: `bhava-p13/refs/consolidated_manifest.json`  
Approved package list: `bhava-p13/refs/approved_packages.md`  
Import into `apps/web/public/{brand,heroes,collections,sections,social,icons,empty-states}` with deterministic names + WebP derivatives + `apps/web/config/brand-assets.json`.
