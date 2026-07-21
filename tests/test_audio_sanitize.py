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


def test_no_low_credit_compression_path() -> None:
    """Approved narration must not be compressed for OpenAI or production ElevenLabs."""
    import krishna_story_factory.audio.tts as tts

    assert not hasattr(tts, "_to_concise_narration")
