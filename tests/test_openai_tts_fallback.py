"""Tests for OpenAI TTS fallback, lossless chunking, and pilot safety."""
from __future__ import annotations

import inspect
from dataclasses import replace
from pathlib import Path

import pytest

from krishna_story_factory.audio.chunking import chunk_narration, normalize_whitespace, sha256_text
from krishna_story_factory.audio.openai_tts import classify_openai_error
from krishna_story_factory.audio.provider import (
    ProviderDecision,
    reset_provider_preflight_cache,
    select_audio_provider,
)
from krishna_story_factory.audio.sanitize import sanitize_audio_script
from krishna_story_factory.audio import tts as tts_module
from krishna_story_factory.config import load_settings
from krishna_story_factory.outputs import FINAL_OUTPUT_FILES


ROOT = Path(__file__).resolve().parents[1]


def test_exact_eight_file_production_contract() -> None:
    assert len(FINAL_OUTPUT_FILES) == 8
    assert "simple_coloring_page.png" in FINAL_OUTPUT_FILES
    assert "video" not in " ".join(FINAL_OUTPUT_FILES).lower()


def test_story_007_is_next_pending(tmp_path) -> None:
    """Queue contract after Stories 001–006: next pending is 007."""
    import shutil

    from krishna_story_factory.csv_store import ensure_csv_files, read_next_pending, read_plan_by_chapter, update_plan_status

    project = tmp_path / "proj"
    (project / "input").mkdir(parents=True)
    (project / "tracking").mkdir(parents=True)
    shutil.copy2(ROOT / "input" / "series_plan.csv", project / "input" / "series_plan.csv")
    ensure_csv_files(project)
    for chapter in ("001", "002", "003", "004", "005", "006"):
        plan = read_plan_by_chapter(project, chapter)
        assert plan is not None
        update_plan_status(project, plan, "done")
    pending = read_next_pending(project)
    assert pending is not None
    assert pending.chapter_no == "007"
    assert pending.slug == "kamsa-begins-his-persecutions"
    assert pending.status == "pending"


def test_openai_error_classification_distinguishes_quota_and_rate() -> None:
    assert classify_openai_error(RuntimeError("invalid_api_key 401")) == "authentication_invalid_key"
    assert classify_openai_error(RuntimeError("Error code: 429 - insufficient_quota")) == "insufficient_quota"
    assert classify_openai_error(RuntimeError("Error code: 429 - rate_limit_exceeded")) == "rate_limit"
    assert classify_openai_error(RuntimeError("The model `xyz` does not exist")) == "model_access"
    assert classify_openai_error(RuntimeError("payment_required billing")) == "billing_payment_failure"


def test_sanitize_strips_ssml_for_openai_path() -> None:
    cleaned = sanitize_audio_script('Hello [pause] <break time="1s" /> world', model_id="openai")
    assert "[pause]" not in cleaned.lower()
    assert "<break" not in cleaned.lower()


def test_no_concise_compression_helper_in_tts() -> None:
    source = Path(inspect.getfile(tts_module)).read_text(encoding="utf-8")
    assert "_to_concise_narration" not in source
    assert "target_max=560" not in source
    assert "rsplit" not in source or " ..." not in source


def test_short_narration_single_chunk() -> None:
    plan = chunk_narration("Hare Krishna. Soft bedtime blessing.", max_input_chars=3600)
    assert len(plan.chunks) == 1
    assert plan.reconstruction_equal
    assert plan.original_sha256 == plan.reconstructed_sha256


