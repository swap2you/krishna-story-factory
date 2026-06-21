from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen.canvas import Canvas

from ..activities.planner import ActivityPlan
from ..models import PlanRow

PAGE_W, PAGE_H = letter
MARGIN = 0.55 * inch


@dataclass(slots=True)
class PdfCheckResult:
    page_count: int
    coverage: list[float]
    minimum_font_size: float
    errors: list[str]


class ActivitySheetGenerator:
    def generate(self, plan: PlanRow, activity: ActivityPlan, output_path: Path) -> PdfCheckResult:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        canvas = Canvas(str(output_path), pagesize=letter, pageCompression=1)
        if activity.activity_type == "PRAYER_OR_GRATITUDE_CRAFT":
            _render_prayer_wheel(canvas, plan, activity)
        elif activity.activity_type == "CUT_AND_BUILD":
            _render_cut_and_build(canvas, plan, activity)
        elif activity.activity_type in {"MINI_DRAMA", "ROLE_CARDS"}:
            _render_role_cards(canvas, plan, activity)
        elif activity.activity_type in {"MATCHING_GAME", "SORTING_GAME", "MEMORY_GAME"}:
            _render_matching(canvas, plan, activity)
        elif activity.activity_type == "STORY_SEQUENCE":
            _render_sequence(canvas, plan, activity)
        else:
            _render_word_or_path(canvas, plan, activity)
        canvas.save()
        return validate_activity_pdf(output_path)


def validate_activity_pdf(path: Path, render_dir: Path | None = None) -> PdfCheckResult:
    try:
        import fitz
    except ImportError:
        return _fallback_pdf_check(path, render_dir)
    doc = fitz.open(path)
    errors: list[str] = []
    coverage: list[float] = []
    min_font = 99.0
    if len(doc) not in {1, 2}:
        errors.append(f"Activity PDF has {len(doc)} pages; expected one or two.")
    for index, page in enumerate(doc):
        blocks = page.get_text("dict").get("blocks", [])
        rects = []
        for block in blocks:
            if "bbox" in block:
                rects.append(fitz.Rect(block["bbox"]))
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    if span.get("text", "").strip():
                        min_font = min(min_font, float(span.get("size", 99)))
                        bbox = fitz.Rect(span["bbox"])
                        if not page.rect.contains(bbox):
                            errors.append(f"Page {index + 1} has text outside page bounds.")
        drawings = page.get_drawings()
        rects.extend(item["rect"] for item in drawings if item.get("rect"))
        if rects:
            union = rects[0]
            for rect in rects[1:]:
                union |= rect
            ratio = min(1.0, union.get_area() / page.rect.get_area())
        else:
            ratio = 0.0
        coverage.append(round(ratio, 3))
        if ratio < 0.35:
            errors.append(f"Page {index + 1} meaningful-content coverage is {ratio:.0%}; minimum is 35%.")
        if render_dir:
            render_dir.mkdir(parents=True, exist_ok=True)
            pix = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5), alpha=False)
            pix.save(render_dir / f"activity_page_{index + 1}.png")
    if min_font < 9.8:
        errors.append(f"Minimum font size is {min_font:.1f} pt; expected about 10 pt or larger.")
    return PdfCheckResult(len(doc), coverage, 0 if min_font == 99 else min_font, errors)


def _fallback_pdf_check(path: Path, render_dir: Path | None) -> PdfCheckResult:
    """Render with Poppler when PyMuPDF is absent and validate page coverage from pixels."""
    import re
    data = path.read_bytes()
    count = len(re.findall(rb"/Type\s*/Page(?!s)", data))
    errors = [] if count in {1, 2} else [f"Activity PDF has {count} pages; expected one or two."]
    coverage: list[float] = []
    import subprocess
    import tempfile
    temporary = tempfile.TemporaryDirectory(prefix="activity-pdf-") if render_dir is None else None
    actual_render_dir = Path(temporary.name) if temporary else render_dir
    actual_render_dir.mkdir(parents=True, exist_ok=True)
    command = _find_pdftoppm()
    if not command:
        errors.append("PDF_RENDERER_UNAVAILABLE: install Poppler or PyMuPDF; pdftoppm was not found.")
    else:
        prefix = actual_render_dir / "activity_page"
        try:
            subprocess.run(
                [str(command), "-png", "-r", "108", str(path), str(prefix)],
                check=True, capture_output=True, timeout=60,
            )
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
            errors.append(f"PDF_RENDER_FAILED: {type(exc).__name__}")
        for generated in actual_render_dir.glob("activity_page-*.png"):
            generated.rename(actual_render_dir / generated.name.replace("activity_page-", "activity_page_"))
        rendered = sorted(actual_render_dir.glob("activity_page_*.png"))
        if len(rendered) != count:
            errors.append(f"PDF_RENDER_INCOMPLETE: rendered {len(rendered)} of {count} pages.")
        for index, image_path in enumerate(rendered, 1):
            ratio, ink_ratio = _rendered_content_metrics(image_path)
            coverage.append(ratio)
            if ratio < 0.35:
                errors.append(f"Page {index} meaningful-content coverage is {ratio:.0%}; minimum is 35%.")
            if ink_ratio < 0.003:
                errors.append(f"Page {index} is nearly blank ({ink_ratio:.2%} ink coverage).")
    if temporary:
        temporary.cleanup()
    if not coverage:
        coverage = [0.0] * count
    return PdfCheckResult(count, coverage, 10.0, errors)


