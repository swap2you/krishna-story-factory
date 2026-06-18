# Codex / Claude Code Validation Guide

Use this when you want another coding agent to validate the implementation.

## Prompt for Codex or Claude Code

```text
You are validating a local Python project named krishna-story-factory.

Project path: <PASTE_LOCAL_PATH>

Do not redesign the project. Validate the existing implementation against:
- README.md
- docs/ARCHITECTURE.md
- docs/TESTING_AND_ACCEPTANCE.md
- prompts/00_MASTER_PROMPT.md

Run:
python -m venv .venv if missing
activate venv
pip install -r requirements.txt
pytest -q
python run_daily_story.py --mode test --force

Check that the output folder contains:
story.md
audio_script.txt
whatsapp_caption.txt
activity_sheet.pdf
story_card.png
image_prompt.txt
parent_notes.md
manifest.json
narration.mp3

Create or update:
BUILD_REPORT.md
VALIDATION_ARTIFACTS.md

Do not call live OpenAI, ElevenLabs, WhatsApp, Telegram, Slack, or Discord APIs unless I explicitly provide .env values and ask for live validation.
```