def test_long_narration_multiple_chunks_and_exact_reconstruction() -> None:
    paragraphs = []
    for i in range(12):
        paragraphs.append(
            f"Paragraph {i}. Krishna blesses Devaki and Vasudeva in Mathura while Kamsa listens. "
            f"Narada, Brahma, Shiva, and Vishnu are remembered with love. "
            + (" ".join(f"Sentence {j} continues the gentle bedtime narration carefully." for j in range(40)))
        )
    text = "\n\n".join(paragraphs)
    plan = chunk_narration(text, max_input_chars=800)
    assert len(plan.chunks) > 1
    assert plan.reconstruction_equal
    assert "".join(c.text for c in plan.chunks) == plan.original_normalized
    assert plan.original_sha256 == sha256_text(normalize_whitespace(text))
    assert all(c.char_count <= 800 for c in plan.chunks)
    assert all(c.text.strip() for c in plan.chunks)


def test_paragraph_boundary_preferred() -> None:
    left = "A" * 100 + "."
    right = "B" * 100 + "."
    text = f"{left}\n\n{right}"
    plan = chunk_narration(text, max_input_chars=150)
    assert len(plan.chunks) >= 2
    assert plan.chunks[0].boundary == "paragraph" or "\n\n" in (plan.chunks[0].text + plan.chunks[1].text)


def test_insufficient_elevenlabs_selects_openai(monkeypatch) -> None:
    reset_provider_preflight_cache()
    settings = load_settings(ROOT)
    settings = replace(
        settings,
        elevenlabs_enabled=True,
        elevenlabs_api_key="x",
        elevenlabs_pronunciation_dictionary_id="dict",
        elevenlabs_voice_id="Itr6exdQTrvjpW1lNztS",
        elevenlabs_model_id="eleven_v3",
        elevenlabs_output_format="mp3_44100_128",
        openai_tts_enabled=True,
        openai_api_key="y",
        audio_provider_mode="auto",
        audio_required=True,
    )

    monkeypatch.setattr(
        "krishna_story_factory.audio.provider.elevenlabs_available_characters",
        lambda _key: (100, {"character_count": 1, "character_limit": 101}),
    )
    monkeypatch.setattr(
        "krishna_story_factory.audio.provider.elevenlabs_voice_resolves",
        lambda _key, _vid: (True, "Renee - Rich, Calm and Smooth"),
    )
    calls = {"openai": 0}

    def _pf(**_kwargs):
        calls["openai"] += 1
        return {"ok": True, "provider": "openai", "model_id": "gpt-4o-mini-tts", "voice": "marin"}

    monkeypatch.setattr("krishna_story_factory.audio.provider.preflight_openai_tts", _pf)
    decision = select_audio_provider(settings, estimated_chars=3000)
    assert decision.status == "READY"
    assert decision.provider == "openai"
    # Cached: second call must not re-hit OpenAI speech preflight.
    decision2 = select_audio_provider(settings, estimated_chars=3000)
    assert decision2.provider == "openai"
    assert calls["openai"] == 1


def test_neither_provider_available_skips_cleanly(monkeypatch) -> None:
    reset_provider_preflight_cache()
    settings = load_settings(ROOT)
    settings = replace(
        settings,
        elevenlabs_enabled=False,
        openai_tts_enabled=True,
        openai_api_key="y",
        audio_required=True,
    )
    monkeypatch.setattr(
        "krishna_story_factory.audio.provider.preflight_openai_tts",
        lambda **_kwargs: {"ok": False, "error_class": "insufficient_quota", "blocked_status": "BLOCKED_OPENAI_TTS_QUOTA"},
    )
    decision = select_audio_provider(settings, estimated_chars=3000)
    assert decision.status == "SKIPPED_AUDIO_PROVIDER_UNAVAILABLE"
    assert decision.provider == ""


