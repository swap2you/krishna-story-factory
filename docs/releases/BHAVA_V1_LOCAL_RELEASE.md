# Bhāva v1 Local Release

## Branch

`feature/bhava-portal-v1` (open, not merged)

## Base

`main` @ `3bae97850ef8b934bbec3a48f42f92fbe6de169f`

## Delivered

- Next.js public portal + FastAPI catalog/gateway
- Stories 001–007 discovered from locked packages
- Story listening/reading/activities/coloring/notes/source shells
- Teacher toolkit (local)
- Factory Studio (demo-disabled actions)
- PWA manifest/icons, privacy/accessibility/source pages
- Local start/stop/test/reindex scripts
- Review packet + screenshots under `docs/product/screenshots/`

## Safety

- Queue unchanged (008 pending)
- Stories 001–007 hash-guarded
- No paid APIs, Drive writes, or scheduler triggers during build
- `main` / `master` / existing tags untouched

## Operator start

```powershell
.\scripts\start_bhava_local.ps1
```
