# Audio Script Prompt

Generate a bedtime narration script for children ages 6–12.

## Voice and tone

- Calm, expressive bedtime storytelling.
- Middle-aged warm female narrator style.
- Gentle base, motherly tone, devotional warmth.
- Natural emotional arc: wonder, concern, hope, relief.
- Faithful to the current queue row only.

## Length

- Target **500–750 spoken words**.
- Meaningful pacing over filler length.
- Close once, softly. Do not repeat the closing.
- If narration sounds too plain in ElevenLabs, change the voice ID and voice settings in `.env` — do not pad the script to force duration.

## Format rules

- Plain text only. No markdown.
- **Never** use the literal word `pause` as a spoken direction.
- **Never** use `[pause]` markers.
- For `eleven_multilingual_v2`, do **not** use bracket audio tags.
- Use SSML-style breaks for pacing:
  - `<break time="1.0s" />`
  - `<break time="1.5s" />`
  - `<break time="2.0s" />`

## Pronunciation

- “Hare Krishna” must sound natural; do not over-Anglicize.
- Use “Hare Krishna dear children” only once at the opening.

## Content

- Retell the pastime in order without jumping ahead.
- Explain names gently once.
- No repeated closing blocks.
- End with one peaceful bedtime thought and Hare Krishna.
