# Bhāva Portal V1.5 — Release Candidate (in progress)

**Branch:** `feature/bhava-portal-v1`  
**Tip at write time:** see `git rev-parse HEAD`  
**PR:** none (not created)  
**Main/master/tags:** unchanged

## Completed this release

1. **Scheduler forensics + repair** — PowerShell stderr abort root cause; Start-Process runner; stale lock reclaim; staging + stage state; atomic publish; Story 008 quarantine/recovery.
2. **Story 008 recovery** — reused story.md + narration.mp3; generated missing six artifacts; exact-eight PASS; Drive upload+verify PASS; queue 008=done / 009=pending.
3. **Catalog** — incomplete packages excluded; 008 discoverable; Story 007→008 nav when published.
4. **Audio DEF-06** — observable path states; short native probe then Blob fallback; Pause only after advancement.
5. **Design / nav / home** — Tillana brand display (no unofficial Samarkan); Learning menu; platform homepage tagline/audiences.
6. **Knowledge / About / teachers restore** — pathway readability; migration candidate report; missing art requests.

## Still required before READY FOR FINAL COWORK UAT

- Full Playwright matrix (Chromium/Firefox/WebKit desktop + mobile) with **0 failed**, committed SHA-bound evidence bundle under `docs/product/uat/v1.5/runs/`
- Exhaustive route visual matrix at all mandated viewports
- Fresh axe + Lighthouse numbers on all major page families
- Independent review docs (Codex/Claude/parent/brand/factory) fully filled from live pass
- Live CoWork audio re-proof on Stories 001–008 after player change

## Safety

- Stories 001–007 hashes frozen and rechecked against V1.5 baseline
- Story 008 only exposed after exact-eight + publishable
- No PR/merge

## Verdict

**BLOCKED** — product and factory recovery landed, but full post-fix SHA-bound Playwright/a11y evidence for the final tip SHA is not yet committed.
