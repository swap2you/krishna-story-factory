"""Sample-first TTS orchestration (create-next / Story 021+).

Required order before full narration:
1. resolve canonical narration text
2. compute narration_source_sha
3. resolve provider/model/voice/settings
4. generate one short sample (45–60s)
5. validate sample objectively
6. write bound audio_sample_pass.json via write_sample_pass
7. validate the pass
8. caller may then invoke full generate_mp3 exactly once
"""
from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping

from .drift import narration_source_sha
from .pronunciation import normalize_for_tts
from .sample_first_gate import (
    SAMPLE_PASS_FILENAME,
    AudioSampleFirstError,
    build_tts_settings_binding,
    load_sample_pass,
    sample_first_required,
    validate_sample_pass,
    write_sample_pass,
)
from .sanitize import sanitize_audio_script
from .waveform import WaveformMetrics, validate_mp3_waveform

logger = logging.getLogger(__name__)

SAMPLE_MIN_SECONDS = 45.0
SAMPLE_MAX_SECONDS = 60.0
# Bedtime WPM band used to size the excerpt (~50s target).
_TARGET_SAMPLE_SECONDS = 52.0
_BEDTIME_WPM = 130.0
_WORDS_PER_SECOND = _BEDTIME_WPM / 60.0
_TARGET_WORDS = int(_TARGET_SAMPLE_SECONDS * _WORDS_PER_SECOND)  # ~112
_MAX_SAMPLE_RETRIES = 1  # one initial + one corrected retry


class SampleFirstPipelineError(RuntimeError):
    """Raised when sample generation or sample QA fails closed."""


@dataclass(slots=True)
class SampleQaResult:
    status: str
    duration_seconds: float
    peak: float
    clipping_ratio: float
    longest_silence_seconds: float
    reasons: tuple[str, ...] = ()
    detail: str = ""
    human_listening_status: str = "NOT_CLAIMED"

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "duration_seconds": self.duration_seconds,
            "peak": self.peak,
            "clipping_ratio": self.clipping_ratio,
            "longest_silence_seconds": self.longest_silence_seconds,
            "reasons": list(self.reasons),
            "detail": self.detail,
            "human_listening_status": self.human_listening_status,
        }


@dataclass(slots=True)
class SampleFirstResult:
    pass_path: Path
    sample_path: Path
    sample_text: str
    narration_source_sha: str
    binding: dict[str, Any]
    qa: SampleQaResult
    retry_count: int = 0
    report_path: Path | None = None


def estimate_spoken_seconds(text: str, *, wpm: float = _BEDTIME_WPM) -> float:
    words = len((text or "").split())
    if words <= 0 or wpm <= 0:
        return 0.0
    return words / (wpm / 60.0)


def build_sample_excerpt(
    narration_text: str,
    *,
    target_words: int = _TARGET_WORDS,
    min_words: int = 90,
    max_words: int = 140,
) -> str:
    """Build a representative 45–60s excerpt from canonical narration.

    Prefer opening narration, include at least one likely name token, ordinary
    descriptive sentence, dialogue when present, and sentence/paragraph transitions.
    """
    text = (narration_text or "").strip()
    if not text:
        raise SampleFirstPipelineError("Cannot build sample excerpt from empty narration text.")

    # Split into paragraphs then sentences for controlled inclusion.
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    if not paragraphs:
        paragraphs = [text]

    sentences: list[str] = []
    for para in paragraphs:
        parts = re.split(r"(?<=[.!?])\s+", para.strip())
        sentences.extend(s.strip() for s in parts if s.strip())
    if not sentences:
        sentences = [text]

    selected: list[str] = []
    word_count = 0
    has_dialogue = False
    has_name = False
    name_hint = re.compile(
        r"\b(Kṛṣṇa|Krishna|Balarāma|Balarama|Yaśodā|Yashoda|Brahmā|Brahma|"
        r"Vṛndāvana|Vrindavana|Viṣṇu|Vishnu|Nanda|Rāma|Rama)\b",
        re.I,
    )

    for idx, sentence in enumerate(sentences):
        selected.append(sentence)
        word_count += len(sentence.split())
        if '"' in sentence or "'" in sentence or "“" in sentence or "”" in sentence:
            has_dialogue = True
        if name_hint.search(sentence):
            has_name = True
        # Ensure we cross at least one paragraph boundary when available.
        if word_count >= min_words and idx > 0:
            # Prefer including a bit more until target if dialogue/name still missing.
            if (has_dialogue and has_name) or word_count >= target_words:
                break
        if word_count >= max_words:
            break

    # If dialogue exists later in the story and we missed it, append one dialogue sentence.
    if not has_dialogue:
        for sentence in sentences[len(selected) :]:
            if '"' in sentence or "“" in sentence:
                selected.append(sentence)
                has_dialogue = True
                break

    excerpt = " ".join(selected).strip()
    if len(excerpt.split()) < 40:
        raise SampleFirstPipelineError(
            f"Sample excerpt too short ({len(excerpt.split())} words); narration may be incomplete."
        )
    return excerpt


