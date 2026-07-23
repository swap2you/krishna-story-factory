# Bhāva Portal V1.2 — Final CoWork UAT Prompt

Use this prompt unchanged for the final CoWork live UAT pass.

## Authority

Repository: `C:\Development\Workspace\DevotionalRepo\krishna-story-factory`  
Branch: `feature/bhava-portal-v1`  
Release SHA (verify with `git rev-parse HEAD`): `67313285411101aaf20bfed3a0159b77ab1a53ff`  
Contract: `MyPilotDropbox/bhava-v1.2-release/BHAVA_V1_2_CURSOR_MASTER_RELEASE_PROMPT.md`  
Cursor evidence root: `docs/product/uat/v1.2/`

## Running instance (KeepRunning)

- Instance: `cursor-v12`
- Web: `http://127.0.0.1:3004`
- API: `http://127.0.0.1:8002`
- Stop: `.\scripts\stop_bhava_local.ps1 -InstanceName cursor-v12`

If ports differ, trust `.bhava/instances/cursor-v12/runtime.json` and `docs/product/uat/v1.2/runtime.json`.

Restart only if needed:

```powershell
.\scripts\run_bhava_uat.ps1 -InstanceName cursor-v12 -PreferredWebPort 3002 -PreferredApiPort 8001 -KeepRunning
```

Do not create a PR, merge, modify main/master/tags, generate Story 008, change the queue, trigger the scheduler, modify Drive, or call paid APIs.

## Public identity (must match exactly)

- Steward: **Svarna Gauranga Das**
- Email: **svarnagaurangdas@gmail.com** (not `swarnagaurangadas@…`)
- Location: **Harrisburg, Pennsylvania**
- Must not appear: phone, LinkedIn, GitHub, civil/professional identity, private address

## Known blocker (do not overlook)

Approved brand package is incomplete: **8 Phase-5 Bhāgavatam canto covers (1–7, 10)** missing from `bhava-brand-assets-v1-phase5-recreated-complete.zip`. See `docs/releases/BHAVA_V1_2_ASSET_IMPORT_BLOCKERS.md`. Cursor verdict is **BLOCKED** for READY until those assets are imported. CoWork should still verify product quality and record brand gaps.

## Mandatory human checks

### 1) DEF-06 Audio (genuine Play click)

On Stories **001, 006, 007** in Chromium, Firefox, and WebKit (desktop):

1. Open `/stories/00N`
2. Click **Play** with a real pointer/keyboard activation
3. Confirm Pause label, `currentTime` advances, waveform/progress moves, correct duration, no console media errors, no duplicate competing loads
4. Pause / replay / sticky player remain coherent

### 2) DEF-07 Keyboard isolation

While audio plays, open a coloring lightbox/modal:

- ArrowLeft/ArrowRight must not seek audio ±15s
- Space must not toggle background audio while modal is focused
- Escape closes modal; focus returns sanely

### 3) Preachers outline

`/preachers` — select a reviewed story; outline preview, Print, and Export TXT must update visibly. No fabricated quotations.

### 4) Contact mailto

`/contact` — fill Name, Email, Topic, Subject, Message. Confirm encoded `mailto:svarnagaurangdas@gmail.com` and Copy message fallback. Never show false “sent”.

### 5) About / FAQ / Harrisburg

Confirm stewardship language, Harrisburg, AI-assist + human review, FAQ answers, and no identity leaks.

### 6) Prayers & Printables

- `/library/prayers-mantras` — planned taxonomy only; no unpublished full texts
- `/printables` — live posters/coloring/activity sheets for Stories 001–007; planned types clearly marked

### 7) Brand assets

Confirm imported logo/hero/icons/section art where present. Note missing canto covers 1–7 and 10 as residual.

### 8) Future Story 008 (fixture only)

Do not create a real package. Confirm Cursor documented isolated fixture tests only. Real queue **008** remains `pending`.

### 9) Factory safety

Confirm Stories 001–007 unchanged, no Drive/scheduler/paid API activity, Studio not in public nav, loopback factory actions disabled by default.

### 10) Responsive / a11y / console

Spot-check viewports 390×844 through 1920×1080. Review console/network for broken images and asset Range behavior. Prefer zero critical/serious axe findings on covered routes.

## Evidence rules

Append CoWork findings under `docs/product/uat/v1.2/cowork-final/` only.  
Do not commit `.env`, `MyPilotDropbox/`, `KrishnaBook.pdf`, keys, or package regenerations.  
If product code must change, leave findings for Cursor; do not merge to main.

## Exit criteria

Report **PASS**, **PASS WITH NOTES**, or **FAIL** for each mandatory check.  
Do not declare the release READY while the 8 canto covers remain missing or any P0/P1 product defect remains.
