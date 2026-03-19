from io import BytesIO
from datetime import datetime
from typing import List, Dict, Any

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
)


PAGE_WIDTH, PAGE_HEIGHT = A4


def safe_text(value: Any) -> str:
    if value is None:
        return ""
    text = str(value)
    text = text.replace("&", "&amp;")
    text = text.replace("<", "&lt;")
    text = text.replace(">", "&gt;")
    text = text.replace("\n", "<br/>")
    return text


def build_metric_table(rows: List[List[str]], col_widths=None) -> Table:
    table = Table(rows, colWidths=col_widths, repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#dbeafe")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#94a3b8")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    return table


def build_evaluation_pdf(
    prompt: str,
    results: List[Dict[str, Any]],
    recommendations: Dict[str, Any],
    summary: Dict[str, Any],
) -> bytes:
    """
    Builds a readable A4 PDF report for dashboard evaluation results.
    """
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=1.4 * cm,
        leftMargin=1.4 * cm,
        topMargin=1.4 * cm,
        bottomMargin=1.4 * cm,
    )

    styles = getSampleStyleSheet()

    title_style = styles["Title"]
    heading_style = styles["Heading2"]
    subheading_style = styles["Heading3"]

    body_style = ParagraphStyle(
        name="BodyCustom",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        alignment=TA_LEFT,
        spaceAfter=6,
    )

    muted_style = ParagraphStyle(
        name="Muted",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        textColor=colors.HexColor("#6b7280"),
        spaceAfter=6,
    )

    story = []

    # Header
    story.append(Paragraph("LLM Evaluation Report", title_style))
    story.append(
        Paragraph(
            f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            muted_style,
        )
    )
    story.append(Spacer(1, 0.3 * cm))

    # Prompt section
    story.append(Paragraph("Prompt", heading_style))
    story.append(Paragraph(safe_text(prompt), body_style))
    story.append(Spacer(1, 0.2 * cm))

    # Summary section
    story.append(Paragraph("Summary", heading_style))
    summary_rows = [
        ["Metric", "Value"],
        ["Models Tested", str(summary.get("models_tested", ""))],
        ["Average Latency (s)", str(summary.get("avg_latency", ""))],
        ["Average Quality", str(summary.get("avg_quality", ""))],
        ["Total Estimated Cost ($)", str(summary.get("total_cost", ""))],
    ]
    story.append(build_metric_table(summary_rows, col_widths=[7 * cm, 8 * cm]))
    story.append(Spacer(1, 0.3 * cm))

    # Recommendation section
    story.append(Paragraph("Recommendations", heading_style))
    recommendation_rows = [
        ["Category", "Model"],
        ["Fastest", str(recommendations.get("fastest", "N/A"))],
        ["Cheapest", str(recommendations.get("cheapest", "N/A"))],
        ["Best Quality", str(recommendations.get("best_quality", "N/A"))],
        ["Best Overall", str(recommendations.get("best_overall", "N/A"))],
    ]
    story.append(build_metric_table(recommendation_rows, col_widths=[7 * cm, 8 * cm]))
    story.append(Spacer(1, 0.4 * cm))

    # Model sections
    story.append(Paragraph("Per-Model Evaluation", heading_style))
    story.append(Spacer(1, 0.1 * cm))

    for index, result in enumerate(results):
        model_name = str(result.get("model", "Unknown Model"))
        story.append(Paragraph(model_name, subheading_style))

        metric_rows = [
            ["Metric", "Value"],
            ["Latency (s)", str(result.get("latency_seconds", ""))],
            ["Response Length (words)", str(result.get("response_length_words", ""))],
            ["Estimated Cost ($)", str(result.get("estimated_cost_usd", ""))],
            ["Relevance Score", str(result.get("relevance_score", ""))],
            ["Clarity Score", str(result.get("clarity_score", ""))],
            ["Completeness Score", str(result.get("completeness_score", ""))],
            ["Quality Score", str(result.get("quality_score", ""))],
            ["Overall Score", str(result.get("overall_score", ""))],
        ]
        story.append(build_metric_table(metric_rows, col_widths=[7 * cm, 8 * cm]))
        story.append(Spacer(1, 0.2 * cm))

        story.append(Paragraph("Response", subheading_style))
        story.append(Paragraph(safe_text(result.get("response", "")), body_style))
        story.append(Spacer(1, 0.35 * cm))

        if index < len(results) - 1:
            story.append(PageBreak())

    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes
