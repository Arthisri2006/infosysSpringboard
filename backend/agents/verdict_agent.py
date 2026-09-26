from backend.models.results import (
    AgentResult,
    CompletenessResult,
    HallucinationResult,
    VerdictResult,
)


class VerdictAgent:
    name = "verdict"

    def __init__(self, weights: dict[str, float]) -> None:
        total = sum(weights.values())
        if total <= 0:
            raise ValueError("Verdict weights must have a positive total")
        self.weights = {name: value / total for name, value in weights.items()}

    def evaluate(
        self,
        relevance: AgentResult,
        accuracy: AgentResult,
        hallucination: HallucinationResult,
        completeness: CompletenessResult,
    ) -> VerdictResult:
        scores = {
            "relevance": relevance.score,
            "accuracy": accuracy.score,
            "groundedness": hallucination.score,
            "completeness": completeness.score,
        }
        available = {name: score for name, score in scores.items() if score is not None}
        available_weight = sum(self.weights[name] for name in available)
        overall = (
            sum(float(score) * self.weights[name] for name, score in available.items())
            / available_weight
            if available_weight
            else 0.0
        )
        overall = round(overall, 2)
        if overall >= 85:
            verdict = "strong"
        elif overall >= 70:
            verdict = "acceptable"
        elif overall >= 45:
            verdict = "needs_review"
        else:
            verdict = "poor"
        unavailable = sorted(set(scores) - set(available))
        caveat = f" Unavailable dimensions: {', '.join(unavailable)}." if unavailable else ""
        return VerdictResult(
            overall_score=overall,
            verdict=verdict,
            explanation=(
                "The verdict is a normalized weighted combination of relevance, accuracy, "
                f"groundedness, and completeness.{caveat}"
            ),
            weights=self.weights,
            component_scores=scores,
        )
