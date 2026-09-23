from collections.abc import Iterable

from backend.datasets.normalizer import NormalizedDocument
from backend.rag.chunker import Chunker, TextChunk
from backend.rag.cleaner import deduplicate_documents
from backend.rag.embeddings import EmbeddingProvider
from backend.rag.vector_store import ChromaVectorStore


class KnowledgeBaseLoader:
    def __init__(
        self,
        chunker: Chunker,
        embeddings: EmbeddingProvider,
        vector_store: ChromaVectorStore,
        batch_size: int = 64,
    ) -> None:
        self.chunker = chunker
        self.embeddings = embeddings
        self.vector_store = vector_store
        self.batch_size = batch_size

    def ingest(self, documents: Iterable[NormalizedDocument]) -> dict[str, int]:
        unique_documents = deduplicate_documents(documents)
        chunks = [chunk for document in unique_documents for chunk in self.chunker.chunk_document(document)]
        for start in range(0, len(chunks), self.batch_size):
            batch: list[TextChunk] = chunks[start : start + self.batch_size]
            vectors = self.embeddings.embed_documents([chunk.text for chunk in batch])
            self.vector_store.upsert(batch, vectors)
        return {"documents": len(unique_documents), "chunks": len(chunks), "index_size": self.vector_store.count}

