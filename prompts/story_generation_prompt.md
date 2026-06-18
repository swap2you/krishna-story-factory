# Story Generation Prompt

Generate a Krishna Book bedtime story package for children ages 6–12.

Return only valid JSON with these keys:

- title
- source_reference
- scripture_reference
- age_range
- recap
- main_story (900–1300 words, bedtime style, short paragraphs, no markdown headings inside)
- moral (from this pastime only)
- takeaway
- five_star_challenge (array of 5 practical child actions)
- parent_notes (markdown with source and discussion question)
- whatsapp_caption (parent-facing, Hare Krishna greeting, ask for photo/audio/video after activity)
- audio_script (5–8 minute narration, [pause] markers, no markdown)
- image_prompt (ultra-realistic devotional painting, child-safe, 16:9 hero image)
- line_art_prompt (simple coloring page line art)
- story_card_text (short title/tagline for card)
- activity_sheet object with:
  - recall_questions (3)
  - thinking_questions (2)
  - word_search_words (10)
  - draw_activity
  - family_activity

Requirements:

- Krishna Book sequence only for the provided queue row.
- Faithful to summary_seed and source_reference.
- Do not invent unrelated episodes or jump ahead.
- Do not mix other pastimes unless they are the current row.
- One natural Hare Krishna moment.
- One bedtime reflection question in parent_notes or takeaway.
- Beautiful, emotionally clear, child-understandable language.
