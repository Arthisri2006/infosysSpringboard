from collections import Counter, defaultdict
from datetime import datetime
from typing import Any
from uuid import UUID

from backend.database.repository import EvaluationRepository
from backend.models.results import (
    BatchTrendPoint,
    CompletenessAnalytics,
    DashboardFilters,
    DashboardSummary,
    EvaluationHistoryItem,
    HallucinationAnalytics,
    OutcomeSummary,
)


DIMENSIONS = ("relevance", "accuracy", "groundedness", "completeness", "overall")
SCORE_COLUMNS = {
    "relevance": "relevance_score",
    "accuracy": "accuracy_score",
    "groundedness": "groundedness_score",
    "completeness": "completeness_score",
    "overall": "overall_score",
}


def outcome_for_score(score: float) -> str:
    """Map the 0-100 overall score to a mentor-facing outcome bucket."""
    if score >= 70:
        return "pass"
    if score >= 45:
        return "needs_improvement"
    return "fail"


def issue_tags(row: dict[str, Any]) -> list[str]:
    result = row["result"]
    tags: list[str] = []
    if (row.get("relevance_score") or 0) < 60:
        tags.append("Low relevance")
    if (row.get("accuracy_score") or 0) < 60:
        tags.append("Accuracy risk")
    hallucination = result.get("hallucination", {})
    if hallucination.get("unsupported_claims", 0):
        tags.append("Unsupported claims")
    if hallucination.get("contradicted_claims", 0):
        tags.append("Contradicted claims")
    if result.get("completeness", {}).get("missing_aspects"):
        tags.append("Missing information")
    return tags


