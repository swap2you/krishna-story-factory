# V1.6 live UAT notes (`cursor-v16`)

## Instance

| Field | Value |
|-------|-------|
| Name | `cursor-v16` |
| Mode | production |
| Web | see `.bhava/instances/cursor-v16/runtime.json` (preferred 3000; may allocate next free port on collision) |
| API | `http://127.0.0.1:8000` |
| Stop | `.\scripts\stop_bhava_local.ps1 -InstanceName cursor-v16` |

## Live checks performed during stabilization

- Home CORE AREAS contrast at multiple viewports (automated + visual).
- Story 008 all tabs (automated across Chromium/Firefox/WebKit desktop + mobile).
- Stories 001–008 remain catalog-visible; Story 009 not linked.
- Knowledge search public surface; roadmap records remain private.
- Scheduler validation mode only (no production generation).

## Operator follow-up (non-blocking)

- Confirm preferred ports when other Bhāva instances are stopped.
- Complete Safari/iOS hardware checklist: `docs/product/uat/v1.6/audio/SAFARI_IOS_MANUAL_CHECKLIST.md`.
