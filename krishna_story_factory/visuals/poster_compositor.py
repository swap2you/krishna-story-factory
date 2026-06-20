from __future__ import annotations

import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

from .models import PosterCopy


def _load_fonts() -> tuple[ImageFont.FreeTypeFont | ImageFont.ImageFont, ...]:
    candidates = [
        ("Segoe UI Bold", 52),
        ("Segoe UI", 34),
        ("Arial Bold", 52),
        ("Arial", 34),
        ("DejaVuSans-Bold.ttf", 52),
        ("DejaVuSans.ttf", 30),
    ]
    title_font = body_font = small_font = caption_font = ImageFont.load_default()
    for name, size in candidates:
        try:
            font = ImageFont.truetype(name, size)
            if size >= 50:
                title_font = font
            elif size >= 32:
                body_font = font
            else:
                small_font = font
        except OSError:
            continue
    caption_font = small_font
    return title_font, body_font, small_font, caption_font


def _wrap(draw: ImageDraw.ImageDraw, text: str, font, max_width: int) -> list[str]:
    if not text.strip():
        return []
    words = text.split()
    lines: list[str] = []
    current: list[str] = []
    for word in words:
        trial = " ".join(current + [word])
        if draw.textlength(trial, font=font) <= max_width:
            current.append(word)
        else:
            if current:
                lines.append(" ".join(current))
            current = [word]
    if current:
        lines.append(" ".join(current))
    return lines


def compose_poster(raw_path: Path, output_path: Path, copy: PosterCopy, whatsapp_path: Path | None = None) -> None:
    base = Image.open(raw_path).convert("RGB")
    width, height = base.size
    canvas = Image.new("RGB", (width, height + 220), "#1a1208")
    canvas.paste(base, (0, 110))

    draw = ImageDraw.Draw(canvas)
    title_font, body_font, small_font, caption_font = _load_fonts()

    margin = int(width * 0.06)
    max_text = width - margin * 2

    draw.rounded_rectangle((margin // 2, 20, width - margin // 2, 100), radius=18, fill="#2b1d0f", outline="#c9a227", width=2)
    title_lines = _wrap(draw, copy.title, title_font, max_text)
    y = 34
    for line in title_lines[:2]:
        draw.text((width // 2, y), line, font=title_font, fill="#f6e7b8", anchor="ma")
        y += title_font.size + 4
    if copy.subtitle:
        draw.text((width // 2, 88), copy.subtitle, font=small_font, fill="#d8c792", anchor="ma")

    if copy.heavenly_quote:
        panel_top = 120
        panel_bottom = panel_top + 90
        draw.rounded_rectangle((margin, panel_top, width - margin, panel_bottom), radius=14, fill="#120c06cc", outline="#c9a227")
        quote_lines = _wrap(draw, f'"{copy.heavenly_quote}"', body_font, max_text - 40)
        qy = panel_top + 12
        for line in quote_lines[:3]:
            draw.text((width // 2, qy), line, font=body_font, fill="#fff6df", anchor="ma")
            qy += body_font.size + 4

    footer_top = height + 120
    draw.rounded_rectangle((margin, footer_top, width - margin, height + 200), radius=14, fill="#2b1d0f", outline="#c9a227", width=2)
    one_liner_lines = _wrap(draw, copy.one_liner, body_font, max_text - 20)
    oy = footer_top + 16
    for line in one_liner_lines[:3]:
        draw.text((width // 2, oy), line, font=body_font, fill="#f6e7b8", anchor="ma")
        oy += body_font.size + 4

    side_y = int(height * 0.35)
    for idx, caption in enumerate(copy.supporting_captions[:3]):
        label = caption.label.strip()
        text = caption.text.strip()
        if not text:
            continue
        x = margin if idx % 2 == 0 else width - margin
        anchor = "la" if idx % 2 == 0 else "ra"
        block = f"{label}: {text}" if label else text
        lines = _wrap(draw, block, caption_font, int(width * 0.28))
        cy = side_y + idx * 70
        for line in lines[:2]:
            draw.text((x, cy), line, font=caption_font, fill="#f0dfaa", anchor=anchor)
            cy += caption_font.size + 2

    canvas.save(output_path, "PNG")
    if whatsapp_path:
        rgb = canvas.convert("RGB")
        rgb.save(whatsapp_path, "JPEG", quality=88, optimize=True)


def create_placeholder_poster_raw(output_path: Path, *, title: str, scene: str) -> None:
    width, height = 1024, 1536
    image = Image.new("RGB", (width, height), "#1b1208")
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((60, 120, 964, 1410), radius=28, outline="#c9a227", width=4, fill="#2a1c10")
    font = ImageFont.load_default()
    draw.text((512, 80), title[:60], font=font, fill="#f6e7b8", anchor="ma")
    for i, line in enumerate(textwrap.wrap(scene, width=42)[:18]):
        draw.text((512, 180 + i * 28), line, font=font, fill="#efe2c0", anchor="ma")
    image.save(output_path, "PNG")
