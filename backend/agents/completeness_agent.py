from backend.agents.semantic import SemanticAnalyzer, score_label, split_sentences
from backend.models.evaluation import EvidencePackage
from backend.models.results import CompletenessResult


class CompletenessJudgeAgent:
    name = "completeness"

    def __init__(self, analyzer: SemanticAnalyzer, coverage_threshold: float) -> None:
        self.analyzer = analyzer
        self.coverage_threshold = coverage_threshold

    def evaluate(self, package: EvidencePackage) -> CompletenessResult:
        aspects = self.analyzer.required_aspects(package)
        if not aspects:
            return CompletenessResult(
                agent=self.name,
                score=None,
                label="unavailable",
                explanation="Completeness requires a reference answer or usable evidence aspects.",
                warnings=["No required aspects could be derived from the evidence package."],
            )
        response_units = split_sentences(package.ai_response) or [package.ai_response]
        similarities = self.analyzer.similarity_matrix(aspects, response_units)
        covered: list[str] = []
        missing: list[str] = []
        for index, aspect in enumerate(aspects):
            if float(similarities[index].max()) >= self.coverage_threshold:
                covered.append(aspect)
            else:
                missing.append(aspect)
        score = round(len(covered) / len(aspects) * 100, 2)
        return CompletenessResult(
            agent=self.name,
            score=score,
            label=score_label(score),
            explanation=f"The response covers {len(covered)} of {len(aspects)} required evidence aspects.",
            covered_aspects=covered,
            missing_aspects=missing,
        )
