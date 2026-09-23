from backend.core.config import Settings
from backend.models.evaluation import EvaluationInput
from backend.rag.chunker import Chunker
from backend.services.evidence_service import EvidenceService


class TinyEmbeddings:
    def embed_query(self, text):
        return [1.0, 0.0]

    def embed_documents(self, texts):
        return [([1.0, 0.0] if "relevant" in text else [0.0, 1.0]) for text in texts]


class EmptyRetriever:
    def __init__(self):
        self.calls = 0

    def retrieve(self, query, top_k):
        self.calls += 1
        return []


def make_service(retriever=None):
    settings = Settings(top_k=2, chunk_size=10, chunk_overlap=2)
    return EvidenceService(settings, Chunker(10, 2), TinyEmbeddings(), retriever or EmptyRetriever())


def test_reference_answer_is_preserved_without_benchmark_lookup() -> None:
    retriever = EmptyRetriever()
    package = make_service(retriever).prepare(
        EvaluationInput(question="Q?", ai_response="A", reference_answer="Trusted answer")
    )
    assert package.reference_answer == "Trusted answer"
    assert package.evidence_source_type == "reference_answer"
    assert retriever.calls == 0


def test_source_text_is_chunked_and_ranked_temporarily() -> None:
    package = make_service().prepare(
        EvaluationInput(
            question="Q?",
            ai_response="A",
            source_text="irrelevant words here only relevant evidence appears now",
        )
    )
    assert package.source_text_evidence
    assert package.source_text_evidence[0].dataset == "user_source"
    assert package.source_text_evidence[0].metadata["temporary"] is True


def test_no_direct_evidence_triggers_benchmark_retrieval() -> None:
    retriever = EmptyRetriever()
    package = make_service(retriever).prepare(EvaluationInput(question="Q?", ai_response="A"))
    assert retriever.calls == 1
    assert package.retrieval_metadata.benchmark_retrieval_attempted is True
    assert package.retrieval_metadata.warnings
