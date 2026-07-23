"""Narration-to-text alignment stub for Bhāva follow-along.

Real alignment requires either a forced-alignment tool (e.g. Whisper with
word-level timestamps) or manually reviewed timings from a devotee reviewer.
This module provides the contract so the pipeline can emit honest
``needs_alignment`` status files without fabricating timings.
"""
from __future__ import annotations

from typing import Any


def align_sentences(
    reader_sentences: list[str],
    narration_txt: str,
    duration_sec: float,
) -> dict[str, Any]:
    """Return alignment cues or an honest ``needs_alignment`` status.

    Parameters
    ----------
    reader_sentences:
        Ordered list of sentences extracted from the reader markdown.
    narration_txt:
        Narration-ready text (may differ from reader text due to
        pronunciation guides, pauses, etc.).
    duration_sec:
        Total narration audio duration in seconds.

    Returns
    -------
    dict
        A sync-cue payload conforming to ``sync.schema.json``.
        Until a real aligner is wired in, every call returns
        ``status: "needs_alignment"`` with an empty cues list.
    """
    return {
        "status": "needs_alignment",
        "method": "none",
        "confidence": 0,
        "duration_sec": round(duration_sec, 2),
        "cues": [],
    }
