import json
from pathlib import Path
from typing import Any, Sequence

from backend.rag.chunker import TextChunk


def _chroma_metadata(chunk: TextChunk) -> dict[str, str | int | float | bool]:
    return {
        "dataset": chunk.dataset,
        "document_id": chunk.document_id,
        "source": chunk.source,
        "metadata_json": json.dumps(chunk.metadata, ensure_ascii=False, default=str),
    }


class ChromaVectorStore:
    """Persistent Chroma collection adapter with idempotent upserts."""

    def __init__(self, persist_dir: Path | str, collection_name: str) -> None:
        try:
            import chromadb
            from chromadb.config import Settings as ChromaSettings

            path = Path(persist_dir)
            path.mkdir(parents=True, exist_ok=True)
            self._client = chromadb.PersistentClient(
                path=str(path), settings=ChromaSettings(anonymized_telemetry=False)
            )
            self.collection_name = collection_name
            self._collection = self._client.get_or_create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine", "description": "Benchmark evidence chunks"},
            )
        except Exception as exc:
            raise RuntimeError(f"Unable to initialize ChromaDB: {exc}") from exc

    @property
    def count(self) -> int:
        return self._collection.count()

    def upsert(self, chunks: Sequence[TextChunk], embeddings: Sequence[Sequence[float]]) -> int:
        if len(chunks) != len(embeddings):
            raise ValueError("Each chunk must have exactly one embedding")
        if not chunks:
            return 0
        self._collection.upsert(
            ids=[chunk.chunk_id for chunk in chunks],
            documents=[chunk.text for chunk in chunks],
            metadatas=[_chroma_metadata(chunk) for chunk in chunks],
            embeddings=[list(vector) for vector in embeddings],
        )
        return len(chunks)

    def query(self, query_embedding: Sequence[float], top_k: int) -> list[dict[str, Any]]:
        if top_k < 1:
            raise ValueError("top_k must be at least 1")
        if self.count == 0:
            return []
        result = self._collection.query(
            query_embeddings=[list(query_embedding)],
            n_results=min(top_k, self.count),
            include=["documents", "metadatas", "distances"],
        )
        rows: list[dict[str, Any]] = []
        for chunk_id, text, metadata, distance in zip(
            result["ids"][0],
            result["documents"][0],
            result["metadatas"][0],
            result["distances"][0],
        ):
            extra = json.loads(metadata.get("metadata_json", "{}"))
            rows.append(
                {
                    "chunk_id": chunk_id,
                    "text": text,
                    "source": metadata.get("source", "unknown"),
                    "dataset": metadata.get("dataset"),
                    "document_id": metadata.get("document_id", "unknown"),
                    "distance": float(distance),
                    # The collection uses cosine distance, so similarity is 1 - distance.
                    "similarity_score": 1.0 - float(distance),
                    "metadata": extra,
                }
            )
        return rows

    def reset(self) -> None:
        """Delete and recreate only this configured collection."""
        try:
            self._client.delete_collection(self.collection_name)
        except Exception:
            pass
        self._collection = self._client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine", "description": "Benchmark evidence chunks"},
        )
