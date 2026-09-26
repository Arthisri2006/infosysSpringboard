import json
import sqlite3
from pathlib import Path
from typing import Any
from uuid import UUID

from backend.models.results import EvaluationResult


class EvaluationRepository:
    """SQLite persistence for evaluations and their optional batch provenance."""

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
                    result_json TEXT NOT NULL,
                    batch_id TEXT,
                    batch_name TEXT,
                    system_name TEXT
                )
                """
            )
            columns = {row["name"] for row in connection.execute("PRAGMA table_info(evaluations)")}
            for name in ("batch_id", "batch_name", "system_name"):
                if name not in columns:
                    connection.execute(f"ALTER TABLE evaluations ADD COLUMN {name} TEXT")
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS batches (
                    batch_id TEXT PRIMARY KEY,
                    batch_name TEXT NOT NULL,
                    system_name TEXT,
                    created_at TEXT NOT NULL
                )
                """
            )
            connection.execute("CREATE INDEX IF NOT EXISTS idx_evaluations_batch ON evaluations(batch_id)")
            connection.execute("CREATE INDEX IF NOT EXISTS idx_evaluations_created ON evaluations(created_at)")

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
                    str(result.evaluation_id), result.created_at.isoformat(), package.question,
                    package.evidence_source_type, result.relevance.score, result.accuracy.score,
                    result.hallucination.score, result.completeness.score,
                    result.verdict.overall_score, result.verdict.verdict, result.model_dump_json(),
                ),
            )

    def create_batch(self, batch_id: UUID, batch_name: str, system_name: str | None, created_at: str) -> None:
        with self._connect() as connection:
            connection.execute(
                "INSERT OR REPLACE INTO batches VALUES (?, ?, ?, ?)",
                (str(batch_id), batch_name, system_name, created_at),
            )

    def assign_batch(self, evaluation_id: UUID, batch_id: UUID, batch_name: str, system_name: str | None) -> None:
        with self._connect() as connection:
            connection.execute(
                "UPDATE evaluations SET batch_id = ?, batch_name = ?, system_name = ? WHERE evaluation_id = ?",
                (str(batch_id), batch_name, system_name, str(evaluation_id)),
            )

    def get(self, evaluation_id: UUID) -> EvaluationResult | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT result_json FROM evaluations WHERE evaluation_id = ?", (str(evaluation_id),)
            ).fetchone()
        return EvaluationResult.model_validate_json(row["result_json"]) if row else None

    def get_batch_results(self, batch_id: UUID) -> list[EvaluationResult]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT result_json FROM evaluations WHERE batch_id = ? ORDER BY created_at",
                (str(batch_id),),
            ).fetchall()
        return [EvaluationResult.model_validate_json(row["result_json"]) for row in rows]

    def get_batch(self, batch_id: UUID) -> dict[str, Any] | None:
        with self._connect() as connection:
            row = connection.execute("SELECT * FROM batches WHERE batch_id = ?", (str(batch_id),)).fetchone()
        return dict(row) if row else None

    def query_rows(
        self, *, verdict: str | None = None, min_score: float | None = None,
        max_score: float | None = None, batch_id: UUID | None = None,
        system_name: str | None = None,
    ) -> list[dict[str, Any]]:
        clauses: list[str] = []
        values: list[Any] = []
        for clause, value in (
            ("verdict = ?", verdict), ("overall_score >= ?", min_score),
            ("overall_score <= ?", max_score), ("batch_id = ?", str(batch_id) if batch_id else None),
            ("system_name = ?", system_name),
        ):
            if value is not None:
                clauses.append(clause)
                values.append(value)
        where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        with self._connect() as connection:
            rows = connection.execute(
                f"SELECT * FROM evaluations {where} ORDER BY created_at DESC", values
            ).fetchall()
        output: list[dict[str, Any]] = []
        for row in rows:
            item = dict(row)
            item["result"] = json.loads(item["result_json"])
            output.append(item)
        return output

    def list_batches(self) -> list[dict[str, Any]]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT b.*, COUNT(e.evaluation_id) AS count
                FROM batches b LEFT JOIN evaluations e ON b.batch_id = e.batch_id
                GROUP BY b.batch_id ORDER BY b.created_at DESC
                """
            ).fetchall()
        return [dict(row) for row in rows]

    def dashboard(self, limit: int = 20):
        """Backward-compatible entry point used by earlier Milestone 3 clients."""
        from backend.services.analytics_service import AnalyticsService

        return AnalyticsService(self).summarize(limit=limit)
