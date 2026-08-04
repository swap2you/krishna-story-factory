"""Measured bedtime narration pace (spoken WPM) gates."""
from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

_WORD_RE = re.compile(r"[A-Za-z0-9\u0100-\u024F\u1E00-\u1EFF']+")

# Children's bedtime narration standard (measured, not estimated).
MIN_WPM_HARD = 105.0
MIN_WPM_ACCEPT = 115.0
MAX_WPM_ACCEPT = 150.0
PREFERRED_WPM_LOW = 130.0
PREFERRED_WPM_HIGH = 140.0


@dataclass(frozen=True)
class PaceQaResult:
    status: str
    spoken_word_count: int
    duration_seconds: float
    measured_wpm: float
    min_wpm: float
    max_wpm: float
    preferred_band: str
    detail: str
    human_listening_status: str = "HUMAN_REVIEW_PENDING"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def count_spoken_words(text: str) -> int:
    return len(_WORD_RE.findall(text or ""))


def measured_wpm(*, word_count: int, duration_seconds: float) -> float:
    if duration_seconds <= 0:
        return 0.0
    return (word_count * 60.0) / float(duration_seconds)


def expected_duration_window(word_count: int) -> tuple[float, float]:
    """Seconds window implied by accept WPM band (with small tolerance)."""
    if word_count <= 0:
        return 180.0, 360.0
    # max duration at slowest acceptable pace; min at fastest
    max_seconds = (word_count * 60.0) / MIN_WPM_ACCEPT
    min_seconds = (word_count * 60.0) / MAX_WPM_ACCEPT
    # Tolerances for leading/trailing silence and decoder variance.
    return max(60.0, min_seconds * 0.95), max_seconds * 1.05


def evaluate_pace_qa(
    *,
    narration_text: str,
    duration_seconds: float,
    allow_below_accept_floor: bool = False,
) -> PaceQaResult:
    words = count_spoken_words(narration_text)
    wpm = measured_wpm(word_count=words, duration_seconds=duration_seconds)
    failures: list[str] = []
    if duration_seconds <= 0:
        failures.append("non-positive duration")
    if words <= 0:
        failures.append("empty spoken word count")
    if wpm > MAX_WPM_ACCEPT + 0.5:
        failures.append(f"measured WPM {wpm:.1f} > {MAX_WPM_ACCEPT:.0f} (too fast for bedtime)")
    if wpm < MIN_WPM_HARD:
        failures.append(f"measured WPM {wpm:.1f} < {MIN_WPM_HARD:.0f} (excessively slow)")
    elif wpm < MIN_WPM_ACCEPT and not allow_below_accept_floor:
        failures.append(
            f"measured WPM {wpm:.1f} < {MIN_WPM_ACCEPT:.0f} (below bedtime accept band)"
        )
    status = "PASS" if not failures else "FAIL"
    return PaceQaResult(
        status=status,
        spoken_word_count=words,
        duration_seconds=round(float(duration_seconds), 3),
        measured_wpm=round(wpm, 2),
        min_wpm=MIN_WPM_ACCEPT,
        max_wpm=MAX_WPM_ACCEPT,
        preferred_band=f"{PREFERRED_WPM_LOW:.0f}-{PREFERRED_WPM_HIGH:.0f}",
        detail="; ".join(failures) if failures else (
            f"Measured {wpm:.1f} WPM within bedtime band "
            f"{MIN_WPM_ACCEPT:.0f}-{MAX_WPM_ACCEPT:.0f}."
        ),
        human_listening_status="HUMAN_REVIEW_PENDING",
    )


def write_audio_quality_qa(payload: dict[str, Any], path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


__all__ = [
    "MAX_WPM_ACCEPT",
    "MIN_WPM_ACCEPT",
    "MIN_WPM_HARD",
    "PaceQaResult",
    "count_spoken_words",
    "evaluate_pace_qa",
    "expected_duration_window",
    "measured_wpm",
    "write_audio_quality_qa",
]
