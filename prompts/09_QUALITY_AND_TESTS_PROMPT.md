# 09 Quality and Tests Prompt

Strengthen quality checks and test coverage.

Quality checks must verify:
- all nine required output files exist
- no file is empty
- `story.md` includes Recap, Main Story, Moral, Takeaway, Five-Star Challenge
- story length is reasonable for ages 7–11
- `manifest.json` includes `source_reference`, `library_id`, `age_range`, `generated_at`
- `whatsapp_caption.txt` exists and is not too long
- `narration.mp3` exists
- `story_card.png` or `image_prompt.txt` exists
- daily send guard blocks more than one send per day unless `--force`

Tests:
- `pytest -q` must pass.
- Use mocks for API senders.
- Test mode must never call paid APIs.

Deliverable: update tests and produce `BUILD_REPORT.md`.
