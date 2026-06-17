# Build Report

Build pack version: `1.0`  
Repository: [github.com/swap2you/krishna-story-factory](https://github.com/swap2you/krishna-story-factory)

## Scope

Local Python automation for daily Krishna-conscious bedtime story packages (ages 7–11).

- CSV queue and logs as source of truth
- CLI pipeline with optional Streamlit dashboard
- Pluggable senders (WhatsApp Cloud, Telegram, Slack, Discord, manual)
- Test mode with deterministic mocks; prod mode with OpenAI + ElevenLabs

## Pre-check-in validation

```powershell
pytest -q
python run_daily_story.py --mode test --force
```

| Check | Result |
|-------|--------|
| `pytest -q` | PASSED |
| Test pipeline | SUCCESS, quality PASS |
| Dashboard import | OK |
| `.env` gitignored | Yes |
| Secrets in repo | None committed |

## Known limitations

- WhatsApp group automation is stub-only; use Cloud API or `web_test` outbox
- Slack/Discord send webhook notifications only (no full attachment upload)
- Prod APIs require valid `.env` keys (not included in repo)

## Docs

See [README.md](README.md) for full project flow and documentation index.
