# Krishna Story Factory — Operations Prompt Bank

Repository:
`C:\Development\Workspace\DevotionalRepo\krishna-story-factory`

Current production contract (exact eight files):
1. `story.md`
2. `narration.mp3`
3. `story_poster.png`
4. `coloring_page.png`
5. `simple_coloring_page.png`
6. `activity_sheet.pdf`
7. `whatsapp_caption.txt`
8. `manifest.json`

Important operating rules:
- Normal runs use `--mode prod`.
- Never use `--force` for daily generation.
- A normal run must select exactly one next-pending episode.
- Generated media belongs in local `output/` and Google Drive, not Git.
- Commit only source, tests, prompts, scripts, and documentation.
- WhatsApp and Telegram remain disabled.
- Google Drive remains enabled.
- The Windows scheduled task must run daily at 6:00 AM local time.
- The scheduled task must not overlap another run.
- Test mode must not mutate production queue state.
- A manual production run plus a scheduler run on the same calendar day must not produce two stories unless an explicit force/rebuild option is used.
- No video is currently part of the eight-file contract. Treat video as a future feature, not a missing output.

Recommended sequence:
1. Run `01_CURSOR_RUN_NEXT_STORY_AND_SET_6AM.md` in Cursor Agent mode.
2. Run the three independent review prompts:
   - `02_CODEX_TECHNICAL_VALIDATION.md`
   - `03_CLAUDE_CODE_CONTENT_VALIDATION.md`
   - `04_COWORK_PARENT_PACKAGE_VALIDATION.md`
3. Run `05_FINAL_SYNTHESIS_AND_LOCK.md` in Cursor or Codex.
