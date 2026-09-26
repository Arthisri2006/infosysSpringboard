# Milestone 4 - Analytics, Reporting, and Final Validation

## Scope

Milestone 4 turns stored evaluation results into decision-ready analytics and downloadable reports. It does not change the Milestone 2 judge logic or the Milestone 3 weighted verdict. Dashboard calculations and PDF content are derived from the same persisted `EvaluationResult` records.

## Requirement mapping

| Mentor requirement | Implementation |
| --- | --- |
| Pass / needs improvement / fail totals and percentages | `AnalyticsService`; visible on the dashboard |
| Average dimension scores | Dashboard average bars for relevance, accuracy, groundedness, completeness, and overall |
| Score distribution | Four fixed score bands for every dimension |
| Hallucination and unsupported-claim frequency | Claim totals, response frequency, and issue labels |
| Missing-information frequency | Missing-aspect count, response rate, and common aspects |
| Trends across batches | Per-batch average scores and outcome distributions |
| Filters | Outcome, score range, batch, and system/source |
| Drill-down | Dashboard list opens the stored full evaluation and explanations |
| CSV workflow | CSV upload with required-header validation and row-level failure isolation |
| PDF report | Batch metadata, metrics, dimensions, recommendations, detailed results, claims, gaps, evidence, and verdict |
| Two-system comparison | Batch records carry `system_name`; dashboard can compare/filter multiple response sources |
| Calculation validation | `tests/test_milestone4.py` verifies thresholds, averages, distributions, filters, CSV errors, and PDF content |

## Outcome rules

The existing verdict labels remain unchanged. For the mentor-facing dashboard, the overall 0-100 score is also mapped to:

- Pass: 70-100
- Needs improvement: 45-69.99
- Fail: below 45

These boundaries are centralized in `backend/services/analytics_service.py` and are not duplicated in the frontend.

## CSV format

Required columns:

```text
question,ai_response
```

Optional columns:

```text
reference_answer,source_text
```

The batch name and AI system/source are entered once in the interface. A malformed row is returned in `failures`; other valid rows continue.

## PDF consistency

The report endpoint reads the selected batch and all successful results from SQLite. It does not rerun the judge agents, invent metrics, or use frontend state. This ensures the dashboard, drill-down, and report all represent the same stored evaluation run.

## API additions

- `POST /api/v1/evaluations/batch` - JSON batch with metadata and failure isolation
- `POST /api/v1/evaluations/batch/csv` - raw CSV batch ingestion
- `GET /api/v1/evaluations/dashboard` - filtered analytics
- `GET /api/v1/evaluations/reports/batch/{batch_id}.pdf` - stored batch report
- `GET /api/v1/evaluations/{evaluation_id}` - detailed result drill-down

## Verification

Run:

```powershell
.\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider
cd frontend
npm run build
```

Formal demonstrations should capture outputs from two named AI systems under equivalent prompts and references. The files under `data/demo/` are transparent local fixtures for exercising the workflow; they are not claimed to be live outputs from commercial systems.
