from __future__ import annotations

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from ..models import PlanRow, StoryContent


class ActivitySheetGenerator:
    def generate(self, plan: PlanRow, content: StoryContent, output_path) -> None:
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

        page1 = []
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

        page2 = [PageBreak()]
        page2.append(Paragraph("Word search word list", h2))
        words = content.word_search_words[:10] or ["Krishna", "bhakti", "prayer", "devotee", "love"]
        page2.append(Paragraph(", ".join(words), body))
        page2.append(Spacer(1, 8))
        page2.append(Paragraph("Draw or color", h2))
        page2.append(Paragraph(content.draw_activity or "Draw your favorite scene from the story.", body))
        draw_box = Table([[""]], colWidths=[6.5 * inch], rowHeights=[1.6 * inch])
        draw_box.setStyle(TableStyle([("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#8a5a2b"))]))
        page2.append(draw_box)
        page2.append(Spacer(1, 8))
        page2.append(Paragraph("Family activity / craft", h2))
        page2.append(Paragraph(content.family_activity or "Do one kind service together as a family.", body))
        page2.append(Spacer(1, 8))
        page2.append(Paragraph("Five-star challenge", h2))
        for i, item in enumerate(content.five_star_challenge[:5], start=1):
            page2.append(Paragraph(f"☐ Star {i}: {item}", body))
        page2.append(Spacer(1, 10))
        page2.append(
            Paragraph(
                "<b>Parent note:</b> Please send a photo/audio/video after completion.",
                body,
            )
        )
        page2.append(Spacer(1, 6))
        page2.append(Paragraph("Parent sign: ______________________   Child name: ______________________", body))

        doc.build(page1 + page2)
