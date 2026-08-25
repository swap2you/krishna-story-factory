"""Sample-first orchestration ordering — no paid API calls."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from krishna_story_factory.audio.sample_first_gate import (
    AudioSampleFirstError,
    load_sample_pass,
    validate_sample_pass,
    write_sample_pass,
)
from krishna_story_factory.audio.sample_pipeline import (
    SampleFirstPipelineError,
    build_sample_excerpt,
    run_sample_first,
    validate_sample_waveform,
)
from krishna_story_factory.audio.tts import AudioGenerator
from krishna_story_factory.content.story_tts_equivalence import evaluate_story_tts_equivalence


ROOT = Path(__file__).resolve().parents[1]

NARRATION = (
    "Hare Krishna, dear children and families. "
    "Tonight Krishna and His friends walked into the forests of Vrindavana. "
    '"Come, let us find a good place to eat!" Krishna said with a gentle smile. '
    "The boys laughed and sat in a circle. Soft grass shone under the morning dew. "
    "Then Lord Brahma watched from above, curious about the wonderful boy. "
    "He hid the calves in a secret cave. Krishna searched calmly among the trees. "
    "When the boys also disappeared, Krishna expanded Himself into their forms. "
    "The mothers of Vrindavana felt deeper love for their children. "
    "After a year for them, Brahma returned and saw the same boys playing again. "
    "He offered humble prayers and understood Krishna's loving protection."
)


def _settings():
    from krishna_story_factory.config import load_settings

    return load_settings(ROOT)


def test_sample_excerpt_includes_opening_name_and_dialogue() -> None:
    excerpt = build_sample_excerpt(NARRATION)
    words = excerpt.split()
    assert 90 <= len(words) <= 140
    assert "Krishna" in excerpt or "Brahma" in excerpt
    assert '"' in excerpt or "“" in excerpt
    assert excerpt.lower().startswith("hare krishna")


def test_run_sample_first_writes_pass_before_full_tts(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("AUDIO_SAMPLE_FIRST_REQUIRED", "1")
    settings = _settings()
    gen = AudioGenerator(settings, mode="prod")
    model_id = settings.elevenlabs_model_id or "eleven_v3"
    decision = MagicMock(status="READY", provider="elevenlabs", model_id=model_id, reason="")
    order: list[str] = []

    def fake_sample(self, text, output_path, **_kwargs):
        order.append("sample")
        Path(output_path).write_bytes(b"ID3" + b"\x00" * 2000)
        self.last_provider = "elevenlabs"
        return "elevenlabs"

    def fake_full(self, text, output_path, **_kwargs):
        order.append("full")
        Path(output_path).write_bytes(b"ID3" + b"\x00" * 4000)
        self.last_provider = "elevenlabs"
        return "elevenlabs"

    monkeypatch.setattr(AudioGenerator, "_synthesize_elevenlabs", fake_sample)
    monkeypatch.setattr(
        "krishna_story_factory.audio.sample_pipeline.validate_sample_waveform",
        lambda path, **_k: __import__(
            "krishna_story_factory.audio.sample_pipeline", fromlist=["SampleQaResult"]
        ).SampleQaResult(
            status="PASS",
            duration_seconds=52.0,
            peak=0.4,
            clipping_ratio=0.0,
            longest_silence_seconds=0.2,
            detail="stub PASS",
        ),
    )

    result = run_sample_first(
        audio_gen=gen,
        narration_text=NARRATION,
        work_dir=tmp_path,
        provider_decision=decision,
        mode="prod",
        project_root=settings.project_root,
    )
    assert result is not None
    assert result.pass_path.is_file()
    assert order == ["sample"]

    # Full TTS now allowed exactly once with same binding.
    monkeypatch.setattr(AudioGenerator, "_synthesize_elevenlabs", fake_full)
    out = tmp_path / "narration.mp3"
    provider = gen.generate_mp3(NARRATION, out, provider_decision=decision, work_dir=tmp_path)
    assert provider == "elevenlabs"
    assert order == ["sample", "full"]


def test_missing_sample_blocks_full_tts(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("AUDIO_SAMPLE_FIRST_REQUIRED", "1")
    settings = _settings()
    gen = AudioGenerator(settings, mode="prod")
    decision = MagicMock(status="READY", provider="elevenlabs", model_id="eleven_v3", reason="")
    called = {"n": 0}

    def boom(*_a, **_k):
        called["n"] += 1
        raise AssertionError("must not synthesize")

    monkeypatch.setattr(AudioGenerator, "_synthesize_elevenlabs", boom)
    with pytest.raises(AudioSampleFirstError):
        gen.generate_mp3(NARRATION, tmp_path / "n.mp3", provider_decision=decision, work_dir=tmp_path)
    assert called["n"] == 0


def test_stale_sample_blocks_full_tts(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("AUDIO_SAMPLE_FIRST_REQUIRED", "1")
    settings = _settings()
    gen = AudioGenerator(settings, mode="prod")
    model_id = settings.elevenlabs_model_id or "eleven_v3"
    voice = settings.elevenlabs_voice_id or "Itr6exdQTrvjpW1lNztS"
    write_sample_pass(
        tmp_path,
        provider="elevenlabs",
        model=model_id,
        voice=voice,
        settings=gen._voice_settings(model_id),
        narration_text="old narration text",
        sample_duration_seconds=50.0,
    )
    decision = MagicMock(status="READY", provider="elevenlabs", model_id=model_id, reason="")
    with pytest.raises(AudioSampleFirstError, match="narration_source_sha"):
        gen.generate_mp3(NARRATION, tmp_path / "n.mp3", provider_decision=decision, work_dir=tmp_path)


@pytest.mark.parametrize(
    "mutate",
    ["voice", "model", "settings", "text"],
)
def test_binding_change_invalidates_sample(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, mutate: str
) -> None:
    monkeypatch.setenv("AUDIO_SAMPLE_FIRST_REQUIRED", "1")
    settings = _settings()
    gen = AudioGenerator(settings, mode="prod")
    model_id = settings.elevenlabs_model_id or "eleven_v3"
    voice = settings.elevenlabs_voice_id or "Itr6exdQTrvjpW1lNztS"
    voice_settings = gen._voice_settings(model_id)
    from krishna_story_factory.audio.sample_pipeline import prepare_narration_text

    prepared = prepare_narration_text(
        NARRATION, project_root=settings.project_root, model_id=model_id
    )
    write_sample_pass(
        tmp_path,
        provider="elevenlabs",
        model=model_id,
        voice=voice,
        settings=voice_settings,
        narration_text=prepared,
        sample_duration_seconds=50.0,
    )
    check_provider = "elevenlabs"
    check_model = model_id
    check_voice = voice
    check_settings = dict(voice_settings)
    check_text = prepared
    if mutate == "voice":
        check_voice = "other-voice"
    elif mutate == "model":
        check_model = "other-model"
    elif mutate == "settings":
        check_settings = {**voice_settings, "stability": 0.99}
    else:
        check_text = prepared + " changed ending."
    errors = validate_sample_pass(
        load_sample_pass(tmp_path),
        narration_text=check_text,
        provider=check_provider,
        model=check_model,
        voice=check_voice,
        settings=check_settings,
    )
    assert errors


def test_sample_qa_failure_blocks_pass_write(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("AUDIO_SAMPLE_FIRST_REQUIRED", "1")
    settings = _settings()
    gen = AudioGenerator(settings, mode="prod")
    decision = MagicMock(status="READY", provider="elevenlabs", model_id="eleven_v3", reason="")

    def fake_el(self, text, output_path):
        Path(output_path).write_bytes(b"ID3" + b"\x00" * 500)
        return "elevenlabs"

    monkeypatch.setattr(AudioGenerator, "_synthesize_elevenlabs", fake_el)
    monkeypatch.setattr(
        "krishna_story_factory.audio.sample_pipeline.validate_sample_waveform",
        lambda path, **_k: __import__(
            "krishna_story_factory.audio.sample_pipeline", fromlist=["SampleQaResult"]
        ).SampleQaResult(
            status="FAIL",
            duration_seconds=12.0,
            peak=0.1,
            clipping_ratio=0.0,
            longest_silence_seconds=0.0,
            reasons=("sample duration 12.0s < 45s",),
            detail="sample duration 12.0s < 45s",
        ),
    )
    with pytest.raises(SampleFirstPipelineError, match="Sample QA FAILED"):
        run_sample_first(
            audio_gen=gen,
            narration_text=NARRATION,
            work_dir=tmp_path,
            provider_decision=decision,
            mode="prod",
            project_root=settings.project_root,
            allow_one_retry=False,
        )
    assert load_sample_pass(tmp_path) is None


def test_story_021_legacy_independent_audio_fails_exact_gate() -> None:
    """Independent rewritten Audio Narration must FAIL exact-canonical gate."""
    from krishna_story_factory.content.canonical_narration import (
        extract_main_story,
        sync_audio_narration_from_main_story,
    )

    story = ROOT / "tests/fixtures/story_021/story.md"
    text = story.read_text(encoding="utf-8")
    main = extract_main_story(text)
    # Simulate the original defect: independent unpunctuated oral rewrite.
    legacy_audio = (
        "Hare Krishna dear children Tonight Brahmā tested Kṛṣṇa while the boys "
        "played near the calves under the trees and then Kṛṣṇa expanded Himself."
    )
    legacy = evaluate_story_tts_equivalence(
        story_md=text,
        tts_source=legacy_audio,
        require_exact_canonical=True,
    )
    assert legacy.status == "FAIL", legacy.notes

    synced = sync_audio_narration_from_main_story(text)
    repaired = evaluate_story_tts_equivalence(
        story_md=synced,
        tts_source=extract_main_story(synced) or main,
        require_exact_canonical=True,
    )
    assert repaired.status == "PASS", repaired.notes


def test_public_story_max_is_035() -> None:
    import json

    pin = json.loads((ROOT / "deploy/content/RELEASE_CONTENT.json").read_text(encoding="utf-8"))
    assert int(pin["public_story_max"]) == 35
    assert str(pin["tag"]).startswith("bhava-content-001-035-")
    sitemap = (ROOT / "apps/web/app/sitemap.ts").read_text(encoding="utf-8")
    assert "PUBLIC_STORY_MAX" in sitemap
