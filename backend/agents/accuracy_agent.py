from backend.agents.semantic import score_label
from backend.models.results import AgentResult, ClaimAssessment


class AccuracyJudgeAgent:
    name = "accuracy"

    def evaluate(self, claims: list[ClaimAssessment]) -> AgentResult:
        if not claims:
            return AgentResult(
                agent=self.name,
                score=None,
                label="unavailable",
                explanation="The response did not contain a claim that could be checked.",
                warnings=["No checkable claims were extracted."],
            )
        supported = sum(claim.status == "supported" for claim in claims)
        contradicted = sum(claim.status == "contradicted" for claim in claims)
        score = round(max(0.0, (supported - 0.5 * contradicted) / len(claims)) * 100, 2)
        evidence_ids = sorted({claim.evidence_chunk_id for claim in claims if claim.evidence_chunk_id})
        return AgentResult(
            agent=self.name,
            score=score,
            label=score_label(score),
            explanation=(
                f"{supported} of {len(claims)} claims are supported and {contradicted} are contradicted. "
                "Contradicted claims receive an additional penalty."
            ),
            evidence_chunk_ids=evidence_ids,
        )
