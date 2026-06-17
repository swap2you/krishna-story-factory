# Testing and Acceptance

## Required validation commands

```powershell
pytest -q
python run_daily_story.py --mode test --force
```

## Required output files

Each generated package must contain:

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

## Quality checks

Must verify:

- all required files exist
- no required file is empty
- story has Recap, Main Story, Moral, Takeaway, Five-Star Challenge
- age range is 7–11
- MP3 exists
- image exists or image prompt exists
- WhatsApp caption exists
- manifest has source reference
- manifest has library ID
- manifest has generated timestamp
- daily send guard works

## Acceptance criteria

The project is acceptable when:

1. `pytest -q` passes.
2. `python run_daily_story.py --mode test --force` succeeds.
3. A package folder is created under `output/`.
4. All nine required files exist.
5. `manifest.json` is valid JSON.
6. Dashboard starts with `streamlit run dashboard.py`.
7. `.env` is ignored by Git.
8. No API keys are committed.
