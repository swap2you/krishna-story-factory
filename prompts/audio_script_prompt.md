# Audio Script Prompt

Generate a bedtime narration script for children ages 6–12.

## Length and tone

- Target **650–850 spoken words**.
- Calm, expressive bedtime narration.
- Rich emotional context in natural prose.
- Faithful to the current queue row only.

## Format rules

- Plain text only. No markdown.
- **Never** use the literal word `pause` as a spoken direction.
- **Never** use `[pause]` markers.
- Use SSML-style breaks for pacing:
  - `<break time="1.0s" />`
  - `<break time="1.5s" />`
  - `<break time="2.0s" />`
- Describe mood in narration language: softly, gently, with wonder, with concern, with relief.

## ElevenLabs model behavior

- If `ELEVENLABS_MODEL_ID` contains `v3`, you may use approved audio tags such as `[softly]`, `[with wonder]`, `[gentle pause]`.
- If the model is **not** v3, do **not** use bracket tags. Use `<break time="..."/>` and prose instead.

## Content

- Opening greeting: Hare Krishna dear children.
- Retell the pastime in order without jumping ahead.
- Explain names gently once.
- Close with a peaceful bedtime thought and Hare Krishna.
