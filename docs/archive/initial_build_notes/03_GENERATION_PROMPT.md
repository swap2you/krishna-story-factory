# 03 Story Generation Prompt

Improve story generation while keeping test mode deterministic.

Generation requirements:
- In `--mode test`, use local mock content only.
- In `--mode prod`, call OpenAI only when `OPENAI_TEXT_ENABLED=true`.
- Return structured story content with:
  - title
  - recap
  - main_story
  - moral
  - takeaway
  - five_star_challenge
  - audio_script
  - whatsapp_caption
  - image_prompt
  - parent_notes
  - activity_questions
  - vocabulary_words

Content rules:
- Age range: 7–11.
- Faithful to `source_reference` and `summary_seed`.
- Devotional and child-friendly.
- Avoid adult themes, graphic violence, or speculative invented scripture claims.
- Explain Sanskrit names simply when needed.
- Keep tone sweet, clear, and not overly preachy.

Deliverable: update `krishna_story_factory/generation/story_generator.py` and tests.
