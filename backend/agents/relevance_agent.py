from backend.agents.semantic import SemanticAnalyzer, score_label
from backend.models.evaluation import EvidencePackage
from backend.models.results import AgentResult


class RelevanceJudgeAgent:
    name = "relevance"

    def __init__(self, analyzer: SemanticAnalyzer) -> None:
        self.analyzer = analyzer

    def evaluate(self, package: EvidencePackage) -> AgentResult:
        similarity = self.analyzer.similarity(package.question, package.ai_response)
        score = round(max(0.0, min(1.0, similarity)) * 100, 2)
        return AgentResult(
            agent=self.name,
            score=score,
            label=score_label(score),
            explanation=(
                f"The response-question semantic similarity is {similarity:.3f}. "
                "Higher alignment indicates that the response addresses the submitted question."
            ),
        )
