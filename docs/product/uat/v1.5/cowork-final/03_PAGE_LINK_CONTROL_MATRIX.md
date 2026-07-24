# 03 — Page / Link / Control Matrix

Controls independently exercised live (not just visually inspected):

| Page | Control | Result |
|---|---|---|
| `/knowledge` | Search input + Search submit button | Works — navigates to `/knowledge/search?q=...`, real results returned |
| `/teachers` | Age-mode selector (Bal Gopal / Dāmodara / Mixed) | Switches copy correctly |
| `/teachers` | Tap-to-select asset cards (Story reading, Audio listening, Coloring pages, etc.) | Selection state reflected in "Selected:" summary and live class-pack preview |
| `/teachers` | "Reveal answer key" (adults-only gate) | Hidden by default from child-facing view; explicit reveal action required |
| `/teachers` | "Save to classroom playlist" | Persists to `localStorage` per `/privacy` claim (device-only) |
| `/contact` | Topic dropdown, Name/Email/Subject/Message fields | Render and accept input; "Open in email app" / "Copy message" are the only actions (both client-side, non-uploading) |
| Story pages (all 8) | Audio player Play/Pause, ±15s | Functions correctly on all 8 stories (see file 09) |
| Story pages | Coloring dialog open/close via thumbnail | Opens correctly; Escape closes and returns focus to originating thumbnail (see file 17 for full keyboard-isolation detail) |
| `/library` → collection cards | Navigation links | All resolve to 200 destination routes |
| `/` → "CORE AREAS" cards | Navigation links | Links resolve correctly (200) despite the visual contrast defect on the cards themselves — the defect is visual/contrast only, not a broken-link issue |

## Verdict for this section

**PASS for control functionality.** No broken or dead controls found among those exercised. (See file 04 for the separate, real visual-contrast defect on the homepage cards — the links themselves work.)
