from pathlib import Path

from backend.database.repository import EvaluationRepository
from backend.models.evaluation import EvidencePackage, RetrievalMetadata
from backend.models.results import (
    AgentResult,
    CompletenessResult,
    EvaluationResult,
    HallucinationResult,
    VerdictResult,
)


def test_repository_saves_result_and_builds_dashboard(tmp_path: Path) -> None:
    package = EvidencePackage(
        evaluation_id="11111111-1111-1111-1111-111111111111",
        question="What is RAG?",
        ai_response="Retrieval augmented generation.",
        reference_answer="Retrieval augmented generation.",
        evidence_source_type="reference_answer",
        retrieval_metadata=RetrievalMetadata(query="What is RAG?", requested_top_k=5, returned_count=0),
    )
    base = AgentResult(agent="relevance", score=90, label="excellent", explanation="test")
    result = EvaluationResult(
        evaluation_id=package.evaluation_id,
        evidence_package=package,
        relevance=base,
        accuracy=base.model_copy(update={"agent": "accuracy"}),
        hallucination=HallucinationResult(
            agent="hallucination", score=100, label="excellent", explanation="test", hallucination_rate=0
        ),
        completeness=CompletenessResult(
            agent="completeness", score=100, label="excellent", explanation="test"
        ),
        verdict=VerdictResult(
            overall_score=95,
            verdict="strong",
            explanation="test",
            weights={"relevance": 1},
            component_scores={"relevance": 90},
        ),
    )
    repository = EvaluationRepository(tmp_path / "evaluations.db")
    repository.save(result)
    assert repository.get(result.evaluation_id) is not None
    dashboard = repository.dashboard()
    assert dashboard.total_evaluations == 1
    assert dashboard.average_scores["overall"] == 95
