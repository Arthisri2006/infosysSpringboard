from backend.agents.semantic import (
    SemanticAnalyzer,
    has_negation,
    named_terms,
    numbers_in,
    split_sentences,
)
from backend.models.evaluation import EvidencePackage
from backend.models.results import ClaimAssessment


class ClaimAnalyzer:
    """Classifies response claims against the best available evidence."""

    def __init__(
        self,
        analyzer: SemanticAnalyzer,
        support_threshold: float,
        contradiction_threshold: float,
    ) -> None:
        self.analyzer = analyzer
        self.support_threshold = support_threshold
        self.contradiction_threshold = contradiction_threshold

    def analyze(self, package: EvidencePackage) -> list[ClaimAssessment]:
        claims = split_sentences(package.ai_response) or [package.ai_response]
        evidence = self.analyzer.evidence_texts(package)
        if not evidence:
            return [
                ClaimAssessment(
                    claim=claim,
                    status="unsupported",
                    confidence=0.0,
                    explanation="No reference or retrieved evidence was available for this claim.",
                )
                for claim in claims
            ]

        evidence_texts = [item.text for item in evidence]
        similarities = self.analyzer.similarity_matrix(claims, evidence_texts)
        results: list[ClaimAssessment] = []
        for claim_index, claim in enumerate(claims):
            best_index = int(similarities[claim_index].argmax())
            similarity = float(similarities[claim_index, best_index])
            best = evidence[best_index]
            claim_numbers = numbers_in(claim)
            evidence_numbers = numbers_in(best.text)
            # Extra precision in either text is compatible (for example, "1969"
            # versus "July 20, 1969"). Treat numbers as conflicting only when
            # both sides contain numbers and neither set contains the other.
            number_conflict = bool(
                claim_numbers
                and evidence_numbers
                and not claim_numbers.issubset(evidence_numbers)
                and not evidence_numbers.issubset(claim_numbers)
            )
            negation_conflict = has_negation(claim) != has_negation(best.text)
            claim_names = named_terms(claim)
            evidence_names = named_terms(best.text)
            name_conflict = bool(claim_names and evidence_names and not claim_names.issubset(evidence_names))
            contradicted = similarity >= self.contradiction_threshold and (
                number_conflict or negation_conflict or name_conflict
            )

            if contradicted:
                status = "contradicted"
                explanation = "The closest evidence is related but conflicts in a name, negation, or numeric detail."
            elif similarity >= self.support_threshold:
                status = "supported"
                explanation = "The closest evidence semantically supports the claim."
            else:
                status = "unsupported"
                explanation = "No available evidence passed the configured support threshold."

            results.append(
                ClaimAssessment(
                    claim=claim,
                    status=status,
                    confidence=round(max(0.0, min(1.0, similarity)), 4),
                    best_evidence_text=best.text,
                    evidence_chunk_id=best.chunk_id,
                    explanation=explanation,
                )
            )
        return results
