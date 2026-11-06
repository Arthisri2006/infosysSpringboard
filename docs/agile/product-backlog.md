# Product Backlog

Snapshot: November 6, 2026. **Done** describes implemented scope supported by the listed artifacts. **To do** describes proposed work. Priorities organize future delivery; they do not represent recorded historical estimates.

## Delivered backlog

| ID | Story | Priority | Increment | Status | Evidence |
| --- | --- | --- | --- | --- | --- |
| PB-01 | US-01: Submit validated evaluation inputs | Must | Sprint 1 | Done | `frontend/components/EvaluationForm.tsx`; `backend/models/evaluation.py`; `tests/test_api.py` |
| PB-02 | US-02: Prepare traceable reference/source evidence | Must | Sprint 1 | Done | `backend/services/evidence_service.py`; `tests/test_evidence_service.py` |
| PB-03 | US-03: Retrieve benchmark evidence | Must | Sprint 1 | Done | `scripts/ingest_datasets.py`; `backend/rag/`; `tests/test_retrieval.py` |
| PB-04 | US-04: Inspect relevance and claim assessments | Must | Sprint 2 | Done | `backend/agents/`; `tests/test_agents.py` |
| PB-05 | US-05: Inspect completeness and weighted verdict | Must | Sprint 3 | Done | Completeness/verdict agents; `backend/core/config.py`; `tests/test_agents.py` |
| PB-06 | US-06: Save and reopen evaluations | Must | Sprint 3 | Done | `backend/database/repository.py`; `tests/test_persistence.py` |
| PB-07 | US-07: Evaluate a batch with failure isolation | Must | Sprint 3–4 | Done | Batch API and CSV workflow; `tests/test_milestone4.py` |
| PB-08 | US-08: Filter analytics and compare response sources | Should | Sprint 4 | Done | `frontend/components/Dashboard.tsx`; `backend/services/analytics_service.py`; `tests/test_milestone4.py` |
| PB-09 | US-09: Download a traceable PDF batch report | Should | Sprint 4 | Done | Report endpoint; `tests/test_milestone4.py`; deployed PDF smoke check |
| PB-10 | US-10: Use a deployed frontend and backend | Must | Release hardening | Done | `render.yaml`; live evaluation, CORS, batch, dashboard, and PDF checks on November 6, 2026 |
| PB-11 | US-11: Avoid capitalization-only claim conflicts | Must | Release hardening | Done | Commit `219c4a5`; regression in `tests/test_agents.py` |
| PB-12 | Document the Agile delivery model and license | Must | Documentation follow-up | Done | This folder; root `LICENSE`; README links |

## Future backlog

| ID | User need / proposed change | Priority | Status | Acceptance target | Dependencies |
| --- | --- | --- | --- | --- | --- |
| PB-13 | Preserve evaluation history across hosting restarts | Must for production | To do | A saved evaluation remains available after a service restart | Persistent disk or managed database; hosting budget decision |
| PB-14 | Calibrate judgement against human-reviewed examples | Must for quality validation | To do | Publish labelled examples, measurement method, errors, and actual results | Human annotations and representative benchmark selection |
| PB-15 | Improve entity-role and sentence-level contradiction handling | Should | To do | Correctly distinguish who performed an action when several names occur in the same evidence | Labelled contradiction cases; PB-14 |
| PB-16 | Process large batches asynchronously | Should | To do | Return a job ID; expose progress, completion, and per-row failures | Job queue and worker hosting |
| PB-17 | Add authentication and per-user data access | Must before multi-user production | To do | Users can access only their own saved results; unauthorized requests are rejected | Identity provider and access-control design |
| PB-18 | Add optional LLM judges and evaluation version tracking | Could | To do | Provider failures are handled and results identify the model and scoring version | Provider credentials, cost approval, calibration |
| PB-19 | Improve cold-start feedback and request recovery | Should | To do | Explain warm-up delays, bound waiting, and offer a retry without misleading success | Deployment timing observations |

## Dependency order

PB-01 enables PB-02/PB-03. Evidence preparation enables PB-04. PB-04 enables PB-05. Saved structured results (PB-06) enable history-based analytics and reporting (PB-08/PB-09). PB-07 reuses the same evaluation workflow. PB-10 requires both services and the correct public API/CORS configuration.

## Scope boundaries

- The evaluator currently uses local MiniLM similarity and explicit rules, not an external LLM judge.
- System labels support comparison of submitted responses; the app does not automatically generate answers from commercial AI systems.
- Retrieval measurement is implemented, but no benchmark accuracy or retrieval score is asserted here.
- Persistent production storage, authentication, and background jobs remain future work.
