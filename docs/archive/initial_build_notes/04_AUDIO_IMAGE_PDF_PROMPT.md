# 04 Audio, Image, and PDF Prompt

Validate and improve package asset generation.

Audio:
- In test mode, generate a non-empty placeholder MP3 file.
- In prod mode, use ElevenLabs when `ELEVENLABS_ENABLED=true`.
- Output file: `narration.mp3`.

Image:
- Always create `image_prompt.txt`.
- If OpenAI image generation is enabled, generate `story_card.png` through the image API.
- If disabled or failed, create a local fallback PNG with Pillow.

PDF:
- Generate `activity_sheet.pdf` using ReportLab.
- Include title, story questions, activity, challenge checklist, and parent note.
- Keep it print-friendly.

Deliverable: tests proving all nine required outputs exist and are non-empty in test mode.
