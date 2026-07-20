from __future__ import annotations

import array
from pathlib import Path

import miniaudio

from krishna_story_factory.audio.waveform import validate_mp3_waveform


def _write_wav(path: Path, samples: list[int], *, sample_rate: int = 8000) -> Path:
    pcm = array.array("h", samples)
    sound = miniaudio.DecodedSoundFile(
        path.name, 1, sample_rate, miniaudio.SampleFormat.SIGNED16, pcm
    )
    miniaudio.wav_write_file(str(path), sound)
    return path


def test_tiny_corrupt_file_fails(tmp_path: Path) -> None:
    path = tmp_path / "tiny.mp3"
    path.write_bytes(b"not-an-audio-file")
    metrics = validate_mp3_waveform(path)
    assert metrics.status == "FAIL"
    assert metrics.reasons
    assert any("decode" in reason or "Cannot decode" in metrics.detail for reason in (*metrics.reasons, metrics.detail))


def test_empty_file_fails(tmp_path: Path) -> None:
    path = tmp_path / "empty.mp3"
    path.write_bytes(b"")
    metrics = validate_mp3_waveform(path)
    assert metrics.status == "FAIL"
    assert "truncated/empty" in metrics.reasons or "empty" in metrics.detail.lower()


def test_long_silence_fails(tmp_path: Path) -> None:
    # 3.0 seconds of near-silence at 8 kHz mono
    samples = [0] * (8000 * 3)
    path = _write_wav(tmp_path / "silent.wav", samples)
    metrics = validate_mp3_waveform(path, expected_duration=3.0)
    assert metrics.status == "FAIL"
    assert metrics.longest_silence_seconds > 2.5
    assert any("silence" in reason for reason in metrics.reasons)


def test_clipped_waveform_fails(tmp_path: Path) -> None:
    # Mostly loud clipped signal for 1 second
    samples = [32767 if i % 2 == 0 else -32767 for i in range(8000)]
    path = _write_wav(tmp_path / "clipped.wav", samples)
    metrics = validate_mp3_waveform(path, expected_duration=1.0)
    assert metrics.status == "FAIL"
    assert metrics.clipping_ratio > 0.005
    assert any("clipping" in reason for reason in metrics.reasons)


def test_clean_short_tone_passes(tmp_path: Path) -> None:
    # Soft tone (~0.25 amplitude) for 1 second — no clipping, no long silence
    samples = [int(8000 * ((i % 40) / 40.0 - 0.5)) for i in range(8000)]
    path = _write_wav(tmp_path / "clean.wav", samples)
    metrics = validate_mp3_waveform(path, expected_duration=1.0)
    assert metrics.status == "PASS"
    assert metrics.peak > 0
    assert metrics.clipping_ratio <= 0.005
    assert metrics.longest_silence_seconds <= 2.5
