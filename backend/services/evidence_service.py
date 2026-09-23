from functools import lru_cache
from uuid import uuid4

import numpy as np

from backend.core.config import Settings, get_settings
from backend.models.evaluation import (
    EvaluationInput,
    EvidenceChunk,
    EvidencePackage,
    RetrievalMetadata,
)
from backend.rag.chunker import Chunker, TextChunk
from backend.rag.embeddings import EmbeddingProvider, get_embedding_service
from backend.rag.retriever import SemanticRetriever
from backend.rag.vector_store import ChromaVectorStore


class EvidenceService:
    """Builds provenance-rich evidence packages for future judge agents."""

    def __init__(
        self,
        settings: Settings,
        chunker: Chunker,
        embeddings: EmbeddingProvider,
        retriever: SemanticRetriever,
    ) -> None:
        self.settings = settings
        self.chunker = chunker
        self.embeddings = embeddings
        self.retriever = retriever

    def prepare(self, evaluation: EvaluationInput) -> EvidencePackage:
        source_evidence: list[EvidenceChunk] = []
        retrieved: list[EvidenceChunk] = []
        warnings: list[str] = []
        benchmark_attempted = False

        if evaluation.source_text:
            chunks = self.chunker.chunk_text(
                evaluation.source_text,
                document_id=f"submission-{evaluation.id}",
                source="user-provided source text",
                metadata={"evaluation_id": str(evaluation.id), "temporary": True},
            )
            source_evidence = self._rank_temporary_chunks(evaluation.question, chunks)

        # Benchmark retrieval is the fallback when no direct evidence was supplied.
        if not evaluation.reference_answer and not evaluation.source_text:
            benchmark_attempted = True
            try:
                retrieved = self.retriever.retrieve(evaluation.question, self.settings.top_k)
                if not retrieved:
                    warnings.append(
                        "The benchmark knowledge base is empty. Run the ingestion script before retrieval."
                    )
            except Exception as exc:
                warnings.append(f"Benchmark retrieval was unavailable: {exc}")

        source_types = []
        if evaluation.reference_answer:
            source_types.append("reference_answer")
        if source_evidence:
            source_types.append("source_text")
        if retrieved:
            source_types.append("knowledge_base")
        evidence_source_type = (
            "combined" if len(source_types) > 1 else source_types[0] if source_types else "none"
        )

        return EvidencePackage(
            evaluation_id=evaluation.id,
            question=evaluation.question,
            ai_response=evaluation.ai_response,
            reference_answer=evaluation.reference_answer,
            evidence_source_type=evidence_source_type,
            retrieved_evidence=retrieved,
            source_text_evidence=source_evidence,
            retrieval_metadata=RetrievalMetadata(
                query=evaluation.question,
                requested_top_k=self.settings.top_k,
                returned_count=len(retrieved) + len(source_evidence),
                collection=self.settings.chroma_collection,
                benchmark_retrieval_attempted=benchmark_attempted,
                warnings=warnings,
            ),
        )

    def _rank_temporary_chunks(self, query: str, chunks: list[TextChunk]) -> list[EvidenceChunk]:
        if not chunks:
            return []
        query_vector = np.asarray(self.embeddings.embed_query(query), dtype=float)
        chunk_vectors = np.asarray(self.embeddings.embed_documents([chunk.text for chunk in chunks]))
        query_norm = np.linalg.norm(query_vector)
        chunk_norms = np.linalg.norm(chunk_vectors, axis=1)
        denominators = np.maximum(chunk_norms * query_norm, 1e-12)
        similarities = (chunk_vectors @ query_vector) / denominators
        ranked = sorted(zip(chunks, similarities.tolist()), key=lambda item: item[1], reverse=True)
        return [
            EvidenceChunk(
                chunk_id=chunk.chunk_id,
                text=chunk.text,
                source=chunk.source,
                dataset=chunk.dataset,
                document_id=chunk.document_id,
                similarity_score=float(score),
                metadata=chunk.metadata,
            )
            for chunk, score in ranked[: self.settings.top_k]
        ]


@lru_cache(maxsize=1)
def get_evidence_service() -> EvidenceService:
    settings = get_settings()
    embeddings = get_embedding_service()
    vector_store = ChromaVectorStore(settings.chroma_persist_dir, settings.chroma_collection)
    return EvidenceService(
        settings=settings,
        chunker=Chunker(settings.chunk_size, settings.chunk_overlap),
        embeddings=embeddings,
        retriever=SemanticRetriever(embeddings, vector_store),
    )

