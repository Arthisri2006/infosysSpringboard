from backend.models.evaluation import EvidenceChunk
from backend.rag.embeddings import EmbeddingProvider
from backend.rag.vector_store import ChromaVectorStore


class SemanticRetriever:
    def __init__(self, embeddings: EmbeddingProvider, vector_store: ChromaVectorStore) -> None:
        self.embeddings = embeddings
        self.vector_store = vector_store

    def retrieve(self, query: str, top_k: int) -> list[EvidenceChunk]:
        query = query.strip()
        if not query:
            return []
        vector = self.embeddings.embed_query(query)
        return [EvidenceChunk.model_validate(row) for row in self.vector_store.query(vector, top_k)]

