"""OpenAI TTS pilot: voice A/B samples + Story 002/005 local candidate narrations.

Does not overwrite production narration.mp3, manifests, Drive, or queue.
All outputs stay under output/_audio_validation/.
"""
from __future__ import annotations

import hashlib
import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output" / "_audio_validation"
CRITICAL_NAMES = (
    "Krishna",
    "Devaki",
    "Vasudeva",
    "Kamsa",
    "Narada",
    "Brahma",
    "Shiva",
    "Mathura",
    "Vishnu",
)

SAMPLE_SCRIPT = (
    "Hare Krishna. Tonight we remember Krishna, Devaki, Vasudeva, Kamsa, "
    "Narada, Brahma, Shiva, Mathura, and Vishnu with gentle hearts. "
    "In a calm bedtime voice: when fear rises, loving prayer can make the heart brave again. "
    "We chant together: Hare Krishna Hare Krishna Krishna Krishna Hare Hare "
    "Hare Rama Hare Rama Rama Rama Hare Hare. "
    "Rest softly, dear children, and let the Lord's names stay close as you sleep."
)


def _sha(data: bytes | str) -> str:
    raw = data.encode("utf-8") if isinstance(data, str) else data
    return hashlib.sha256(raw).hexdigest().upper()


def _extract_audio_narration(md: str) -> str:
    """Prefer the approved Audio Narration section; never abridge it."""
    from krishna_story_factory.content.story_format_v2 import extract_section

    audio = extract_section(md, "Audio Narration") or extract_section(md, "Audio Performance Script")
    if audio and len(re.findall(r"\S+", audio)) >= 80:
        return audio.strip()
    # Fallback: concatenate spoken sections without truncation.
    parts = []
    for heading in (
        "Series Introduction",
        "Recap",
        "Main Story",
        "Devotional Meaning",
        "Five Lessons",
        "Bedtime Prayer",
        "Next Story Preview",
    ):
        section = extract_section(md, heading)
        if section:
            parts.append(section.strip())
    if not parts:
        raise RuntimeError("Could not locate Audio Narration or spoken story sections.")
    return "\n\n".join(parts)


def _waveform(path: Path, duration: float | None = None):
    from krishna_story_factory.audio.waveform import validate_mp3_waveform

    return validate_mp3_waveform(path, expected_duration=duration)


def _duration(path: Path) -> float | None:
    try:
        from mutagen.mp3 import MP3

        return float(MP3(path).info.length)
    except Exception:  # noqa: BLE001
        return None


def _transcribe(path: Path, api_key: str) -> str:
    """Best-effort Whisper transcription for QA evidence (not sole proof)."""
    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key)
        with path.open("rb") as handle:
            result = client.audio.transcriptions.create(model="whisper-1", file=handle)
        return (getattr(result, "text", None) or str(result) or "").strip()
    except Exception as exc:  # noqa: BLE001
        return f"[transcription_unavailable: {type(exc).__name__}]"


def _name_hits(transcript: str) -> dict[str, bool]:
    lower = transcript.lower()
    return {name: name.lower() in lower for name in CRITICAL_NAMES}


