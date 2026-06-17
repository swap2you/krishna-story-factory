from __future__ import annotations

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from ..models import PlanRow, StoryContent


class ActivitySheetGenerator:
    def generate(self, plan: PlanRow, content: StoryContent, output_path) -> None:
        doc = SimpleDocTemplate(
            str(output_path),
            pagesize=letter,
            rightMargin=0.55 * inch,
            leftMargin=0.55 * inch,
            topMargin=0.5 * inch,
            bottomMargin=0.5 * inch,
        )
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            "TitleCustom",
            parent=styles["Title"],
            fontName="Helvetica-Bold",
            fontSize=20,
            leading=24,
            textColor=colors.HexColor("#4b2e16"),
            spaceAfter=10,
        )
        h2 = ParagraphStyle(
            "H2Custom",
            parent=styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=13,
            leading=16,
            textColor=colors.HexColor("#5d3a1a"),
            spaceBefore=8,
            spaceAfter=5,
        )
        body = ParagraphStyle(
            "BodyCustom",
            parent=styles["BodyText"],
            fontSize=10.5,
            leading=14,
        )

        story = []
        story.append(Paragraph("Krishna Bedtime Activity Sheet", title_style))
        story.append(Paragraph(f"Story: <b>{content.title}</b>", body))
        story.append(Paragraph(f"Source: {plan.source_reference}", body))
        story.append(Spacer(1, 8))

        story.append(Paragraph("1. Quick Recap", h2))
        story.append(Paragraph(content.recap, body))

        story.append(Paragraph("2. Answer in one sentence", h2))
        questions = content.activity_questions or [
            "What happened in the story?",
            "Who showed devotion?",
            "What did Krishna teach us?",
            "What was your favorite part?",
            "What service can you do today?",
        ]
        for i, question in enumerate(questions[:5], start=1):
            story.append(Paragraph(f"{i}. {question}", body))
            story.append(Paragraph("____________________________________________________________", body))
            story.append(Spacer(1, 3))

        story.append(Paragraph("3. Five-Star Challenge", h2))
        for i, item in enumerate(content.five_star_challenge[:5], start=1):
            story.append(Paragraph(f"☐ Star {i}: {item}", body))

        story.append(Paragraph("4. Devotional Vocabulary", h2))
        vocab = content.vocabulary_words or ["Krishna", "bhakti", "service", "prasadam", "Vrindavana"]
        rows = [[Paragraph("Word", body), Paragraph("Meaning / drawing", body)]]
        for word in vocab[:5]:
            rows.append([Paragraph(word, body), Paragraph("____________________________________", body)])
        table = Table(rows, colWidths=[1.6 * inch, 5.1 * inch])
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f5e0b7")),
                    ("BOX", (0, 0), (-1, -1), 0.75, colors.HexColor("#8a5a2b")),
                    ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#c7a36b")),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 6),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                    ("TOPPADDING", (0, 0), (-1, -1), 6),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ]
            )
        )
        story.append(table)

        story.append(Paragraph("5. Draw the scene", h2))
        story.append(Paragraph("Draw Krishna, the devotee, or the moment you liked most.", body))
        draw_box = Table([[""]], colWidths=[6.7 * inch], rowHeights=[1.8 * inch])
        draw_box.setStyle(TableStyle([("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#8a5a2b"))]))
        story.append(draw_box)

        story.append(Spacer(1, 8))
        story.append(Paragraph("Parent sign: ______________________   Child name: ______________________", body))
        doc.build(story)
