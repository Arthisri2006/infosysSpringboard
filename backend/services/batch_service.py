import csv
import io
from collections import Counter
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from pydantic import ValidationError

from backend.database.repository import EvaluationRepository
from backend.models.evaluation import EvaluationInput, PrepareEvaluationRequest
from backend.models.results import (
    BatchEvaluationResponse,
    BatchFailure,
    BatchSummary,
    EvaluationResult,
)
from backend.orchestrator.evaluation_orchestrator import EvaluationOrchestrator
from backend.services.analytics_service import outcome_for_score


CSV_COLUMNS = ("question", "ai_response", "reference_answer", "source_text")


def parse_csv_records(csv_text: str) -> tuple[list[dict[str, Any]], list[BatchFailure]]:
    """Parse CSV rows while retaining row-level errors for failure isolation."""
    if not csv_text.strip():
        raise ValueError("The CSV file is empty.")
    reader = csv.DictReader(io.StringIO(csv_text.lstrip("\ufeff")))
    headers = {header.strip() for header in (reader.fieldnames or []) if header}
    missing = {"question", "ai_response"} - headers
    if missing:
        raise ValueError(f"CSV is missing required columns: {', '.join(sorted(missing))}.")
    records: list[dict[str, Any]] = []
    failures: list[BatchFailure] = []
    for row_number, row in enumerate(reader, start=2):
        record = {key: (row.get(key) or "").strip() or None for key in CSV_COLUMNS}
        try:
            validated = PrepareEvaluationRequest.model_validate(record)
            records.append(validated.model_dump())
        except ValidationError as exc:
            message = exc.errors()[0].get("msg", "Invalid row")
            failures.append(
                BatchFailure(row_number=row_number, error=message, question=record.get("question"))
            )
    return records, failures


class BatchEvaluationService:
    """Runs batch evaluations independently so one invalid item does not stop the batch."""

    def __init__(self, orchestrator: EvaluationOrchestrator, repository: EvaluationRepository) -> None:
        self.orchestrator = orchestrator
        self.repository = repository

    def evaluate(
        self,
        items: list[dict[str, Any]],
        *,
        batch_name: str | None = None,
        system_name: str | None = None,
        initial_failures: list[BatchFailure] | None = None,
    ) -> BatchEvaluationResponse:
        batch_id = uuid4()
        clean_name = (batch_name or f"Batch {datetime.now().strftime('%Y-%m-%d %H:%M')}").strip()
        clean_system = system_name.strip() if system_name and system_name.strip() else None
        created_at = datetime.now(timezone.utc).isoformat()
        self.repository.create_batch(batch_id, clean_name, clean_system, created_at)
        results: list[EvaluationResult] = []
        failures = list(initial_failures or [])
        for index, item in enumerate(items, start=1):
            try:
                payload = PrepareEvaluationRequest.model_validate(item)
                result = self.orchestrator.evaluate(EvaluationInput(**payload.model_dump()))
                self.repository.assign_batch(result.evaluation_id, batch_id, clean_name, clean_system)
                results.append(result)
            except (ValidationError, ValueError, RuntimeError) as exc:
                message = exc.errors()[0].get("msg", "Invalid item") if isinstance(exc, ValidationError) else str(exc)
                failures.append(
                    BatchFailure(row_number=index, error=message, question=str(item.get("question") or "") or None)
                )
        return BatchEvaluationResponse(
            batch_id=batch_id,
            batch_name=clean_name,
            system_name=clean_system,
            results=results,
            failures=failures,
            summary=self._summarize(results, len(failures)),
        )

    @staticmethod
    def _summarize(results: list[EvaluationResult], failed_count: int) -> BatchSummary:
        dimensions = ("relevance", "accuracy", "groundedness", "completeness", "overall")
        if not results:
            averages = {name: 0.0 for name in dimensions}
        else:
            def score(result: EvaluationResult, dimension: str) -> float:
                return float(
                    result.relevance.score if dimension == "relevance"
                    else result.accuracy.score if dimension == "accuracy"
                    else result.hallucination.score if dimension == "groundedness"
                    else result.completeness.score if dimension == "completeness"
                    else result.verdict.overall_score
                    or 0.0
                )
            averages = {
                name: round(sum(score(result, name) for result in results) / len(results), 2)
                for name in dimensions
            }
        return BatchSummary(
            count=len(results),
            failed_count=failed_count,
            average_scores=averages,
            verdict_counts=dict(Counter(result.verdict.verdict for result in results)),
            outcome_counts=dict(Counter(outcome_for_score(result.verdict.overall_score) for result in results)),
        )
