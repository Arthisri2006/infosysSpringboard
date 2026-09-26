import json
import sqlite3
from pathlib import Path
from uuid import UUID

from backend.models.results import DashboardSummary, EvaluationHistoryItem, EvaluationResult


class EvaluationRepository:
    """Small SQLite repository for Milestone 3 history and dashboard summaries."""

    def __init__(self, database_path: Path | str) -> None:
        self.database_path = Path(database_path)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS evaluations (
                    evaluation_id TEXT PRIMARY KEY,
                    created_at TEXT NOT NULL,
                    question TEXT NOT NULL,
                    evidence_source_type TEXT NOT NULL,
                    relevance_score REAL,
                    accuracy_score REAL,
                    groundedness_score REAL,
                    completeness_score REAL,
                    overall_score REAL NOT NULL,
                    verdict TEXT NOT NULL,
                    result_json TEXT NOT NULL
                )
                """
            )

    def save(self, result: EvaluationResult) -> None:
        package = result.evidence_package
        with self._connect() as connection:
            connection.execute(
                """
                INSERT OR REPLACE INTO evaluations (
                    evaluation_id, created_at, question, evidence_source_type,
                    relevance_score, accuracy_score, groundedness_score,
                    completeness_score, overall_score, verdict, result_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    str(result.evaluation_id),
                    result.created_at.isoformat(),
                    package.question,
                    package.evidence_source_type,
                    result.relevance.score,
                    result.accuracy.score,
                    result.hallucination.score,
                    result.completeness.score,
                    result.verdict.overall_score,
                    result.verdict.verdict,
                    result.model_dump_json(),
                ),
            )

    def get(self, evaluation_id: UUID) -> EvaluationResult | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT result_json FROM evaluations WHERE evaluation_id = ?", (str(evaluation_id),)
            ).fetchone()
        return EvaluationResult.model_validate_json(row["result_json"]) if row else None

    def dashboard(self, limit: int = 20) -> DashboardSummary:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT * FROM evaluations ORDER BY created_at DESC LIMIT ?", (limit,)
            ).fetchall()
            aggregates = connection.execute(
                """
                SELECT COUNT(*) AS total,
                       AVG(relevance_score) AS relevance,
                       AVG(accuracy_score) AS accuracy,
                       AVG(groundedness_score) AS groundedness,
                       AVG(completeness_score) AS completeness,
                       AVG(overall_score) AS overall
                FROM evaluations
                """
            ).fetchone()
            verdict_rows = connection.execute(
                "SELECT verdict, COUNT(*) AS count FROM evaluations GROUP BY verdict"
            ).fetchall()
        averages = {
            name: round(float(aggregates[name] or 0.0), 2)
            for name in ("relevance", "accuracy", "groundedness", "completeness", "overall")
        }
        history = [
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
            )
            for row in rows
        ]
        return DashboardSummary(
            total_evaluations=int(aggregates["total"] or 0),
            average_scores=averages,
            verdict_counts={row["verdict"]: row["count"] for row in verdict_rows},
            recent_evaluations=history,
        )
