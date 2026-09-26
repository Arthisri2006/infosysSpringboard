from datetime import datetime, timezone
from typing import Literal
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
    items: list[PrepareEvaluationRequest] = Field(min_length=1, max_length=50)


class BatchSummary(BaseModel):
    count: int
    average_scores: dict[str, float]
    verdict_counts: dict[str, int]


class BatchEvaluationResponse(BaseModel):
    batch_id: UUID = Field(default_factory=uuid4)
    status: Literal["completed"] = "completed"
    results: list[EvaluationResult]
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


class DashboardSummary(BaseModel):
    total_evaluations: int
    average_scores: dict[str, float]
    verdict_counts: dict[str, int]
    recent_evaluations: list[EvaluationHistoryItem]
