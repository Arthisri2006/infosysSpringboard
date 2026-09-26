import math

from backend.agents.accuracy_agent import AccuracyJudgeAgent
from backend.agents.claim_analyzer import ClaimAnalyzer
from backend.agents.completeness_agent import CompletenessJudgeAgent
from backend.agents.hallucination_agent import HallucinationDetectionAgent
from backend.agents.relevance_agent import RelevanceJudgeAgent
from backend.agents.semantic import SemanticAnalyzer
from backend.agents.verdict_agent import VerdictAgent
from backend.models.evaluation import EvidencePackage, RetrievalMetadata


class BagEmbeddings:
    vocabulary = ["neil", "armstrong", "buzz", "aldrin", "moon", "1969", "first", "walked"]

    def embed_documents(self, texts):
        vectors = []
        for text in texts:
            lowered = text.lower()
            vector = [float(lowered.count(token)) for token in self.vocabulary]
            norm = math.sqrt(sum(value * value for value in vector)) or 1.0
            vectors.append([value / norm for value in vector])
        return vectors

    def embed_query(self, text):
        return self.embed_documents([text])[0]


def package(response: str) -> EvidencePackage:
    return EvidencePackage(
        evaluation_id="11111111-1111-1111-1111-111111111111",
        question="Who was the first person to walk on the Moon?",
        ai_response=response,
        reference_answer="Neil Armstrong was the first person to walk on the Moon in 1969.",
        evidence_source_type="reference_answer",
        retrieval_metadata=RetrievalMetadata(query="moon", requested_top_k=5, returned_count=0),
    )


def test_supported_claim_produces_high_accuracy_and_low_hallucination() -> None:
    analyzer = SemanticAnalyzer(BagEmbeddings())
    claims = ClaimAnalyzer(analyzer, 0.6, 0.5).analyze(
        package("Neil Armstrong was the first person to walk on the Moon in 1969.")
    )
    accuracy = AccuracyJudgeAgent().evaluate(claims)
    hallucination = HallucinationDetectionAgent().evaluate(claims)
    assert claims[0].status == "supported"
    assert accuracy.score == 100
    assert hallucination.hallucination_rate == 0


def test_conflicting_name_is_marked_contradicted() -> None:
    analyzer = SemanticAnalyzer(BagEmbeddings())
    claims = ClaimAnalyzer(analyzer, 0.6, 0.45).analyze(
        package("Buzz Aldrin was the first person to walk on the Moon in 1969.")
    )
    assert claims[0].status == "contradicted"


def test_more_precise_evidence_number_is_not_a_conflict() -> None:
    analyzer = SemanticAnalyzer(BagEmbeddings())
    evidence = package("Neil Armstrong was the first person to walk on the Moon in 1969.")
    evidence.reference_answer = (
        "Neil Armstrong was the first person to walk on the Moon on July 20, 1969."
    )
    claims = ClaimAnalyzer(analyzer, 0.6, 0.5).analyze(evidence)
    assert claims[0].status == "supported"


def test_completeness_and_verdict_use_normalized_scores() -> None:
    analyzer = SemanticAnalyzer(BagEmbeddings())
    evidence = package("Neil Armstrong walked on the Moon in 1969.")
    relevance = RelevanceJudgeAgent(analyzer).evaluate(evidence)
    claims = ClaimAnalyzer(analyzer, 0.5, 0.5).analyze(evidence)
    accuracy = AccuracyJudgeAgent().evaluate(claims)
    hallucination = HallucinationDetectionAgent().evaluate(claims)
    completeness = CompletenessJudgeAgent(analyzer, 0.5).evaluate(evidence)
    verdict = VerdictAgent(
        {"relevance": 0.2, "accuracy": 0.35, "groundedness": 0.25, "completeness": 0.2}
    ).evaluate(relevance, accuracy, hallucination, completeness)
    assert completeness.score == 100
    assert 0 <= verdict.overall_score <= 100
    assert verdict.verdict in {"strong", "acceptable", "needs_review", "poor"}