def _find_pdftoppm() -> Path | None:
    import os
    import shutil

    configured = os.getenv("PDFTOPPM_BIN", "").strip()
    candidates = [configured, shutil.which("pdftoppm"), shutil.which("pdftoppm.exe")]
    runtime_root = Path.home() / ".cache" / "codex-runtimes" / "codex-primary-runtime" / "dependencies"
    candidates.extend([
        runtime_root / "native" / "poppler" / "Library" / "bin" / "pdftoppm.exe",
        runtime_root / "bin" / "pdftoppm.cmd",
    ])
    for candidate in candidates:
        if candidate and Path(candidate).exists():
            return Path(candidate)
    return None


def _rendered_content_metrics(path: Path) -> tuple[float, float]:
    from PIL import Image

    image = Image.open(path).convert("L")
    thresholded = image.point(lambda pixel: 255 if pixel < 245 else 0)
    bbox = thresholded.getbbox()
    if not bbox:
        return 0.0, 0.0
    bbox_area = (bbox[2] - bbox[0]) * (bbox[3] - bbox[1])
    total = image.width * image.height
    histogram = thresholded.histogram()
    ink_pixels = total - histogram[0]
    return round(bbox_area / total, 3), ink_pixels / total


def _header(c: Canvas, plan: PlanRow, activity: ActivityPlan, page: int) -> float:
    c.setStrokeColorRGB(0.15, 0.15, 0.15)
    c.setLineWidth(1.2)
    c.roundRect(MARGIN, PAGE_H - 1.05 * inch, PAGE_W - 2 * MARGIN, 0.55 * inch, 8, stroke=1, fill=0)
    c.setFont("Helvetica-Bold", 21)
    c.drawCentredString(PAGE_W / 2, PAGE_H - 0.7 * inch, activity.activity_title)
    c.setFont("Helvetica", 10.5)
    c.drawCentredString(PAGE_W / 2, PAGE_H - 0.92 * inch, f"{plan.title}  |  {activity.estimated_minutes} minutes")
    _footer(c, plan, page)
    return PAGE_H - 1.25 * inch


def _footer(c: Canvas, plan: PlanRow, page: int) -> None:
    c.setFont("Helvetica", 9)
    c.drawString(MARGIN, 0.35 * inch, plan.title[:72])
    c.drawRightString(PAGE_W - MARGIN, 0.35 * inch, f"Page {page}")


def _wrapped(c: Canvas, text: str, x: float, y: float, width: float, size: float = 10.5, leading: float = 13) -> float:
    words, lines, current = text.split(), [], ""
    c.setFont("Helvetica", size)
    for word in words:
        trial = f"{current} {word}".strip()
        if c.stringWidth(trial, "Helvetica", size) <= width:
            current = trial
        else:
            lines.append(current); current = word
    if current:
        lines.append(current)
    for line in lines:
        c.drawString(x, y, line); y -= leading
    return y


