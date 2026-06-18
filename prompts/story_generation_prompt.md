# Story Generation Prompt

Generate a Krishna Book bedtime story package for children ages 6–12.

Return only valid JSON with these keys:

- title
- source_reference
- scripture_reference
- age_range
- recap
- main_story (750–1050 words, polished children's bedtime Krishna-katha, short paragraphs, no markdown headings inside)
- moral (from this pastime only)
- takeaway
- bedtime_reflection_question
- five_star_challenge (array of 5 practical child actions)
- parent_notes (markdown with source, discussion question, and bedtime reflection)
- whatsapp_caption (leave blank; pipeline fills the approved caption template)
- audio_script (500–750 spoken words; see prompts/audio_script_prompt.md)
- hero_image_prompt (ultra-realistic 3D devotional cinematic hero scene)
- story_card_square_prompt (1080x1080, one clear focal scene, not crowded)
- story_card_wide_prompt (optional wide card scene)
- image_prompt (alias of hero_image_prompt for compatibility)
- line_art_prompt (cute devotional coloring book line art reference)
- coloring_page_prompt (printable cute coloring page)
- story_card_text (short title/tagline for card)
- activity_sheet object with:
  - recall_questions (3)
  - thinking_questions (2)
  - word_search_words (10 single words from the story)
  - draw_activity
  - family_activity

## Story style

- Do not write a generic essay.
- Make it a polished children's bedtime Krishna-katha.
- Every paragraph must either:
  a) advance the pastime,
  b) deepen emotion,
  c) add source-faithful atmosphere,
  d) help the child understand devotional courage.
- No filler repetition.
- No repeated moral paragraph.
- No repeated closing paragraph.
- Close once, softly.
- Faithful to summary_seed and source_reference.
- Do not invent unrelated episodes or jump ahead.
- Explain names gently.
- No graphic violence.

## Story 002 special wording

- Do **not** call Kamsa “king of Mathura” or “King Kamsa”.
- Use “Devaki’s powerful brother” or “a prince of the royal family”.

## Story 004 Prayers in the Prison

- Focus on Devaki’s peaceful spiritual glow.
- Vasudeva’s quiet strength.
- Prayers of the demigods.
- Hope in darkness.
- Krishna’s coming appearance.
- Do not overstate that Devaki “loved Krishna very much” in a modern emotional sense; keep it devotional and respectful.
- Do not make the guards sentimental unless source supports it.
- Avoid repeating darkness/light clichés.

## Audio script

- No `[pause]` markers.
- No literal spoken “pause”.
- Use `<break time="1.0s" />`, `<break time="1.5s" />`, and `<break time="2.0s" />`.
- Closing appears once only.

## Image prompts

See prompts/image_prompt_prompt.md for hero, square card, wide card, coloring page, and line art rules.
