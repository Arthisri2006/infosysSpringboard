from backend.agents.semantic import score_label
from backend.models.results import ClaimAssessment, HallucinationResult


class HallucinationDetectionAgent:
    name = "hallucination"

    def evaluate(self, claims: list[ClaimAssessment]) -> HallucinationResult:
        if not claims:
            return HallucinationResult(
                agent=self.name,
                score=None,
                label="unavailable",
                explanation="No checkable claims were extracted.",
                hallucination_rate=None,
                warnings=["Hallucination analysis requires at least one claim."],
            )
        supported = sum(claim.status == "supported" for claim in claims)
        unsupported = sum(claim.status == "unsupported" for claim in claims)
        contradicted = sum(claim.status == "contradicted" for claim in claims)
        hallucination_rate = (unsupported + contradicted) / len(claims)
        groundedness = round((1.0 - hallucination_rate) * 100, 2)
        return HallucinationResult(
            agent=self.name,
            score=groundedness,
            label=score_label(groundedness),
            explanation=(
                f"{unsupported + contradicted} of {len(claims)} claims lack support or conflict with evidence. "
                "The displayed score is groundedness, so a higher value is better."
            ),
            hallucination_rate=round(hallucination_rate, 4),
            supported_claims=supported,
            unsupported_claims=unsupported,
            contradicted_claims=contradicted,
            claims=claims,
            evidence_chunk_ids=sorted(
                {claim.evidence_chunk_id for claim in claims if claim.evidence_chunk_id}
            ),
        )
