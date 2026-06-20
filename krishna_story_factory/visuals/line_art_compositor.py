from __future__ import annotations

import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

from .models import PosterCopy, VisualBrief


def _load_fonts() -> tuple:
    title_candidates = ("Segoe UI Bold", "Arial Bold", "DejaVuSans-Bold.ttf")
    body_candidates = ("Segoe UI", "Arial", "DejaVuSans.ttf")
    title_font = body_font = ImageFont.load_default()
    for name in title_candidates:
        try:
            title_font = ImageFont.truetype(name, 40)
            break
        except OSError:
            continue
    for name in body_candidates:
        try:
            body_font = ImageFont.truetype(name, 24)
            break
        except OSError:
            continue
    return title_font, body_font


def clean_line_art(raw_path: Path, output_path: Path) -> None:
    image = Image.open(raw_path).convert("L")
    image = ImageOps.autocontrast(image, cutoff=2)
    bw = image.point(lambda p: 255 if p > 210 else (0 if p < 120 else p))
    bw = bw.convert("RGB")
    bw.save(output_path, "PNG")


def compose_line_art_portrait(
    raw_path: Path,
    portrait_path: Path,
    coloring_page_path: Path,
    pdf_path: Path,
    *,
    title: str,
    quote: str = "",
) -> None:
    clean_line_art(raw_path, raw_path)
    base = Image.open(raw_path).convert("RGB")
    width, height = base.size
    top_pad = 120 if title else 40
    canvas = Image.new("RGB", (width, height + top_pad), "white")
    canvas.paste(base, (0, top_pad))

    draw = ImageDraw.Draw(canvas)
    title_font, quote_font = _load_fonts()
    margin = int(width * 0.05)
    draw.rectangle((margin, 16, width - margin, top_pad - 16), outline="#222222", width=2)
    title_lines = textwrap.wrap(title, width=34)[:2]
    y = 28
    for line in title_lines:
        draw.text((width // 2, y), line, font=title_font, fill="#111111", anchor="ma")
        y += title_font.size + 2

    if quote:
        qy = top_pad - 34
        quote_line = textwrap.shorten(quote, width=70, placeholder="...")
        draw.text((width // 2, qy), quote_line, font=quote_font, fill="#333333", anchor="ma")

    draw.rectangle((12, 12, width - 12, canvas.height - 12), outline="#444444", width=3)
    canvas.save(portrait_path, "PNG")
    canvas.save(coloring_page_path, "PNG")
    _write_print_pdf(canvas, pdf_path)


def _write_print_pdf(image: Image.Image, pdf_path: Path) -> None:
    for page_size, page_name in ((A4, "A4"), (letter, "Letter")):
        pass
    page_w, page_h = letter
    pdf = canvas.Canvas(str(pdf_path), pagesize=letter)
    img_w, img_h = image.size
    scale = min((page_w - 72) / img_w, (page_h - 72) / img_h)
    draw_w = img_w * scale
    draw_h = img_h * scale
    x = (page_w - draw_w) / 2
    y = (page_h - draw_h) / 2
    pdf.drawImage(ImageReader(image), x, y, width=draw_w, height=draw_h, preserveAspectRatio=True, anchor="c")
    pdf.showPage()
    pdf.save()


def create_placeholder_line_art_raw(output_path: Path, *, brief: VisualBrief) -> None:
    width, height = 1024, 1536
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((80, 160, 944, 1380), radius=24, outline="black", width=4)
    font = ImageFont.load_default()
    scene = brief.central_scene or brief.line_art_focus or brief.title
    for i, line in enumerate(textwrap.wrap(scene, width=40)[:16]):
        draw.text((512, 200 + i * 30), line, font=font, fill="black", anchor="ma")
    image.save(output_path, "PNG")
