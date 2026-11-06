# User Stories and Acceptance Criteria

These stories describe the implemented scope as of November 6, 2026. They are reconstructed from the code and milestone requirements. Future acceptance targets are tracked separately in the [backlog](product-backlog.md).

## US-01 — Submit evaluation inputs

**As a reviewer, I want to submit a question and an AI-generated answer so that I can assess the answer's quality.**

- Given blank or whitespace-only required inputs, submission is rejected with a clear validation error.
- Given valid inputs, the API accepts the question and response and normalizes optional blank fields.
- The form displays loading, success, and failure states.
- Verification: `tests/test_api.py`; evaluation form and API schemas.

## US-02 — Use supplied evidence

**As a reviewer, I want to provide a reference answer or source text so that the evaluation has an explicit basis.**

- A direct reference remains identifiable in the evidence package.
- Submitted source text is cleaned, chunked, and ranked when used.
- Submitted source-text passages are ranked temporarily and are not written to the permanent benchmark collection.
- Verification: `tests/test_evidence_service.py`; evidence service.

## US-03 — Retrieve benchmark evidence

**As a reviewer without reference material, I want relevant benchmark passages so that evaluation can use available evidence.**

- Ingestion normalizes SQuAD and TruthfulQA records and stores stable passage identifiers.
- Configured Top-K retrieval returns passage content and provenance.
- Empty or invalid queries are handled explicitly.
- The retrieval script calculates actual Hit@1/3/5 and MRR@5 rather than placeholder values.
- Verification: normalization, chunking, and retrieval tests; ingestion/retrieval scripts.

## US-04 — Understand claim assessments

**As a reviewer, I want relevance scores and claim-level explanations so that I can see why a response needs review.**

- Relevance describes the relationship between question and response.
- Claims receive supported, unsupported, or contradicted classifications with explanations.
- Accuracy and groundedness summarize the claim assessments.
- Higher groundedness means better support; the raw hallucination rate remains distinct.
- Missing evidence is reported rather than replaced by fabricated evidence.
- Verification: `tests/test_agents.py`; agent implementations.

## US-05 — Understand completeness and verdict

**As a reviewer, I want missing-aspect analysis and an overall verdict so that I can review quality across dimensions.**

- Completeness exposes covered and missing aspects derived from the available evidence.
- Default weights are relevance 20%, accuracy 35%, groundedness 25%, and completeness 20%.
- Configured weights are normalized and the component results remain visible.
- The overall score remains in the 0–100 range.
- Verification: `tests/test_agents.py`; completeness and verdict agents.

## US-06 — Save and reopen results

**As a reviewer, I want completed evaluations saved so that I can inspect them later.**

- Completed structured results are stored in SQLite with an evaluation identifier.
- A known identifier returns the saved result; an unknown identifier returns a structured 404.
- Results retain their component explanations and evidence.
- Verification: `tests/test_persistence.py`; repository implementation.
- Boundary: this story covers application persistence, not durable storage across free-hosting restarts.

## US-07 — Evaluate a batch

**As a reviewer, I want JSON or CSV batch submission so that I can review several answers efficiently.**

- CSV requires `question` and `ai_response`; `reference_answer` and `source_text` are optional.
- Missing required headers produce a clear validation failure.
- Invalid items/rows are reported while valid items continue.
- Results include individual evaluations and calculated batch summaries.
- Verification: `tests/test_milestone4.py`; batch endpoints and interface.

## US-08 — Inspect analytics and response-source comparison

**As a reviewer, I want filtered metrics and drill-down so that I can compare stored evaluation runs.**

- Filters include outcome, score range, batch, and system/source.
- Totals, percentages, distributions, issue frequencies, and trends derive from saved evaluations.
- A selected evaluation opens its stored detailed result.
- Dashboard outcome bands are pass 70–100, needs improvement 45–69.99, and fail below 45.
- Verification: `tests/test_milestone4.py`; dashboard API/interface; deployed dashboard check.

## US-09 — Export a PDF report

**As a reviewer, I want a downloadable batch report so that I can share an evaluation record.**

- A valid batch produces a PDF containing summary metrics and detailed evaluation information.
- Reports use persisted results and do not rerun the evaluation agents.
- The downloaded response is a valid PDF.
- Verification: `tests/test_milestone4.py`; deployed PDF export check.

## US-10 — Use the hosted application

**As a user, I want a public frontend connected to a running API so that I can evaluate answers without running local servers.**

- Both Render services deploy with the documented configuration.
- The frontend uses the backend HTTPS URL, not a localhost address.
- The API allows the frontend's origin and returns a healthy `/health` response.
- A real evaluation, batch, dashboard request, and report download complete.
- Verification: Render deployment and live API/browser checks on November 6, 2026.
- Boundary: the free backend can sleep and its first evaluation can be slow; permanent availability is not claimed.

## US-11 — Avoid capitalization-only contradictions

**As a reviewer, I want ordinary sentence capitalization handled consistently so that a supported claim is not rejected merely because a word starts a sentence.**

- `Seasons` in the response can match `seasons` in the evidence.
- Existing checks for genuinely conflicting names continue to pass.
- The deployed seasons example is classified as supported after the fix.
- Verification: regression test and existing name-conflict test in `tests/test_agents.py`; live score 96.01 on the recorded test input. This is one functional example, not a benchmark performance claim.
