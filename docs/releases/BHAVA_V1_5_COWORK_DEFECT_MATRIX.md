# Bhāva V1.5 — CoWork Defect Matrix

Source of truth: `docs/reviews/BHAVA_V1_4_COWORK_FINAL_UAT.md` and `docs/product/uat/v1.4/cowork-final/**`, plus operator-reported Story 008 scheduler failure (2026-07-24).

| ID | Finding | Severity | Evidence | Target phase | Status |
|----|---------|----------|----------|--------------|--------|
| DEF-06 | Audio playback non-functional on Stories 001–007: native `<audio>` issues no request (`readyState=0`); fetch succeeds; Blob fallback does not engage | P0 | CoWork `05_AUDIO_EVIDENCE.md` | Phase 4 | open |
| DEF-MATRIX | Automated-matrix evidence unverifiable / contradicted (`playwright_exit_code: 1` in committed live summary vs claimed 346/0) | P1 | CoWork `15_AUTOMATED_MATRIX_AUDIT.md` | Phase 5 | open |
| DEF-RESP | Responsive overflow signals in committed V1.4 Playwright traces | P1 | CoWork `13_ACCESSIBILITY_RESPONSIVE.md`, `docs/product/uat/live/traces/` | Phases 13–14 | open |
| DEF-COV | Partial route and story-tab coverage in CoWork round (Activities/Coloring/Source/Notes/Ślokās, Education not exhaustively verified) | P1 | CoWork coverage section | Phases 13, 15–16 | open |
| DEF-008 | Story 008 partial scheduled run: only `story.md` + `narration.mp3` (+ chunks); queue stuck `processing`; stale `.pipeline.lock`; LastTaskResult=1 at 10:00 and 12:00 | P0 | Operator task info; `logs/scheduler/daily_20260724_*`; `tracking/queue_state.csv` | Phases 1–2 | investigating |
| DEF-HOME | Homepage positioning mismatch — platform reads as bedtime-story site rather than full learning platform | P1 | Master prompt product decisions | Phase 8 | open |
| DEF-KNOW | Knowledge UX/readability gaps — oversized headings, sparse pathway pages, thin public set | P1 | CoWork Knowledge section; master prompt Phase 10 | Phase 10 | open |
| DEF-ART | Missing or incomplete collection artwork for several Library collections | P2 | Master prompt Phase 9 | Phase 9 | open |
| DEF-LOGO | Undersized header logo at normal zoom (icon/wordmark lockup targets not met) | P1 | Master prompt Phase 7; V1.4 fixed crop but size still short of V1.5 targets | Phase 7 | open |
| DEF-PATH | Sparse pathway/detail pages (Knowledge + Learning) | P1 | Master prompt Phases 10–11 | Phases 10–11 | open |
| DEF-EDU | Education areas not independently verified in CoWork | P1 | CoWork Education section | Phases 11, 16 | open |

## Story 008 forensic snapshot (Phase 0)

- Task: `Krishna Story Factory MWF`
- LastRunTime (at intake): 2026-07-24 12:00:00 — LastTaskResult **1**
- Prior 10:00 run: also **1** (operator report)
- Partial artifacts preserved under `work/stories/008/20260724-100002/` (removed from public `output/`)
- Reusable: `story.md` (SHA-256 in recovery manifest), `narration.mp3` (~350.76s)
- First failing stage signal: poster generation warning on stderr aborted PowerShell runner before completion; lock not released; 12:00 blocked on stale lock

## Notes

- V1.4 CoWork evidence commit `5675784` already on origin; tip at Phase 0 start was `b1bc133`.
- Mutable live UAT telemetry under tracked paths must stop creating dirty-tree noise; prefer `.bhava/instances/**` for runtime status.
