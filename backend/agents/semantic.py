import re
from dataclasses import dataclass

import numpy as np

from backend.models.evaluation import EvidenceChunk, EvidencePackage
from backend.rag.embeddings import EmbeddingProvider


SENTENCE_BOUNDARY = re.compile(r"(?<=[.!?])\s+|\n+")
NUMBER_PATTERN = re.compile(r"\b\d+(?:\.\d+)?%?\b")
ENTITY_PATTERN = re.compile(r"\b[A-Z][a-z]{2,}\b")
NEGATION_PATTERN = re.compile(r"\b(?:no|not|never|neither|nor|without|cannot|can't|isn't|wasn't|don't|doesn't|didn't)\b", re.I)


def split_sentences(text: str, *, minimum_length: int = 3) -> list[str]:
    """Split natural text into stable claim/aspect units without external NLP downloads."""
    return [part.strip(" -\t") for part in SENTENCE_BOUNDARY.split(text.strip()) if len(part.strip()) >= minimum_length]


def score_label(score: float | None) -> str:
    if score is None:
        return "unavailable"
    if score >= 85:
        return "excellent"
    if score >= 70:
        return "good"
    if score >= 45:
        return "mixed"
    return "poor"


@dataclass(frozen=True)
class EvidenceText:
    text: str
    chunk_id: str


class SemanticAnalyzer:
    """Shared embedding and evidence helpers used by all judge agents."""

    def __init__(self, embeddings: EmbeddingProvider) -> None:
        self.embeddings = embeddings

    def similarity(self, left: str, right: str) -> float:
        matrix = self.similarity_matrix([left], [right])
        return float(matrix[0, 0])

    def similarity_matrix(self, left: list[str], right: list[str]) -> np.ndarray:
        if not left or not right:
            return np.empty((len(left), len(right)))
        vectors = np.asarray(self.embeddings.embed_documents([*left, *right]), dtype=float)
        left_vectors = vectors[: len(left)]
        right_vectors = vectors[len(left) :]
        left_norms = np.maximum(np.linalg.norm(left_vectors, axis=1, keepdims=True), 1e-12)
        right_norms = np.maximum(np.linalg.norm(right_vectors, axis=1, keepdims=True), 1e-12)
        return (left_vectors / left_norms) @ (right_vectors / right_norms).T

    def evidence_texts(self, package: EvidencePackage) -> list[EvidenceText]:
        result: list[EvidenceText] = []
        if package.reference_answer:
            result.append(EvidenceText(package.reference_answer, "direct-reference-answer"))
        for chunk in [*package.source_text_evidence, *package.retrieved_evidence]:
            result.append(EvidenceText(chunk.text, chunk.chunk_id))
        return result

    def required_aspects(self, package: EvidencePackage, limit: int = 8) -> list[str]:
        if package.reference_answer:
            aspects = split_sentences(package.reference_answer)
            return aspects[:limit] or [package.reference_answer]

        candidates: list[str] = []
        seen: set[str] = set()
        for chunk in [*package.source_text_evidence, *package.retrieved_evidence]:
            metadata_answer = chunk.metadata.get("reference_answer")
            texts = [str(metadata_answer)] if metadata_answer else split_sentences(chunk.text)
            for text in texts:
                normalized = text.casefold().strip()
                if text and normalized not in seen:
                    seen.add(normalized)
                    candidates.append(text)
        if not candidates:
            return []
        similarities = self.similarity_matrix([package.question], candidates)[0]
        ranked = sorted(zip(candidates, similarities.tolist()), key=lambda item: item[1], reverse=True)
        return [text for text, _ in ranked[:limit]]


def has_negation(text: str) -> bool:
    return bool(NEGATION_PATTERN.search(text))


def numbers_in(text: str) -> set[str]:
    return set(NUMBER_PATTERN.findall(text))


def named_terms(text: str) -> set[str]:
    """Return capitalized name-like terms while ignoring common sentence starters."""
    ignored = {"The", "This", "That", "These", "Those", "A", "An", "It", "In", "On", "At"}
    return {term.casefold() for term in ENTITY_PATTERN.findall(text) if term not in ignored}


def evidence_chunks(package: EvidencePackage) -> list[EvidenceChunk]:
    return [*package.source_text_evidence, *package.retrieved_evidence]