def test_provider_preflight_cached_once_per_run(monkeypatch) -> None:
    reset_provider_preflight_cache()
    settings = load_settings(ROOT)
    settings = replace(
        settings,
        elevenlabs_enabled=True,
        elevenlabs_api_key="x",
        elevenlabs_pronunciation_dictionary_id="dict",
        elevenlabs_voice_id="Itr6exdQTrvjpW1lNztS",
        elevenlabs_model_id="eleven_v3",
        elevenlabs_output_format="mp3_44100_128",
        openai_tts_enabled=True,
        openai_api_key="y",
        audio_provider_mode="auto",
    )
    calls = {"el": 0, "oa": 0}

    def el_chars(_key):
        calls["el"] += 1
        return (50_000, {"character_count": 0, "character_limit": 50_000})

    monkeypatch.setattr("krishna_story_factory.audio.provider.elevenlabs_available_characters", el_chars)
    monkeypatch.setattr(
        "krishna_story_factory.audio.provider.elevenlabs_voice_resolves",
        lambda _key, _vid: (True, "Renee - Rich, Calm and Smooth"),
    )
    monkeypatch.setattr(
        "krishna_story_factory.audio.provider.preflight_openai_tts",
        lambda **_kwargs: calls.__setitem__("oa", calls["oa"] + 1) or {"ok": True, "model_id": "m", "voice": "marin"},
    )
    d1 = select_audio_provider(settings, estimated_chars=1000)
    d2 = select_audio_provider(settings, estimated_chars=1000)
    assert d1.provider == "elevenlabs"
    assert d2.provider == "elevenlabs"
    assert calls["el"] == 1
    assert calls["oa"] == 0  # OpenAI not needed when ElevenLabs ready


def test_failed_chunk_does_not_leave_complete_candidate(tmp_path, monkeypatch) -> None:
    from krishna_story_factory.audio import openai_tts as oa

    calls = {"n": 0}

    def boom(**kwargs):
        calls["n"] += 1
        if calls["n"] == 2:
            raise oa.OpenAITtsError("fail chunk 2", error_class="server_error")
        path = kwargs.get("output_path")
        # synthesize_openai_speech_once doesn't take output_path — patch speech once
        return b"ID3fakeaudio" * 40, "req", "gpt-4o-mini-tts", {
            "model_attempts": ["gpt-4o-mini-tts"],
            "request_attempt_count": 1,
            "retryable_error_classes": [],
            "final_successful_attempt": 1,
            "fallback_model_used": False,
            "estimated_extra_paid_attempts": 0,
        }

    monkeypatch.setattr(oa, "synthesize_openai_speech_once", boom)
    monkeypatch.setattr(
        oa,
        "assemble_mp3_chunks",
        lambda *a, **k: (_ for _ in ()).throw(RuntimeError("should not assemble")),
    )

    out = tmp_path / "candidate.mp3"
    long = ("Krishna walks gently. " * 200) + "\n\n" + ("Devaki prays softly. " * 200)
    with pytest.raises(oa.OpenAITtsError):
        oa.synthesize_openai_tts(
            api_key="k",
            text=long,
            output_path=out,
            model="gpt-4o-mini-tts",
            voice="marin",
            speed=0.92,
            max_input_chars=400,
            work_dir=tmp_path / "chunks",
        )
    assert not out.exists()


def test_pilot_outputs_must_not_target_production_paths() -> None:
    out = ROOT / "output" / "_audio_validation"
    forbidden = [
        ROOT / "output" / "002_devaki-and-vasudeva-wedding" / "narration.mp3",
        ROOT / "output" / "005_prayers-by-the-demigods-for-lord-krishna-in-the-womb" / "narration.mp3",
    ]
    assert out.name == "_audio_validation"
    for path in forbidden:
        assert "_audio_validation" not in str(path)


def test_changed_docs_have_no_stale_seven_file_claims() -> None:
    docs = [
        ROOT / "docs" / "13_OPENAI_TTS_FALLBACK.md",
        ROOT / "docs" / "14_STORY_002_005_REPAIR_BACKLOG.md",
    ]
    for path in docs:
        text = path.read_text(encoding="utf-8").lower()
        assert "seven-file" not in text
        assert "seven file" not in text
        if "13_OPENAI" in path.name:
            assert "eight-file" in text or "eight file" in text or "eight-file" in text.replace(" ", "-")