def validate_sample_waveform(
    sample_path: Path,
    *,
    min_seconds: float = SAMPLE_MIN_SECONDS,
    max_seconds: float = SAMPLE_MAX_SECONDS,
) -> SampleQaResult:
    """Objective sample QA — does not claim human listening approval."""
    metrics: WaveformMetrics = validate_mp3_waveform(
        sample_path,
        max_silence_seconds=3.0,
        max_clipping_ratio=0.01,
    )
    reasons = list(metrics.reasons)
    duration = float(metrics.duration_seconds or 0.0)
    if duration < min_seconds:
        reasons.append(f"sample duration {duration:.1f}s < {min_seconds:.0f}s")
    if duration > max_seconds:
        reasons.append(f"sample duration {duration:.1f}s > {max_seconds:.0f}s")
    if metrics.peak < 0.05:
        reasons.append(f"peak too low ({metrics.peak:.4f}) — possible silence/volume defect")
    if metrics.peak > 0.999:
        reasons.append("peak near full-scale — possible distortion/loudness jump")

    status = "FAIL" if reasons else "PASS"
    detail = "; ".join(reasons) if reasons else "Objective sample waveform checks passed."
    return SampleQaResult(
        status=status,
        duration_seconds=duration,
        peak=metrics.peak,
        clipping_ratio=metrics.clipping_ratio,
        longest_silence_seconds=metrics.longest_silence_seconds,
        reasons=tuple(reasons),
        detail=detail,
        human_listening_status="NOT_CLAIMED",
    )


def prepare_narration_text(raw_audio_script: str, *, project_root: Path, model_id: str) -> str:
    """Normalize + sanitize narration the same way full TTS will."""
    normalized = normalize_for_tts(raw_audio_script, project_root=project_root)
    return sanitize_audio_script(normalized.audio_text, model_id=model_id)


