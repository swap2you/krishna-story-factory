"""Generate Renee pronunciation smoke MP3 + JSON under output/_audio_validation/."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SCRIPT = (
    "[softly] Hare Krishna. [warmly] Tonight we remember Krishna, Devaki, Vasudeva, "
    "Kamsa, Narada, Brahma, Shiva, and Mathura with gentle hearts."
)


def main() -> int:
    from mutagen.mp3 import MP3

    from krishna_story_factory.audio.pronunciation import (
        LOCKED_MODEL_ID,
        LOCKED_OUTPUT_FORMAT,
        LOCKED_VOICE_ID,
        LOCKED_VOICE_NAME,
        normalize_for_tts,
    )
    from krishna_story_factory.audio.tts import AudioGenerator
    from krishna_story_factory.audio.waveform import validate_mp3_waveform
    from krishna_story_factory.config import load_settings

    settings = load_settings(ROOT)
    out_dir = ROOT / "output" / "_audio_validation"
    out_dir.mkdir(parents=True, exist_ok=True)
    mp3_path = out_dir / "renee_pronunciation_test.mp3"
    json_path = out_dir / "renee_pronunciation_test.json"

    display = SCRIPT
    normalized = normalize_for_tts(display, project_root=ROOT)
    gen = AudioGenerator(settings, mode="prod")
    source = gen.generate_mp3(normalized.audio_text, mp3_path)
    duration = float(MP3(mp3_path).info.length)
    wave = validate_mp3_waveform(mp3_path, expected_duration=duration)
    size = mp3_path.stat().st_size
    if size < 5_000 or wave.status != "PASS":
        raise SystemExit(f"Pronunciation smoke failed: size={size} wave={wave.status} {wave.detail}")
    if gen.last_voice_name and "renee" not in gen.last_voice_name.lower():
        raise SystemExit(f"Wrong voice resolved: {gen.last_voice_name}")
    payload = {
        "voice_id": settings.elevenlabs_voice_id or LOCKED_VOICE_ID,
        "voice_name": gen.last_voice_name or settings.elevenlabs_voice_name or LOCKED_VOICE_NAME,
        "model": settings.elevenlabs_model_id or LOCKED_MODEL_ID,
        "output_format": getattr(settings, "elevenlabs_output_format", "") or LOCKED_OUTPUT_FORMAT,
        "source_text": display,
        "normalized_audio_text": normalized.audio_text,
        "aliases_applied": list(normalized.aliases_applied),
        "dictionary_usage": {
            "attached": bool(gen.last_dictionary_attached),
            "dictionary_id": settings.elevenlabs_pronunciation_dictionary_id,
            "version_id": getattr(settings, "elevenlabs_pronunciation_dictionary_version_id", ""),
            "fallback": "normalized_audio_text",
        },
        "audio_source": source,
        "file_duration_seconds": round(duration, 2),
        "file_size_bytes": size,
        "waveform": {
            "status": wave.status,
            "detail": wave.detail,
            "peak": getattr(wave, "peak", None),
            "clipping_ratio": getattr(wave, "clipping_ratio", None),
            "longest_silence_seconds": getattr(wave, "longest_silence_seconds", None),
        },
    }
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({"status": "PASS", "mp3": str(mp3_path), "json": str(json_path), **payload}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
