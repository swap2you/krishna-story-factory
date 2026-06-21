from __future__ import annotations

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from ..models import PlanRow, StoryContent
from .word_search import WordSearchPuzzle, build_word_search


class ActivitySheetGenerator:
    def generate(self, plan: PlanRow, content: StoryContent, output_path) -> WordSearchPuzzle:
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
        page1.append(Paragraph(f"<b>{content.title}</b>", title_style))
        page1.append(Paragraph(f"Source: {plan.source_reference}", body))
        page1.append(Spacer(1, 6))
        page1.append(Paragraph("Recap", h2))
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
        reflection = content.bedtime_reflection or content.takeaway
        page1.append(Paragraph("Bedtime reflection", h2))
        page1.append(Paragraph(reflection, body))

        page2: list = [PageBreak()]
        page2.append(Paragraph("Word search", h2))
        page2.append(Paragraph("Find these words:", body))
        page2.append(Paragraph(", ".join(puzzle.placed_words), body))
        page2.append(Spacer(1, 6))
        page2.append(_grid_table(puzzle))
        page2.append(Spacer(1, 8))
        page2.append(Paragraph("Drawing prompt", h2))
        page2.append(Paragraph(content.draw_activity, body))
        page2.append(Spacer(1, 8))
        page2.append(_drawing_box())
        page2.append(Spacer(1, 8))
        page2.append(Paragraph("Family game / craft", h2))
        page2.append(Paragraph(content.family_activity, body))
        page2.append(Spacer(1, 8))
        page2.append(Paragraph("Five-star challenge", h2))
        for i, item in enumerate(content.five_star_challenge[:5], start=1):
            page2.append(Paragraph(f"☐ {i}. {item}", body))
        page2.append(Spacer(1, 8))
        page2.append(Paragraph("Parent reminder: sign and date when your child completes the challenge.", body))

        doc.build(page1 + page2)
        return puzzle


def _grid_table(puzzle: WordSearchPuzzle) -> Table:
    data = [[cell for cell in row] for row in puzzle.grid]
    table = Table(data, colWidths=18, rowHeights=18)
    table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ]
        )
    )
    return table


def _drawing_box() -> Table:
    box = Table([[""]], colWidths=[6.8 * inch], rowHeights=[2.2 * inch])
    box.setStyle(TableStyle([("BOX", (0, 0), (-1, -1), 1, colors.black)]))
    return box
