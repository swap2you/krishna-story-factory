from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(slots=True)
class WaveformMetrics:
    peak: float
    clipping_ratio: float
    longest_silence_seconds: float
    duration_seconds: float
    status: str
    detail: str = ""
    reasons: tuple[str, ...] = field(default_factory=tuple)


def validate_mp3_waveform(
    path: Path,
    *,
    expected_duration: float | None = None,
    silence_threshold: float = 0.01,
    clip_threshold: float = 0.99,
    max_silence_seconds: float = 2.5,
    max_clipping_ratio: float = 0.005,
    duration_tolerance: float = 0.15,
) -> WaveformMetrics:
    """Decode an MP3 and score peak/clipping/silence. Returns PASS or FAIL with reasons."""
    reasons: list[str] = []
    if not path.exists() or path.stat().st_size == 0:
        return WaveformMetrics(
            peak=0.0,
            clipping_ratio=0.0,
            longest_silence_seconds=0.0,
            duration_seconds=0.0,
            status="FAIL",
            detail="Audio file missing or empty.",
            reasons=("truncated/empty",),
        )

    try:
        import miniaudio
        import numpy as np
    except ImportError as exc:
        return WaveformMetrics(
            peak=0.0,
            clipping_ratio=0.0,
            longest_silence_seconds=0.0,
            duration_seconds=0.0,
            status="FAIL",
            detail=f"Waveform dependencies missing: {exc}",
            reasons=("cannot decode",),
        )

    try:
        info = miniaudio.get_file_info(str(path))
        decoded = miniaudio.decode_file(
            str(path),
            output_format=miniaudio.SampleFormat.FLOAT32,
            nchannels=1,
            sample_rate=int(info.sample_rate) if info.sample_rate else 44100,
        )
    except Exception as exc:
        return WaveformMetrics(
            peak=0.0,
            clipping_ratio=0.0,
            longest_silence_seconds=0.0,
            duration_seconds=0.0,
            status="FAIL",
            detail=f"Cannot decode audio: {type(exc).__name__}: {exc}",
            reasons=("cannot decode",),
        )

    samples = np.asarray(decoded.samples, dtype=np.float64)
    if samples.size == 0:
        return WaveformMetrics(
            peak=0.0,
            clipping_ratio=0.0,
            longest_silence_seconds=0.0,
            duration_seconds=0.0,
            status="FAIL",
            detail="Decoded audio has no samples (truncated/empty).",
            reasons=("truncated/empty",),
        )

    # FLOAT32 path is already in [-1, 1]; tolerate rare int-scaled payloads.
    max_abs = float(np.max(np.abs(samples)))
    if max_abs > 1.5:
        samples = samples / 32768.0
        max_abs = float(np.max(np.abs(samples)))

    nchannels = 1
    sample_rate = int(getattr(decoded, "sample_rate", 0) or getattr(info, "sample_rate", 0) or 44100)
    if sample_rate <= 0:
        reasons.append("invalid sample rate")
        sample_rate = 44100

    frame_count = samples.size // nchannels
    duration_seconds = frame_count / float(sample_rate)
    if duration_seconds <= 0.05:
        reasons.append("truncated/empty")

    peak = float(max_abs)
    clipped = float(np.mean(np.abs(samples) >= clip_threshold)) if samples.size else 0.0
    if clipped > max_clipping_ratio:
        reasons.append(f"clipping_ratio {clipped:.4%} > {max_clipping_ratio:.2%}")

    mono = samples
    silent = np.abs(mono) < silence_threshold
    # Vectorized longest-run of True values (silence).
    padded = np.concatenate(([False], silent.astype(bool), [False]))
    edges = np.diff(padded.astype(np.int8))
    starts = np.where(edges == 1)[0]
    ends = np.where(edges == -1)[0]
    longest_run = int(np.max(ends - starts)) if starts.size else 0
    longest_silence_seconds = longest_run / float(sample_rate)
    if longest_silence_seconds > max_silence_seconds:
        reasons.append(
            f"longest silence {longest_silence_seconds:.2f}s > {max_silence_seconds:.1f}s"
        )

    if expected_duration is not None and expected_duration > 0:
        delta = abs(duration_seconds - expected_duration) / expected_duration
        if delta > duration_tolerance:
            reasons.append(
                f"duration mismatch {duration_seconds:.1f}s vs expected {expected_duration:.1f}s "
                f"({delta:.0%} > {duration_tolerance:.0%})"
            )

    status = "FAIL" if reasons else "PASS"
    detail = "; ".join(reasons) if reasons else "Waveform checks passed."
    return WaveformMetrics(
        peak=round(peak, 6),
        clipping_ratio=round(clipped, 6),
        longest_silence_seconds=round(longest_silence_seconds, 3),
        duration_seconds=round(duration_seconds, 3),
        status=status,
        detail=detail,
        reasons=tuple(reasons),
    )


__all__ = ["WaveformMetrics", "validate_mp3_waveform"]