def run_sample_first(
    *,
    audio_gen: Any,
    narration_text: str,
    work_dir: Path,
    provider_decision: Any | None,
    mode: str,
    project_root: Path,
    allow_one_retry: bool = True,
) -> SampleFirstResult | None:
    """Generate sample, QA, and write bound pass — or no-op when sample-first is opted out / test mode.

    ``narration_text`` must be the canonical full narration body that full TTS will use
    (already normalized/sanitized preferred; will re-normalize for binding SHA consistency).
    """
    if mode == "test":
        # Test mode never calls paid APIs; write a synthetic bound pass so generate_mp3 gate passes.
        if not sample_first_required():
            return None
        binding = audio_gen._intended_tts_binding("placeholder")
        # Use elevenlabs-shaped binding for gate when provider not selected in test.
        prepared = prepare_narration_text(
            narration_text,
            project_root=project_root,
            model_id=getattr(audio_gen.settings, "elevenlabs_model_id", "") or "eleven_v3",
        )
        # Test mode generate_mp3 bypasses the gate entirely — still write pass for durability tests.
        pass_path = write_sample_pass(
            work_dir,
            provider="placeholder",
            model="test",
            voice="test",
            settings={"mode": "test"},
            narration_text=prepared,
            sample_duration_seconds=50.0,
            extra={"qa": {"status": "PASS", "human_listening_status": "NOT_CLAIMED", "mode": "test"}},
        )
        return SampleFirstResult(
            pass_path=pass_path,
            sample_path=work_dir / "narration_sample.mp3",
            sample_text="",
            narration_source_sha=narration_source_sha(prepared),
            binding={"provider": "placeholder", "model": "test", "voice": "test", "settings_hash": ""},
            qa=SampleQaResult(
                status="PASS",
                duration_seconds=50.0,
                peak=0.0,
                clipping_ratio=0.0,
                longest_silence_seconds=0.0,
                detail="test-mode synthetic sample pass",
            ),
            retry_count=0,
        )

    if not sample_first_required():
        return None

    work = Path(work_dir)
    work.mkdir(parents=True, exist_ok=True)

    decision = provider_decision
    provider = ((decision.provider if decision else "") or "").strip().lower()
    if not provider:
        raise SampleFirstPipelineError("No audio provider selected for sample-first synthesis.")
    if decision is not None and getattr(decision, "status", "READY") != "READY":
        raise SampleFirstPipelineError(f"{decision.status}: {decision.reason}")

    model_id = (decision.model_id if decision else "") or (
        audio_gen.settings.elevenlabs_model_id if provider == "elevenlabs" else audio_gen.settings.openai_tts_model
    )
    prepared = prepare_narration_text(
        narration_text,
        project_root=project_root,
        model_id=str(model_id or ""),
    )
    intended = audio_gen._intended_tts_binding(provider, model=str(model_id or "") or None)
    binding = build_tts_settings_binding(
        provider=intended["provider"],
        model=intended["model"],
        voice=intended["voice"],
        settings=intended["settings"],
    )
    source_sha = narration_source_sha(prepared)

    # Reuse durable pass when still valid for this binding/text.
    existing = load_sample_pass(work)
    if existing:
        errors = validate_sample_pass(
            existing,
            narration_text=prepared,
            provider=binding["provider"],
            model=binding["model"],
            voice=binding["voice"],
            settings=binding["settings"],
        )
        if not errors:
            logger.info("Reusing valid audio_sample_pass.json under %s", work)
            qa = SampleQaResult(
                status="PASS",
                duration_seconds=float(existing.get("sample_duration_seconds") or 0.0),
                peak=0.0,
                clipping_ratio=0.0,
                longest_silence_seconds=0.0,
                detail="Reused existing bound sample PASS",
                human_listening_status=str(
                    (existing.get("qa") or {}).get("human_listening_status") or "NOT_CLAIMED"
                ),
            )
            return SampleFirstResult(
                pass_path=work / SAMPLE_PASS_FILENAME,
                sample_path=work / "narration_sample.mp3",
                sample_text=str(existing.get("sample_text") or ""),
                narration_source_sha=source_sha,
                binding=binding,
                qa=qa,
                retry_count=0,
            )

    excerpt = build_sample_excerpt(prepared)
    sample_path = work / "narration_sample.mp3"
    retry_count = 0
    last_qa: SampleQaResult | None = None

    while True:
        _synthesize_sample(audio_gen, prepared_excerpt=excerpt, output_path=sample_path, provider=provider, model=str(model_id or "") or None)
        qa = validate_sample_waveform(sample_path)
        last_qa = qa
        if qa.status == "PASS":
            break
        # One corrected retry only for concrete setting/duration sizing defects.
        duration_defect = any("duration" in r for r in qa.reasons)
        if allow_one_retry and retry_count < _MAX_SAMPLE_RETRIES and duration_defect:
            retry_count += 1
            words = len(excerpt.split())
            if any("< 45" in r or "< 45.0" in r or " < 45" in r for r in qa.reasons):
                excerpt = build_sample_excerpt(prepared, target_words=min(140, words + 25), min_words=words + 10)
            else:
                excerpt = build_sample_excerpt(prepared, target_words=max(90, words - 20), max_words=max(100, words - 10))
            logger.warning("Sample QA failed (%s); retrying once with adjusted excerpt.", qa.detail)
            continue
        raise SampleFirstPipelineError(
            "Sample QA FAILED — full TTS blocked: " + (qa.detail or "; ".join(qa.reasons))
        )

    assert last_qa is not None
    pass_path = write_sample_pass(
        work,
        provider=binding["provider"],
        model=binding["model"],
        voice=binding["voice"],
        settings=binding["settings"],
        narration_text=prepared,
        sample_duration_seconds=last_qa.duration_seconds,
        extra={
            "qa": last_qa.to_dict(),
            "sample_text_sha": narration_source_sha(excerpt),
            "sample_word_count": len(excerpt.split()),
            "retry_count": retry_count,
        },
    )
    # Confirm binding validates.
    record = load_sample_pass(work)
    errors = validate_sample_pass(
        record,
        narration_text=prepared,
        provider=binding["provider"],
        model=binding["model"],
        voice=binding["voice"],
        settings=binding["settings"],
    )
    if errors:
        raise SampleFirstPipelineError("Wrote sample pass but validation failed: " + " | ".join(errors))

    report = {
        "status": "PASS",
        "provider": binding["provider"],
        "model": binding["model"],
        "voice": binding["voice"],
        "settings_hash": binding["settings_hash"],
        "narration_source_sha": source_sha,
        "sample_duration_seconds": last_qa.duration_seconds,
        "retry_count": retry_count,
        "qa": last_qa.to_dict(),
        "pass_file": SAMPLE_PASS_FILENAME,
    }
    report_path = work / "sample_first_report.json"
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    return SampleFirstResult(
        pass_path=pass_path,
        sample_path=sample_path,
        sample_text=excerpt,
        narration_source_sha=source_sha,
        binding=binding,
        qa=last_qa,
        retry_count=retry_count,
        report_path=report_path,
    )


def _synthesize_sample(
    audio_gen: Any,
    *,
    prepared_excerpt: str,
    output_path: Path,
    provider: str,
    model: str | None,
) -> None:
    """Synthesize sample using the same provider path as full TTS, bypassing the full-TTS gate."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if provider == "openai":
        audio_gen._synthesize_openai(
            prepared_excerpt,
            output_path,
            work_dir=output_path.parent,
            model=model,
            allow_model_fallback=not bool(model),
        )
        return
    if provider == "elevenlabs":
        audio_gen._synthesize_elevenlabs(prepared_excerpt, output_path)
        return
    raise SampleFirstPipelineError(f"Unsupported sample provider: {provider!r}")


def sample_pass_work_dir(run_root: Path | None, fallback: Path) -> Path:
    """Prefer durable recovery run root for the sample pass artifact."""
    if run_root is not None:
        return Path(run_root)
    return Path(fallback)


__all__ = [
    "SAMPLE_MIN_SECONDS",
    "SAMPLE_MAX_SECONDS",
    "SampleFirstPipelineError",
    "SampleFirstResult",
    "SampleQaResult",
    "build_sample_excerpt",
    "estimate_spoken_seconds",
    "prepare_narration_text",
    "run_sample_first",
    "sample_pass_work_dir",
    "validate_sample_waveform",
]
