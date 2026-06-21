from __future__ import annotations

import base64
import logging
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from ..config import Settings

logger = logging.getLogger(__name__)

PORTRAIT_SIZES = ("1024x1536", "1024x1792", "1536x1024", "1792x1024", "1024x1024")
FORBIDDEN_MODELS = {"gpt-image-1", "gpt-image-1-mini"}
EXPLICIT_REPLACEMENT_MODEL = "gpt-image-2"


class ColoringAPIError(RuntimeError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code


@dataclass(slots=True)
class ImageResult:
    model: str
    requested_size: str
    actual_size: str
    quality: str
    reference_used: bool
    reference_path: str
    output_path: Path
    api_error: str = ""
    timestamp: str = ""
    elapsed_seconds: float = 0.0
    api_attempts: int = 0


class ImageClient:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        configured = (settings.openai_image_model or EXPLICIT_REPLACEMENT_MODEL).strip()
        if configured in FORBIDDEN_MODELS:
            self.model = EXPLICIT_REPLACEMENT_MODEL
            self.model_override = f"MODEL_OVERRIDE: {configured} -> {self.model} (configured model is prohibited)"
        else:
            self.model = configured
            self.model_override = ""

    def resolve_portrait_size(self, requested: str | None = None) -> str:
        size = requested or self.settings.openai_image_size or "1024x1536"
        return size if size in PORTRAIT_SIZES else "1024x1536"

    def generate(
        self,
        prompt: str,
        output_path: Path,
        *,
        reference_path: Path | None = None,
        reference_required: bool = False,
        style_reference_path: Path | None = None,
        story_title: str = "",
        max_api_attempts: int = 2,
        requested_size: str | None = None,
    ) -> ImageResult:
        if not self.settings.openai_api_key:
            raise ColoringAPIError("COLORING_API_ERROR", "OPENAI_API_KEY is required for image generation.")
        actual_size = self.resolve_portrait_size(requested_size)
        ref_path = reference_path or self.settings.image_reference_poster or self.settings.image_reference_line_art
        ref_exists = bool(ref_path and ref_path.exists())
        if reference_required and not ref_exists:
            raise ColoringAPIError("COLORING_API_ERROR", f"Required reference image missing: {ref_path}")
        style_exists = bool(style_reference_path and style_reference_path.exists())
        quality = self.settings.openai_image_quality or "high"
        if self.model_override:
            print(self.model_override, flush=True)

        last_error: Exception | None = None
        total_started = time.monotonic()
        for attempt in range(1, max_api_attempts + 1):
            started_at = datetime.now(timezone.utc)
            print("COLORING GENERATION", flush=True)
            print(f"story: {story_title or 'unknown'}", flush=True)
            print(f"attempt: {attempt}/{max_api_attempts}", flush=True)
            print(f"model: {self.model}", flush=True)
            print(f"size: {actual_size}", flush=True)
            print(f"poster reference attached: {'yes' if ref_exists else 'no'}", flush=True)
            print(f"style reference attached: {'yes' if style_exists else 'no'}", flush=True)
            print(f"started: {started_at.isoformat(timespec='seconds')}", flush=True)
            attempt_started = time.monotonic()
            try:
                client = self._fresh_openai_client()
                if ref_exists:
                    self._generate_with_reference(
                        client, prompt, output_path, actual_size, quality, ref_path,
                        style_reference_path if style_exists else None,
                    )
                else:
                    self._generate_text_only(client, prompt, output_path, actual_size, quality)
                elapsed = time.monotonic() - attempt_started
                completed_at = datetime.now(timezone.utc)
                print(f"completed: {completed_at.isoformat(timespec='seconds')}", flush=True)
                print(f"elapsed: {elapsed:.1f}s", flush=True)
                print("result: success", flush=True)
                return ImageResult(
                    model=self.model, requested_size=actual_size, actual_size=actual_size,
                    quality=quality, reference_used=ref_exists,
                    reference_path=str(ref_path) if ref_exists else "", output_path=output_path,
                    api_error=self.model_override,
                    timestamp=completed_at.isoformat(timespec="seconds"),
                    elapsed_seconds=round(time.monotonic() - total_started, 1), api_attempts=attempt,
                )
            except Exception as exc:
                last_error = exc
                elapsed = time.monotonic() - attempt_started
                status = getattr(exc, "status_code", None)
                transient = _is_transient_api_error(exc)
                logger.warning(
                    "Coloring API attempt failed: class=%s status=%s elapsed=%.1fs model=%s size=%s",
                    type(exc).__name__, status if status is not None else "none", elapsed, self.model, actual_size,
                )
                print(f"completed: {datetime.now(timezone.utc).isoformat(timespec='seconds')}", flush=True)
                print(f"elapsed: {elapsed:.1f}s", flush=True)
                print(f"result: {type(exc).__name__} status={status if status is not None else 'none'}", flush=True)
                if not transient or attempt >= max_api_attempts:
                    break
                time.sleep(2.0)

        code = "COLORING_API_TIMEOUT" if _is_timeout_error(last_error) else "COLORING_API_ERROR"
        safe_detail = f"{type(last_error).__name__}: {last_error}" if last_error else "Unknown API failure"
        raise ColoringAPIError(code, safe_detail) from last_error

    def _fresh_openai_client(self):
        import httpx
        from openai import OpenAI

        timeout = httpx.Timeout(connect=30.0, write=60.0, read=360.0, pool=30.0)
        return OpenAI(api_key=self.settings.openai_api_key, timeout=timeout, max_retries=0)

    def _generate_text_only(self, client, prompt: str, output_path: Path, size: str, quality: str) -> None:
        kwargs = {"model": self.model, "prompt": prompt, "size": size, "quality": quality, "n": 1}
        fmt = self.settings.openai_image_format or self.settings.openai_image_output_format or "png"
        try:
            response = client.images.generate(**kwargs, output_format=fmt)
        except TypeError:
            response = client.images.generate(**kwargs)
        self._save_b64(response, output_path)

    def _generate_with_reference(
        self, client, prompt: str, output_path: Path, size: str, quality: str,
        reference_path: Path, style_reference_path: Path | None = None,
    ) -> None:
        edit_prompt = (
            f"{prompt}\n\nREFERENCE PRIORITY: Image 1 is the approved story poster and is authoritative for content, "
            "character identity, approximate age, clothing, role, placement, expression, and story event. "
            "If Image 2 is present, use it only for clean line-art style. Poster content always overrides style reference content. "
            "Do not copy poster color, lighting, or photographic texture."
        )
        with reference_path.open("rb") as content_file:
            if style_reference_path:
                with style_reference_path.open("rb") as style_file:
                    response = client.images.edit(
                        model=self.model, image=[content_file, style_file], prompt=edit_prompt,
                        size=size, quality=quality, n=1,
                    )
            else:
                response = client.images.edit(
                    model=self.model, image=content_file, prompt=edit_prompt,
                    size=size, quality=quality, n=1,
                )
        self._save_b64(response, output_path)

    @staticmethod
    def _save_b64(response, output_path: Path) -> None:
        first = response.data[0]
        b64 = getattr(first, "b64_json", None)
        if not b64:
            raise ColoringAPIError("COLORING_API_ERROR", "OpenAI image response did not include base64 image data.")
        output_path.write_bytes(base64.b64decode(b64))


def _is_timeout_error(exc: Exception | None) -> bool:
    if exc is None:
        return False
    try:
        from openai import APITimeoutError
        import httpx
        return isinstance(exc, (APITimeoutError, httpx.TimeoutException))
    except ImportError:
        return "timeout" in type(exc).__name__.lower()


def _is_transient_api_error(exc: Exception) -> bool:
    try:
        import httpx
        from openai import APIConnectionError, APIStatusError, APITimeoutError
        if isinstance(exc, (APITimeoutError, APIConnectionError, httpx.TransportError)):
            return True
        if isinstance(exc, APIStatusError):
            return exc.status_code in {408, 409, 429} or exc.status_code >= 500
    except ImportError:
        pass
    return False
