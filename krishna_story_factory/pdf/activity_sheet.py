from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen.canvas import Canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from ..activities.models import (
    ActivityPack, ActivityPage, DecisionNode, MatchingCard, RolePlayCard, SequenceCard, SIMPLE_TYPES,
    component_label,
)
from ..activities.qa import (
    activity_presentation_errors,
    matching_coverage_from_pdf_text,
    pdf_text_has_generic_placeholders,
    retain_matching_coverage_evidence,
)
from ..models import PlanRow

PAGE_W, PAGE_H = letter
MARGIN = 0.55 * inch


def _register_fonts() -> tuple[str, str]:
    candidates = [
        (Path("C:/Windows/Fonts/arial.ttf"), Path("C:/Windows/Fonts/arialbd.ttf")),
        (Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"), Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")),
    ]
    for regular, bold in candidates:
        if regular.exists() and bold.exists():
            pdfmetrics.registerFont(TTFont("KSF-Regular", str(regular)))
            pdfmetrics.registerFont(TTFont("KSF-Bold", str(bold)))
            return "KSF-Regular", "KSF-Bold"
    return "Helvetica", "Helvetica-Bold"


FONT_REGULAR, FONT_BOLD = _register_fonts()


@dataclass(slots=True)
class PdfCheckResult:
    page_count: int
    coverage: list[float]
    minimum_font_size: float
    errors: list[str]
    matching_coverage: dict | None = None


class ActivitySheetGenerator:
    def generate(self, plan: PlanRow, activity: ActivityPack, output_path: Path) -> PdfCheckResult:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        canvas = Canvas(str(output_path), pagesize=letter, pageCompression=1)
        canvas.setTitle(activity.activity_title or "Activity Sheet")
        canvas.setAuthor("Krishna Story Factory")
        # Prefer rich deterministic layouts for known packs; otherwise render each page.
        if activity.activity_type == "PRAYER_OR_GRATITUDE_CRAFT" and any(
            p.page_type == "PRAYER_WHEEL" for p in activity.pages
        ):
            _render_prayer_wheel(canvas, plan, activity)
            support = [p for p in activity.pages if p.page_type != "PRAYER_WHEEL"]
            for page in support:
                _render_page(canvas, plan, activity, page)
        elif activity.activity_type == "CUT_AND_BUILD":
            _render_cut_and_build(canvas, plan, activity)
            support = [p for p in activity.pages if p.page_type not in {"CUT_AND_BUILD_PARTS", "STORY_SEQUENCE_CARDS"}]
            # cut_and_build already renders 2 pages covering parts+sequence; add remaining support pages
            for page in support:
                _render_page(canvas, plan, activity, page)
        else:
            for page in activity.pages:
                if page.page_type == "ANSWER_KEY_INTERNAL_ONLY":
                    continue
                if page.page_type == "PRAYER_WHEEL":
                    _render_lotus_prayer_page(canvas, plan, activity, page)
                else:
                    _render_page(canvas, plan, activity, page)
        canvas.save()
        return validate_activity_pdf(output_path, activity=activity)


def validate_activity_pdf(
    path: Path,
    render_dir: Path | None = None,
    activity: ActivityPack | None = None,
) -> PdfCheckResult:
    try:
        import pypdfium2  # noqa: F401
    except ImportError:
        pass
    else:
        return _pdfium_pdf_check(path, render_dir, activity=activity)
    try:
        import fitz
    except ImportError:
        return _fallback_pdf_check(path, render_dir, activity=activity)
    doc = fitz.open(path)
    errors: list[str] = []
    coverage: list[float] = []
    min_font = 99.0
    page_count = len(doc)
    min_pages, max_pages = _page_bounds(activity)
    if not min_pages <= page_count <= max_pages:
        errors.append(f"Activity PDF has {page_count} pages; expected {min_pages}-{max_pages}.")
    if page_count > 5:
        errors.append(f"Activity PDF has {page_count} pages; maximum is 5.")
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
    # Hard reject if coloring image appears embedded
    text_blob = " ".join(page.get_text() for page in doc).lower()
    if "coloring_page.png" in text_blob or "embedded coloring" in text_blob:
        errors.append("Activity PDF must not embed coloring_page.png.")
    placeholder_hits = pdf_text_has_generic_placeholders(text_blob)
    if placeholder_hits:
        errors.append("Activity PDF contains generic placeholders: " + ", ".join(placeholder_hits[:6]))
    matching_meta = None
    if activity is not None:
        matching_meta = _append_matching_coverage_errors(errors, activity, text_blob, render_dir)
    if min_font < 9.8:
        errors.append(f"Minimum font size is {min_font:.1f} pt; expected about 10 pt or larger.")
    return PdfCheckResult(page_count, coverage, 0 if min_font == 99 else min_font, errors, matching_meta)


def _pdfium_pdf_check(
    path: Path, render_dir: Path | None, activity: ActivityPack | None = None,
) -> PdfCheckResult:
    import tempfile
    import pypdfium2 as pdfium

    doc = pdfium.PdfDocument(str(path))
    page_count = len(doc)
    min_pages, max_pages = _page_bounds(activity)
    errors: list[str] = []
    if not min_pages <= page_count <= max_pages:
        errors.append(f"Activity PDF has {page_count} pages; expected {min_pages}-{max_pages}.")
    if page_count > 5:
        errors.append(f"Activity PDF has {page_count} pages; maximum is 5.")
    temporary = tempfile.TemporaryDirectory(prefix="activity-pdf-") if render_dir is None else None
    actual_render_dir = Path(temporary.name) if temporary else render_dir
    actual_render_dir.mkdir(parents=True, exist_ok=True)
    coverage: list[float] = []
    text_blob: list[str] = []
    for index in range(page_count):
        page = doc[index]
        image = page.render(scale=1.5).to_pil().convert("RGB")
        image_path = actual_render_dir / f"activity_page_{index + 1}.png"
        image.save(image_path, "PNG")
        ratio, ink_ratio = _rendered_content_metrics(image_path)
        coverage.append(ratio)
        if ratio < 0.35:
            errors.append(f"Page {index + 1} meaningful-content coverage is {ratio:.0%}; minimum is 35%.")
        if ink_ratio < 0.003:
            errors.append(f"Page {index + 1} is nearly blank ({ink_ratio:.2%} ink coverage).")
        try:
            text_blob.append(page.get_textpage().get_text_range())
        except Exception:
            pass
    joined = " ".join(text_blob).lower()
    if "coloring_page.png" in joined or "embedded coloring" in joined:
        errors.append("Activity PDF must not embed coloring_page.png.")
    placeholder_hits = pdf_text_has_generic_placeholders(joined)
    if placeholder_hits:
        errors.append("Activity PDF contains generic placeholders: " + ", ".join(placeholder_hits[:6]))
    matching_meta = _append_matching_coverage_errors(errors, activity, joined, render_dir)
    if activity is not None:
        errors.extend(activity_presentation_errors(activity, text_blob))
        for index, ratio in enumerate(coverage, start=1):
            if ratio < 0.55 and activity.pages and index <= len(activity.pages):
                page = activity.pages[index - 1]
                if page.page_type == "PRAYER_WHEEL" and ratio < 0.45:
                    errors.append(f"Page {index} lotus layout under-uses the page ({ratio:.0%} coverage).")
    doc.close()
    if temporary:
        temporary.cleanup()
    return PdfCheckResult(page_count, coverage, 10.0, errors, matching_meta)


