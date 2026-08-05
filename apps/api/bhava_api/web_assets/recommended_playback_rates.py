"""Temporary recommended playback rates for Stories 001–022.

Derived from local narration metrics (no paid API calls). Target bedtime pace
is ~150 WPM (AUDIO_NARRATION_STANDARD hard-fail band starts above 165 WPM).
Stories at or below the band keep 1.0; faster retained 011–020 narrations
recommend 0.75 while preserving pitch and user speed control.
Story 021 uses marin @ 0.92 synthesis, so player rate stays 1.0.
"""
from __future__ import annotations

# Story -> recommended HTMLAudioElement.playbackRate (player snaps to SPEEDS).
RECOMMENDED_PLAYBACK_RATES: dict[str, float] = {
    "001": 1.0,
    "002": 1.0,
    "003": 1.0,
    "004": 1.0,
    "005": 1.0,
    "006": 1.0,
    "007": 1.0,
    "008": 1.0,
    "009": 1.0,
    "010": 1.0,
    # Faster retained narrations (measured WPM > 165 against ~150 target).
    "011": 0.75,
    "012": 1.0,
    "013": 1.0,
    "014": 0.75,
    "015": 1.0,
    "016": 0.75,
    "017": 1.0,
    "018": 0.75,
    "019": 0.75,
    "020": 0.75,
    # 021/022 bedtime target uses marin @ ~0.90 synthesis; keep player at 1.0.
    "021": 1.0,
    "022": 1.0,
}


def recommended_playback_rate_for_story(story_no: str) -> float:
    padded = (story_no or "").strip().zfill(3)
    return float(RECOMMENDED_PLAYBACK_RATES.get(padded, 1.0))
