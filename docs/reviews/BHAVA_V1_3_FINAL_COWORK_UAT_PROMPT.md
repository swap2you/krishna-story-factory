# Bhāva Portal V1.3 — Final CoWork UAT Prompt

Use this prompt for independent live UAT. Do not merge or create a PR.

## Authority

- Repo: `C:\Development\Workspace\DevotionalRepo\krishna-story-factory`
- Branch: `feature/bhava-portal-v1`
- Confirm tip: `git rev-parse HEAD` (must include Knowledge + audio + brand commits after `7c17c58`)
- Evidence: `docs/product/uat/v1.3/`

## Running instance

- Name: `cursor-v13`
- Web / API: read `.bhava/instances/cursor-v13/runtime.json` (last Cursor run used http://127.0.0.1:3005 and http://127.0.0.1:8003)
- Stop: `.\scripts\stop_bhava_local.ps1 -InstanceName cursor-v13`
- Restart: `.\scripts\run_bhava_uat.ps1 -InstanceName cursor-v13 -PreferredWebPort 3000 -PreferredApiPort 8000 -KeepRunning`

## Mandatory checks

1. **Audio (DEF-06):** On Stories 001, 006, 007 click Play. Confirm narration network activity (Chromium DevTools), usable `readyState`, advancing `currentTime`, Pause/replay.
2. **Keyboard (DEF-07):** With coloring modal open, arrows/Space must not seek/toggle background audio.
3. **Brand:** Library collection art; all **12** canto covers on `/library/srimad-bhagavatam`; Contact + FAQ heroes.
4. **Knowledge:** Nav label Knowledge; `/knowledge` home; `/blog` redirects; search; a published article; private ask/correction mailto (no false sent).
5. **Editorial privacy:** `/studio/knowledge` not linked from public nav/footer.
6. **Factory safety:** Stories 001–007 unchanged; real 008 pending; no Drive/scheduler/paid APIs.
7. **Identity:** Svarna Gauranga Das · svarnagaurangdas@gmail.com · Harrisburg only.
8. **A11y/console:** Spot-check mobile/desktop; no critical axe regressions on covered routes.

## Evidence rules

Append only under `docs/product/uat/v1.3/cowork-final/`. Do not commit secrets, Dropbox, or regenerate packages.

## Exit

Report PASS / PASS WITH NOTES / FAIL per check. Fabricated scripture or unpublished backlog appearing as finished content is FAIL.
