# Setup Guide

## Requirements

- Python 3.11 or 3.12
- Cursor or VS Code
- Optional: Google Drive Desktop Sync
- Optional: OpenAI API key
- Optional: ElevenLabs API key
- Optional: WhatsApp Business Cloud API credentials

## Windows setup

Open PowerShell in the project folder.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
pytest -q
python run_daily_story.py --mode test --force
```

## Mac/Linux setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
pytest -q
python run_daily_story.py --mode test --force
```

## Dashboard

```bash
streamlit run dashboard.py
```

## Output

Generated packages go here by default:

```text
output/<chapter_no>_<slug>/
```

To use Google Drive Desktop Sync, set `OUTPUT_ROOT` in `.env` to a synced local Google Drive folder.

Example:

```env
OUTPUT_ROOT=C:\Users\YOUR_NAME\Google Drive\Krishna Story Factory\output
```
