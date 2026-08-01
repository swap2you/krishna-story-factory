"""Sample-first TTS gate (Phase 7 / Phase 9 scaffolding).

Governed audio sequence requires a short sample (45–60s) with the exact intended
provider/voice/model/settings to pass QA before full narration synthesis.

When ``AUDIO_SAMPLE_FIRST_REQUIRED=true``, full narration synthesis must not
proceed unless a validated sample-pass artifact is present. Default is **off**
so the existing production path is unchanged mid-release.

TODO (wire before enabling in production):
  - Synthesize a 45–60s sample with locked voice settings
  - Validate voice, pace, pauses, pronunciation, transcript agreement, endings,
    bedtime quality, and devotional mood
  - Persist a durable pass record (e.g. work/.../audio_sample_pass.json)
  - Only then allow full narration; fail closed on missing/failed sample
"""
from __future__ import annotations

import os
from pathlib import Path


class AudioSampleFirstError(RuntimeError):
    """Raised when sample-first is required but full TTS is not yet allowed."""


SAMPLE_PASS_FILENAME = "audio_sample_pass.json"


def sample_first_required() -> bool:
    return os.getenv("AUDIO_SAMPLE_FIRST_REQUIRED", "").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }


def sample_pass_path(work_dir: Path | None) -> Path | None:
    if work_dir is None:
        return None
    return Path(work_dir) / SAMPLE_PASS_FILENAME


def assert_full_tts_allowed(*, work_dir: Path | None = None) -> None:
    """Fail closed when sample-first is enabled and no sample pass exists.

    Default (env unset / false): no-op so current prod runs are unaffected.
    """
    if not sample_first_required():
        return
    path = sample_pass_path(work_dir)
    if path is None or not path.is_file() or path.stat().st_size < 1:
        raise AudioSampleFirstError(
            "AUDIO_SAMPLE_FIRST_REQUIRED=true but no validated sample pass was "
            f"recorded (expected {SAMPLE_PASS_FILENAME} under the run work dir). "
            "Full narration synthesis is blocked until sample QA passes. "
            "See krishna_story_factory/audio/sample_first_gate.py."
        )
