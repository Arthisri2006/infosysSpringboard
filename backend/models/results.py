from datetime import datetime, timezone
from typing import Any, Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from backend.models.evaluation import EvidencePackage, PrepareEvaluationRequest


JudgementLabel = Literal["excellent", "good", "mixed", "poor", "unavailable"]
ClaimStatus = Literal["supported", "unsupported", "contradicted"]
VerdictLabel = Literal["strong", "acceptable", "needs_review", "poor"]


class ClaimAssessment(BaseModel):
    claim: str
    status: ClaimStatus
    confidence: float = Field(ge=0.0, le=1.0)
    best_evidence_text: str | None = None
    evidence_chunk_id: str | None = None
    explanation: str


class AgentResult(BaseModel):
    agent: str
    score: float | None = Field(default=None, ge=0.0, le=100.0)
    label: JudgementLabel
    explanation: str
    evidence_chunk_ids: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class HallucinationResult(AgentResult):
    hallucination_rate: float | None = Field(default=None, ge=0.0, le=1.0)
    supported_claims: int = 0
    unsupported_claims: int = 0
    contradicted_claims: int = 0
    claims: list[ClaimAssessment] = Field(default_factory=list)


class CompletenessResult(AgentResult):
    covered_aspects: list[str] = Field(default_factory=list)
    missing_aspects: list[str] = Field(default_factory=list)


class VerdictResult(BaseModel):
    overall_score: float = Field(ge=0.0, le=100.0)
    verdict: VerdictLabel
    explanation: str
    weights: dict[str, float]
    component_scores: dict[str, float | None]


class EvaluationResult(BaseModel):
    evaluation_id: UUID
    status: Literal["completed"] = "completed"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    evidence_package: EvidencePackage
    relevance: AgentResult
    accuracy: AgentResult
    hallucination: HallucinationResult
    completeness: CompletenessResult
    verdict: VerdictResult


class EvaluateResponse(BaseModel):
    status: Literal["completed"] = "completed"
    message: str = "Multi-agent evaluation completed."
    result: EvaluationResult


class BatchEvaluationRequest(BaseModel):
    items: list[dict[str, Any]] = Field(min_length=1, max_length=200)
    batch_name: str | None = Field(default=None, max_length=120)
    system_name: str | None = Field(default=None, max_length=120)


class BatchFailure(BaseModel):
    row_number: int
    error: str
    question: str | None = None


class BatchSummary(BaseModel):
    count: int
    failed_count: int = 0
    average_scores: dict[str, float]
    verdict_counts: dict[str, int]
    outcome_counts: dict[str, int] = Field(default_factory=dict)


class BatchEvaluationResponse(BaseModel):
    batch_id: UUID = Field(default_factory=uuid4)
    status: Literal["completed"] = "completed"
    batch_name: str | None = None
    system_name: str | None = None
    results: list[EvaluationResult]
    failures: list[BatchFailure] = Field(default_factory=list)
    summary: BatchSummary


class EvaluationHistoryItem(BaseModel):
    evaluation_id: UUID
    created_at: datetime
    question: str
    evidence_source_type: str
    relevance_score: float | None
    accuracy_score: float | None
    groundedness_score: float | None
    completeness_score: float | None
    overall_score: float
    verdict: VerdictLabel
    outcome: Literal["pass", "needs_improvement", "fail"] = "fail"
    batch_id: UUID | None = None
    batch_name: str | None = None
    system_name: str | None = None
    issue_tags: list[str] = Field(default_factory=list)


class OutcomeSummary(BaseModel):
    counts: dict[str, int]
    percentages: dict[str, float]


class HallucinationAnalytics(BaseModel):
    responses_with_issues: int = 0
    response_rate: float = 0.0
    unsupported_claims: int = 0
    contradicted_claims: int = 0
    total_claims: int = 0
    unsupported_claim_rate: float = 0.0


class CompletenessAnalytics(BaseModel):
    responses_with_missing_aspects: int = 0
    response_rate: float = 0.0
    total_missing_aspects: int = 0
    frequent_missing_aspects: list[dict[str, Any]] = Field(default_factory=list)


class BatchTrendPoint(BaseModel):
    batch_id: UUID
    batch_name: str
    system_name: str | None = None
    created_at: datetime
    count: int
    average_scores: dict[str, float]
    outcome_counts: dict[str, int]


class DashboardFilters(BaseModel):
    verdict: str | None = None
    min_score: float | None = None
    max_score: float | None = None
    batch_id: UUID | None = None
    system_name: str | None = None


class DashboardSummary(BaseModel):
    total_evaluations: int
    average_scores: dict[str, float]
    verdict_counts: dict[str, int]
    outcomes: OutcomeSummary = Field(
        default_factory=lambda: OutcomeSummary(counts={}, percentages={})
    )
    score_distributions: dict[str, dict[str, int]] = Field(default_factory=dict)
    hallucination: HallucinationAnalytics = Field(default_factory=HallucinationAnalytics)
    completeness: CompletenessAnalytics = Field(default_factory=CompletenessAnalytics)
    frequent_issues: list[dict[str, Any]] = Field(default_factory=list)
    batch_trends: list[BatchTrendPoint] = Field(default_factory=list)
    available_batches: list[dict[str, Any]] = Field(default_factory=list)
    available_systems: list[str] = Field(default_factory=list)
    filters: DashboardFilters = Field(default_factory=DashboardFilters)
    recent_evaluations: list[EvaluationHistoryItem]
