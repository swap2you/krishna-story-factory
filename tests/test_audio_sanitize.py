from __future__ import annotations

from krishna_story_factory.audio.sanitize import sanitize_audio_script


def test_audio_sanitizer_removes_pause_brackets() -> None:
    raw = "Hare Krishna. [pause] Tonight we hear the story. [Pause] Sweet dreams."
    cleaned = sanitize_audio_script(raw, model_id="eleven_multilingual_v2")
    assert "[pause]" not in cleaned.lower()
    assert "pause" not in cleaned.lower()
    assert "<break" not in cleaned.lower()


def test_audio_sanitizer_strips_break_tags() -> None:
    raw = 'Hello <break time="1.5s" /> world.'
    cleaned = sanitize_audio_script(raw, model_id="eleven_multilingual_v2")
    assert "<break" not in cleaned.lower()
    assert "Hello" in cleaned and "world" in cleaned


def test_non_v3_mode_strips_unsupported_bracket_tags() -> None:
    raw = "Hare Krishna. [with wonder] Listen softly. [unknown tag]"
    cleaned = sanitize_audio_script(raw, model_id="eleven_multilingual_v2")
    assert "[with wonder]" not in cleaned
    assert "[unknown tag]" not in cleaned


def test_v3_mode_preserves_only_conservative_tags() -> None:
    raw = "Hare Krishna. [softly] [warmly] [gently] [reassuringly] Listen [with wonder] to the story."
    cleaned = sanitize_audio_script(raw, model_id="eleven_v3")
    assert "[softly]" in cleaned
    assert "[warmly]" in cleaned
    assert "[gently]" in cleaned
    assert "[reassuringly]" in cleaned
    assert "[with wonder]" not in cleaned


def test_low_credit_mode_shortens_narration_without_placeholder() -> None:
    from krishna_story_factory.audio.tts import _to_concise_narration

    long = " ".join([f"Sentence {i} about Vasudeva keeping his word carefully." for i in range(120)])
    concise = _to_concise_narration(long, target_min=420, target_max=560)
    words = concise.split()
    assert 420 <= len(words) <= 560
    assert "placeholder" not in concise.lower()
    assert "Vasudeva" in concise
