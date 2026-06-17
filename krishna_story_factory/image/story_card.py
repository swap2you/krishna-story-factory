from __future__ import annotations

import base64
import textwrap

from PIL import Image, ImageDraw, ImageFont

from ..config import Settings
from ..models import StoryContent


class ImageGenerationError(RuntimeError):
    pass


class StoryCardGenerator:
    def __init__(self, settings: Settings, mode: str) -> None:
        self.settings = settings
        self.mode = mode

    def generate(self, content: StoryContent, output_path) -> None:
        if self.mode != "test" and self.settings.openai_image_enabled and self.settings.openai_api_key:
            try:
                self._openai_image(content.image_prompt, output_path)
                return
            except Exception:
                # Fallback keeps the daily pipeline running. The manifest records local fallback.
                pass
        self._local_card(content, output_path)

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

    def _local_card(self, content: StoryContent, output_path) -> None:
        width, height = 1024, 1024
        image = Image.new("RGB", (width, height), "#fff8e7")
        draw = ImageDraw.Draw(image)
        try:
            title_font = ImageFont.truetype("DejaVuSans-Bold.ttf", 54)
            body_font = ImageFont.truetype("DejaVuSans.ttf", 32)
            small_font = ImageFont.truetype("DejaVuSans.ttf", 26)
        except OSError:
            title_font = body_font = small_font = ImageFont.load_default()

        draw.rounded_rectangle((60, 60, 964, 964), radius=48, outline="#8a5a2b", width=5, fill="#fffdf5")
        draw.ellipse((377, 155, 647, 425), outline="#8a5a2b", width=5, fill="#ffe3a3")
        draw.ellipse((443, 225, 581, 363), outline="#8a5a2b", width=5, fill="#ffd7a8")
        draw.arc((420, 225, 604, 385), start=205, end=335, fill="#8a5a2b", width=5)
        draw.line((512, 425, 512, 570), fill="#8a5a2b", width=8)
        draw.arc((352, 390, 512, 610), start=300, end=35, fill="#8a5a2b", width=7)
        draw.arc((512, 390, 672, 610), start=145, end=240, fill="#8a5a2b", width=7)
        draw.rectangle((300, 650, 724, 760), outline="#8a5a2b", width=5, fill="#eec27d")
        draw.text((0, 790), "Hare Krishna Bedtime Story", font=small_font, fill="#6b4226", anchor="ma")

        title_lines = textwrap.wrap(content.title, width=24)
        y = 95
        for line in title_lines[:3]:
            draw.text((512, y), line, font=title_font, fill="#4b2e16", anchor="ma")
            y += 64

        takeaway_lines = textwrap.wrap(content.takeaway, width=38)
        y = 835
        for line in takeaway_lines[:4]:
            draw.text((512, y), line, font=body_font, fill="#4b2e16", anchor="ma")
            y += 42

        image.save(output_path, "PNG")
