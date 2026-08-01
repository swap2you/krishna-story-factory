"""Unit tests for sample-first TTS gate scaffolding."""
from __future__ import annotations

from pathlib import Path

import pytest

from krishna_story_factory.audio.sample_first_gate import (
    AudioSampleFirstError,
    assert_full_tts_allowed,
    sample_first_required,
)


def test_sample_first_default_off(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("AUDIO_SAMPLE_FIRST_REQUIRED", raising=False)
    assert sample_first_required() is False
    assert_full_tts_allowed(work_dir=None)  # no-op


def test_sample_first_fails_closed_without_pass(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("AUDIO_SAMPLE_FIRST_REQUIRED", "true")
    assert sample_first_required() is True
    with pytest.raises(AudioSampleFirstError):
        assert_full_tts_allowed(work_dir=tmp_path)


def test_sample_first_allows_with_pass_file(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("AUDIO_SAMPLE_FIRST_REQUIRED", "1")
    (tmp_path / "audio_sample_pass.json").write_text('{"status":"PASS"}', encoding="utf-8")
    assert_full_tts_allowed(work_dir=tmp_path)
