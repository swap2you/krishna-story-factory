from __future__ import annotations

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Image as RLImage
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from ..models import PlanRow, StoryContent
from .word_search import WordSearchPuzzle, build_word_search


class ActivitySheetGenerator:
    def generate(
        self,
        plan: PlanRow,
        content: StoryContent,
        output_path,
        *,
        coloring_page_path: Path | None = None,
    ) -> WordSearchPuzzle:
        puzzle = build_word_search(content.word_search_words)
        doc = SimpleDocTemplate(
            str(output_path),
            pagesize=letter,
            rightMargin=0.6 * inch,
            leftMargin=0.6 * inch,
            topMargin=0.55 * inch,
            bottomMargin=0.55 * inch,
        )
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            "TitleCustom",
            parent=styles["Title"],
            fontName="Helvetica-Bold",
            fontSize=18,
            leading=22,
            textColor=colors.HexColor("#4b2e16"),
            spaceAfter=8,
        )
        h2 = ParagraphStyle(
            "H2Custom",
            parent=styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=12,
            leading=15,
            textColor=colors.HexColor("#5d3a1a"),
            spaceBefore=10,
            spaceAfter=6,
        )
        body = ParagraphStyle("BodyCustom", parent=styles["BodyText"], fontSize=10.5, leading=14)

        page1: list = []
        page1.append(Paragraph("Krishna Book Bedtime Activity Sheet", title_style))
        page1.append(Paragraph(f"<b>{content.title}</b>", body))
        page1.append(Paragraph(f"Source: {plan.source_reference}", body))
        page1.append(Spacer(1, 6))
        page1.append(Paragraph("Today's Krishna-katha recap", h2))
        page1.append(Paragraph(content.recap, body))
        page1.append(Paragraph("Recall questions", h2))
        for i, q in enumerate(content.recall_questions[:3], start=1):
            page1.append(Paragraph(f"{i}. {q}", body))
            page1.append(Paragraph("_" * 72, body))
            page1.append(Spacer(1, 4))
        page1.append(Paragraph("Thinking questions", h2))
        for i, q in enumerate(content.thinking_questions[:2], start=1):
            page1.append(Paragraph(f"{i}. {q}", body))
            page1.append(Paragraph("_" * 72, body))
            page1.append(Spacer(1, 4))

        page2: list = [PageBreak()]
        page2.append(Paragraph("Word search", h2))
        page2.append(Paragraph("Find these words in the grid:", body))
        page2.append(Paragraph(", ".join(puzzle.placed_words), body))
        page2.append(Spacer(1, 6))
        page2.append(_grid_table(puzzle))
        page2.append(Spacer(1, 8))
        page2.append(Paragraph("Drawing prompt", h2))
        page2.append(Paragraph(content.draw_activity or "Draw your favorite scene from the story.", body))
        draw_box = Table([[""]], colWidths=[6.5 * inch], rowHeights=[1.8 * inch])
        draw_box.setStyle(TableStyle([("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#8a5a2b"))]))
        page2.append(draw_box)

        page3: list = [PageBreak()]
        page3.append(Paragraph("Coloring and family activity", h2))
        if coloring_page_path and coloring_page_path.exists():
            page3.append(RLImage(str(coloring_page_path), width=5.5 * inch, height=5.5 * inch))
        else:
            prompt = content.coloring_page_prompt or content.line_art_prompt
            page3.append(Paragraph("Coloring prompt", h2))
            page3.append(Paragraph(prompt or "Color the main scene from tonight's story.", body))
            color_box = Table([[""]], colWidths=[6.5 * inch], rowHeights=[2.2 * inch])
            color_box.setStyle(TableStyle([("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#8a5a2b"))]))
            page3.append(color_box)
        page3.append(Spacer(1, 8))
        page3.append(Paragraph("Family craft / game", h2))
        page3.append(Paragraph(content.family_activity or "Do one kind service together as a family.", body))
        page3.append(Spacer(1, 8))
        page3.append(Paragraph("Five-star challenge", h2))
        for i, item in enumerate(content.five_star_challenge[:5], start=1):
            page3.append(Paragraph(f"☐ Star {i}: {item}", body))
        page3.append(Spacer(1, 10))
        page3.append(
            Paragraph(
                "<b>Parent note:</b> Please reply here with a photo, audio, or short video after completion.",
                body,
            )
        )

        doc.build(page1 + page2 + page3)
        return puzzle


def _grid_table(puzzle: WordSearchPuzzle) -> Table:
    size = len(puzzle.grid)
    cell = 0.42 * inch
    data = [[letter for letter in row] for row in puzzle.grid]
    table = Table(data, colWidths=[cell] * size, rowHeights=[cell] * size)
    table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#8a5a2b")),
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#fffdf5")),
            ]
        )
    )
    return table
