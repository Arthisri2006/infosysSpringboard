from io import BytesIO
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import StreamingResponse

from backend.models.evaluation import EvaluationInput, PrepareEvaluationRequest, PrepareEvaluationResponse
from backend.models.results import BatchEvaluationRequest, BatchEvaluationResponse, DashboardSummary, EvaluateResponse, EvaluationResult
from backend.orchestrator.evaluation_orchestrator import get_evaluation_orchestrator, get_evaluation_repository
from backend.services.analytics_service import AnalyticsService
from backend.services.batch_service import BatchEvaluationService, parse_csv_records
from backend.services.evidence_service import get_evidence_service
from backend.services.report_service import BatchReportService


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
    service = BatchEvaluationService(get_evaluation_orchestrator(), get_evaluation_repository())
    return service.evaluate(
        payload.items, batch_name=payload.batch_name, system_name=payload.system_name
    )


@router.post("/batch/csv", response_model=BatchEvaluationResponse)
async def evaluate_csv_batch(
    request: Request,
    batch_name: str | None = Query(default=None, max_length=120),
    system_name: str | None = Query(default=None, max_length=120),
) -> BatchEvaluationResponse:
    try:
        text = (await request.body()).decode("utf-8-sig")
        items, failures = parse_csv_records(text)
    except (UnicodeDecodeError, ValueError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    service = BatchEvaluationService(get_evaluation_orchestrator(), get_evaluation_repository())
    return service.evaluate(
        items,
        batch_name=batch_name,
        system_name=system_name,
        initial_failures=failures,
    )


@router.get("/dashboard", response_model=DashboardSummary)
def dashboard(
    limit: int = Query(20, ge=1, le=100),
    verdict: str | None = None,
    min_score: float | None = Query(default=None, ge=0, le=100),
    max_score: float | None = Query(default=None, ge=0, le=100),
    batch_id: UUID | None = None,
    system_name: str | None = None,
) -> DashboardSummary:
    if min_score is not None and max_score is not None and min_score > max_score:
        raise HTTPException(status_code=422, detail="Minimum score cannot exceed maximum score.")
    repository = get_evaluation_repository()
    if not hasattr(repository, "query_rows"):
        return repository.dashboard(limit)
    return AnalyticsService(repository).summarize(
        limit=limit,
        verdict=verdict,
        min_score=min_score,
        max_score=max_score,
        batch_id=batch_id,
        system_name=system_name,
    )


@router.get("/reports/batch/{batch_id}.pdf")
def batch_report(batch_id: UUID) -> StreamingResponse:
    try:
        content, filename = BatchReportService(get_evaluation_repository()).create_pdf(batch_id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return StreamingResponse(
        BytesIO(content),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/{evaluation_id}", response_model=EvaluationResult)
def get_evaluation(evaluation_id: UUID) -> EvaluationResult:
    result = get_evaluation_repository().get(evaluation_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Evaluation not found")
    return result
