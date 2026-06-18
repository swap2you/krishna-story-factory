# Validation Artifacts

Validation date: 2026-06-18

## Commands

```powershell
pytest -q
python run_daily_story.py --mode test --force
python -m streamlit run dashboard.py
```

## Pytest result

```text
1 passed in ~1s
```

Test: `tests/test_pipeline_test_mode.py::test_pipeline_generates_required_files_in_test_mode`

Isolated copy ignores: `.git`, `.pytest_cache`, `.codex_validation_tmp`, `.cursor`, `.venv`, `output`, `__pycache__`, `.env`, `krishna-story-factory-v1-buildpack`

## Pipeline result (test mode)

```json
{
  "status": "SUCCESS",
  "output_dir": "output/004_prahlada",
  "quality_status": "PASS",
  "whatsapp_status": "NOT_ATTEMPTED",
  "detail": "WhatsApp send disabled."
}
```

## Dashboard startup

```text
You can now view your Streamlit app in your browser.
Local URL: http://localhost:8501
```

Started with `python -m streamlit run dashboard.py` (headless smoke test). Stopped after confirming startup.

## Required output files (local validation run)

```text
story.md
audio_script.txt
whatsapp_caption.txt
activity_sheet.pdf
story_card.png
image_prompt.txt
parent_notes.md
manifest.json
narration.mp3
```

## Manifest fields verified

- `source_reference`
- `library_id`
- `age_range` (`7-11`)
- `generated_at`

## Tracking CSV state committed to repo

- `tracking/story_log.csv` — headers only
- `tracking/send_log.csv` — headers only
- `tracking/quality_log.csv` — headers only
- `input/series_plan.csv` — `004_prahlada` pending

## Regenerate locally

```powershell
.\.venv\Scripts\Activate.ps1
pytest -q
python run_daily_story.py --mode test --force
python -m streamlit run dashboard.py
```