def _append_matching_coverage_errors(
    errors: list[str], activity: ActivityPack | None, text_blob: str, render_dir: Path | None
) -> dict | None:
    if activity is None:
        return None
    coverage_check = matching_coverage_from_pdf_text(activity, text_blob)
    if not coverage_check.pass_:
        if coverage_check.missing_labels:
            errors.append("Matching coverage missing labels: " + ", ".join(coverage_check.missing_labels[:8]))
        if coverage_check.orphan_labels:
            errors.append("Matching coverage orphans: " + "; ".join(coverage_check.orphan_labels[:6]))
    try:
        chapter_guess = ""
        if render_dir and render_dir.parent:
            chapter_guess = render_dir.parent.name[:3]
        retain_matching_coverage_evidence(
            Path.cwd(),
            chapter_no=chapter_guess or "005",
            coverage=coverage_check,
            pdf_text=text_blob,
        )
    except Exception:
        pass
    return coverage_check.to_dict()


def _page_bounds(activity: ActivityPack | None) -> tuple[int, int]:
    if activity and activity.activity_type in SIMPLE_TYPES:
        return 1, 2
    return 2, 4


def _fallback_pdf_check(path: Path, render_dir: Path | None, activity: ActivityPack | None = None) -> PdfCheckResult:
    import re
    data = path.read_bytes()
    count = len(re.findall(rb"/Type\s*/Page(?!s)", data))
    min_pages, max_pages = _page_bounds(activity)
    errors = [] if min_pages <= count <= max_pages else [f"Activity PDF has {count} pages; expected {min_pages}-{max_pages}."]
    if count > 5:
        errors.append(f"Activity PDF has {count} pages; maximum is 5.")
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
    matching_meta = None
    # Fallback path may lack text extraction; still fail closed if activity provided and no text.
    if activity is not None:
        text_blob = ""
        try:
            import fitz
            doc = fitz.open(path)
            text_blob = "\n".join(page.get_text() for page in doc)
            doc.close()
        except Exception:
            try:
                data = path.read_bytes()
                text_blob = data.decode("latin-1", errors="ignore")
            except Exception:
                text_blob = ""
        matching_meta = _append_matching_coverage_errors(errors, activity, text_blob, render_dir)
    return PdfCheckResult(count, coverage, 10.0, errors, matching_meta)


def _find_pdftoppm() -> Path | None:
    import os
    import shutil

    configured = os.getenv("PDFTOPPM_BIN", "").strip()
    candidates = [configured, shutil.which("pdftoppm"), shutil.which("pdftoppm.exe")]
    for candidate in candidates:
        if candidate and Path(candidate).exists() and Path(candidate).suffix.lower() != ".cmd":
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


def _header(c: Canvas, plan: PlanRow, activity: ActivityPack, page: int, page_title: str = "") -> float:
    c.setStrokeColorRGB(0.15, 0.15, 0.15)
    c.setLineWidth(1.2)
    c.roundRect(MARGIN, PAGE_H - 1.05 * inch, PAGE_W - 2 * MARGIN, 0.55 * inch, 8, stroke=1, fill=0)
    title = page_title or activity.activity_title
    c.setFont(FONT_BOLD, 18 if len(title) > 42 else 21)
    c.drawCentredString(PAGE_W / 2, PAGE_H - 0.7 * inch, title[:70])
    c.setFont(FONT_REGULAR, 10.5)
    c.drawCentredString(PAGE_W / 2, PAGE_H - 0.92 * inch, f"{plan.title}  |  {activity.estimated_minutes} minutes")
    _footer(c, plan, page)
    return PAGE_H - 1.25 * inch


def _footer(c: Canvas, plan: PlanRow, page: int) -> None:
    c.setFont(FONT_REGULAR, 9)
    c.drawString(MARGIN, 0.35 * inch, plan.title[:72])
    c.drawRightString(PAGE_W - MARGIN, 0.35 * inch, f"Page {page}")


def _wrapped(c: Canvas, text: str, x: float, y: float, width: float, size: float = 10.5, leading: float = 13) -> float:
    words, lines, current = text.split(), [], ""
    c.setFont(FONT_REGULAR, size)
    for word in words:
        trial = f"{current} {word}".strip()
        if c.stringWidth(trial, FONT_REGULAR, size) <= width:
            current = trial
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    for line in lines:
        c.drawString(x, y, line)
        y -= leading
    return y


def _wrapped_font(c: Canvas, text: str, x: float, y: float, width: float, *, font: str, size: float, leading: float) -> float:
    words, lines, current = text.split(), [], ""
    c.setFont(font, size)
    for word in words:
        trial = f"{current} {word}".strip()
        if c.stringWidth(trial, font, size) <= width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    for line in lines[:3]:
        c.drawString(x, y, line)
        y -= leading
    return y