class AnalyticsService:
    """Calculates dashboard metrics only from persisted structured results."""

    def __init__(self, repository: EvaluationRepository) -> None:
        self.repository = repository

    def summarize(
        self,
        *,
        limit: int = 20,
        verdict: str | None = None,
        min_score: float | None = None,
        max_score: float | None = None,
        batch_id: UUID | None = None,
        system_name: str | None = None,
    ) -> DashboardSummary:
        raw_verdict = verdict if verdict in {"strong", "acceptable", "needs_review", "poor"} else None
        rows = self.repository.query_rows(
            verdict=raw_verdict,
            min_score=min_score,
            max_score=max_score,
            batch_id=batch_id,
            system_name=system_name,
        )
        if verdict in {"pass", "needs_improvement", "fail"}:
            rows = [row for row in rows if outcome_for_score(row["overall_score"]) == verdict]

        total = len(rows)
        averages = {
            name: round(
                sum(float(row[SCORE_COLUMNS[name]] or 0.0) for row in rows) / total, 2
            ) if total else 0.0
            for name in DIMENSIONS
        }
        verdict_counts = Counter(row["verdict"] for row in rows)
        outcome_counts = Counter(outcome_for_score(row["overall_score"]) for row in rows)
        outcomes = OutcomeSummary(
            counts={key: outcome_counts.get(key, 0) for key in ("pass", "needs_improvement", "fail")},
            percentages={
                key: round(outcome_counts.get(key, 0) * 100 / total, 2) if total else 0.0
                for key in ("pass", "needs_improvement", "fail")
            },
        )

        distributions = {
            name: {band: 0 for band in ("0-39", "40-59", "60-79", "80-100")}
            for name in DIMENSIONS
        }
        issue_counter: Counter[str] = Counter()
        missing_counter: Counter[str] = Counter()
        responses_with_hallucination = 0
        responses_with_missing = 0
        unsupported = contradicted = total_claims = total_missing = 0
        history: list[EvaluationHistoryItem] = []

        for row in rows:
            for name in DIMENSIONS:
                score = float(row[SCORE_COLUMNS[name]] or 0.0)
                band = "0-39" if score < 40 else "40-59" if score < 60 else "60-79" if score < 80 else "80-100"
                distributions[name][band] += 1
            tags = issue_tags(row)
            issue_counter.update(tags)
            result = row["result"]
            hall = result.get("hallucination", {})
            row_unsupported = int(hall.get("unsupported_claims", 0))
            row_contradicted = int(hall.get("contradicted_claims", 0))
            unsupported += row_unsupported
            contradicted += row_contradicted
            total_claims += len(hall.get("claims", []))
            if row_unsupported or row_contradicted:
                responses_with_hallucination += 1
            missing = result.get("completeness", {}).get("missing_aspects", [])
            total_missing += len(missing)
            if missing:
                responses_with_missing += 1
                missing_counter.update(str(item).strip() for item in missing if str(item).strip())
            if len(history) < limit:
                history.append(
                    EvaluationHistoryItem(
                        evaluation_id=row["evaluation_id"],
                        created_at=row["created_at"],
                        question=row["question"],
                        evidence_source_type=row["evidence_source_type"],
                        relevance_score=row["relevance_score"],
                        accuracy_score=row["accuracy_score"],
                        groundedness_score=row["groundedness_score"],
                        completeness_score=row["completeness_score"],
                        overall_score=row["overall_score"],
                        verdict=row["verdict"],
                        outcome=outcome_for_score(row["overall_score"]),
                        batch_id=row.get("batch_id"),
                        batch_name=row.get("batch_name"),
                        system_name=row.get("system_name"),
                        issue_tags=tags,
                    )
                )

        trends = self._build_trends(rows)
        batches = self.repository.list_batches()
        systems = sorted({str(item["system_name"]) for item in batches if item.get("system_name")})
        return DashboardSummary(
            total_evaluations=total,
            average_scores=averages,
            verdict_counts=dict(verdict_counts),
            outcomes=outcomes,
            score_distributions=distributions,
            hallucination=HallucinationAnalytics(
                responses_with_issues=responses_with_hallucination,
                response_rate=round(responses_with_hallucination * 100 / total, 2) if total else 0.0,
                unsupported_claims=unsupported,
                contradicted_claims=contradicted,
                total_claims=total_claims,
                unsupported_claim_rate=round((unsupported + contradicted) * 100 / total_claims, 2) if total_claims else 0.0,
            ),
            completeness=CompletenessAnalytics(
                responses_with_missing_aspects=responses_with_missing,
                response_rate=round(responses_with_missing * 100 / total, 2) if total else 0.0,
                total_missing_aspects=total_missing,
                frequent_missing_aspects=[{"aspect": key, "count": count} for key, count in missing_counter.most_common(8)],
            ),
            frequent_issues=[{"issue": key, "count": count} for key, count in issue_counter.most_common(8)],
            batch_trends=trends,
            available_batches=batches,
            available_systems=systems,
            filters=DashboardFilters(
                verdict=verdict, min_score=min_score, max_score=max_score,
                batch_id=batch_id, system_name=system_name,
            ),
            recent_evaluations=history,
        )

    def _build_trends(self, rows: list[dict[str, Any]]) -> list[BatchTrendPoint]:
        grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for row in rows:
            if row.get("batch_id"):
                grouped[str(row["batch_id"])].append(row)
        trends: list[BatchTrendPoint] = []
        for batch_key, items in grouped.items():
            count = len(items)
            outcome_counts = Counter(outcome_for_score(item["overall_score"]) for item in items)
            trends.append(
                BatchTrendPoint(
                    batch_id=batch_key,
                    batch_name=items[0].get("batch_name") or "Untitled batch",
                    system_name=items[0].get("system_name"),
                    created_at=min(datetime.fromisoformat(item["created_at"]) for item in items),
                    count=count,
                    average_scores={
                        name: round(sum(float(item[SCORE_COLUMNS[name]] or 0.0) for item in items) / count, 2)
                        for name in DIMENSIONS
                    },
                    outcome_counts={key: outcome_counts.get(key, 0) for key in ("pass", "needs_improvement", "fail")},
                )
            )
        return sorted(trends, key=lambda item: item.created_at)