def _generate_candidate(
    *,
    chapter: str,
    story_dir: Path,
    settings,
    voice: str,
) -> dict:
    from krishna_story_factory.audio.openai_tts import synthesize_openai_tts
    from krishna_story_factory.audio.pronunciation import normalize_for_tts
    from krishna_story_factory.audio.sanitize import sanitize_audio_script

    md = (story_dir / "story.md").read_text(encoding="utf-8")
    raw = _extract_audio_narration(md)
    normalized = normalize_for_tts(raw, project_root=ROOT)
    narration = sanitize_audio_script(normalized.audio_text, model_id="openai")

    out_mp3 = OUT / f"story_{chapter}_openai_candidate.mp3"
    out_json = OUT / f"story_{chapter}_openai_candidate.json"
    chunks_dir = OUT / f"story_{chapter}_chunks"
    if chunks_dir.exists():
        shutil.rmtree(chunks_dir, ignore_errors=True)
    chunks_dir.mkdir(parents=True, exist_ok=True)

    # Never write into production folder.
    prod_mp3 = story_dir / "narration.mp3"
    prod_before = _sha(prod_mp3.read_bytes()) if prod_mp3.exists() else ""

    result = synthesize_openai_tts(
        api_key=settings.openai_api_key,
        text=narration,
        output_path=out_mp3,
        model=settings.openai_tts_model,
        voice=voice,
        speed=settings.openai_tts_speed,
        response_format=settings.openai_tts_response_format,
        max_input_chars=settings.openai_tts_max_input_chars,
        allow_model_fallback=True,
        work_dir=chunks_dir,
        pause_ms=280,
    )
    duration = _duration(out_mp3)
    wave = _waveform(out_mp3, duration)
    transcript = _transcribe(out_mp3, settings.openai_api_key)
    prod_after = _sha(prod_mp3.read_bytes()) if prod_mp3.exists() else ""
    if prod_before != prod_after:
        raise RuntimeError(f"Production narration.mp3 changed for story {chapter} — aborting.")

    plan = result.chunk_plan
    payload = {
        "chapter": chapter,
        "story_dir": str(story_dir),
        "candidate_mp3": str(out_mp3),
        "provider": "openai",
        "audio_source": "openai",
        "audio": {
            "provider": "openai",
            "model_id": result.model_id,
            "voice": result.voice,
            "speed": result.speed,
            "response_format": result.response_format,
        },
        "original_text_sha256": plan.original_sha256 if plan else "",
        "reconstructed_text_sha256": plan.reconstructed_sha256 if plan else "",
        "reconstruction_equal": bool(plan.reconstruction_equal) if plan else False,
        "chunk_count": result.chunk_count,
        "chunks": result.chunk_metadata,
        "duration_seconds": duration,
        "waveform": {
            "status": wave.status,
            "detail": wave.detail,
            "peak": wave.peak,
            "longest_silence_seconds": wave.longest_silence_seconds,
            "clipping_ratio": wave.clipping_ratio,
        },
        "transcript": transcript,
        "pronunciation_hits": _name_hits(transcript),
        "mantra_hit": "hare krishna" in transcript.lower(),
        "production_mp3_unchanged": prod_before == prod_after,
        "byte_size": out_mp3.stat().st_size,
        "audio_sha256": _sha(out_mp3.read_bytes()),
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    out_json.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return payload


def main() -> int:
    from dataclasses import replace

    from krishna_story_factory.audio.openai_tts import synthesize_openai_tts
    from krishna_story_factory.audio.provider import (
        preflight_elevenlabs,
        preflight_openai,
        reset_provider_preflight_cache,
        select_audio_provider,
    )
    from krishna_story_factory.config import load_settings

    OUT.mkdir(parents=True, exist_ok=True)
    settings = load_settings(ROOT)
    # Pilot forces OpenAI path without touching production settings permanently.
    settings = replace(
        settings,
        openai_tts_enabled=True,
        audio_provider_mode="openai",
        audio_required=True,
    )

    key_present = bool(settings.openai_api_key and len(settings.openai_api_key) > 10)
    report: dict = {
        "started_at": datetime.now(timezone.utc).isoformat(),
        "openai_key_present": key_present,
        "outputs_root": str(OUT),
        "production_untouched": True,
    }
    if not key_present:
        report["status"] = "BLOCKED_OPENAI_TTS_AUTH"
        (OUT / "openai_pilot_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(json.dumps(report, indent=2))
        return 2

    reset_provider_preflight_cache()
    eleven = preflight_elevenlabs(settings, estimated_chars=4500, require_dictionary=True)
    openai_pf = preflight_openai(settings)
    decision = select_audio_provider(settings, estimated_chars=4500)
    report["elevenlabs_preflight"] = {
        "ok": eleven.get("ok"),
        "available": eleven.get("available"),
        "required_with_reserve": eleven.get("required_with_reserve"),
        "voice_ok": eleven.get("voice_ok"),
        "voice_name": eleven.get("voice_name"),
    }
    report["openai_preflight"] = {
        "ok": openai_pf.get("ok"),
        "model_id": openai_pf.get("model_id"),
        "voice": openai_pf.get("voice"),
        "error_class": openai_pf.get("error_class"),
        "blocked_status": openai_pf.get("blocked_status"),
        # Never echo credentials or full error bodies with secrets.
        "detail": (openai_pf.get("detail") or "")[:200],
    }
    report["provider_decision"] = {
        "status": decision.status,
        "provider": decision.provider,
        "reason": decision.reason,
    }

    if not openai_pf.get("ok"):
        report["status"] = openai_pf.get("blocked_status") or "BLOCKED_OPENAI_TTS"
        (OUT / "openai_pilot_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(json.dumps(report, indent=2))
        return 3

    selected_voice = settings.openai_tts_voice or "marin"
    comparison_voice = "shimmer"
    sample_dir = OUT / "openai_samples"
    sample_dir.mkdir(parents=True, exist_ok=True)

    marin_path = OUT / "openai_marin_sample.mp3"
    shimmer_path = OUT / "openai_shimmer_sample.mp3"
    synthesize_openai_tts(
        api_key=settings.openai_api_key,
        text=SAMPLE_SCRIPT,
        output_path=marin_path,
        model=settings.openai_tts_model,
        voice="marin",
        speed=settings.openai_tts_speed,
        max_input_chars=settings.openai_tts_max_input_chars,
        work_dir=sample_dir / "marin_chunks",
        pause_ms=0,
    )
    synthesize_openai_tts(
        api_key=settings.openai_api_key,
        text=SAMPLE_SCRIPT,
        output_path=shimmer_path,
        model=settings.openai_tts_model,
        voice=comparison_voice,
        speed=settings.openai_tts_speed,
        max_input_chars=settings.openai_tts_max_input_chars,
        work_dir=sample_dir / "shimmer_chunks",
        pause_ms=0,
    )

    marin_tx = _transcribe(marin_path, settings.openai_api_key)
    shimmer_tx = _transcribe(shimmer_path, settings.openai_api_key)
    comparison = {
        "criteria": [
            "warm bedtime tone",
            "natural human cadence",
            "devotional mood",
            "not theatrical",
            "not promotional",
            "no robotic list reading",
            "clear prayer ending",
            "correct pronunciation",
            "stable pacing",
            "low harshness",
            "natural paragraph pauses",
        ],
        "marin": {
            "path": str(marin_path),
            "duration": _duration(marin_path),
            "waveform": _waveform(marin_path).status,
            "transcript": marin_tx,
            "pronunciation_hits": _name_hits(marin_tx),
        },
        "shimmer": {
            "path": str(shimmer_path),
            "duration": _duration(shimmer_path),
            "waveform": _waveform(shimmer_path).status,
            "transcript": shimmer_tx,
            "pronunciation_hits": _name_hits(shimmer_tx),
        },
        "selected_voice": selected_voice,
        "selection_reason": (
            "Default marin after successful sample generation; manual listening still required. "
            "Shimmer retained for A/B comparison only."
        ),
    }
    (OUT / "openai_voice_comparison.json").write_text(
        json.dumps(comparison, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    story_005 = ROOT / "output" / "005_prayers-by-the-demigods-for-lord-krishna-in-the-womb"
    story_002 = ROOT / "output" / "002_devaki-and-vasudeva-wedding"
    cand_005 = _generate_candidate(chapter="005", story_dir=story_005, settings=settings, voice=selected_voice)
    cand_002 = _generate_candidate(chapter="002", story_dir=story_002, settings=settings, voice=selected_voice)

    report.update(
        {
            "status": "PASS" if cand_005.get("reconstruction_equal") and cand_002.get("reconstruction_equal") else "FAIL",
            "selected_voice": selected_voice,
            "samples": {
                "marin": str(marin_path),
                "shimmer": str(shimmer_path),
                "comparison": str(OUT / "openai_voice_comparison.json"),
            },
            "story_005": {
                "candidate": cand_005.get("candidate_mp3"),
                "chunk_count": cand_005.get("chunk_count"),
                "duration": cand_005.get("duration_seconds"),
                "waveform": cand_005.get("waveform"),
                "original_sha": cand_005.get("original_text_sha256"),
                "reconstructed_sha": cand_005.get("reconstructed_text_sha256"),
            },
            "story_002": {
                "candidate": cand_002.get("candidate_mp3"),
                "chunk_count": cand_002.get("chunk_count"),
                "duration": cand_002.get("duration_seconds"),
                "waveform": cand_002.get("waveform"),
                "original_sha": cand_002.get("original_text_sha256"),
                "reconstructed_sha": cand_002.get("reconstructed_text_sha256"),
            },
            "completed_at": datetime.now(timezone.utc).isoformat(),
        }
    )
    (OUT / "openai_pilot_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
