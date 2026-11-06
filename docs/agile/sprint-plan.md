# Sprint Plan and Delivery Record

The four increments below align with the project's four milestones. Their sprint grouping is documented retrospectively; no historical start/end dates, sprint length, planning meetings, or story-point totals are inferred. Git dates indicate when changes were committed, not how long the work took. Milestones 2 and 3 were committed together.

## Sprint 1 — Validated input and RAG foundation

- **Goal:** Turn a submitted question/answer into a traceable evidence package.
- **Stories:** US-01, US-02, US-03.
- **Tasks:** Implement form/API schemas; normalize benchmarks; clean/chunk passages; add embeddings, Chroma storage, retrieval, and evidence selection.
- **Dependencies:** Dataset/model access and a configured local index.
- **Increment:** An input and evidence-preparation workflow with source provenance and retrieval measurement tooling.
- **Acceptance:** Input validation and evidence-policy behavior meet US-01–03; ingestion/retrieval scripts use actual data.
- **Evidence:** Commit `9ac18b5`; [Milestone 1 map](../milestone-1.md); normalization/chunking/retrieval/evidence/API tests.
- **Status:** Implemented.

## Sprint 2 — Explainable core evaluation

- **Goal:** Explain relevance and claim support against available evidence.
- **Story:** US-04.
- **Tasks:** Add the relevance agent, claim analyzer, accuracy/groundedness results, orchestrator, and structured result UI.
- **Dependencies:** Sprint 1 evidence package.
- **Increment:** Dimension scores with claim classifications and explanations.
- **Acceptance:** Supported/conflicting claim examples and structured result checks pass; limitations of similarity and rules remain explicit.
- **Evidence:** Commit `0cb80de` (also includes Sprint 3 scope); [Milestone 2](../milestone-2.md); `tests/test_agents.py`.
- **Status:** Implemented.

## Sprint 3 — Completeness, verdict, batches, and history

- **Goal:** Provide a complete scoring workflow and reusable saved results.
- **Stories:** US-05, US-06, JSON portion of US-07.
- **Tasks:** Add missing-aspect analysis, configurable verdict weights, batch orchestration, SQLite storage, lookup, and initial dashboard UI.
- **Dependencies:** Sprint 2 structured evaluations.
- **Increment:** A saved evaluation and batch workflow with aggregate scores and verdicts.
- **Acceptance:** Scores are bounded; weights normalize; saved results round-trip; batch failures are isolated.
- **Evidence:** Commit `0cb80de`; [Milestone 3](../milestone-3.md); agent and persistence tests.
- **Status:** Implemented.

## Sprint 4 — Analytics, CSV, and reporting

- **Goal:** Make stored evaluations useful for review and comparison.
- **Stories:** CSV portion of US-07, US-08, US-09.
- **Tasks:** Implement CSV validation, filtered analytics, distributions, issue frequencies, batch trends, result drill-down, and PDF reports.
- **Dependencies:** Sprint 3 persistence and batch results.
- **Increment:** A dashboard/report workflow derived from the same stored evaluations.
- **Acceptance:** Header/row errors, calculation boundaries, filters, and PDF content checks pass.
- **Evidence:** Commit `d707007`; [Milestone 4](../milestone-4.md); `tests/test_milestone4.py`.
- **Status:** Implemented.

## Release hardening — November 6, 2026

This is a recorded deployment follow-up, not an additional historical milestone.

| Change | Evidence | Outcome |
| --- | --- | --- |
| Configure both services on Render | `d01e44c`; `render.yaml` | Frontend and backend use Render service URLs |
| Reduce backend dependency footprint | `97e910a` | CPU-only PyTorch and thread controls; subsequent live workflow checks passed |
| Fix capitalization-only claim conflicts | `219c4a5` | Regression added; 29 backend tests passed in the recorded run |
| Verify hosted workflows | Live API and browser checks | Evaluation, CORS, batch, dashboard, and PDF succeeded |

## Proposed next iteration

Prioritize PB-13 (durable storage), PB-14 (human-labelled calibration), PB-15 (contradiction quality), and PB-19 (cold-start feedback). Select a feasible subset after confirming hosting budget and review data availability. Do not mark these items Done until their acceptance targets are demonstrated.
