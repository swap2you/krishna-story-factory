"""OpenAI TTS provider with precise error classification and lossless chunking."""
from __future__ import annotations

import hashlib
import logging
import random
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .assemble import assemble_mp3_chunks, sha256_bytes
from .chunking import ChunkPlan, chunk_narration

logger = logging.getLogger(__name__)

DEFAULT_OPENAI_TTS_MODEL = "gpt-4o-mini-tts-2025-12-15"
FALLBACK_OPENAI_TTS_MODELS = ("gpt-4o-mini-tts", "tts-1-hd")

# Terminal statuses for callers
BLOCKED_OPENAI_TTS_QUOTA = "BLOCKED_OPENAI_TTS_QUOTA"
BLOCKED_OPENAI_TTS_AUTH = "BLOCKED_OPENAI_TTS_AUTH"
BLOCKED_OPENAI_TTS_BILLING = "BLOCKED_OPENAI_TTS_BILLING"

BEDTIME_INSTRUCTIONS = (
    "Narrate as a warm, calm, natural bedtime storyteller speaking to children "
    "ages six to twelve. Sound devotional, reassuring and human, not theatrical "
    "or promotional. Use clear emotional expression and a gentle pace. Pronounce "
    "Indian and Vaishnava names carefully using the normalized pronunciation guide. "
    "Pause naturally between paragraphs. Do not rush lists. "
    "End the prayer and next-story preview softly.\n\n"
    "Pronunciation guide:\n"
    "Hare Krishna = huh-ray KRISH-nuh\n"
    "Krishna = KRISH-nuh\n"
    "Devaki = day-vuh-KEE\n"
    "Vasudeva = vuh-soo-DAY-vuh\n"
    "Kamsa = KUM-suh\n"
    "Narada = NAA-ruh-duh\n"
    "Brahma = BRUH-maa\n"
    "Shiva = SHEE-vuh\n"
    "Mathura = muh-TOO-ruh\n"
    "Vishnu = VISH-noo"
)

INSTRUCTIONS_SHA256 = hashlib.sha256(BEDTIME_INSTRUCTIONS.encode("utf-8")).hexdigest()

NO_RETRY_CLASSES = frozenset(
    {
        "authentication_invalid_key",
        "insufficient_quota",
        "billing_payment_failure",
        "invalid_request",
        "input_limit",
    }
)


@dataclass(slots=True)
class OpenAITtsResult:
    provider: str
    model_id: str
    voice: str
    speed: float
    response_format: str
    request_id: str
    audio_bytes: bytes
    used_instructions: bool
    error_class: str = ""
    chunk_count: int = 1
    chunk_plan: ChunkPlan | None = None
    chunk_metadata: list[dict[str, Any]] = field(default_factory=list)
    blocked_status: str = ""


class OpenAITtsError(RuntimeError):
    def __init__(
        self,
        message: str,
        *,
        error_class: str = "unknown",
        blocked_status: str = "",
        retryable: bool = False,
    ) -> None:
        super().__init__(message)
        self.error_class = error_class
        self.blocked_status = blocked_status
        self.retryable = retryable


def classify_openai_error(exc: BaseException) -> str:
    """Classify OpenAI TTS failures into distinct actionable classes."""
    text = str(exc).lower()
    name = type(exc).__name__.lower()
    status = getattr(exc, "status_code", None)
    if status is None:
        response = getattr(exc, "response", None)
        status = getattr(response, "status_code", None)
    code = ""
    body = getattr(exc, "body", None)
    if isinstance(body, dict):
        err = body.get("error") or {}
        if isinstance(err, dict):
            code = str(err.get("code") or err.get("type") or "").lower()
            text = f"{text} {err.get('message', '')}".lower()

    if status == 401 or "invalid_api_key" in text or "authentication" in name or code in {
        "invalid_api_key",
        "authentication_error",
    }:
        return "authentication_invalid_key"
    if code == "insufficient_quota" or "insufficient_quota" in text:
        return "insufficient_quota"
    if status == 402 or "payment_required" in text or "billing_hard_limit" in text or (
        "billing" in text and "payment" in text
    ):
        return "billing_payment_failure"
    if status == 429 or "rate_limit" in text or code in {"rate_limit_exceeded", "rate_limit_error"}:
        # Prefer quota when both markers appear with insufficient_quota code already handled.
        if "quota" in text and "insufficient" in text:
            return "insufficient_quota"
        return "rate_limit"
    if status == 404 or ("model" in text and ("not found" in text or "does not exist" in text or "access" in text)):
        return "model_access"
    if "maximum context" in text or "input too long" in text or "max_input" in text or "too many characters" in text:
        return "input_limit"
    if status == 400 or "invalid_request" in text or code == "invalid_request_error":
        return "invalid_request"
    if "timeout" in text or "timed out" in text:
        return "timeout"
    if "connection" in text or "network" in text or "temporarily unavailable" in text:
        return "network"
    if status is not None and int(status) >= 500:
        return "server_error"
    return "unknown"


