"""Bedtime pace and punctuation gate regressions."""
from __future__ import annotations

from krishna_story_factory.audio.pace import evaluate_pace_qa
from krishna_story_factory.audio.punctuation_gate import evaluate_punctuation_gate


def test_measured_wpm_over_150_fails() -> None:
    # 150 words in 50s => 180 WPM
    text = " ".join(["Krishna"] * 150)
    result = evaluate_pace_qa(narration_text=text, duration_seconds=50.0)
    assert result.status == "FAIL"
    assert result.measured_wpm > 150


def test_bedtime_pace_passes() -> None:
    # 130 words in 60s => 130 WPM
    text = " ".join(["Krishna"] * 130)
    result = evaluate_pace_qa(narration_text=text, duration_seconds=60.0)
    assert result.status == "PASS"
    assert 115 <= result.measured_wpm <= 150


def test_punctuation_density_failure_for_run_on() -> None:
    run_on = " ".join(["Krishna smiled at the boys and calves in Vrindavana"] * 40)
    result = evaluate_punctuation_gate(run_on)
    assert result.status == "FAIL"


def test_punctuation_ok_for_normal_prose() -> None:
    prose = (
        "Kṛṣṇa led the boys into the forest. Brahmā hid the calves in a cave. "
        "Kṛṣṇa expanded Himself into every missing boy and calf. "
        "Brahmā saw the Viṣṇu forms and offered humble prayers. "
        "The parents felt deeper love for their children."
    )
    result = evaluate_punctuation_gate(prose)
    assert result.status == "PASS"


def test_joined_sentences_fail() -> None:
    joined = "Kṛṣṇa smiled.Brahmā watched from above."
    result = evaluate_punctuation_gate(joined)
    assert result.status == "FAIL"
    assert any("concatenated" in f for f in result.failures)
