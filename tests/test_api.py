from fastapi.testclient import TestClient

from backend.main import app
from backend.models.evaluation import EvidencePackage, RetrievalMetadata


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
