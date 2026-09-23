import re
from dataclasses import dataclass, field
from typing import Any

from backend.datasets.normalizer import NormalizedDocument
from backend.rag.cleaner import clean_text


TOKEN_PATTERN = re.compile(r"\S+")


@dataclass(frozen=True)
class TextChunk:
    chunk_id: str
    text: str
    dataset: str
    document_id: str
    source: str
    metadata: dict[str, Any] = field(default_factory=dict)


class Chunker:
    """Whitespace-token chunker that preserves the original text and metadata."""

    def __init__(self, chunk_size: int, chunk_overlap: int) -> None:
        if chunk_size <= 0 or chunk_overlap < 0 or chunk_overlap >= chunk_size:
            raise ValueError("Require chunk_size > chunk_overlap >= 0")
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_text(
        self,
        text: str,
        *,
        document_id: str,
        source: str,
        dataset: str = "user_source",
        metadata: dict[str, Any] | None = None,
    ) -> list[TextChunk]:
        cleaned = clean_text(text)
        matches = list(TOKEN_PATTERN.finditer(cleaned))
        if not matches:
            return []
        step = self.chunk_size - self.chunk_overlap
        chunks: list[TextChunk] = []
        for chunk_number, start in enumerate(range(0, len(matches), step)):
            window = matches[start : start + self.chunk_size]
            if not window:
                break
            chunk_text = cleaned[window[0].start() : window[-1].end()]
            chunks.append(
                TextChunk(
                    chunk_id=f"{dataset}:{document_id}:{chunk_number}",
                    text=chunk_text,
                    dataset=dataset,
                    document_id=document_id,
                    source=source,
                    metadata={**(metadata or {}), "chunk_index": chunk_number},
                )
            )
            if start + self.chunk_size >= len(matches):
                break
        return chunks

    def chunk_document(self, document: NormalizedDocument) -> list[TextChunk]:
        metadata = {
            **document.metadata,
            "original_question": document.question,
            "reference_answer": document.answer,
        }
        return self.chunk_text(
            document.context,
            document_id=document.document_id,
            source=document.source,
            dataset=document.dataset,
            metadata=metadata,
        )