def blocked_status_for(error_class: str) -> str:
    if error_class == "insufficient_quota":
        return BLOCKED_OPENAI_TTS_QUOTA
    if error_class == "authentication_invalid_key":
        return BLOCKED_OPENAI_TTS_AUTH
    if error_class == "billing_payment_failure":
        return BLOCKED_OPENAI_TTS_BILLING
    return ""


def _retry_after_seconds(exc: BaseException, attempt: int) -> float:
    response = getattr(exc, "response", None)
    headers = getattr(response, "headers", None) or {}
    raw = headers.get("retry-after") or headers.get("Retry-After")
    if raw:
        try:
            return max(0.5, float(raw))
        except ValueError:
            pass
    base = min(20.0, (2**attempt) * 0.75)
    return base + random.uniform(0.05, 0.45)


def synthesize_openai_speech_once(
    *,
    api_key: str,
    text: str,
    model: str,
    voice: str,
    speed: float,
    response_format: str = "mp3",
    max_retries: int = 3,
) -> tuple[bytes, str, str]:
    """Single-request OpenAI speech synthesis with bounded retries for retryable errors."""
    if not api_key:
        raise OpenAITtsError(
            "OPENAI_API_KEY is required for OpenAI TTS.",
            error_class="authentication_invalid_key",
            blocked_status=BLOCKED_OPENAI_TTS_AUTH,
        )

    from openai import OpenAI

    client = OpenAI(api_key=api_key)
    used_instructions = "tts-1" not in model
    kwargs: dict[str, Any] = {
        "model": model,
        "voice": voice,
        "input": text,
        "response_format": response_format,
        "speed": speed,
    }
    if used_instructions:
        kwargs["instructions"] = BEDTIME_INSTRUCTIONS

    last_exc: BaseException | None = None
    for attempt in range(max_retries + 1):
        try:
            response = client.audio.speech.create(**kwargs)
            audio_bytes = response.content if hasattr(response, "content") else bytes(response.read())
            request_id = ""
            headers = getattr(response, "response", None)
            if headers is not None and getattr(headers, "headers", None):
                request_id = headers.headers.get("x-request-id") or headers.headers.get("request-id") or ""
            return audio_bytes, request_id, model
        except Exception as exc:  # noqa: BLE001
            last_exc = exc
            error_class = classify_openai_error(exc)
            blocked = blocked_status_for(error_class)
            retryable = error_class in {"rate_limit", "network", "timeout", "server_error"}
            if error_class in NO_RETRY_CLASSES or not retryable or attempt >= max_retries:
                raise OpenAITtsError(
                    str(exc),
                    error_class=error_class,
                    blocked_status=blocked,
                    retryable=False,
                ) from exc
            delay = _retry_after_seconds(exc, attempt)
            logger.warning(
                "OpenAI TTS retryable error (%s) attempt %s; sleeping %.2fs",
                error_class,
                attempt + 1,
                delay,
            )
            time.sleep(delay)

    assert last_exc is not None
    raise OpenAITtsError(str(last_exc), error_class=classify_openai_error(last_exc)) from last_exc