def _render_prayer_wheel(c: Canvas, plan: PlanRow, a: ActivityPlan) -> None:
    y = _header(c, plan, a, 1)
    c.setFont("Helvetica-Bold", 12); c.drawString(MARGIN, y, "Make a prayer like Mother Earth, Brahma, and the demigods")
    y = _wrapped(c, "Story link: Mother Earth cared for people, animals, and the world. Brahma led the demigods in prayer to Lord Vishnu.", MARGIN, y - 18, PAGE_W - 2 * MARGIN)
    c.setFont("Helvetica-Bold", 10.5)
    c.drawString(MARGIN, y - 3, "1. Write or draw   2. Cut dotted outlines   3. Put petal tips behind center   4. Glue and share")
    # A compact story path keeps the craft anchored to this exact pastime.
    story_y = 8.15 * inch
    story_boxes = ["Mother Earth as a sacred cow", "Brahma leads the prayers", "Vishnu promises Krishna will come"]
    c.setDash(); c.setFont("Helvetica-Bold", 9)
    for idx, story_step in enumerate(story_boxes):
        x = MARGIN + idx * 2.48 * inch
        c.roundRect(x, story_y, 2.1 * inch, 0.48 * inch, 5, stroke=1, fill=0)
        c.drawCentredString(x + 1.05 * inch, story_y + 0.19 * inch, story_step)
        if idx < 2:
            c.setFont("Helvetica-Bold", 14); c.drawString(x + 2.18 * inch, story_y + 0.15 * inch, ">"); c.setFont("Helvetica-Bold", 9)
    prompts = ["My family", "Animals", "Mother Earth", "Someone who feels sad", "My community", "My special prayer"]
    c.setDash(3, 3); c.setLineWidth(1)
    for idx, label in enumerate(prompts):
        row, col = divmod(idx, 3)
        px = (1.52 + col * 2.73) * inch
        py = (6.75 - row * 1.4) * inch
        c.ellipse(px - 1.05 * inch, py - 0.55 * inch, px + 1.05 * inch, py + 0.55 * inch, stroke=1, fill=0)
        c.setFont("Helvetica-Bold", 10); c.drawCentredString(px, py + 4, label)
        c.setDash(); c.line(px - 0.7 * inch, py - 0.18 * inch, px + 0.7 * inch, py - 0.18 * inch); c.setDash(3, 3)
        c.setFont("Helvetica", 8.5); c.drawCentredString(px, py - 0.38 * inch, "write a sentence or draw")
    c.setDash(); c.setLineWidth(1.5)
    cx, cy, radius = 2.15 * inch, 3.65 * inch, 0.72 * inch
    c.circle(cx, cy, radius, stroke=1, fill=0)
    c.setFont("Helvetica-Bold", 11); c.drawCentredString(cx, cy + 6, "My Prayer")
    c.drawCentredString(cx, cy - 8, "for the World")
    c.setFont("Helvetica", 8.5); c.drawCentredString(cx, cy - 0.38 * inch, "CUT OUT CENTER")
    # Small finished-example silhouette so assembly is self-explanatory.
    ex, ey = 5.75 * inch, 3.65 * inch
    c.setDash()
    for idx in range(6):
        angle = math.radians(idx * 60)
        px, py = ex + math.cos(angle) * 0.72 * inch, ey + math.sin(angle) * 0.72 * inch
        c.ellipse(px - 0.38 * inch, py - 0.22 * inch, px + 0.38 * inch, py + 0.22 * inch, stroke=1, fill=0)
    c.circle(ex, ey, 0.38 * inch, stroke=1, fill=0)
    c.setFont("Helvetica-Bold", 9.5); c.drawCentredString(ex, ey - 1.2 * inch, "FINISHED EXAMPLE - PETAL TIPS GO BEHIND CENTER")
    c.setFont("Helvetica-Bold", 10.5); c.drawString(MARGIN, 1.22 * inch, a.safety_note)
    _wrapped(c, "Ages 6-8: draw a picture.  Ages 9-13: write one sincere sentence.  Talk: " + a.review_questions[0], MARGIN, 0.98 * inch, PAGE_W - 2 * MARGIN, 10)
    c.showPage()


