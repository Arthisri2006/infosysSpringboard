from fastapi import APIRouter, HTTPException

from backend.models.evaluation import (
    EvaluationInput,
    PrepareEvaluationRequest,
    PrepareEvaluationResponse,
)
from backend.services.evidence_service import get_evidence_service


router = APIRouter(prefix="/api/v1/evaluations", tags=["evaluations"])


@router.post("/prepare", response_model=PrepareEvaluationResponse)
def prepare_evaluation(payload: PrepareEvaluationRequest) -> PrepareEvaluationResponse:
    evaluation = EvaluationInput(**payload.model_dump())
    try:
        evidence_package = get_evidence_service().prepare(evaluation)
    except (ValueError, RuntimeError) as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return PrepareEvaluationResponse(evidence_package=evidence_package)

