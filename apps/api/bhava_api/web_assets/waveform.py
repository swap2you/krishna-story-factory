"""Generate lightweight waveform peaks for story narration without client full-file decode."""
from __future__ import annotations

import json
from pathlib import Path


def peaks_for_mp3_placeholder(path: Path, bars: int = 96) -> list[float]:
    """Deterministic decorative peaks from file bytes when PCM decode is unavailable.

    Avoids bundling a speech model or ffmpeg dependency in the API process.
    """
    data = path.read_bytes()[: 64 * 1024]
    if not data:
        return [0.25] * bars
    peaks: list[float] = []
    block = max(1, len(data) // bars)
    for i in range(bars):
        chunk = data[i * block : (i + 1) * block]
        if not chunk:
            peaks.append(0.2)
            continue
        peaks.append(sum(chunk) / (len(chunk) * 255.0))
    mx = max(peaks) or 0.0001
    return [round(max(0.08, p / mx), 4) for p in peaks]


def write_peaks_json(mp3_path: Path, dest: Path, bars: int = 96) -> dict:
    peaks = peaks_for_mp3_placeholder(mp3_path, bars=bars)
    payload = {
        "bars": bars,
        "method": "byte-energy-preview",
        "confidence": 0.2,
        "note": "Preview peaks only; not sample-accurate. Client must not full-fetch audio for waveform.",
        "peaks": peaks,
    }
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(payload), encoding="utf-8")
    return payload
