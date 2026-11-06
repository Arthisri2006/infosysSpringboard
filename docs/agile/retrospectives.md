# Retrospectives and Improvement Actions

These are retrospective observations reconstructed from repository artifacts and the November 6, 2026 deployment session. They are not minutes of meetings that were not recorded. No team votes, attendance, satisfaction scores, or velocity figures are invented.

## Sprint 1 — Evidence foundation

- **Worked:** A common document schema and explicit evidence package separate retrieval from later evaluation.
- **Concern:** Dataset/model downloads and a populated index are setup dependencies; unit checks alone cannot establish retrieval quality.
- **Lesson:** Keep deterministic component checks separate from actual ingestion and retrieval measurement.
- **Action:** Run the retrieval measurement workflow for the chosen benchmark slice and preserve its actual metrics before making performance claims (PB-14; To do for calibrated reporting).
- **Evidence:** [Milestone 1 map](../milestone-1.md); ingestion and retrieval scripts; evidence-policy tests.

## Sprint 2 — Explainable assessment

- **Worked:** Separate relevance, accuracy, and groundedness components preserve claim-level explanations and supporting evidence.
- **Concern:** Similarity can accept an incorrect entity-role relationship; sentence-level rules cannot establish factual truth universally.
- **Lesson:** Explainability does not replace measurement against human-labelled cases.
- **Action:** Expand labelled contradiction examples, including several names in one passage, and calibrate thresholds (PB-14/PB-15; To do).
- **Evidence:** Claim analyzer; agent tests; known limitations in [Milestone 2](../milestone-2.md).

## Sprint 3 — Aggregation and history

- **Worked:** A shared orchestrator and structured results let batches reuse single-evaluation behavior; SQLite enables history and analytics.
- **Concern:** A weighted average can hide weak dimensions, and local persistence does not guarantee durable production history.
- **Lesson:** Show component scores alongside verdicts and describe persistence boundaries explicitly.
- **Action:** Retain dimension explanations (implemented); provide managed or persistent storage before durable production use (PB-13; To do).
- **Evidence:** Verdict agent, repository, and persistence tests; [Milestone 3](../milestone-3.md).

## Sprint 4 — Review tools

- **Worked:** Dashboard, drill-down, and PDF reports use the same persisted result records. CSV failures are isolated by row.
- **Concern:** Comparison labels alone do not prove a fair comparison between live commercial models; synchronous processing limits large batches.
- **Lesson:** Use equivalent prompts/references and label fixtures honestly.
- **Action:** Preserve comparison metadata (implemented); add asynchronous jobs for larger batches (PB-16; To do).
- **Evidence:** Analytics service, report endpoint, CSV checks, and [Milestone 4](../milestone-4.md).

## Deployment hardening — November 6, 2026

| Observation | Change / lesson | Status |
| --- | --- | --- |
| A static Netlify frontend pointed at a localhost API | A published page is not proof of a working application. Move the complete workflow to the two connected Render services. | Done; `d01e44c` |
| Render reported a backend failure above the 512 MB limit | Install CPU-only PyTorch and limit threads; validate actual evaluation under the hosting constraints. | Change delivered in `97e910a`; subsequent live evaluation/batch/report checks passed |
| The correct seasons response was marked contradicted because of sentence capitalization | Compare candidate name-like terms with case-insensitive evidence words; keep the genuine conflicting-name regression. | Done; `219c4a5`; recorded suite: 29 passed |
| Free hosting sleeps and uses ephemeral storage | Explain warm-up delays and avoid promises of permanent history or instant availability. | Limitation documented; PB-13/PB-19 remain To do |

## Next review checklist

1. Demonstrate the selected stories against their acceptance criteria.
2. Record actual observations and unresolved defects, including incorrect judgements.
3. Review open backlog dependencies and hosting constraints.
4. Select improvement actions and update their status with evidence.
5. Record a future iteration's real dates and actual participants only when available.
