"""Optional future enhancement notes: ElevenLabs background music.

Status: DEFERRED (non-blocking for Final V2 rebuild).

Investigation summary (2026-07):
- The project's TTS path uses `POST /v1/text-to-speech/{voice_id}` with
  `eleven_v3` and `mp3_44100_128`.
- Native background-music mixing is not part of this locked request path
  in a cost-safe, deterministic way for bedtime packages.
- External music mixing would add licensing, loudness, and pipeline risk.

Decision:
- Do not enable background music in the daily pipeline now.
- Keep ENABLE_AMBIENT_AUDIO / ELEVENLABS_SFX_ENABLED off by default.
- Revisit only if ElevenLabs exposes a stable, documented music option on
  the exact TTS endpoint we use, with predictable cost controls.
"""