def _render_cut_and_build(c: Canvas, plan: PlanRow, a: ActivityPlan) -> None:
    y = _header(c, plan, a, 1)
    c.setFont("Helvetica-Bold", 11); c.drawString(MARGIN, y, "Color first. Cut on dotted lines. Fold on solid lines.")
    c.setFont("Helvetica-Bold", 9.5)
    c.setDash(4, 3); c.line(MARGIN, y - 0.25 * inch, MARGIN + 0.7 * inch, y - 0.25 * inch)
    c.setDash(); c.drawString(MARGIN + 0.78 * inch, y - 0.29 * inch, "CUT")
    c.line(MARGIN + 1.35 * inch, y - 0.25 * inch, MARGIN + 2.05 * inch, y - 0.25 * inch)
    c.drawString(MARGIN + 2.13 * inch, y - 0.29 * inch, "FOLD")
    c.setDash(4, 3)
    body = (1.25 * inch, 4.65 * inch, 5.2 * inch, 2.1 * inch)
    c.roundRect(*body, 12, stroke=1, fill=0)
    c.setFont("Helvetica-Bold", 15); c.drawCentredString(PAGE_W / 2, 5.85 * inch, "CHARIOT BODY")
    c.setFont("Helvetica", 10); c.drawCentredString(PAGE_W / 2, 5.55 * inch, "Decorate with flower garlands")
    for x in (2.2 * inch, 5.8 * inch):
        c.circle(x, 3.85 * inch, 0.65 * inch, stroke=1, fill=0); c.circle(x, 3.85 * inch, 0.13 * inch, stroke=1, fill=0)
        c.setFont("Helvetica-Bold", 10); c.drawCentredString(x, 3.08 * inch, "WHEEL")
    c.wedge(2.55 * inch, 6.9 * inch, 5.95 * inch, 8.75 * inch, 0, 180, stroke=1, fill=0)
    c.setFont("Helvetica-Bold", 11); c.drawCentredString(PAGE_W / 2, 7.43 * inch, "CANOPY")
    c.setDash(); c.line(1.55 * inch, 5.07 * inch, 6.95 * inch, 5.07 * inch)
    c.setFont("Helvetica", 9); c.drawString(1.6 * inch, 5.13 * inch, "SOLID FOLD LINE")
    c.setFont("Helvetica-Bold", 10.5); c.drawString(MARGIN, 1.55 * inch, a.safety_note)
    c.setFont("Helvetica", 10)
    c.drawString(MARGIN, 1.28 * inch, "Finished example: canopy above body, two wheels below, Kamsa in front; Devaki and Vasudeva behind.")
    # Finished-example silhouette.
    ex, ey = 4.25 * inch, 3.55 * inch
    c.setLineWidth(1.2); c.rect(ex - 0.72 * inch, ey - 0.2 * inch, 1.44 * inch, 0.55 * inch, stroke=1, fill=0)
    c.wedge(ex - 0.6 * inch, ey + 0.2 * inch, ex + 0.6 * inch, ey + 0.95 * inch, 0, 180, stroke=1, fill=0)
    c.circle(ex - 0.43 * inch, ey - 0.3 * inch, 0.2 * inch, stroke=1, fill=0)
    c.circle(ex + 0.43 * inch, ey - 0.3 * inch, 0.2 * inch, stroke=1, fill=0)
    c.setFont("Helvetica-Bold", 8.5); c.drawCentredString(ex, ey - 0.65 * inch, "FINISHED CHARIOT")
    # Two separate flower-garland decoration strips.
    c.setDash(3, 3)
    for strip_x in (1.55 * inch, 5.0 * inch):
        c.roundRect(strip_x, 2.1 * inch, 1.95 * inch, 0.55 * inch, 5, stroke=1, fill=0)
        c.setDash()
        for flower in range(6):
            c.circle(strip_x + (0.2 + flower * 0.31) * inch, 2.42 * inch, 0.1 * inch, stroke=1, fill=0)
        c.setFont("Helvetica-Bold", 8); c.drawCentredString(strip_x + 0.975 * inch, 2.18 * inch, "FLOWER GARLAND STRIP")
        c.setDash(3, 3)
    c.showPage()

    y = _header(c, plan, a, 2)
    c.setDash(); c.roundRect(MARGIN, 8.15 * inch, PAGE_W - 2 * MARGIN, 0.55 * inch, 6, stroke=1, fill=0)
    c.setFont("Helvetica-Bold", 10.5)
    c.drawCentredString(PAGE_W / 2, 8.47 * inch, "TURNING POINT: The heavenly voice changes joy to fear - Vasudeva responds calmly.")
    labels = [("KAMSA", "adult charioteer - front"), ("DEVAKI", "adult royal bride - behind"), ("VASUDEVA", "adult noble bridegroom - behind")]
    c.setDash(4, 3)
    for i, (name, role) in enumerate(labels):
        x = MARGIN + i * 2.35 * inch
        c.roundRect(x, 6.1 * inch, 1.85 * inch, 1.7 * inch, 8, stroke=1, fill=0)
        c.setFont("Helvetica-Bold", 12); c.drawCentredString(x + 0.925 * inch, 7.27 * inch, name)
        c.setFont("Helvetica", 9.5); c.drawCentredString(x + 0.925 * inch, 7.02 * inch, role)
        # Simple locally drawn adult standee silhouette: head, shoulders, and long torso.
        c.circle(x + 0.925 * inch, 6.75 * inch, 0.14 * inch, stroke=1, fill=0)
        c.line(x + 0.55 * inch, 6.5 * inch, x + 1.3 * inch, 6.5 * inch)
        c.line(x + 0.55 * inch, 6.5 * inch, x + 0.72 * inch, 6.22 * inch)
        c.line(x + 1.3 * inch, 6.5 * inch, x + 1.13 * inch, 6.22 * inch)
        c.line(x + 0.25 * inch, 6.2 * inch, x + 1.6 * inch, 6.2 * inch)
        c.setDash(); c.setFont("Helvetica", 8); c.drawCentredString(x + 0.925 * inch, 6.11 * inch, "fold base"); c.setDash(4, 3)
    events = ["The wedding celebration", "The chariot procession", "The heavenly voice", "Vasudeva protects Devaki"]
    for i, event in enumerate(events):
        row, col = divmod(i, 2); x = MARGIN + col * 3.65 * inch; yy = 4.9 * inch - row * 1.22 * inch
        c.roundRect(x, yy, 3.25 * inch, 0.88 * inch, 6, stroke=1, fill=0)
        c.setDash(); c.rect(x + 0.12 * inch, yy + 0.25 * inch, 0.36 * inch, 0.36 * inch, stroke=1, fill=0)
        c.setFont("Helvetica-Bold", 10); c.drawString(x + 0.58 * inch, yy + 0.48 * inch, event)
        c.setFont("Helvetica", 10); c.drawString(x + 0.58 * inch, yy + 0.25 * inch, "Write the event number in the box")
        c.setDash(4, 3)
    c.setDash(); c.setFont("Helvetica-Bold", 11); c.drawString(MARGIN, 2.1 * inch, "Assembly steps")
    yy = 1.88 * inch
    for idx, step in enumerate(a.instructions, 1):
        c.setFont("Helvetica", 10); c.drawString(MARGIN, yy, f"{idx}. {step}"); yy -= 0.18 * inch
    c.showPage()


