from __future__ import annotations

import base64
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from ..config import Settings

logger = logging.getLogger(__name__)

PORTRAIT_SIZES = ("1024x1536", "1024x1792", "1536x1024", "1792x1024", "1024x1024")
FORBIDDEN_MODELS = {"gpt-image-1"}
FALLBACK_MODEL = "gpt-image-1.5"


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


class ImageClient:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._resolved_model: str | None = None
        self._model_fallback_reason = ""

    @property
    def model(self) -> str:
        if self._resolved_model:
            return self._resolved_model
        preferred = (self.settings.openai_image_model or "gpt-image-2").strip()
        if preferred in FORBIDDEN_MODELS:
            preferred = "gpt-image-2"
        self._resolved_model = preferred
        return preferred

    def resolve_portrait_size(self, requested: str | None = None) -> str:
        size = requested or self.settings.openai_image_size or "1024x1536"
        if size in PORTRAIT_SIZES:
            return size
        return "1024x1536"

    def generate(
        self,
        prompt: str,
        output_path: Path,
        *,
        reference_path: Path | None = None,
        reference_required: bool = False,
    ) -> ImageResult:
        if not self.settings.openai_api_key:
            raise RuntimeError("OPENAI_API_KEY is required for image generation.")
        actual_size = self.resolve_portrait_size()
        ref_path = reference_path
        if ref_path is None:
            ref_path = self.settings.image_reference_poster or self.settings.image_reference_line_art
        ref_exists = bool(ref_path and ref_path.exists())
        if reference_required and not ref_exists:
            raise RuntimeError(f"Required reference image missing: {ref_path}")
        reference_used = ref_exists
        quality = self.settings.openai_image_quality or "high"
        from openai import OpenAI

        client = OpenAI(api_key=self.settings.openai_api_key)
        model = self._pick_model(client)
        api_error = ""
        try:
            if reference_used:
                self._generate_with_reference(client, model, prompt, output_path, actual_size, quality, ref_path)
            else:
                self._generate_text_only(client, model, prompt, output_path, actual_size, quality)
        except Exception as exc:
            api_error = f"{type(exc).__name__}: {exc}"
            if model != FALLBACK_MODEL and "gpt-image-2" in model:
                logger.warning("gpt-image-2 failed (%s); trying %s", type(exc).__name__, FALLBACK_MODEL)
                model = FALLBACK_MODEL
                self._resolved_model = FALLBACK_MODEL
                self._model_fallback_reason = api_error
                if reference_used:
                    self._generate_with_reference(client, model, prompt, output_path, actual_size, quality, ref_path)
                else:
                    self._generate_text_only(client, model, prompt, output_path, actual_size, quality)
            else:
                raise
        if reference_used and not ref_path.exists():
            raise RuntimeError("Reference image claimed but file missing.")
        return ImageResult(
            model=model,
            requested_size=actual_size,
            actual_size=actual_size,
            quality=quality,
            reference_used=reference_used,
            reference_path=str(ref_path) if reference_used else "",
            output_path=output_path,
            api_error=self._model_fallback_reason,
            timestamp=datetime.now(timezone.utc).isoformat(timespec="seconds"),
        )

    def _pick_model(self, client) -> str:
        preferred = self.model
        if preferred in FORBIDDEN_MODELS:
            preferred = "gpt-image-2"
        try:
            models = client.models.list()
            available = {m.id for m in models.data}
            if preferred in available:
                self._resolved_model = preferred
                return preferred
            if "gpt-image-2" in available:
                self._resolved_model = "gpt-image-2"
                return "gpt-image-2"
            if FALLBACK_MODEL in available:
                logger.warning("gpt-image-2 unavailable; using explicit fallback %s", FALLBACK_MODEL)
                self._resolved_model = FALLBACK_MODEL
                return FALLBACK_MODEL
        except Exception as exc:
            logger.warning("Could not list image models (%s); attempting %s", type(exc).__name__, preferred)
        self._resolved_model = preferred
        return preferred

    def _generate_text_only(self, client, model: str, prompt: str, output_path: Path, size: str, quality: str) -> None:
        kwargs = {"model": model, "prompt": prompt, "size": size, "quality": quality, "n": 1}
        fmt = self.settings.openai_image_format or self.settings.openai_image_output_format or "png"
        try:
            response = client.images.generate(**kwargs, output_format=fmt)
        except TypeError:
            response = client.images.generate(**kwargs)
        self._save_b64(response, output_path)

    def _generate_with_reference(
        self, client, model: str, prompt: str, output_path: Path, size: str, quality: str, reference_path: Path
    ) -> None:
        style_prompt = (
            f"{prompt}\n\nUse the reference image ONLY for visual language, expression quality, composition richness, "
            "and professional finish. The current story scene above must override reference characters and events."
        )
        with reference_path.open("rb") as ref_file:
            response = client.images.edit(model=model, image=ref_file, prompt=style_prompt, size=size, n=1)
        self._save_b64(response, output_path)

    @staticmethod
    def _save_b64(response, output_path: Path) -> None:
        first = response.data[0]
        b64 = getattr(first, "b64_json", None)
        if not b64:
            raise RuntimeError("OpenAI image response did not include base64 image data.")
        output_path.write_bytes(base64.b64decode(b64))
