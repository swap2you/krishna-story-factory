# 00 MASTER PROMPT — Krishna Story Factory

You are Cursor acting as the implementation agent for a local Python project named `krishna-story-factory`.

Goal: build and validate a lightweight local automation system that generates one daily Krishna-conscious bedtime story package for children ages 7–11.

Do not use Notion. Do not add a database unless explicitly instructed. Use local CSV files as the project-management source of truth.

Read these files first, in this order:

1. `README.md`
2. `docs/ARCHITECTURE.md`
3. `docs/IMPLEMENTATION_PLAN.md`
4. `docs/SETUP_GUIDE.md`
5. `docs/API_KEYS_GUIDE.md`
6. `docs/WHATSAPP_BUSINESS_CLOUD_GUIDE.md`
7. `docs/DAILY_AUTOMATION_GUIDE.md`
8. `docs/DASHBOARD_GUIDE.md`
9. `docs/TESTING_AND_ACCEPTANCE.md`
10. All files under `prompts/`

Then execute the build in phases:

Phase 1 — Baseline validation:
- Create a Python virtual environment if missing.
- Install `requirements.txt`.
- Run `.\scripts\run_test.ps1 --force`.
- Run `pytest -q`.
- Fix any breakages without changing the intended architecture.

Phase 2 — Documentation and prompt validation:
- Confirm all docs and prompt files exist.
- Confirm `.env.example` is complete.
- Confirm `.env` is not committed and is ignored.

Phase 3 — Dashboard:
- Run `streamlit run dashboard.py` only enough to verify import/startup issues.
- Fix dashboard import/runtime errors.
- Keep CLI as source of truth. Dashboard must not replace CLI.

Phase 4 — Sender interfaces:
- Preserve `ManualSender`, `WhatsAppCloudSender`, `WhatsAppGroupSender`, and `WhatsAppWebTestSender`.
- Preserve fallback senders for Telegram, Slack, and Discord.
- Do not implement unsafe WhatsApp Web automation beyond private test/staging mode.
- WhatsApp Business Cloud should be the primary real WhatsApp path.

Phase 5 — Quality and acceptance:
- Ensure every story package creates:
  - `story.md`
  - `audio_script.txt`
  - `whatsapp_caption.txt`
  - `activity_sheet.pdf`
  - `story_card.png`
  - `image_prompt.txt`
  - `parent_notes.md`
  - `manifest.json`
  - `narration.mp3`
- Ensure quality checks fail on missing/empty files.
- Ensure no more than one story is sent per day unless `--force` is passed.
- Ensure `manifest.json` has `source_reference`, `library_id`, `age_range`, and `generated_at`.

Constraints:
- Keep the project lightweight.
- Prefer simple Python modules over frameworks.
- Use Streamlit only for the dashboard.
- Use Windows Task Scheduler for daily local automation.
- Use Google Drive Desktop Sync optionally by pointing `OUTPUT_ROOT` to a synced local folder.
- Do not hardcode API keys or secrets.
- Do not commit `.env`, generated output, logs, or test outbox files.

When finished, produce these files:

1. `BUILD_REPORT.md` with:
   - what was changed
   - commands run
   - pytest result
   - dashboard startup result
   - known limitations
2. `VALIDATION_ARTIFACTS.md` with:
   - generated output folder path
   - files created
   - quality status
   - sender status
3. Update `README.md` only if needed.

Start now. Do not ask follow-up questions unless a required secret/API key is needed for a live external call.
