# Krishna Story Factory — Activity Engine v2 Release Report

Validated on 2026-07-20 from branch `fix/activity-engine-v2-production-lock`.

## Release gates

- Local tests: PASS — 82 tests passed via `scripts/test_all.ps1`.
- Test-mode isolation: PASS — Story 005 preview written under `.work/test_preview`; production queue SHA-256 unchanged.
- Windows CI: PENDING.
- Ubuntu CI: PENDING.
- Story 003 package: PASS — exactly seven files; 866 main-story words; real 220.5-second MP3; poster QA 91; coloring QA 92; two-page dynamic activity QA 94.
- Story 003 boundary: PASS — Kīrtimān and Vasudeva's truthful delivery through Kaṁsa initially returning the child; no wedding recap, Nārada warning, imprisonment, six-sons episode, or Krishna birth.
- Story 003 Drive: PASS — per-story folder contains exactly the seven final filenames and no intermediates.
- Story 004 package: PASS — exactly seven files; 796 main-story words; real 188.6-second MP3; poster QA 92; coloring QA 92; three-page dynamic activity QA 92.
- Story 004 boundary: PASS — Nārada's warning, the Yadu and Vṛṣṇi families, Kālanemi, imprisonment, Ugrasena's removal, and devotional remembrance; no Mother Earth, Ocean of Milk, wedding recap, first-child episode, or Krishna birth.
- Story 004 Drive: PASS — per-story folder contains exactly the seven final filenames and no intermediates.
- Scheduler: PASS — canonical production runner uses `--mode prod` without `--force`, disables WhatsApp and Telegram, logs runs, prevents overlap with `IgnoreNew`, and is installed disabled.
- Repository hygiene: PASS — `.env`, generated packages, runtime CSV state, logs, and work files are ignored; no secret or generated release artifact is tracked.
- Merge: READY — all local and artifact gates pass; merge remains conditional on both GitHub Actions jobs passing.

## Production links

- Story 003: https://drive.google.com/drive/folders/1wXrCGATPxzDpafBbQ9e_y_A3g4JkwcSn?usp=sharing
- Story 004: https://drive.google.com/drive/folders/1ngcf6RZ2gxClVOt8_njKp-dorSEyaAs-?usp=sharing

## Master plan

The static plan contains 93 episodes, covers Krishna Book Chapters 1–90, and the production queue has Stories 001–004 complete with Story 005 next pending.
