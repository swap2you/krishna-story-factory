from __future__ import annotations

import base64
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from ..config import Settings

logger = logging.getLogger(__name__)

PORTRAIT_SIZES = ("1024x1536", "1536x1024", "1024x1792", "1792x1024", "1024x1024")


@dataclass(slots=True)
class ImageGenerationRecord:
    model: str
    requested_size: str
    actual_size: str
    quality: str
    reference_used: bool
    output_path: Path
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat(timespec="seconds"))


class OpenAIImageClient:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    @property
    def model(self) -> str:
        preferred = self.settings.openai_image_model
        if preferred:
            return preferred
        return "gpt-image-1"

    def resolve_portrait_size(self, requested: str) -> str:
        if requested in PORTRAIT_SIZES:
            return requested
        if "x" in requested:
            w, h = requested.split("x", 1)
            try:
                if int(h) >= int(w):
                    return requested
            except ValueError:
                pass
        for candidate in ("1024x1536", "1024x1792", "1024x1024"):
            if candidate != requested:
                logger.warning("Requested size %s not supported; using %s", requested, candidate)
                return candidate
        return "1024x1536"

    def generate(
        self,
        prompt: str,
        output_path: Path,
        *,
        size: str,
        reference_path: Path | None = None,
    ) -> ImageGenerationRecord:
        if not self.settings.openai_api_key:
            raise RuntimeError("OPENAI_API_KEY is required for image generation.")
        actual_size = self.resolve_portrait_size(size)
        reference_used = bool(reference_path and reference_path.exists())
        from openai import OpenAI

        client = OpenAI(api_key=self.settings.openai_api_key)
        quality = self.settings.openai_image_quality or "high"
        output_format = self.settings.openai_image_output_format or "png"

        if reference_used:
            self._generate_with_reference(client, prompt, output_path, actual_size, quality, reference_path)
        else:
            self._generate_text_only(client, prompt, output_path, actual_size, quality, output_format)

        return ImageGenerationRecord(
            model=self.model,
            requested_size=size,
            actual_size=actual_size,
            quality=quality,
            reference_used=reference_used,
            output_path=output_path,
        )

    def _generate_text_only(self, client, prompt: str, output_path: Path, size: str, quality: str, output_format: str) -> None:
        kwargs = {
            "model": self.model,
            "prompt": prompt,
            "size": size,
            "quality": quality,
            "n": 1,
        }
        try:
            response = client.images.generate(**kwargs, output_format=output_format)
        except TypeError:
            response = client.images.generate(**kwargs)
        self._save_b64(response, output_path)

    def _generate_with_reference(
        self,
        client,
        prompt: str,
        output_path: Path,
        size: str,
        quality: str,
        reference_path: Path,
    ) -> None:
        style_prompt = (
            f"{prompt}\n\nUse the reference image only for visual language, line confidence, lighting, "
            "and composition quality. The current story scene above must override reference characters, "
            "events, title, and quotation."
        )
        try:
            with reference_path.open("rb") as ref_file:
                response = client.images.edit(
                    model=self.model,
                    image=ref_file,
                    prompt=style_prompt,
                    size=size,
                    n=1,
                )
            self._save_b64(response, output_path)
            return
        except Exception as exc:
            logger.warning("Reference image edit failed (%s); falling back to text-only generation.", type(exc).__name__)
        self._generate_text_only(client, style_prompt, output_path, size, quality, self.settings.openai_image_output_format or "png")

    @staticmethod
    def _save_b64(response, output_path: Path) -> None:
        first = response.data[0]
        b64 = getattr(first, "b64_json", None)
        if not b64:
            raise RuntimeError("OpenAI image response did not include base64 image data.")
        output_path.write_bytes(base64.b64decode(b64))
