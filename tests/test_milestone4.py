from io import BytesIO
from pathlib import Path
from uuid import uuid4

from pypdf import PdfReader

from backend.database.repository import EvaluationRepository
from backend.models.evaluation import EvidencePackage, RetrievalMetadata
from backend.models.results import AgentResult, CompletenessResult, EvaluationResult, HallucinationResult, VerdictResult
from backend.services.analytics_service import AnalyticsService, outcome_for_score
from backend.services.batch_service import parse_csv_records
from backend.services.report_service import BatchReportService


def make_result(score: float, *, missing: bool = False, unsupported: int = 0) -> EvaluationResult:
    evaluation_id = uuid4()
    package = EvidencePackage(
        evaluation_id=evaluation_id,
        question="What is retrieval-augmented generation?",
        ai_response="It grounds a response in retrieved evidence.",
        reference_answer="RAG retrieves evidence before generation.",
        evidence_source_type="reference_answer",
        retrieval_metadata=RetrievalMetadata(query="What is RAG?", requested_top_k=5, returned_count=0),
    )
    result = AgentResult(agent="relevance", score=score, label="good", explanation="Traceable explanation")
    return EvaluationResult(
        evaluation_id=evaluation_id,
        evidence_package=package,
        relevance=result,
        accuracy=result.model_copy(update={"agent": "accuracy"}),
        hallucination=HallucinationResult(
            agent="hallucination", score=score, label="good", explanation="Grounding checked",
            hallucination_rate=unsupported / max(unsupported, 1), unsupported_claims=unsupported,
        ),
        completeness=CompletenessResult(
            agent="completeness", score=score, label="good", explanation="Coverage checked",
            missing_aspects=["deployment limitations"] if missing else [],
        ),
        verdict=VerdictResult(
            overall_score=score,
            verdict="strong" if score >= 80 else "acceptable" if score >= 70 else "needs_review" if score >= 45 else "poor",
            explanation="Weighted result from four dimensions.",
            weights={"relevance": 0.25, "accuracy": 0.25, "groundedness": 0.25, "completeness": 0.25},
            component_scores={"relevance": score, "accuracy": score, "groundedness": score, "completeness": score},
        ),
    )


def test_csv_parser_keeps_valid_rows_and_reports_invalid_rows() -> None:
    csv_text = "question,ai_response,reference_answer,source_text\nValid question,Valid response,,\n,Missing question,,"
    records, failures = parse_csv_records(csv_text)
    assert len(records) == 1
    assert records[0]["question"] == "Valid question"
    assert len(failures) == 1
    assert failures[0].row_number == 3


def test_csv_parser_rejects_missing_required_headers() -> None:
    try:
        parse_csv_records("prompt,response\nHello,World")
    except ValueError as exc:
        assert "required columns" in str(exc)
    else:
        raise AssertionError("Missing columns must be rejected")


def test_dashboard_math_filters_and_batch_trend(tmp_path: Path) -> None:
    repository = EvaluationRepository(tmp_path / "analytics.db")
    batch_id = uuid4()
    repository.create_batch(batch_id, "Comparison batch", "System A", "2026-09-26T10:00:00+00:00")
    for result in (make_result(90), make_result(60, missing=True, unsupported=1), make_result(30)):
        repository.save(result)
        repository.assign_batch(result.evaluation_id, batch_id, "Comparison batch", "System A")
    summary = AnalyticsService(repository).summarize()
    assert summary.total_evaluations == 3
    assert summary.average_scores["overall"] == 60
    assert summary.outcomes.counts == {"pass": 1, "needs_improvement": 1, "fail": 1}
    assert summary.score_distributions["overall"] == {"0-39": 1, "40-59": 0, "60-79": 1, "80-100": 1}
    assert summary.hallucination.responses_with_issues == 1
    assert summary.completeness.total_missing_aspects == 1
    assert summary.batch_trends[0].average_scores["overall"] == 60
    assert AnalyticsService(repository).summarize(verdict="pass").total_evaluations == 1


def test_outcome_boundaries() -> None:
    assert outcome_for_score(70) == "pass"
    assert outcome_for_score(45) == "needs_improvement"
    assert outcome_for_score(44.99) == "fail"


def test_pdf_report_contains_stored_batch_content(tmp_path: Path) -> None:
    repository = EvaluationRepository(tmp_path / "report.db")
    batch_id = uuid4()
    repository.create_batch(batch_id, "PDF validation", "System B", "2026-09-26T10:00:00+00:00")
    result = make_result(82, missing=True, unsupported=1)
    repository.save(result)
    repository.assign_batch(result.evaluation_id, batch_id, "PDF validation", "System B")
    content, filename = BatchReportService(repository).create_pdf(batch_id)
    reader = PdfReader(BytesIO(content))
    text = "\n".join(page.extract_text() or "" for page in reader.pages)
    assert filename.endswith(".pdf")
    assert len(reader.pages) >= 2
    assert "LLM Response Evaluation Report" in text
    assert "PDF validation" in text
    assert "Individual evaluation details" in text
