from datetime import datetime, timezone
from typing import Any, Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator


class PrepareEvaluationRequest(BaseModel):
    question: str = Field(min_length=1, max_length=20_000)
    ai_response: str = Field(min_length=1, max_length=100_000)
    reference_answer: str | None = Field(default=None, max_length=100_000)
    source_text: str | None = Field(default=None, max_length=1_000_000)

    @field_validator("question", "ai_response", mode="before")
    @classmethod
    def required_text_must_not_be_blank(cls, value: Any) -> Any:
        if isinstance(value, str):
            value = value.strip()
            if not value:
                raise ValueError("field cannot be blank")
        return value

    @field_validator("reference_answer", "source_text", mode="before")
    @classmethod
    def normalize_optional_text(cls, value: Any) -> Any:
        if isinstance(value, str):
            value = value.strip()
            return value or None
        return value


class EvaluationInput(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    question: str
    ai_response: str
    reference_answer: str | None = None
    source_text: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class EvidenceChunk(BaseModel):
    chunk_id: str
    text: str
    source: str
    dataset: str | None = None
    document_id: str
    similarity_score: float | None = None
    distance: float | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class RetrievalMetadata(BaseModel):
    query: str
    requested_top_k: int
    returned_count: int
    collection: str | None = None
    benchmark_retrieval_attempted: bool = False
    warnings: list[str] = Field(default_factory=list)


EvidenceSourceType = Literal[
    "reference_answer", "source_text", "knowledge_base", "combined", "none"
]


class EvidencePackage(BaseModel):
    evaluation_id: UUID
    question: str
    ai_response: str
    reference_answer: str | None = None
    evidence_source_type: EvidenceSourceType
    retrieved_evidence: list[EvidenceChunk] = Field(default_factory=list)
    source_text_evidence: list[EvidenceChunk] = Field(default_factory=list)
    retrieval_metadata: RetrievalMetadata


class PrepareEvaluationResponse(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    status: Literal["ready_for_evaluation"] = "ready_for_evaluation"
    message: str = "Evidence preparation complete. Ready for Milestone 2 evaluation agents."
    evidence_package: EvidencePackage

