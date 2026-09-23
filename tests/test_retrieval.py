from backend.rag.retriever import SemanticRetriever


class FakeEmbeddings:
    def embed_query(self, text: str) -> list[float]:
        if not text.strip():
            raise ValueError("empty")
        return [1.0, 0.0]


class FakeStore:
    def query(self, query_embedding, top_k: int):
        rows = [
            {
                "chunk_id": f"chunk-{index}",
                "text": f"Evidence {index}",
                "source": "test-index",
                "dataset": "squad",
                "document_id": f"doc-{index}",
                "similarity_score": 0.9 - index / 10,
                "distance": 0.1 + index / 10,
                "metadata": {"rank": index + 1},
            }
            for index in range(4)
        ]
        return rows[:top_k]


def test_query_returns_top_k_results_with_metadata() -> None:
    results = SemanticRetriever(FakeEmbeddings(), FakeStore()).retrieve("moon landing", 2)
    assert len(results) == 2
    assert results[0].dataset == "squad"
    assert results[0].metadata["rank"] == 1


def test_empty_query_is_safe() -> None:
    assert SemanticRetriever(FakeEmbeddings(), FakeStore()).retrieve("   ", 5) == []