def synthesize_openai_tts(
    *,
    api_key: str,
    text: str,
    output_path: Path,
    model: str,
    voice: str,
    speed: float,
    response_format: str = "mp3",
    max_input_chars: int = 3600,
    allow_model_fallback: bool = True,
    work_dir: Path | None = None,
    pause_ms: int = 280,
) -> OpenAITtsResult:
    """Lossless chunked OpenAI TTS with atomic final write."""
    plan = chunk_narration(text, max_input_chars=max_input_chars)
    candidates = [model]
    if allow_model_fallback:
        for item in FALLBACK_OPENAI_TTS_MODELS:
            if item not in candidates:
                candidates.append(item)

    output_path = Path(output_path)
    base_work = Path(work_dir) if work_dir else output_path.parent / f".{output_path.stem}_chunks"
    if base_work.exists():
        # Keep diagnostics; clear previous chunk mp3s for this run.
        for stale in base_work.glob("chunk_*.mp3"):
            try:
                stale.unlink()
            except OSError:
                pass
    base_work.mkdir(parents=True, exist_ok=True)

    last_error: OpenAITtsError | None = None
    for candidate in candidates:
        chunk_paths: list[Path] = []
        chunk_meta: list[dict[str, Any]] = []
        try:
            for chunk in plan.chunks:
                chunk_path = base_work / f"chunk_{chunk.sequence:03d}.mp3"
                audio_bytes, request_id, used_model = synthesize_openai_speech_once(
                    api_key=api_key,
                    text=chunk.text,
                    model=candidate,
                    voice=voice,
                    speed=speed,
                    response_format=response_format,
                )
                chunk_path.write_bytes(audio_bytes)
                chunk_paths.append(chunk_path)
                chunk_meta.append(
                    {
                        "sequence": chunk.sequence,
                        "char_count": chunk.char_count,
                        "word_count": chunk.word_count,
                        "text_sha256": chunk.text_sha256,
                        "boundary": chunk.boundary,
                        "model_id": used_model,
                        "voice": voice,
                        "speed": speed,
                        "response_format": response_format,
                        "request_id": request_id,
                        "api_error_class": "",
                        "audio_sha256": sha256_bytes(audio_bytes),
                        "byte_size": len(audio_bytes),
                    }
                )

            assemble_mp3_chunks(chunk_paths, output_path, pause_ms=pause_ms)
            final_bytes = output_path.read_bytes()
            return OpenAITtsResult(
                provider="openai",
                model_id=chunk_meta[0]["model_id"] if chunk_meta else candidate,
                voice=voice,
                speed=speed,
                response_format=response_format,
                request_id=chunk_meta[0].get("request_id", "") if chunk_meta else "",
                audio_bytes=final_bytes,
                used_instructions="tts-1" not in candidate,
                chunk_count=len(chunk_paths),
                chunk_plan=plan,
                chunk_metadata=chunk_meta,
            )
        except OpenAITtsError as exc:
            last_error = exc
            # Quarantine incomplete assembly — never leave a partial final candidate.
            partial = output_path.with_suffix(output_path.suffix + ".partial")
            for path in (output_path, partial):
                try:
                    path.unlink(missing_ok=True)
                except OSError:
                    pass
            for path in chunk_paths:
                try:
                    # Keep chunk diagnostics under work_dir; mark failed metadata.
                    pass
                except OSError:
                    pass
            logger.warning(
                "OpenAI TTS model %s failed (%s): %s",
                candidate,
                exc.error_class,
                type(exc).__name__,
            )
            if exc.error_class in {"authentication_invalid_key", "insufficient_quota", "billing_payment_failure"}:
                raise
            if exc.error_class != "model_access":
                raise
            continue

    assert last_error is not None
    raise last_error


def preflight_openai_tts(*, api_key: str, model: str, voice: str, speed: float) -> dict[str, Any]:
    """One minimal speech request to validate key/model/voice access."""
    import tempfile

    tmp = Path(tempfile.gettempdir()) / "krishna_openai_tts_preflight.mp3"
    try:
        result = synthesize_openai_tts(
            api_key=api_key,
            text="Hare Krishna.",
            output_path=tmp,
            model=model,
            voice=voice,
            speed=speed,
            response_format="mp3",
            max_input_chars=3600,
            allow_model_fallback=True,
            work_dir=Path(tempfile.gettempdir()) / "krishna_openai_tts_preflight_chunks",
            pause_ms=0,
        )
        size = tmp.stat().st_size if tmp.exists() else 0
        return {
            "ok": size > 200,
            "provider": "openai",
            "model_id": result.model_id,
            "voice": result.voice,
            "request_id": result.request_id,
            "bytes": size,
            "error_class": "",
            "blocked_status": "",
        }
    except OpenAITtsError as exc:
        return {
            "ok": False,
            "provider": "openai",
            "model_id": model,
            "voice": voice,
            "request_id": "",
            "bytes": 0,
            "error_class": exc.error_class,
            "blocked_status": exc.blocked_status,
            "detail": str(exc)[:300],
        }
    finally:
        try:
            tmp.unlink(missing_ok=True)
        except OSError:
            pass
