from collections import Counter
from html import escape
from io import BytesIO
from uuid import UUID

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from backend.database.repository import EvaluationRepository
from backend.models.results import EvaluationResult
from backend.services.analytics_service import outcome_for_score


class BatchReportService:
    """Builds a paginated, evidence-rich PDF from persisted batch results."""

    def __init__(self, repository: EvaluationRepository) -> None:
        self.repository = repository

    def create_pdf(self, batch_id: UUID) -> tuple[bytes, str]:
        batch = self.repository.get_batch(batch_id)
        results = self.repository.get_batch_results(batch_id)
        if batch is None:
            raise LookupError("Batch not found.")
        if not results:
            raise ValueError("This batch has no successful evaluations to report.")

        stream = BytesIO()
        document = SimpleDocTemplate(
            stream,
            pagesize=A4,
            rightMargin=18 * mm,
            leftMargin=18 * mm,
            topMargin=20 * mm,
            bottomMargin=18 * mm,
            title=f"Evaluation report - {batch['batch_name']}",
            author="Evidence Lab",
        )
        styles = self._styles()
        story = self._build_story(batch, results, styles)
        document.build(story, onFirstPage=self._footer, onLaterPages=self._footer)
        safe_name = "-".join(str(batch["batch_name"]).lower().split())[:60] or "batch"
        return stream.getvalue(), f"{safe_name}-evaluation-report.pdf"

    @staticmethod
    def _styles():
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name="ReportTitle", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=25, leading=30, textColor=colors.HexColor("#14213D"), spaceAfter=10))
        styles.add(ParagraphStyle(name="Section", parent=styles["Heading2"], fontName="Helvetica-Bold", fontSize=14, leading=18, textColor=colors.HexColor("#2447D8"), spaceBefore=12, spaceAfter=8))
        styles.add(ParagraphStyle(name="Subsection", parent=styles["Heading3"], fontName="Helvetica-Bold", fontSize=11, leading=14, textColor=colors.HexColor("#172033"), spaceBefore=8, spaceAfter=4))
        styles.add(ParagraphStyle(name="BodySmall", parent=styles["BodyText"], fontSize=8.5, leading=12, textColor=colors.HexColor("#46546A"), spaceAfter=5))
        styles.add(ParagraphStyle(name="TableHeader", parent=styles["BodyText"], fontName="Helvetica-Bold", fontSize=8.5, leading=11, textColor=colors.white))
        styles.add(ParagraphStyle(name="Metric", parent=styles["BodyText"], alignment=TA_CENTER, fontName="Helvetica-Bold", fontSize=15, leading=18, textColor=colors.HexColor("#172033")))
        return styles

    def _build_story(self, batch: dict, results: list[EvaluationResult], styles) -> list:
        story: list = [
            Paragraph("LLM Response Evaluation Report", styles["ReportTitle"]),
            Paragraph(escape(str(batch["batch_name"])), styles["Heading2"]),
            Paragraph(
                f"System/source: <b>{escape(str(batch.get('system_name') or 'Not specified'))}</b><br/>"
                f"Generated from stored results | Batch ID: {batch['batch_id']} | Created: {batch['created_at']}",
                styles["BodySmall"],
            ),
            Spacer(1, 5 * mm),
        ]
        averages = self._averages(results)
        outcomes = Counter(outcome_for_score(result.verdict.overall_score) for result in results)
        claims = sum(len(result.hallucination.claims) for result in results)
        unsupported = sum(result.hallucination.unsupported_claims + result.hallucination.contradicted_claims for result in results)
        metrics = [
            ("Responses", str(len(results))),
            ("Average score", f"{averages['overall']:.1f}"),
            ("Pass", str(outcomes["pass"])),
            ("Needs improvement", str(outcomes["needs_improvement"])),
            ("Fail", str(outcomes["fail"])),
            ("Unsupported claims", f"{unsupported}/{claims}"),
        ]
        story.append(self._metric_table(metrics, styles))
        story.extend([Paragraph("Dimension breakdown", styles["Section"]), self._dimension_table(averages, styles)])
        story.extend([Paragraph("Recurring issues and recommendations", styles["Section"])])
        for recommendation in self._recommendations(results, averages):
            story.append(Paragraph(f"- {escape(recommendation)}", styles["BodyText"]))
        story.append(PageBreak())
        story.append(Paragraph("Individual evaluation details", styles["Section"]))
        for index, result in enumerate(results, start=1):
            story.extend(self._result_section(index, result, styles))
            if index < len(results):
                story.append(PageBreak())
        return story

    @staticmethod
    def _averages(results: list[EvaluationResult]) -> dict[str, float]:
        values = {
            "relevance": [result.relevance.score or 0 for result in results],
            "accuracy": [result.accuracy.score or 0 for result in results],
            "groundedness": [result.hallucination.score or 0 for result in results],
            "completeness": [result.completeness.score or 0 for result in results],
            "overall": [result.verdict.overall_score for result in results],
        }
        return {key: sum(scores) / len(scores) for key, scores in values.items()}

    @staticmethod
    def _metric_table(metrics, styles):
        cells = [[Paragraph(label, styles["BodySmall"]), Paragraph(value, styles["Metric"])] for label, value in metrics]
        table = Table(cells, colWidths=[45 * mm, 45 * mm], hAlign="LEFT")
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F4F6FA")),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#DCE2EC")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#DCE2EC")),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 7),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ]))
        return table

    @staticmethod
    def _dimension_table(averages, styles):
        rows = [[Paragraph("Dimension", styles["TableHeader"]), Paragraph("Average / 100", styles["TableHeader"])]]
        rows.extend([[Paragraph(name.title(), styles["BodyText"]), f"{value:.1f}"] for name, value in averages.items()])
        table = Table(rows, colWidths=[95 * mm, 45 * mm], repeatRows=1)
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2447D8")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#DCE2EC")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8F9FC")]),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]))
        return table

    @staticmethod
    def _recommendations(results: list[EvaluationResult], averages: dict[str, float]) -> list[str]:
        recommendations: list[str] = []
        if averages["relevance"] < 70:
            recommendations.append("Make responses address the question directly before adding background detail.")
        if averages["accuracy"] < 70:
            recommendations.append("Verify factual claims against the retrieved evidence before finalizing responses.")
        if averages["groundedness"] < 70:
            recommendations.append("Remove or qualify claims that cannot be traced to a supplied or retrieved source.")
        if averages["completeness"] < 70:
            recommendations.append("Use a short coverage checklist so every requested aspect is answered.")
        if any(result.hallucination.unsupported_claims for result in results):
            recommendations.append("Prioritize the recurring unsupported claims shown in the detailed section for targeted review.")
        return recommendations or ["Maintain the current evidence-grounded response process and continue monitoring new batches."]

    @staticmethod
    def _result_section(index: int, result: EvaluationResult, styles) -> list:
        package = result.evidence_package
        story: list = [
            Paragraph(f"{index}. {escape(package.question)}", styles["Subsection"]),
            Paragraph(f"<b>AI response:</b> {escape(package.ai_response)}", styles["BodySmall"]),
        ]
        scores = [
            ["Relevance", "Accuracy", "Groundedness", "Completeness", "Overall / verdict"],
            [
                f"{result.relevance.score or 0:.1f}", f"{result.accuracy.score or 0:.1f}",
                f"{result.hallucination.score or 0:.1f}", f"{result.completeness.score or 0:.1f}",
                f"{result.verdict.overall_score:.1f} / {result.verdict.verdict.replace('_', ' ')}",
            ],
        ]
        table = Table(scores, colWidths=[30 * mm, 30 * mm, 30 * mm, 30 * mm, 43 * mm], repeatRows=1)
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E9EEFF")),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD4E3")),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("FONTSIZE", (0, 0), (-1, -1), 7.5),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]))
        story.extend([table, Spacer(1, 3 * mm)])
        for name, agent in (("Relevance", result.relevance), ("Accuracy", result.accuracy), ("Hallucination", result.hallucination), ("Completeness", result.completeness)):
            story.append(KeepTogether([
                Paragraph(name, styles["Subsection"]),
                Paragraph(escape(agent.explanation), styles["BodySmall"]),
            ]))
        unsupported = [claim for claim in result.hallucination.claims if claim.status != "supported"]
        if unsupported:
            story.append(Paragraph("Unsupported or contradicted claims", styles["Subsection"]))
            for claim in unsupported:
                story.append(Paragraph(f"- <b>{escape(claim.status.title())}:</b> {escape(claim.claim)} - {escape(claim.explanation)}", styles["BodySmall"]))
        if result.completeness.missing_aspects:
            story.append(Paragraph("Missing aspects", styles["Subsection"]))
            for aspect in result.completeness.missing_aspects:
                story.append(Paragraph(f"- {escape(aspect)}", styles["BodySmall"]))
        evidence = (package.source_text_evidence + package.retrieved_evidence)[:3]
        if package.reference_answer:
            story.append(Paragraph("Reference answer", styles["Subsection"]))
            story.append(Paragraph(escape(package.reference_answer), styles["BodySmall"]))
        if evidence:
            story.append(Paragraph("Supporting evidence", styles["Subsection"]))
            for chunk in evidence:
                story.append(Paragraph(
                    f"- {escape(chunk.text)}<br/><font color='#667085'>Source: {escape(chunk.source)} | Chunk: {escape(chunk.chunk_id)}</font>",
                    styles["BodySmall"],
                ))
        story.append(Paragraph(f"<b>Weighted verdict:</b> {escape(result.verdict.explanation)}", styles["BodySmall"]))
        return story

    @staticmethod
    def _footer(canvas, document) -> None:
        canvas.saveState()
        canvas.setStrokeColor(colors.HexColor("#DCE2EC"))
        canvas.line(18 * mm, 14 * mm, A4[0] - 18 * mm, 14 * mm)
        canvas.setFont("Helvetica", 7.5)
        canvas.setFillColor(colors.HexColor("#667085"))
        canvas.drawString(18 * mm, 9 * mm, "Evidence Lab - explainable evaluation report")
        canvas.drawRightString(A4[0] - 18 * mm, 9 * mm, f"Page {document.page}")
        canvas.restoreState()
