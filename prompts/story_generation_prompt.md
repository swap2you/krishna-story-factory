# Story Generation Prompt

Generate a Krishna Book bedtime story package for children ages 6–12.

Return only valid JSON with these keys:

- title
- source_reference
- scripture_reference
- age_range
- recap
- main_story (850–1100 words, bedtime Krishna-katha style, short paragraphs, no markdown headings inside)
- moral (from this pastime only)
- takeaway
- bedtime_reflection_question
- five_star_challenge (array of 5 practical child actions)
- parent_notes (markdown with source, discussion question, and bedtime reflection)
- whatsapp_caption (leave blank; pipeline fills the approved caption template)
- audio_script (650–850 spoken words; see prompts/audio_script_prompt.md)
- hero_image_prompt (16:9 devotional cinematic hero scene)
- story_card_square_prompt (1080x1080, one clear focal scene, not crowded)
- story_card_wide_prompt (optional wide card scene)
- image_prompt (alias of hero_image_prompt for compatibility)
- line_art_prompt (simple line art reference)
- coloring_page_prompt (printable black-and-white coloring page)
- story_card_text (short title/tagline for card)
- activity_sheet object with:
  - recall_questions (3)
  - thinking_questions (2)
  - word_search_words (10 single words from the story)
  - draw_activity
  - family_activity

## Story style

- Bedtime Krishna-katha, not a school essay.
- Rich but simple descriptions.
- Faithful to summary_seed and source_reference.
- Do not invent unrelated episodes or jump ahead.
- Do not mix other pastimes unless they are the current row.
- Explain names gently.
- No graphic violence.
- One natural Hare Krishna moment.
- Include recap, main story, moral, takeaway, bedtime reflection, five-star challenge, parent notes, activity content, image prompts, and audio script.

## Story 002 special wording

- Do **not** call Kamsa “king of Mathura” or “King Kamsa”.
- Use “Devaki’s powerful brother” or “a prince of the royal family”.
- Do not mention Gajendra, Prahlada, Damodara, or Fruit Seller pastimes.

## Audio script

- No `[pause]` markers.
- No literal spoken “pause”.
- Use `<break time="1.0s" />`, `<break time="1.5s" />`, and `<break time="2.0s" />` for pacing unless v3 audio tags are enabled in your environment.

## Image prompts

Generate separate prompts for:

1. hero_image_prompt
2. story_card_square_prompt
3. story_card_wide_prompt
4. coloring_page_prompt
5. line_art_prompt

Square card rules:

- 1080x1080 preferred
- devotional cinematic painting
- one clear focal scene
- not too crowded
- fewer background faces
- warm light
- child-safe
- accurate clothing and ancient Mathura setting when applicable
- no modern objects
- no distorted faces or hands
- no text baked into the image

Coloring page rules:

- printable black-and-white coloring page
- thick clean outlines
- white background
- no shading
- large simple shapes
- child-friendly faces
- no weapons, no violence

## Story 002 image direction

- Devaki and Vasudeva seated respectfully in a wedding chariot
- Kamsa driving, visibly troubled after hearing the heavenly voice
- Mathura street in background
- flower petals but not excessive clutter
- soft golden celestial glow from sky
- no sword shown, or if shown, only sheathed and not threatening
- mood: wonder, tension, protection, faith
