from functools import lru_cache

from backend.agents.accuracy_agent import AccuracyJudgeAgent
from backend.agents.claim_analyzer import ClaimAnalyzer
from backend.agents.completeness_agent import CompletenessJudgeAgent
from backend.agents.hallucination_agent import HallucinationDetectionAgent
from backend.agents.relevance_agent import RelevanceJudgeAgent
from backend.agents.semantic import SemanticAnalyzer
from backend.agents.verdict_agent import VerdictAgent
from backend.core.config import Settings, get_settings
from backend.database.repository import EvaluationRepository
from backend.models.evaluation import EvaluationInput
from backend.models.results import EvaluationResult
from backend.rag.embeddings import get_embedding_service
from backend.services.evidence_service import EvidenceService, get_evidence_service


class EvaluationOrchestrator:
    """Runs the evidence pipeline and explainable judge agents in a fixed order."""

    def __init__(
        self,
        settings: Settings,
        evidence_service: EvidenceService,
        analyzer: SemanticAnalyzer,
        repository: EvaluationRepository,
    ) -> None:
        self.evidence_service = evidence_service
        self.repository = repository
        self.relevance_agent = RelevanceJudgeAgent(analyzer)
        self.claim_analyzer = ClaimAnalyzer(
            analyzer,
            settings.support_threshold,
            settings.contradiction_threshold,
        )
        self.accuracy_agent = AccuracyJudgeAgent()
        self.hallucination_agent = HallucinationDetectionAgent()
        self.completeness_agent = CompletenessJudgeAgent(
            analyzer, settings.completeness_threshold
        )
        self.verdict_agent = VerdictAgent(settings.verdict_weights)

    def evaluate(self, evaluation: EvaluationInput) -> EvaluationResult:
        package = self.evidence_service.prepare(evaluation)
        relevance = self.relevance_agent.evaluate(package)
        claims = self.claim_analyzer.analyze(package)
        accuracy = self.accuracy_agent.evaluate(claims)
        hallucination = self.hallucination_agent.evaluate(claims)
        completeness = self.completeness_agent.evaluate(package)
        verdict = self.verdict_agent.evaluate(relevance, accuracy, hallucination, completeness)
        result = EvaluationResult(
            evaluation_id=evaluation.id,
            evidence_package=package,
            relevance=relevance,
            accuracy=accuracy,
            hallucination=hallucination,
            completeness=completeness,
            verdict=verdict,
        )
        self.repository.save(result)
        return result


@lru_cache(maxsize=1)
def get_evaluation_repository() -> EvaluationRepository:
    return EvaluationRepository(get_settings().database_path)


@lru_cache(maxsize=1)
def get_evaluation_orchestrator() -> EvaluationOrchestrator:
    settings = get_settings()
    return EvaluationOrchestrator(
        settings=settings,
        evidence_service=get_evidence_service(),
        analyzer=SemanticAnalyzer(get_embedding_service()),
        repository=get_evaluation_repository(),
    )