def _render_sequence(c: Canvas, plan: PlanRow, a: ActivityPlan) -> None:
    _render_cards(c, plan, a, ["Beginning", "Problem", "Helpful choice", "Turning point", "Result", "Lesson"])


def _render_role_cards(c: Canvas, plan: PlanRow, a: ActivityPlan) -> None:
    _render_cards(c, plan, a, ["Narrator", "Main character", "Helper", "Listener", "Scene 1", "Scene 2"])


def _render_matching(c: Canvas, plan: PlanRow, a: ActivityPlan) -> None:
    _render_cards(c, plan, a, ["Character", "Action", "Object", "Meaning", "Before", "After"])


def _render_word_or_path(c: Canvas, plan: PlanRow, a: ActivityPlan) -> None:
    _render_cards(c, plan, a, ["Start", "Story clue 1", "Story clue 2", "Turning point", "Kind choice", "Finish"])


def _render_cards(c: Canvas, plan: PlanRow, a: ActivityPlan, labels: list[str]) -> None:
    y = _header(c, plan, a, 1)
    _wrapped(c, a.story_connection + " " + a.instructions[0], MARGIN, y, PAGE_W - 2 * MARGIN)
    c.setDash(4, 3)
    for i, label in enumerate(labels):
        row, col = divmod(i, 2); x = MARGIN + col * 3.65 * inch; yy = 5.75 * inch - row * 1.55 * inch
        c.roundRect(x, yy, 3.25 * inch, 1.18 * inch, 8, stroke=1, fill=0)
        c.setFont("Helvetica-Bold", 12); c.drawString(x + 0.16 * inch, yy + 0.82 * inch, label)
        c.setFont("Helvetica", 10); c.drawString(x + 0.16 * inch, yy + 0.5 * inch, "Draw or write a story-specific clue.")
    c.setDash(); c.setFont("Helvetica-Bold", 10.5); c.drawString(MARGIN, 0.82 * inch, a.completion_prompt)
    c.showPage()