def _story_box(c: Canvas, text: str, y: float) -> float:
    c.setStrokeColorRGB(0.2, 0.2, 0.2)
    c.roundRect(MARGIN, y - 0.55 * inch, PAGE_W - 2 * MARGIN, 0.55 * inch, 6, stroke=1, fill=0)
    c.setFont(FONT_BOLD, 10)
    c.drawString(MARGIN + 0.12 * inch, y - 0.18 * inch, "Story connection")
    return _wrapped(c, text, MARGIN + 0.12 * inch, y - 0.36 * inch, PAGE_W - 2 * MARGIN - 0.24 * inch, 10, 12)


def _render_page(c: Canvas, plan: PlanRow, activity: ActivityPack, page: ActivityPage) -> None:
    page_no = c.getPageNumber()
    y = _header(c, plan, activity, page_no, page.page_title)
    y = _story_box(c, page.story_connection or activity.story_connection, y)
    y -= 0.2 * inch
    if page.page_type == "DECISION_TREE":
        _render_decision_tree(c, plan, activity, page, y)
    elif page.page_type in {"MATCHING_CARDS", "SORTING_CARDS"}:
        _render_matching_page(c, plan, activity, page, y)
    elif page.page_type == "ROLE_PLAY_CARDS":
        _render_role_page(c, plan, activity, page, y)
    elif page.page_type == "FAMILY_MISSION":
        _render_family_mission(c, plan, activity, page, y)
    elif page.page_type == "STORY_MAP":
        _render_story_map(c, plan, activity, page, y)
    elif page.page_type == "MAZE_OR_PATH":
        _render_path(c, plan, activity, page, y)
    elif page.page_type == "WORD_SEARCH":
        _render_word_search_page(c, plan, activity, page, y)
    elif page.page_type == "DRAW_AND_REFLECT":
        _render_draw_reflect(c, plan, activity, page, y)
    elif page.page_type == "EMOTION_MAP":
        _render_emotion_map(c, plan, activity, page, y)
    elif page.page_type == "STORY_SEQUENCE_CARDS":
        _render_sequence_page(c, plan, activity, page, y)
    elif page.page_type == "QUICK_DISCUSSION":
        _render_discussion(c, plan, activity, page, y)
    else:
        _render_generic_cards(c, plan, activity, page, y)
    c.showPage()


def _render_decision_tree(c: Canvas, plan: PlanRow, activity: ActivityPack, page: ActivityPage, y: float) -> None:
    c.setFont(FONT_BOLD, 12)
    c.drawString(MARGIN, y, "Promise and duty decision tree")
    y -= 0.28 * inch
    for step in page.instructions:
        y = _wrapped(c, f"• {step}", MARGIN, y, PAGE_W - 2 * MARGIN, 10.5)
        y -= 0.05 * inch
    node = next((item for item in page.components if isinstance(item, DecisionNode)), None)
    question = node.question if node else "Is this promise good and safe?"
    choices = node.choices if node else ["Yes — keep it honestly", "No or unsure — tell a trusted adult"]
    guidance = node.guidance if node else "Choose safety and truthfulness."
    # Tree boxes
    c.roundRect(PAGE_W / 2 - 1.4 * inch, 6.4 * inch, 2.8 * inch, 0.7 * inch, 8, stroke=1, fill=0)
    c.setFont(FONT_BOLD, 11)
    c.drawCentredString(PAGE_W / 2, 6.68 * inch, question[:50])
    c.line(PAGE_W / 2, 6.4 * inch, PAGE_W / 2 - 1.8 * inch, 5.5 * inch)
    c.line(PAGE_W / 2, 6.4 * inch, PAGE_W / 2 + 1.8 * inch, 5.5 * inch)
    c.roundRect(MARGIN + 0.2 * inch, 4.7 * inch, 2.8 * inch, 0.8 * inch, 8, stroke=1, fill=0)
    c.roundRect(PAGE_W - MARGIN - 3.0 * inch, 4.7 * inch, 2.8 * inch, 0.8 * inch, 8, stroke=1, fill=0)
    c.setFont(FONT_BOLD, 10.5)
    c.drawCentredString(MARGIN + 1.6 * inch, 5.05 * inch, choices[0][:38])
    c.drawCentredString(PAGE_W - MARGIN - 1.6 * inch, 5.05 * inch, choices[-1][:38])
    c.setFont(FONT_REGULAR, 9.5)
    c.drawCentredString(MARGIN + 1.6 * inch, 4.85 * inch, "Keep good and safe promises")
    c.drawCentredString(PAGE_W - MARGIN - 1.6 * inch, 4.85 * inch, "Safety comes first")
    c.roundRect(MARGIN, 2.4 * inch, PAGE_W - 2 * MARGIN, 1.8 * inch, 8, stroke=1, fill=0)
    c.setFont(FONT_BOLD, 12)
    c.drawString(MARGIN + 0.2 * inch, 3.85 * inch, "Family promise card")
    c.setFont(FONT_REGULAR, 10.5)
    c.drawString(MARGIN + 0.2 * inch, 3.5 * inch, "One promise I can keep with care:")
    c.line(MARGIN + 0.2 * inch, 3.15 * inch, PAGE_W - MARGIN - 0.2 * inch, 3.15 * inch)
    c.line(MARGIN + 0.2 * inch, 2.8 * inch, PAGE_W - MARGIN - 0.2 * inch, 2.8 * inch)
    _wrapped(c, guidance, MARGIN + 0.2 * inch, 2.65 * inch, PAGE_W - 2 * MARGIN - 0.4 * inch, 9.5, 11)
    if activity.completion_prompt:
        c.setFont(FONT_BOLD, 10.5)
        c.drawString(MARGIN, 1.1 * inch, activity.completion_prompt[:110])


