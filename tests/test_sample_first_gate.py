"""Unit tests for fail-closed sample-first TTS gate (Phase 9) — no paid API calls."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from krishna_story_factory.audio.drift import narration_source_sha
from krishna_story_factory.audio.sample_first_gate import (
    SAMPLE_PASS_FILENAME,
    AudioSampleFirstError,
    assert_full_tts_allowed,
    compute_settings_hash,
    load_sample_pass,
    sample_first_required,
    validate_sample_pass,
    write_sample_pass,
)
from krishna_story_factory.audio.tts import AudioGenerationError, AudioGenerator


NARRATION = "Hare Krishna. Soft bedtime story about baby Krishna in Gokula."
SETTINGS = {"stability": 0.42, "similarity_boost": 0.78, "style": 0.25, "use_speaker_boost": True}


def _write_valid_pass(tmp_path: Path, *, text: str = NARRATION, settings: dict | None = None) -> Path:
    return write_sample_pass(
        tmp_path,
        provider="elevenlabs",
        model="eleven_v3",
        voice="Itr6exdQTrvjpW1lNztS",
        settings=settings if settings is not None else SETTINGS,
        narration_text=text,
        sample_duration_seconds=55.0,
    )


def test_sample_first_default_on(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("AUDIO_SAMPLE_FIRST_REQUIRED", raising=False)
    assert sample_first_required() is True


def test_sample_first_explicit_opt_out(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AUDIO_SAMPLE_FIRST_REQUIRED", "0")
    assert sample_first_required() is False
    assert_full_tts_allowed(work_dir=None)  # no-op when opted out


@pytest.mark.parametrize("value", ["false", "no", "off", "FALSE"])
def test_sample_first_falsy_opt_out(monkeypatch: pytest.MonkeyPatch, value: str) -> None:
    monkeypatch.setenv("AUDIO_SAMPLE_FIRST_REQUIRED", value)
    assert sample_first_required() is False


def test_sample_first_fails_closed_without_pass(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("AUDIO_SAMPLE_FIRST_REQUIRED", "true")
    assert sample_first_required() is True
    with pytest.raises(AudioSampleFirstError, match="no validated sample pass"):
        assert_full_tts_allowed(
            work_dir=tmp_path,
            narration_text=NARRATION,
            provider="elevenlabs",
            model="eleven_v3",
            voice="Itr6exdQTrvjpW1lNztS",
            settings=SETTINGS,
        )


def test_sample_first_fails_without_work_dir(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AUDIO_SAMPLE_FIRST_REQUIRED", "1")
    with pytest.raises(AudioSampleFirstError, match="work_dir"):
        assert_full_tts_allowed(
            work_dir=None,
            narration_text=NARRATION,
            provider="elevenlabs",
            model="eleven_v3",
            voice="Itr6exdQTrvjpW1lNztS",
            settings=SETTINGS,
        )


def test_sample_first_allows_with_bound_pass(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("AUDIO_SAMPLE_FIRST_REQUIRED", "1")
    _write_valid_pass(tmp_path)
    assert_full_tts_allowed(
        work_dir=tmp_path,
        narration_text=NARRATION,
        provider="elevenlabs",
        model="eleven_v3",
        voice="Itr6exdQTrvjpW1lNztS",
        settings=SETTINGS,
    )


def test_pass_artifact_binds_hashes(tmp_path: Path) -> None:
    path = _write_valid_pass(tmp_path)
    record = load_sample_pass(tmp_path)
    assert record is not None
    assert path.name == SAMPLE_PASS_FILENAME
    assert record["status"] == "PASS"
    assert record["provider"] == "elevenlabs"
    assert record["model"] == "eleven_v3"
    assert record["voice"] == "Itr6exdQTrvjpW1lNztS"
    assert record["settings_hash"] == compute_settings_hash(SETTINGS)
    assert record["narration_source_sha"] == narration_source_sha(NARRATION)


def test_text_change_invalidates_pass(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("AUDIO_SAMPLE_FIRST_REQUIRED", "1")
    _write_valid_pass(tmp_path)
    with pytest.raises(AudioSampleFirstError, match="narration_source_sha"):
        assert_full_tts_allowed(
            work_dir=tmp_path,
            narration_text=NARRATION + " Extra sentence.",
            provider="elevenlabs",
            model="eleven_v3",
            voice="Itr6exdQTrvjpW1lNztS",
            settings=SETTINGS,
        )


def test_settings_change_invalidates_pass(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("AUDIO_SAMPLE_FIRST_REQUIRED", "1")
    _write_valid_pass(tmp_path)
    changed = dict(SETTINGS)
    changed["stability"] = 0.99
    with pytest.raises(AudioSampleFirstError, match="settings_hash"):
        assert_full_tts_allowed(
            work_dir=tmp_path,
            narration_text=NARRATION,
            provider="elevenlabs",
            model="eleven_v3",
            voice="Itr6exdQTrvjpW1lNztS",
            settings=changed,
        )


def test_voice_change_invalidates_pass(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("AUDIO_SAMPLE_FIRST_REQUIRED", "1")
    _write_valid_pass(tmp_path)
    with pytest.raises(AudioSampleFirstError, match="voice mismatch"):
        assert_full_tts_allowed(
            work_dir=tmp_path,
            narration_text=NARRATION,
            provider="elevenlabs",
            model="eleven_v3",
            voice="different-voice-id",
            settings=SETTINGS,
        )


def test_non_pass_status_rejected(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("AUDIO_SAMPLE_FIRST_REQUIRED", "1")
    (tmp_path / SAMPLE_PASS_FILENAME).write_text(
        '{"status":"FAIL","provider":"elevenlabs","model":"eleven_v3",'
        '"voice":"Itr6exdQTrvjpW1lNztS","settings_hash":"X","narration_source_sha":"Y"}',
        encoding="utf-8",
    )
    with pytest.raises(AudioSampleFirstError, match="status"):
        assert_full_tts_allowed(
            work_dir=tmp_path,
            narration_text=NARRATION,
            provider="elevenlabs",
            model="eleven_v3",
            voice="Itr6exdQTrvjpW1lNztS",
            settings=SETTINGS,
        )


def test_validate_sample_pass_reports_multiple_mismatches() -> None:
    record = {
        "status": "PASS",
        "provider": "openai",
        "model": "other",
        "voice": "other",
        "settings_hash": "AAAA",
        "narration_source_sha": "BBBB",
    }
    errors = validate_sample_pass(
        record,
        narration_text=NARRATION,
        provider="elevenlabs",
        model="eleven_v3",
        voice="Itr6exdQTrvjpW1lNztS",
        settings=SETTINGS,
    )
    assert any("provider" in e for e in errors)
    assert any("model" in e for e in errors)
    assert any("voice" in e for e in errors)
    assert any("settings_hash" in e for e in errors)
    assert any("narration_source_sha" in e for e in errors)


def test_generate_mp3_blocked_without_pass(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Full TTS path must not call paid synth when sample pass is missing."""
    monkeypatch.setenv("AUDIO_SAMPLE_FIRST_REQUIRED", "1")
    from krishna_story_factory.config import load_settings

    root = Path(__file__).resolve().parents[1]
    settings = load_settings(root)
    gen = AudioGenerator(settings, mode="prod")
    decision = MagicMock(status="READY", provider="elevenlabs", model_id="eleven_v3", reason="")
    out = tmp_path / "narration.mp3"

    called = {"el": 0, "oa": 0}

    def fail_if_called(*_a, **_k):
        called["el"] += 1
        raise AssertionError("paid ElevenLabs path must not run without sample pass")

    def fail_openai(*_a, **_k):
        called["oa"] += 1
        raise AssertionError("paid OpenAI path must not run without sample pass")

    monkeypatch.setattr(AudioGenerator, "_synthesize_elevenlabs", fail_if_called)
    monkeypatch.setattr(AudioGenerator, "_synthesize_openai", fail_openai)

    with pytest.raises(AudioSampleFirstError):
        gen.generate_mp3(NARRATION, out, provider_decision=decision, work_dir=tmp_path)
    assert called["el"] == 0
    assert called["oa"] == 0
    assert not out.exists() or out.stat().st_size == 0


