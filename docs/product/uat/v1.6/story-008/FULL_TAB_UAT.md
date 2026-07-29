# Story 008 — Full tab UAT

**Package:** `output/008_the-meeting-of-nanda-and-vasudeva/` (exact-eight, publishable)  
**Automation:** `apps/web/e2e/story-008-tabs.spec.ts`

| Tab | Result | Notes |
|-----|--------|-------|
| Listen | pass | Player controls, download; audio covered by v14 matrix |
| Read | pass | Body present; no SSML/prompt leakage assertion |
| Activities | pass | PDF embed/link present |
| Coloring | pass | Asset tiles present |
| Source | pass | Honest source/review language |
| Notes | pass | Local textarea persistence |
| Ślokas | pass | Pending/honest copy; `.sanskrit` styled |
| Nav | pass | Story 009 not linked |

Manual sticky-player / Escape / focus-trap depth covered by existing pdf-and-images + audio suites; residual Safari manual checklist in audio docs.
