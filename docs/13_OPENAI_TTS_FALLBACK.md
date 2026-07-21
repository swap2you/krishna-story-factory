# OpenAI TTS Fallback

When ElevenLabs balance is insufficient for the locked Renee voice, the factory can
fall back to OpenAI TTS with **lossless chunked** narration (never compressed).

## Locked behavior

1. Preflight ElevenLabs first (key, subscription balance, Renee voice ID, `eleven_v3`,
   `mp3_44100_128`, pronunciation dictionary, estimated chars + 15% reserve).
2. If ElevenLabs fails, preflight OpenAI once (run-scoped cache).
3. If OpenAI fails too and `AUDIO_REQUIRED=true`, return
   `SKIPPED_AUDIO_PROVIDER_UNAVAILABLE` **before** story/image/PDF/Drive work.
4. Queue stays pending. Scheduler remains disabled during the pilot.

## Config

```env
AUDIO_PROVIDER_MODE=auto
AUDIO_PROVIDER_PRIMARY=elevenlabs
AUDIO_PROVIDER_FALLBACK=openai
AUDIO_REQUIRED=true
OPENAI_TTS_ENABLED=true
OPENAI_TTS_MODEL=gpt-4o-mini-tts-2025-12-15
OPENAI_TTS_VOICE=marin
OPENAI_TTS_SPEED=0.92
OPENAI_TTS_MAX_INPUT_CHARS=3600
```

## Lossless chunking

Long narration is split at paragraph → sentence → clause → hard boundaries.
Chunks are reconstructed and SHA-256 compared to the normalized source before any
speech request. Incomplete assemblies never replace a final candidate file.

## Package contract

Production packages remain the exact eight-file set:

`story.md`, `narration.mp3`, `story_poster.png`, `coloring_page.png`,
`simple_coloring_page.png`, `activity_sheet.pdf`, `whatsapp_caption.txt`,
`manifest.json`.

No video. Pilot audio stays under `output/_audio_validation/` only.

## Pilot

```powershell
.\.venv\Scripts\python.exe scripts\openai_tts_fallback_pilot.py
```

Current queue truth after the OpenAI TTS fallback merge: Stories 001–005 done;
Story 006 (`the-birth-of-lord-krishna`) is next pending when the queue is ready.