def test_generate_mp3_allows_with_valid_pass_fixture(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("AUDIO_SAMPLE_FIRST_REQUIRED", "1")
    from krishna_story_factory.config import load_settings

    root = Path(__file__).resolve().parents[1]
    settings = load_settings(root)
    gen = AudioGenerator(settings, mode="prod")

    # Bind pass to the exact settings AudioGenerator will use for ElevenLabs.
    model_id = settings.elevenlabs_model_id or "eleven_v3"
    voice = settings.elevenlabs_voice_id or "Itr6exdQTrvjpW1lNztS"
    voice_settings = gen._voice_settings(model_id)
    # Narration text after normalize+sanitize may differ; write pass after probing normalize.
    from krishna_story_factory.audio.pronunciation import normalize_for_tts
    from krishna_story_factory.audio.sanitize import sanitize_audio_script

    normalized = normalize_for_tts(NARRATION, project_root=settings.project_root)
    narration_text = sanitize_audio_script(normalized.audio_text, model_id=settings.elevenlabs_model_id)
    write_sample_pass(
        tmp_path,
        provider="elevenlabs",
        model=model_id,
        voice=voice,
        settings=voice_settings,
        narration_text=narration_text,
        sample_duration_seconds=50.0,
    )

    decision = MagicMock(status="READY", provider="elevenlabs", model_id=model_id, reason="")
    out = tmp_path / "narration.mp3"
    calls = {"el": 0}

    def fake_el(self, text, output_path, *, work_dir=None):
        calls["el"] += 1
        Path(output_path).write_bytes(b"1234567890" * 20)
        self.last_provider = "elevenlabs"
        self.last_model_id = model_id
        self.last_voice_id = voice
        return "elevenlabs"

    monkeypatch.setattr(AudioGenerator, "_synthesize_elevenlabs", fake_el)
    provider = gen.generate_mp3(NARRATION, out, provider_decision=decision, work_dir=tmp_path)
    assert provider == "elevenlabs"
    assert calls["el"] == 1
    assert out.exists() and out.stat().st_size > 50


def test_generate_mp3_test_mode_bypasses_gate(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Test mode must never call paid APIs and skips sample-first (placeholder)."""
    monkeypatch.delenv("AUDIO_SAMPLE_FIRST_REQUIRED", raising=False)  # default on
    from krishna_story_factory.config import load_settings

    settings = load_settings(Path(__file__).resolve().parents[1])
    gen = AudioGenerator(settings, mode="test")
    out = tmp_path / "narration.mp3"
    provider = gen.generate_mp3(NARRATION, out, work_dir=None)
    assert provider == "placeholder"
    assert out.exists()


def test_web_assets_ui_gate_defaults_with_sample_first(monkeypatch: pytest.MonkeyPatch) -> None:
    from krishna_story_factory.pipeline import (
        _assert_web_assets_ui_contract,
        _web_assets_ui_gate_required,
    )

    monkeypatch.delenv("BHAVA_WEB_ASSETS_UI_GATE", raising=False)
    monkeypatch.delenv("AUDIO_SAMPLE_FIRST_REQUIRED", raising=False)
    assert _web_assets_ui_gate_required() is True

    monkeypatch.setenv("AUDIO_SAMPLE_FIRST_REQUIRED", "0")
    assert _web_assets_ui_gate_required() is False

    monkeypatch.setenv("BHAVA_WEB_ASSETS_UI_GATE", "1")
    assert _web_assets_ui_gate_required() is True

    monkeypatch.setenv("BHAVA_WEB_ASSETS_UI_GATE", "0")
    monkeypatch.delenv("AUDIO_SAMPLE_FIRST_REQUIRED", raising=False)
    assert _web_assets_ui_gate_required() is False


def test_web_assets_ui_contract_fail_closed(tmp_path: Path) -> None:
    from krishna_story_factory.pipeline import PipelineError, _assert_web_assets_ui_contract

    with pytest.raises(PipelineError, match="fail-closed before Drive"):
        _assert_web_assets_ui_contract(tmp_path / "missing", "021")

    web = tmp_path / "001"
    web.mkdir()
    (web / "reader.md").write_text("x", encoding="utf-8")
    with pytest.raises(PipelineError, match="missing"):
        _assert_web_assets_ui_contract(web, "001")


def test_web_assets_ui_contract_accepts_complete_fixture(tmp_path: Path) -> None:
    from krishna_story_factory.pipeline import _assert_web_assets_ui_contract

    web = tmp_path / "001"
    web.mkdir()
    for name in (
        "reader.md",
        "reader.txt",
        "source_links.json",
        "reflections.json",
        "shlokas.json",
        "sync.json",
        "waveform.json",
        "web_manifest.json",
    ):
        if name.endswith(".json"):
            if name == "web_manifest.json":
                (web / name).write_text('{"assets":{"reader.md":{"bytes":1}}}', encoding="utf-8")
            else:
                (web / name).write_text("{}", encoding="utf-8")
        else:
            (web / name).write_text("ok", encoding="utf-8")
    _assert_web_assets_ui_contract(web, "001")


def test_fallback_requires_openai_sample_pass(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """ElevenLabs→OpenAI fallback must re-check sample-first for the OpenAI binding."""
    monkeypatch.setenv("AUDIO_SAMPLE_FIRST_REQUIRED", "1")
    from krishna_story_factory.config import load_settings
    from krishna_story_factory.audio.pronunciation import normalize_for_tts
    from krishna_story_factory.audio.sanitize import sanitize_audio_script

    from dataclasses import replace

    settings = replace(
        load_settings(Path(__file__).resolve().parents[1]),
        audio_provider_mode="auto",
        audio_provider_fallback="openai",
    )
    gen = AudioGenerator(settings, mode="prod")
    model_id = settings.elevenlabs_model_id or "eleven_v3"
    voice = settings.elevenlabs_voice_id or "Itr6exdQTrvjpW1lNztS"
    normalized = normalize_for_tts(NARRATION, project_root=settings.project_root)
    narration_text = sanitize_audio_script(normalized.audio_text, model_id=settings.elevenlabs_model_id)
    write_sample_pass(
        tmp_path,
        provider="elevenlabs",
        model=model_id,
        voice=voice,
        settings=gen._voice_settings(model_id),
        narration_text=narration_text,
    )

    decision = MagicMock(status="READY", provider="elevenlabs", model_id=model_id, reason="")
    out = tmp_path / "narration.mp3"

    def fail_el(*_a, **_k):
        raise AudioGenerationError("ElevenLabs TTS failed: 429 insufficient quota")

    monkeypatch.setattr(AudioGenerator, "_synthesize_elevenlabs", fail_el)
    monkeypatch.setattr(
        "krishna_story_factory.audio.provider.preflight_openai",
        lambda _s: {"ok": True, "model_id": "gpt-4o-mini-tts-2025-12-15", "voice": "marin"},
    )
    monkeypatch.setattr(
        "krishna_story_factory.audio.provider.invalidate_elevenlabs_cache",
        lambda **_k: None,
    )

    openai_calls = {"n": 0}

    def fake_openai(self, *a, **k):
        openai_calls["n"] += 1
        return "openai"

    monkeypatch.setattr(AudioGenerator, "_synthesize_openai", fake_openai)

    with pytest.raises(AudioSampleFirstError, match="provider mismatch|no validated sample pass|Sample-first"):
        gen.generate_mp3(NARRATION, out, provider_decision=decision, work_dir=tmp_path)
    assert openai_calls["n"] == 0
