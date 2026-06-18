# Build Report

Build pack version: `1.0`  
Repository: [github.com/swap2you/krishna-story-factory](https://github.com/swap2you/krishna-story-factory)  
Validation date: 2026-06-18

## Reconciliation changes

- Confirmed `tests/test_pipeline_test_mode.py` ignores `.git`, `.pytest_cache`, `.codex_validation_tmp`, `.cursor`, `.venv`, `output`, `__pycache__`, `.env`, and `krishna-story-factory-v1-buildpack` during isolated test copies.
- Added `.codex_validation_tmp/` to `.gitignore`.
- Reset `tracking/story_log.csv`, `tracking/send_log.csv`, and `tracking/quality_log.csv` to headers only.
- Restored sample queue with `004_prahlada` as `pending`.
- Added `scripts/run_dashboard.ps1` and `scripts/repair_venv.ps1` for reliable dashboard startup after venv moves.
- Updated `docs/DASHBOARD_GUIDE.md` to prefer `python -m streamlit run dashboard.py`.

## Validation commands run

```powershell
pytest -q
python run_daily_story.py --mode test --force
python -m streamlit run dashboard.py
```

## Validation results

| Check | Result |
|-------|--------|
| `pytest -q` | **PASSED** — 1 test |
| `python run_daily_story.py --mode test --force` | **SUCCESS**, quality **PASS** |
| `python -m streamlit run dashboard.py` | **STARTED** — `http://localhost:8501` |
| `.env` gitignored | Yes |
| Secrets committed | None |

## Generated validation package (local only, not committed)

```text
output/004_prahlada/
```

## Known limitations

- Use `python -m streamlit run dashboard.py` if `streamlit.exe` points at an old venv path after project moves.
- Prod APIs require local `.env` keys (not in repo).
- WhatsApp group sender remains stub-only; use Cloud API or `web_test` outbox.

## Docs

See [README.md](README.md) for project flow and documentation index.
