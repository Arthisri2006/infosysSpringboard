from collections import Counter
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query

from backend.models.evaluation import (
    EvaluationInput,
    PrepareEvaluationRequest,
    PrepareEvaluationResponse,
)
from backend.services.evidence_service import get_evidence_service
from backend.models.results import (
    BatchEvaluationRequest,
    BatchEvaluationResponse,
    BatchSummary,
    DashboardSummary,
    EvaluateResponse,
    EvaluationResult,
)
from backend.orchestrator.evaluation_orchestrator import (
    get_evaluation_orchestrator,
    get_evaluation_repository,
)


router = APIRouter(prefix="/api/v1/evaluations", tags=["evaluations"])


@router.post("/prepare", response_model=PrepareEvaluationResponse)
def prepare_evaluation(payload: PrepareEvaluationRequest) -> PrepareEvaluationResponse:
    evaluation = EvaluationInput(**payload.model_dump())
    try:
        evidence_package = get_evidence_service().prepare(evaluation)
    except (ValueError, RuntimeError) as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return PrepareEvaluationResponse(evidence_package=evidence_package)


@router.post("/evaluate", response_model=EvaluateResponse)
def evaluate_response(payload: PrepareEvaluationRequest) -> EvaluateResponse:
    evaluation = EvaluationInput(**payload.model_dump())
    try:
        result = get_evaluation_orchestrator().evaluate(evaluation)
    except (ValueError, RuntimeError) as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return EvaluateResponse(result=result)


@router.post("/batch", response_model=BatchEvaluationResponse)
def evaluate_batch(payload: BatchEvaluationRequest) -> BatchEvaluationResponse:
    orchestrator = get_evaluation_orchestrator()
    try:
        results = [
            orchestrator.evaluate(EvaluationInput(**item.model_dump())) for item in payload.items
        ]
    except (ValueError, RuntimeError) as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    dimensions = ("relevance", "accuracy", "groundedness", "completeness", "overall")
    average_scores = {
        dimension: round(
            sum(
                (
                    result.relevance.score
                    if dimension == "relevance"
                    else result.accuracy.score
                    if dimension == "accuracy"
                    else result.hallucination.score
                    if dimension == "groundedness"
                    else result.completeness.score
                    if dimension == "completeness"
                    else result.verdict.overall_score
                )
                or 0.0
                for result in results
            )
            / len(results),
            2,
        )
        for dimension in dimensions
    }
    verdict_counts = Counter(result.verdict.verdict for result in results)
    return BatchEvaluationResponse(
        results=results,
        summary=BatchSummary(
            count=len(results),
            average_scores=average_scores,
            verdict_counts=dict(verdict_counts),
        ),
    )


@router.get("/dashboard", response_model=DashboardSummary)
def dashboard(limit: int = Query(20, ge=1, le=100)) -> DashboardSummary:
    return get_evaluation_repository().dashboard(limit)


@router.get("/{evaluation_id}", response_model=EvaluationResult)
def get_evaluation(evaluation_id: UUID) -> EvaluationResult:
    result = get_evaluation_repository().get(evaluation_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Evaluation not found")
    return result
