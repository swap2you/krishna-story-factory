from __future__ import annotations

import base64
import textwrap

from PIL import Image, ImageDraw, ImageFont

from ..config import Settings
from ..models import PlanRow, StoryContent


class ImageGenerationError(RuntimeError):
    pass


class StoryCardGenerator:
    def __init__(self, settings: Settings, mode: str) -> None:
        self.settings = settings
        self.mode = mode

    def generate(self, content: StoryContent, output_path, *, plan: PlanRow | None = None) -> str:
        if self.mode != "test" and self.settings.openai_image_enabled and self.settings.openai_api_key:
            try:
                self._openai_image(content.image_prompt, output_path)
                return "openai"
            except Exception:
                pass
        self._local_card(content, output_path, plan=plan)
        return "fallback"

    def _openai_image(self, prompt: str, output_path) -> None:
        from openai import OpenAI

        client = OpenAI(api_key=self.settings.openai_api_key)
        response = client.images.generate(
            model=self.settings.openai_image_model,
            prompt=prompt,
            size=self.settings.openai_image_size,
            quality=self.settings.openai_image_quality,
            n=1,
        )
        first = response.data[0]
        b64 = getattr(first, "b64_json", None)
        if not b64:
            raise ImageGenerationError("OpenAI image response did not include base64 image data.")
        output_path.write_bytes(base64.b64decode(b64))

    def _local_card(self, content: StoryContent, output_path, *, plan: PlanRow | None = None) -> None:
        width, height = 1024, 1024
        image = Image.new("RGB", (width, height), "#fff8e7")
        draw = ImageDraw.Draw(image)
        try:
            title_font = ImageFont.truetype("DejaVuSans-Bold.ttf", 48)
            body_font = ImageFont.truetype("DejaVuSans.ttf", 28)
            small_font = ImageFont.truetype("DejaVuSans.ttf", 22)
        except OSError:
            title_font = body_font = small_font = ImageFont.load_default()

        draw.rounded_rectangle((50, 50, 974, 974), radius=36, outline="#8a5a2b", width=4, fill="#fffdf5")
        draw.text((512, 80), "Krishna Book Bedtime", font=small_font, fill="#6b4226", anchor="ma")

        title_lines = textwrap.wrap(content.story_card_text or content.title, width=28)
        y = 140
        for line in title_lines[:3]:
            draw.text((512, y), line, font=title_font, fill="#4b2e16", anchor="ma")
            y += 56

        source = plan.source_reference if plan else "Krishna Book"
        draw.text((512, 300), source, font=small_font, fill="#6b4226", anchor="ma")

        tagline = content.takeaway or "Hare Krishna bedtime katha"
        tag_lines = textwrap.wrap(tagline, width=40)
        y = 820
        for line in tag_lines[:3]:
            draw.text((512, y), line, font=body_font, fill="#4b2e16", anchor="ma")
            y += 36

        draw.text((512, 940), "Hare Krishna", font=small_font, fill="#6b4226", anchor="ma")
        image.save(output_path, "PNG")
