from typing import Any

from pydantic import BaseModel, Field, field_validator

from backend.rag.cleaner import clean_text


class NormalizedDocument(BaseModel):
    dataset: str
    document_id: str
    question: str
    answer: str
    context: str
    source: str
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("dataset", "document_id", "question", "answer", "context", "source")
    @classmethod
    def clean_required_text(cls, value: str) -> str:
        cleaned = clean_text(value)
        if not cleaned:
            raise ValueError("normalized document fields cannot be empty")
        return cleaned


def normalize_squad(record: dict[str, Any]) -> NormalizedDocument:
    answers = record.get("answers") or {}
    answer_values = answers.get("text", []) if isinstance(answers, dict) else []
    answer = answer_values[0] if answer_values else "No reference answer supplied"
    return NormalizedDocument(
        dataset="squad",
        document_id=str(record.get("id") or "unknown"),
        question=str(record.get("question") or ""),
        answer=str(answer),
        context=str(record.get("context") or ""),
        source="Hugging Face: rajpurkar/squad",
        metadata={"title": clean_text(str(record.get("title") or ""))},
    )


def normalize_truthfulqa(record: dict[str, Any], index: int = 0) -> NormalizedDocument:
    question = str(record.get("question") or "")
    correct = record.get("correct_answers") or []
    incorrect = record.get("incorrect_answers") or []
    answer = str(record.get("best_answer") or (correct[0] if correct else ""))
    context = " ".join(part for part in [question, answer] if part)
    return NormalizedDocument(
        dataset="truthful_qa",
        document_id=f"truthfulqa-{index}",
        question=question,
        answer=answer,
        context=context,
        source="Hugging Face: truthful_qa (generation)",
        metadata={
            "category": clean_text(str(record.get("category") or "")),
            "correct_answers": [clean_text(str(item)) for item in correct],
            "incorrect_answers": [clean_text(str(item)) for item in incorrect],
        },
    )
