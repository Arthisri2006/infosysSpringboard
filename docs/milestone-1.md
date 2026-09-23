# Milestone 1 Verification Map

| Mentor requirement | Implementation | Verification |
|---|---|---|
| M1.1 Research | `docs/research.md` | Dimension, judge, RAG, framework, and dataset sections |
| M1.2 Architecture | `docs/architecture.md` | Mermaid diagram, flow, boundaries, future agent contracts |
| M1.3 Evaluation input | `frontend/components/EvaluationForm.tsx` | Required/optional labels, client validation, loading/errors |
| Typed API | `backend/api/evaluation.py`, `backend/models/evaluation.py` | `tests/test_api.py`, OpenAPI `/docs` |
| SQuAD ingestion | `backend/datasets/squad_loader.py` | Real load in ingestion; normalizer unit test |
| TruthfulQA ingestion | `backend/datasets/truthfulqa_loader.py` | Real load in ingestion; normalizer unit test |
| Common schema | `NormalizedDocument` | Both loaders produce the same validated type |
| Cleaning/deduplication | `backend/rag/cleaner.py` | Used by normalization and ingestion |
| Configurable chunking | `backend/rag/chunker.py` | Small/long/overlap/metadata tests |
| Central embeddings | `backend/rag/embeddings.py` | Cached service; document/query/batch methods |
| Persistent index | `backend/rag/vector_store.py` | Stable IDs, upsert, query, scoped reset |
| Semantic retrieval | `backend/rag/retriever.py` | Top-K, metadata, and empty-query tests |
| Evidence policy | `backend/services/evidence_service.py` | Reference/source/fallback tests |
| Source-text isolation | In-memory ranking in `EvidenceService` | `temporary: true`; never sent to Chroma |
| Structured package | `EvidencePackage` Pydantic model | API response and frontend TypeScript mirror |
| Retrieval validation | `scripts/evaluate_retrieval.py` | Actual Hit@1/3/5 and MRR@5; optional JSON/CSV |
| Configuration | `backend/core/config.py`, `.env.example` | Values validated at startup |
| Results screen | `frontend/components/EvaluationResults.tsx` | Evidence/provenance/scores shown; no judge scores |
| Repository docs | `README.md`, `docs/` | Setup, commands, limits, roadmap |

## Scope guard

No judge LLM calls, dimension scores, weighted verdicts, batch evaluation orchestration, or analytics dashboard are implemented. Future components are documented only.

