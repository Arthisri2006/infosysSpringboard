from fastapi.testclient import TestClient

from backend.main import app
from backend.models.evaluation import EvidencePackage, RetrievalMetadata
from backend.models.results import (
    AgentResult,
    CompletenessResult,
    DashboardSummary,
    EvaluationResult,
    HallucinationResult,
    VerdictResult,
)


class StubEvidenceService:
    def prepare(self, evaluation):
        return EvidencePackage(
            evaluation_id=evaluation.id,
            question=evaluation.question,
            ai_response=evaluation.ai_response,
            reference_answer=evaluation.reference_answer,
            evidence_source_type="reference_answer" if evaluation.reference_answer else "none",
            retrieval_metadata=RetrievalMetadata(
                query=evaluation.question,
                requested_top_k=5,
                returned_count=0,
            ),
        )


def completed_result(evaluation) -> EvaluationResult:
    package = StubEvidenceService().prepare(evaluation)
    return EvaluationResult(
        evaluation_id=evaluation.id,
        evidence_package=package,
        relevance=AgentResult(agent="relevance", score=80, label="good", explanation="Relevant."),
        accuracy=AgentResult(agent="accuracy", score=100, label="excellent", explanation="Supported."),
        hallucination=HallucinationResult(
            agent="hallucination", score=100, label="excellent", explanation="Grounded."
        ),
        completeness=CompletenessResult(
            agent="completeness", score=100, label="excellent", explanation="Complete."
        ),
        verdict=VerdictResult(
            overall_score=96,
            verdict="strong",
            explanation="Weighted result.",
            weights={"relevance": 0.2, "accuracy": 0.35, "groundedness": 0.25, "completeness": 0.2},
            component_scores={"relevance": 80, "accuracy": 100, "groundedness": 100, "completeness": 100},
        ),
    )


class StubOrchestrator:
    def evaluate(self, evaluation):
        return completed_result(evaluation)


class StubRepository:
    def dashboard(self, limit):
        return DashboardSummary(
            total_evaluations=0,
            average_scores={},
            verdict_counts={},
            recent_evaluations=[],
        )


client = TestClient(app)


def test_local_127_origin_is_allowed() -> None:
    response = client.options(
        "/api/v1/evaluations/prepare",
        headers={
            "Origin": "http://127.0.0.1:3000",
            "Access-Control-Request-Method": "POST",
        },
    )
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://127.0.0.1:3000"


def test_missing_question_is_rejected() -> None:
    response = client.post("/api/v1/evaluations/prepare", json={"ai_response": "An answer"})
    assert response.status_code == 422


def test_missing_ai_response_is_rejected() -> None:
    response = client.post("/api/v1/evaluations/prepare", json={"question": "A question?"})
    assert response.status_code == 422


def test_blank_required_fields_are_rejected() -> None:
    response = client.post(
        "/api/v1/evaluations/prepare", json={"question": "  ", "ai_response": "answer"}
    )
    assert response.status_code == 422


def test_valid_reference_and_source_are_accepted(monkeypatch) -> None:
    monkeypatch.setattr("backend.api.evaluation.get_evidence_service", lambda: StubEvidenceService())
    response = client.post(
        "/api/v1/evaluations/prepare",
        json={
            "question": "  What is RAG? ",
            "ai_response": " A grounded generation method. ",
            "reference_answer": " Retrieval augmented generation. ",
            "source_text": " A source passage. ",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ready_for_evaluation"
    assert body["evidence_package"]["question"] == "What is RAG?"
    assert body["evidence_package"]["reference_answer"] == "Retrieval augmented generation."


def test_evaluate_endpoint_returns_structured_verdict(monkeypatch) -> None:
    monkeypatch.setattr(
        "backend.api.evaluation.get_evaluation_orchestrator", lambda: StubOrchestrator()
    )
    response = client.post(
        "/api/v1/evaluations/evaluate",
        json={"question": "Who first walked on the Moon?", "ai_response": "Neil Armstrong."},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "completed"
    assert body["result"]["verdict"]["overall_score"] == 96
    assert body["result"]["hallucination"]["claims"] == []


def test_dashboard_endpoint_returns_persisted_summary(monkeypatch) -> None:
    monkeypatch.setattr(
        "backend.api.evaluation.get_evaluation_repository", lambda: StubRepository()
    )
    response = client.get("/api/v1/evaluations/dashboard")
    assert response.status_code == 200
    assert response.json()["total_evaluations"] == 0
