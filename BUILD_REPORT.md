# Build Report

Validation date: `2026-06-18`
Project path: `C:\Development\Workspace\DevotionalRepo\krishna-story-factory`

## Scope

Validated the local Python project against:

- `README.md`
- `docs/ARCHITECTURE.md`
- `docs/TESTING_AND_ACCEPTANCE.md`
- `prompts/00_MASTER_PROMPT.md`
- `docs/CODEX_CLAUDE_VALIDATION_GUIDE.md`

## What Changed

- Updated `tests/test_pipeline_test_mode.py` so the isolated copy test ignores local metadata/cache/temp folders:
  - `.git`
  - `.pytest_cache`
  - `.codex_validation_tmp`
  - `.cursor`

This is a test-harness fix only. It does not redesign the project or change the CLI, CSV architecture, dashboard architecture, sender interfaces, or generated output contract.

## Commands Run

```powershell
.\.venv\Scripts\python.exe -m pip install --force-reinstall -r requirements.txt
$env:TMP=(Resolve-Path .codex_validation_tmp).Path; $env:TEMP=(Resolve-Path .codex_validation_tmp).Path; .\.venv\Scripts\python.exe -m pytest -q -o cache_dir=.codex_validation_tmp\pytest_cache
.\.venv\Scripts\python.exe run_daily_story.py --mode test --force
.\.venv\Scripts\python.exe -m json.tool output\004_prahlada\manifest.json
.\.venv\Scripts\python.exe -m py_compile dashboard.py
.\.venv\Scripts\python.exe -m streamlit run dashboard.py --server.headless true --server.address 127.0.0.1 --server.port 8507
git check-ignore -v .env
git ls-files .env
rg -n "sk-[A-Za-z0-9]" -g "!.venv/**" -g "!.git/**" -g "!.env"
rg -n "OPENAI_API_KEY|ELEVENLABS_API_KEY|WHATSAPP_ACCESS_TOKEN|SLACK_BOT_TOKEN|DISCORD_WEBHOOK_URL|TELEGRAM_BOT_TOKEN" -g "!.venv/**" -g "!.git/**" -g "!.env"
```

## Results

| Check | Result |
| --- | --- |
| Requirements install | Passed after approved network access |
| `pytest` | Passed: `1 passed in 1.13s` |
| Test-mode CLI | Passed: `SUCCESS` |
| Quality status | `PASS` |
| Sender status | `NOT_ATTEMPTED` because WhatsApp sending is disabled |
| Required output files | All 9 present and non-empty |
| Manifest JSON | Valid JSON |
| Dashboard compile check | Passed |
| Streamlit startup | Started at `http://127.0.0.1:8507` |
| `.env` ignored | Yes: `.gitignore:1:.env` |
| `.env` tracked | No |
| Secret scan | No matches outside ignored `.env`, `.venv`, and `.git` |

## Known Limitations

- The sample queue had no pending rows before validation, so chapter `004` was temporarily reopened to `pending` and the CLI marked it back to `done` after the deterministic run.
- The local default temp directory was not accessible to pytest in this environment. Pytest was run with workspace-local temp/cache paths.
- Live OpenAI, ElevenLabs, WhatsApp, Telegram, Slack, and Discord APIs were not called.
- Streamlit is a long-running server; startup was verified from launch output and then allowed to stop via command timeout.
