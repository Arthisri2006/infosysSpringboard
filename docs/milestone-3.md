# Milestone 3 — Completeness, Verdict, Batch, and Dashboard

## Objective

Milestone 3 completes the evaluation workflow with missing-aspect analysis, an explicit weighted verdict, saved evaluation history, batch processing, and aggregate presentation.

## Implemented components

| Requirement | Implementation |
|---|---|
| Completeness evaluation | `backend/agents/completeness_agent.py` |
| Weighted verdict | `backend/agents/verdict_agent.py` |
| Configurable thresholds and weights | `backend/core/config.py` and `.env.example` |
| SQLite persistence | `backend/database/repository.py` |
| Batch API | `POST /api/v1/evaluations/batch` |
| Dashboard API | `GET /api/v1/evaluations/dashboard` |
| Result lookup | `GET /api/v1/evaluations/{evaluation_id}` |
| Batch UI | `frontend/components/BatchEvaluation.tsx` |
| Dashboard UI | `frontend/components/Dashboard.tsx` |
| Persistence tests | `tests/test_persistence.py` |

## Completeness and verdict policy

Required aspects come from the direct reference answer when available; otherwise they are derived from relevant evidence metadata and passages. Each aspect is compared with the response, and the API returns both covered and missing items.

The default overall policy is relevance 20%, accuracy 35%, groundedness 25%, and completeness 20%. Weights are normalized and configurable. The verdict never replaces the component results: the API and UI retain every explanation, claim, cited evidence identifier, warning, and missing aspect.

## Batch and dashboard behavior

Batch submissions reuse the same orchestrator for every item and return individual results plus actual averages and verdict counts. Completed evaluations are serialized into a local SQLite database. The dashboard calculates averages from stored runs and lists recent evaluations; it does not fabricate values when the database is empty.

## Deployment note

The complete application is deployed through the root `render.yaml` Blueprint. Render hosts the Next.js static frontend and FastAPI backend as separate connected services, with their public URLs wired through environment variables automatically. Durable production history still requires a persistent disk or external database.

## Limitations and future hardening

Milestone 3 uses synchronous batch processing and local SQLite, appropriate for an internship-scale local deployment. Larger deployments should add authentication, a job queue, rate limits, managed persistence, model/version tracking, and benchmark calibration against human labels.