def _render_matching_page(c: Canvas, plan: PlanRow, activity: ActivityPack, page: ActivityPage, y: float) -> None:
    """Render every MatchingCard pair. Never silently truncate; paginate when needed."""
    c.setFont(FONT_BOLD, 12)
    c.drawString(MARGIN, y, "Match each figure to why they came")
    y -= 0.22 * inch
    for step in page.instructions[:4]:
        y = _wrapped(c, f"• {step}", MARGIN, y, PAGE_W - 2 * MARGIN, 10.5, 13)
        y -= 0.02 * inch
    pairs = [item for item in page.components if isinstance(item, MatchingCard)]
    if not pairs:
        comps = [component_label(item) for item in page.components]
        half = max(1, len(comps) // 2)
        pairs = [
            MatchingCard(comps[i], comps[half + i] if half + i < len(comps) else f"Match {i + 1}", "story", pair_id=chr(65 + i))
            for i in range(min(half, len(comps)))
        ]
    # Stable IDs on the left; shuffle rights without dropping any pair.
    left_items = [(p.pair_id or chr(65 + i), p.left) for i, p in enumerate(pairs)]
    right_items = list(pairs)
    # Deterministic shuffle by reverse + rotate so answers are not in printed left order.
    if len(right_items) > 1:
        right_items = list(reversed(right_items))
        right_items = right_items[1:] + right_items[:1]

    per_page = 5
    remaining_left = left_items
    remaining_right = [(p.pair_id or "", p.right) for p in right_items]
    first = True
    while remaining_left or remaining_right:
        if not first:
            c.showPage()
            y = _header(c, plan, activity, c.getPageNumber(), page.page_title)
            y = _story_box(c, page.story_connection or activity.story_connection, y)
            y -= 0.15 * inch
            c.setFont(FONT_BOLD, 11)
            c.drawString(MARGIN, y, "Match continued")
            y -= 0.25 * inch
        first = False
        batch_left = remaining_left[:per_page]
        batch_right = remaining_right[:per_page]
        remaining_left = remaining_left[per_page:]
        remaining_right = remaining_right[per_page:]
        row_h = 0.95 * inch if len(batch_left) >= 5 else 1.1 * inch
        top = min(y - 0.1 * inch, 6.35 * inch)
        c.setDash(4, 3)
        for i, (pair_id, label) in enumerate(batch_left):
            yy = top - i * row_h
            c.roundRect(MARGIN, yy, 3.15 * inch, row_h - 0.12 * inch, 8, stroke=1, fill=0)
            c.setFont(FONT_BOLD, 10)
            c.drawString(MARGIN + 0.12 * inch, yy + row_h - 0.32 * inch, f"{pair_id}.")
            _wrapped_font(c, label, MARGIN + 0.4 * inch, yy + row_h - 0.32 * inch, 2.55 * inch, font=FONT_BOLD, size=10.5, leading=12)
        for i, (_pair_id, label) in enumerate(batch_right):
            yy = top - i * row_h
            c.roundRect(PAGE_W / 2 + 0.1 * inch, yy, 3.15 * inch, row_h - 0.12 * inch, 8, stroke=1, fill=0)
            _wrapped_font(
                c, label, PAGE_W / 2 + 0.25 * inch, yy + row_h - 0.32 * inch, 2.85 * inch,
                font=FONT_BOLD, size=10.5, leading=12,
            )
        c.setDash()
        if remaining_left or remaining_right:
            continue
        if activity.safety_note:
            c.setFont(FONT_BOLD, 10)
            c.drawString(MARGIN, 0.85 * inch, activity.safety_note[:110])
        ages = activity.age_variants or {}
        younger = _strip_age_prefix(ages.get("ages_6_8", "draw lines or cut-and-match."))
        older = _strip_age_prefix(ages.get("ages_9_13", "write one reason for each match."))
        # Page-1 matching must never leak lotus-petal instructions.
        if "lotus" in younger.lower() or "petal" in younger.lower():
            younger = "draw lines or cut-and-match."
        if "lotus" in older.lower() or "petal" in older.lower():
            older = "write one reason for each match."
        note = f"Younger: {younger}  Older: {older}"
        _wrapped(c, note[:160], MARGIN, 1.15 * inch, PAGE_W - 2 * MARGIN, 9.5, 11)


def _render_role_page(c: Canvas, plan: PlanRow, activity: ActivityPack, page: ActivityPage, y: float) -> None:
    cards = [item for item in page.components if isinstance(item, RolePlayCard)]
    for index, card in enumerate(cards[:5]):
        row, col = divmod(index, 2)
        x = MARGIN + col * 3.65 * inch
        yy = 6.35 * inch - row * 1.65 * inch
        c.roundRect(x, yy, 3.3 * inch, 1.4 * inch, 8, stroke=1, fill=0)
        c.setFont(FONT_BOLD, 11)
        c.drawString(x + 0.12 * inch, yy + 1.12 * inch, card.role[:35])
        c.setFont(FONT_REGULAR, 9.5)
        _wrapped(c, f'Line: “{card.line}”', x + 0.12 * inch, yy + 0.87 * inch, 3.0 * inch, 9.5, 11)
        _wrapped(c, f"Action: {card.action}", x + 0.12 * inch, yy + 0.48 * inch, 3.0 * inch, 9.5, 11)
        c.drawString(x + 0.12 * inch, yy + 0.12 * inch, f"Prop: {card.prop}"[:52])


def _render_family_mission(c: Canvas, plan: PlanRow, activity: ActivityPack, page: ActivityPage, y: float) -> None:
    c.setFont(FONT_BOLD, 12)
    c.drawString(MARGIN, y, "Family mission")
    y -= 0.3 * inch
    for step in page.instructions:
        y = _wrapped(c, f"• {step}", MARGIN, y, PAGE_W - 2 * MARGIN)
        y -= 0.05 * inch
    c.roundRect(MARGIN, 3.2 * inch, PAGE_W - 2 * MARGIN, 2.4 * inch, 10, stroke=1, fill=0)
    c.setFont(FONT_BOLD, 14)
    c.drawCentredString(PAGE_W / 2, 5.2 * inch, "Today's kindness from the story")
    c.setFont(FONT_REGULAR, 11)
    c.drawString(MARGIN + 0.3 * inch, 4.7 * inch, "We will: _______________________________________________")
    c.drawString(MARGIN + 0.3 * inch, 4.2 * inch, "Because the story taught us: ____________________________")
    c.rect(MARGIN + 0.3 * inch, 3.5 * inch, 0.28 * inch, 0.28 * inch, stroke=1, fill=0)
    c.drawString(MARGIN + 0.7 * inch, 3.55 * inch, "Done together")
    if activity.review_questions:
        c.setFont(FONT_BOLD, 10.5)
        c.drawString(MARGIN, 2.5 * inch, "Talk about it:")
        yy = 2.25 * inch
        for q in activity.review_questions[:2]:
            yy = _wrapped(c, f"• {q}", MARGIN, yy, PAGE_W - 2 * MARGIN)
            yy -= 0.08 * inch


def _render_story_map(c: Canvas, plan: PlanRow, activity: ActivityPack, page: ActivityPage, y: float) -> None:
    labels = [component_label(item) for item in page.components[:3]] or ["Beginning", "Turning point", "Lesson"]
    for i, label in enumerate(labels):
        yy = 6.5 * inch - i * 1.7 * inch
        c.roundRect(MARGIN, yy, PAGE_W - 2 * MARGIN, 1.4 * inch, 8, stroke=1, fill=0)
        c.setFont(FONT_BOLD, 12)
        c.drawString(MARGIN + 0.2 * inch, yy + 1.05 * inch, label)
        c.setFont(FONT_REGULAR, 10)
        c.drawString(MARGIN + 0.2 * inch, yy + 0.7 * inch, "Write or draw what happened:")


def _render_path(c: Canvas, plan: PlanRow, activity: ActivityPack, page: ActivityPage, y: float) -> None:
    comps = [component_label(item) for item in page.components] or ["Start", "Clue 1", "Clue 2", "Turning point", "Kind choice", "Finish"]
    c.setFont(FONT_BOLD, 11)
    c.drawString(MARGIN, y, "Trace the path through the pastime")
    for i, label in enumerate(comps[:6]):
        row, col = divmod(i, 2)
        x = MARGIN + col * 3.65 * inch
        yy = 6.3 * inch - row * 1.4 * inch
        c.roundRect(x, yy, 3.25 * inch, 1.05 * inch, 8, stroke=1, fill=0)
        c.circle(x + 0.35 * inch, yy + 0.52 * inch, 0.18 * inch, stroke=1, fill=0)
        c.setFont(FONT_BOLD, 11)
        c.drawString(x + 0.7 * inch, yy + 0.48 * inch, label)
        if i < 5:
            c.setFont(FONT_BOLD, 14)
            c.drawString(x + 3.0 * inch if col == 0 else x - 0.25 * inch, yy + 0.2 * inch, ">")


def _render_word_search_page(c: Canvas, plan: PlanRow, activity: ActivityPack, page: ActivityPage, y: float) -> None:
    from .word_search import build_word_search

    words = [component_label(item) for item in page.components] or ["Krishna", "prayer", "truth", "faith", "promise", "devotee"]
    puzzle = build_word_search(words)
    c.setFont(FONT_BOLD, 12)
    c.drawString(MARGIN, y, "Find these story words:")
    c.setFont(FONT_REGULAR, 10.5)
    c.drawString(MARGIN, y - 0.25 * inch, ", ".join(puzzle.placed_words))
    start_y = 6.8 * inch
    cell = 0.32 * inch
    for r, row in enumerate(puzzle.grid):
        for col, ch in enumerate(row):
            x = MARGIN + col * cell
            yy = start_y - r * cell
            c.rect(x, yy, cell, cell, stroke=1, fill=0)
            c.setFont(FONT_BOLD, 9)
            c.drawCentredString(x + cell / 2, yy + 0.08 * inch, ch)
    c.setFont(FONT_REGULAR, 10.5)
    c.drawString(MARGIN, 1.4 * inch, "Circle one word and tell why it matters in this pastime.")


def _render_draw_reflect(c: Canvas, plan: PlanRow, activity: ActivityPack, page: ActivityPage, y: float) -> None:
    for step in page.instructions[:3]:
        y = _wrapped(c, f"• {step}", MARGIN, y, PAGE_W - 2 * MARGIN)
        y -= 0.05 * inch
    c.rect(MARGIN, 2.4 * inch, PAGE_W - 2 * MARGIN, 3.6 * inch, stroke=1, fill=0)
    c.setFont(FONT_REGULAR, 10)
    c.drawCentredString(PAGE_W / 2, 5.8 * inch, "Draw the central story moment here")
    c.drawString(MARGIN, 1.9 * inch, "One sentence reflection: _______________________________________________")


def _render_emotion_map(c: Canvas, plan: PlanRow, activity: ActivityPack, page: ActivityPage, y: float) -> None:
    for step in page.instructions[:3]:
        y = _wrapped(c, f"• {step}", MARGIN, y, PAGE_W - 2 * MARGIN)
        y -= 0.04 * inch
    box_y, box_h, gap = 3.25 * inch, 2.7 * inch, 0.25 * inch
    box_w = (PAGE_W - 2 * MARGIN - gap) / 2
    for index, (heading, prompt) in enumerate((
        ("FEAR — Kaṁsa", "Draw or write what fear made Kaṁsa do."),
        ("FAITH — Devakī and Vasudeva", "Draw or write how they remembered the Lord."),
    )):
        x = MARGIN + index * (box_w + gap)
        c.roundRect(x, box_y, box_w, box_h, 8, stroke=1, fill=0)
        c.setFont(FONT_BOLD, 12)
        c.drawCentredString(x + box_w / 2, box_y + box_h - 0.35 * inch, heading)
        _wrapped(c, prompt, x + 0.15 * inch, box_y + box_h - 0.68 * inch, box_w - 0.3 * inch, 10, 12)
        c.line(x + 0.18 * inch, box_y + 0.55 * inch, x + box_w - 0.18 * inch, box_y + 0.55 * inch)
    reflection = component_label(page.components[0]) if page.components else "How can faith and wise help guide you when you feel afraid?"
    c.setFont(FONT_BOLD, 10.5)
    _wrapped(c, reflection, MARGIN, 2.75 * inch, PAGE_W - 2 * MARGIN, 10.5, 13)
    c.line(MARGIN, 2.15 * inch, PAGE_W - MARGIN, 2.15 * inch)
    c.setFont(FONT_REGULAR, 10)
    c.drawString(MARGIN, 1.8 * inch, "A trusted adult I can ask for help: _________________________________")


def _render_sequence_page(c: Canvas, plan: PlanRow, activity: ActivityPack, page: ActivityPage, y: float) -> None:
    labels = [component_label(item) for item in page.components] or ["Event 1", "Event 2", "Event 3", "Event 4", "Event 5", "Event 6"]
    for step in page.instructions[:2]:
        y = _wrapped(c, f"• {step}", MARGIN, y, PAGE_W - 2 * MARGIN)
        y -= 0.04 * inch
    c.setDash(4, 3)
    for i, label in enumerate(labels[:6]):
        row, col = divmod(i, 2)
        x = MARGIN + col * 3.65 * inch
        yy = 6.0 * inch - row * 1.55 * inch
        c.roundRect(x, yy, 3.25 * inch, 1.25 * inch, 8, stroke=1, fill=0)
        c.setDash()
        c.rect(x + 0.12 * inch, yy + 0.7 * inch, 0.36 * inch, 0.36 * inch, stroke=1, fill=0)
        _wrapped_font(c, label, x + 0.6 * inch, yy + 0.88 * inch, 2.5 * inch,
                      font=FONT_BOLD, size=9.5, leading=11)
        c.setFont(FONT_REGULAR, 9.5)
        c.drawString(x + 0.6 * inch, yy + 0.45 * inch, "Number + draw one detail")
        c.setDash(4, 3)
    c.setDash()


def _render_discussion(c: Canvas, plan: PlanRow, activity: ActivityPack, page: ActivityPage, y: float) -> None:
    questions = [component_label(item) for item in page.components] or activity.review_questions or ["What was the kind choice?", "How can we practice it?"]
    for i, q in enumerate(questions[:4], 1):
        c.setFont(FONT_BOLD, 11)
        c.drawString(MARGIN, y, f"{i}. {q}")
        y -= 0.25 * inch
        c.line(MARGIN, y, PAGE_W - MARGIN, y)
        y -= 0.45 * inch


def _render_generic_cards(
    c: Canvas, plan: PlanRow, activity: ActivityPack, page: ActivityPage, y: float, prompt: str = "Draw or write a story-specific clue."
) -> None:
    labels = [component_label(item) for item in page.components[:6]] or ["Card 1", "Card 2", "Card 3", "Card 4", "Card 5", "Card 6"]
    for step in page.instructions[:2]:
        y = _wrapped(c, f"• {step}", MARGIN, y, PAGE_W - 2 * MARGIN)
        y -= 0.04 * inch
    c.setDash(4, 3)
    for i, label in enumerate(labels):
        row, col = divmod(i, 2)
        x = MARGIN + col * 3.65 * inch
        yy = 5.75 * inch - row * 1.55 * inch
        c.roundRect(x, yy, 3.25 * inch, 1.18 * inch, 8, stroke=1, fill=0)
        c.setFont(FONT_BOLD, 12)
        c.drawString(x + 0.16 * inch, yy + 0.82 * inch, label[:34])
        c.setFont(FONT_REGULAR, 10)
        c.drawString(x + 0.16 * inch, yy + 0.5 * inch, prompt[:42])
    c.setDash()


# --- Rich legacy layouts retained and extended ---

def _strip_age_prefix(text: str) -> str:
    value = (text or "").strip()
    for prefix in ("Younger:", "Older:", "Family:"):
        if value.lower().startswith(prefix.lower()):
            value = value[len(prefix):].strip()
    return value


def _render_lotus_prayer_page(c: Canvas, plan: PlanRow, a: ActivityPack, page: ActivityPage) -> None:
    """Render a real five-petal lotus around a center circle."""
    import math

    page_no = c.getPageNumber()
    y = _header(c, plan, a, page_no, page.page_title)
    y = _story_box(c, page.story_connection or a.story_connection, y)
    y -= 0.12 * inch
    for instruction in page.instructions[:4]:
        y = _wrapped(c, f"• {instruction}", MARGIN, y, PAGE_W - 2 * MARGIN, 10.5, 13)
        y -= 0.03 * inch
    petals = [component_label(item) for item in page.components]
    if not petals:
        petals = [
            "Someone to protect",
            "A fear I can offer",
            "Something I am thankful for",
            "One kind action",
            "A prayer for the world",
        ]
    petals = petals[:5]
    cx = PAGE_W / 2
    cy = 4.35 * inch
    outer_r = 2.55 * inch
    petal_rx = 1.15 * inch
    petal_ry = 0.78 * inch
    c.setStrokeColorRGB(0.12, 0.12, 0.12)
    c.setLineWidth(1.4)
    # Five petals around center (point-up flower).
    for idx, label in enumerate(petals):
        angle = math.radians(-90 + idx * 72)
        px = cx + math.cos(angle) * (outer_r * 0.62)
        py = cy + math.sin(angle) * (outer_r * 0.62)
        c.saveState()
        c.translate(px, py)
        c.rotate(-90 + idx * 72)
        c.setDash(3, 2)
        c.ellipse(-petal_rx, -petal_ry, petal_rx, petal_ry, stroke=1, fill=0)
        c.setDash()
        c.setFont(FONT_BOLD, 8.5)
        _wrapped_font(c, label, -0.95 * inch, 0.15 * inch, 1.9 * inch, font=FONT_BOLD, size=8.5, leading=10)
        c.setFont(FONT_REGULAR, 8)
        c.drawCentredString(0, -0.35 * inch, "draw or write")
        c.restoreState()
    # Center circle
    c.setDash()
    c.circle(cx, cy, 0.85 * inch, stroke=1, fill=0)
    c.setFont(FONT_BOLD, 11)
    c.drawCentredString(cx, cy + 0.12 * inch, "My Lotus")
    c.drawCentredString(cx, cy - 0.12 * inch, "Prayer")
    younger = _strip_age_prefix((a.age_variants or {}).get("ages_6_8", "draw inside each lotus petal."))
    older = _strip_age_prefix((a.age_variants or {}).get("ages_9_13", "write one or two sentences in each petal."))
    if "match" in younger.lower():
        younger = "draw inside each lotus petal."
    if "match" in older.lower():
        older = "write one or two sentences in each petal."
    note = f"Younger: {younger}  Older: {older}  Family: discuss one chosen petal together."
    _wrapped(c, note, MARGIN, 1.15 * inch, PAGE_W - 2 * MARGIN, 10)
    c.showPage()


def _render_prayer_wheel(c: Canvas, plan: PlanRow, a: ActivityPack) -> None:
    y = _header(c, plan, a, 1)
    c.setFont(FONT_BOLD, 12)
    c.drawString(MARGIN, y, "Make a prayer like Mother Earth, Brahma, and the demigods")
    y = _wrapped(
        c,
        "Story link: Mother Earth cared for people, animals, and the world. Brahma led the demigods in prayer to Lord Vishnu.",
        MARGIN, y - 18, PAGE_W - 2 * MARGIN,
    )
    c.setFont(FONT_BOLD, 10.5)
    c.drawString(MARGIN, y - 3, "1. Write or draw   2. Cut dotted outlines   3. Put petal tips behind center   4. Glue and share")
    story_y = 8.15 * inch
    story_boxes = ["Mother Earth as a sacred cow", "Brahma leads the prayers", "Vishnu promises Krishna will come"]
    c.setDash()
    for idx, story_step in enumerate(story_boxes):
        x = MARGIN + idx * 2.48 * inch
        c.roundRect(x, story_y, 2.1 * inch, 0.55 * inch, 5, stroke=1, fill=0)
        _wrapped_font(
            c,
            story_step,
            x + 0.08 * inch,
            story_y + 0.36 * inch,
            1.94 * inch,
            font=FONT_BOLD,
            size=8,
            leading=9.5,
        )
        if idx < 2:
            c.setFont(FONT_BOLD, 14)
            c.drawString(x + 2.18 * inch, story_y + 0.18 * inch, ">")
            c.setFont(FONT_BOLD, 9)
    prompts = ["My family", "Animals", "Mother Earth", "Someone who feels sad", "My community", "My special prayer"]
    c.setDash(3, 3)
    c.setLineWidth(1)
    for idx, label in enumerate(prompts):
        row, col = divmod(idx, 3)
        px = (1.52 + col * 2.73) * inch
        py = (6.75 - row * 1.4) * inch
        c.ellipse(px - 1.05 * inch, py - 0.55 * inch, px + 1.05 * inch, py + 0.55 * inch, stroke=1, fill=0)
        c.setFont(FONT_BOLD, 10)
        c.drawCentredString(px, py + 4, label)
        c.setDash()
        c.line(px - 0.7 * inch, py - 0.18 * inch, px + 0.7 * inch, py - 0.18 * inch)
        c.setDash(3, 3)
        c.setFont(FONT_REGULAR, 8.5)
        c.drawCentredString(px, py - 0.38 * inch, "write a sentence or draw")
    c.setDash()
    c.setLineWidth(1.5)
    cx, cy, radius = 2.15 * inch, 3.65 * inch, 0.72 * inch
    c.circle(cx, cy, radius, stroke=1, fill=0)
    c.setFont(FONT_BOLD, 11)
    c.drawCentredString(cx, cy + 6, "My Prayer")
    c.drawCentredString(cx, cy - 8, "for the World")
    c.setFont(FONT_REGULAR, 8.5)
    c.drawCentredString(cx, cy - 0.38 * inch, "CUT OUT CENTER")
    ex, ey = 5.75 * inch, 3.65 * inch
    for idx in range(6):
        angle = math.radians(idx * 60)
        px, py = ex + math.cos(angle) * 0.72 * inch, ey + math.sin(angle) * 0.72 * inch
        c.ellipse(px - 0.38 * inch, py - 0.22 * inch, px + 0.38 * inch, py + 0.22 * inch, stroke=1, fill=0)
    c.circle(ex, ey, 0.38 * inch, stroke=1, fill=0)
    c.setFont(FONT_BOLD, 9.5)
    c.drawCentredString(ex, ey - 1.2 * inch, "FINISHED EXAMPLE - PETAL TIPS GO BEHIND CENTER")
    c.setFont(FONT_BOLD, 10.5)
    c.drawString(MARGIN, 1.22 * inch, a.safety_note)
    review = a.review_questions[0] if a.review_questions else "How did prayer show care?"
    _wrapped(c, "Ages 6-8: draw.  Ages 9-13: write one sentence.  Talk: " + review, MARGIN, 0.98 * inch, PAGE_W - 2 * MARGIN, 10)
    c.showPage()


def _render_cut_and_build(c: Canvas, plan: PlanRow, a: ActivityPack) -> None:
    y = _header(c, plan, a, 1)
    c.setFont(FONT_BOLD, 11)
    c.drawString(MARGIN, y, "Color first. Cut on dotted lines. Fold on solid lines.")
    c.setFont(FONT_BOLD, 9.5)
    c.setDash(4, 3)
    c.line(MARGIN, y - 0.25 * inch, MARGIN + 0.7 * inch, y - 0.25 * inch)
    c.setDash()
    c.drawString(MARGIN + 0.78 * inch, y - 0.29 * inch, "CUT")
    c.line(MARGIN + 1.35 * inch, y - 0.25 * inch, MARGIN + 2.05 * inch, y - 0.25 * inch)
    c.drawString(MARGIN + 2.13 * inch, y - 0.29 * inch, "FOLD")
    c.setDash(4, 3)
    body = (1.25 * inch, 4.65 * inch, 5.2 * inch, 2.1 * inch)
    c.roundRect(*body, 12, stroke=1, fill=0)
    c.setFont(FONT_BOLD, 15)
    c.drawCentredString(PAGE_W / 2, 5.85 * inch, "CHARIOT BODY")
    c.setFont(FONT_REGULAR, 10)
    c.drawCentredString(PAGE_W / 2, 5.55 * inch, "Decorate with flower garlands")
    for x in (2.2 * inch, 5.8 * inch):
        c.circle(x, 3.85 * inch, 0.65 * inch, stroke=1, fill=0)
        c.circle(x, 3.85 * inch, 0.13 * inch, stroke=1, fill=0)
        c.setFont(FONT_BOLD, 10)
        c.drawCentredString(x, 3.08 * inch, "WHEEL")
    c.wedge(2.55 * inch, 6.9 * inch, 5.95 * inch, 8.75 * inch, 0, 180, stroke=1, fill=0)
    c.setFont(FONT_BOLD, 11)
    c.drawCentredString(PAGE_W / 2, 7.43 * inch, "CANOPY")
    c.setDash()
    c.line(1.55 * inch, 5.07 * inch, 6.95 * inch, 5.07 * inch)
    c.setFont(FONT_REGULAR, 9)
    c.drawString(1.6 * inch, 5.13 * inch, "SOLID FOLD LINE")
    c.setFont(FONT_BOLD, 10.5)
    c.drawString(MARGIN, 1.55 * inch, a.safety_note)
    c.setFont(FONT_REGULAR, 10)
    c.drawString(MARGIN, 1.28 * inch, "Finished example: canopy above body, two wheels below, Kamsa in front; Devaki and Vasudeva behind.")
    ex, ey = 4.25 * inch, 3.55 * inch
    c.setLineWidth(1.2)
    c.rect(ex - 0.72 * inch, ey - 0.2 * inch, 1.44 * inch, 0.55 * inch, stroke=1, fill=0)
    c.wedge(ex - 0.6 * inch, ey + 0.2 * inch, ex + 0.6 * inch, ey + 0.95 * inch, 0, 180, stroke=1, fill=0)
    c.circle(ex - 0.43 * inch, ey - 0.3 * inch, 0.2 * inch, stroke=1, fill=0)
    c.circle(ex + 0.43 * inch, ey - 0.3 * inch, 0.2 * inch, stroke=1, fill=0)
    c.setFont(FONT_BOLD, 8.5)
    c.drawCentredString(ex, ey - 0.65 * inch, "FINISHED CHARIOT")
    c.setDash(3, 3)
    for strip_x in (1.55 * inch, 5.0 * inch):
        c.roundRect(strip_x, 2.1 * inch, 1.95 * inch, 0.55 * inch, 5, stroke=1, fill=0)
        c.setDash()
        for flower in range(6):
            c.circle(strip_x + (0.2 + flower * 0.31) * inch, 2.42 * inch, 0.1 * inch, stroke=1, fill=0)
        c.setFont(FONT_BOLD, 8)
        c.drawCentredString(strip_x + 0.975 * inch, 2.18 * inch, "FLOWER GARLAND STRIP")
        c.setDash(3, 3)
    c.showPage()

    y = _header(c, plan, a, 2)
    c.setDash()
    c.roundRect(MARGIN, 8.15 * inch, PAGE_W - 2 * MARGIN, 0.55 * inch, 6, stroke=1, fill=0)
    c.setFont(FONT_BOLD, 10.5)
    c.drawCentredString(PAGE_W / 2, 8.47 * inch, "TURNING POINT: The heavenly voice changes joy to fear - Vasudeva responds calmly.")
    labels = [
        ("KAMSA", "adult charioteer"),
        ("DEVAKI", "adult royal bride"),
        ("VASUDEVA", "adult noble groom"),
    ]
    c.setDash(4, 3)
    for i, (name, role) in enumerate(labels):
        x = MARGIN + i * 2.35 * inch
        c.roundRect(x, 6.25 * inch, 1.85 * inch, 1.55 * inch, 8, stroke=1, fill=0)
        c.setFont(FONT_BOLD, 11)
        c.drawCentredString(x + 0.925 * inch, 7.4 * inch, name)
        c.setFont(FONT_REGULAR, 8)
        c.drawCentredString(x + 0.925 * inch, 7.18 * inch, role)
        c.drawCentredString(x + 0.925 * inch, 7.04 * inch, "behind" if name != "KAMSA" else "front")
        c.circle(x + 0.925 * inch, 6.82 * inch, 0.12 * inch, stroke=1, fill=0)
        c.line(x + 0.55 * inch, 6.6 * inch, x + 1.3 * inch, 6.6 * inch)
        c.line(x + 0.55 * inch, 6.6 * inch, x + 0.72 * inch, 6.38 * inch)
        c.line(x + 1.3 * inch, 6.6 * inch, x + 1.13 * inch, 6.38 * inch)
        c.setDash()
        c.setStrokeColorRGB(0.2, 0.2, 0.2)
        c.setDash(1, 2)
        c.line(x + 0.2 * inch, 6.32 * inch, x + 1.65 * inch, 6.32 * inch)
        c.setDash()
        c.setFont(FONT_REGULAR, 7.5)
        c.drawCentredString(x + 0.925 * inch, 6.08 * inch, "fold base")
        c.setDash(4, 3)
    events = ["The wedding celebration", "The chariot procession", "The heavenly voice", "Vasudeva protects Devaki"]
    for i, event in enumerate(events):
        row, col = divmod(i, 2)
        x = MARGIN + col * 3.65 * inch
        yy = 4.9 * inch - row * 1.22 * inch
        c.roundRect(x, yy, 3.25 * inch, 0.88 * inch, 6, stroke=1, fill=0)
        c.setDash()
        c.rect(x + 0.12 * inch, yy + 0.25 * inch, 0.36 * inch, 0.36 * inch, stroke=1, fill=0)
        c.setFont(FONT_BOLD, 10)
        c.drawString(x + 0.58 * inch, yy + 0.48 * inch, event)
        c.setFont(FONT_REGULAR, 10)
        c.drawString(x + 0.58 * inch, yy + 0.25 * inch, "Write the event number in the box")
        c.setDash(4, 3)
    c.setDash()
    c.setFont(FONT_BOLD, 11)
    c.drawString(MARGIN, 2.1 * inch, "Assembly steps")
    yy = 1.88 * inch
    for idx, step in enumerate(a.instructions[:5], 1):
        c.setFont(FONT_REGULAR, 10)
        c.drawString(MARGIN, yy, f"{idx}. {step[:95]}")
        yy -= 0.18 * inch
    c.showPage()
