# LLM Response Evaluation System

## Overview

An explainable, multi-agent, RAG-based system for evaluating AI-generated responses. The application prepares provenance-rich evidence, evaluates relevance, accuracy, groundedness/hallucination, and completeness, then produces a transparent weighted verdict. It also supports batch runs, SQLite history, and an aggregate dashboard.

## Problem Statement

LLM responses may sound plausible while being incomplete, irrelevant, or unsupported. Responsible evaluation needs more than a single opaque score: it needs trusted evidence, traceable provenance, distinct evaluation dimensions, reproducible retrieval, and validation against benchmarks.

## Objective

Provide the production-structured foundation from user submission through semantic evidence retrieval, ready for Milestone 2 agents without redesigning the data or RAG layers.

## Features

- Responsive Next.js evaluation form with validation and request states
- FastAPI endpoint with strict, whitespace-normalizing Pydantic schemas
- SQuAD and TruthfulQA ingestion through Hugging Face `datasets`
- Common validated benchmark-document representation
- Conservative cleaning, duplicate handling, configurable overlap chunking
- Cached local `all-MiniLM-L6-v2` embedding service
- Persistent cosine-distance Chroma collection with idempotent upserts
- Configurable Top-K semantic retrieval with provenance metadata
- Direct reference evidence and temporary in-memory source-text ranking
- Typed evidence package designed for future judge agents
- Actual Hit@1, Hit@3, Hit@5, and MRR@5 retrieval measurement
- Backend tests for validation, normalization, chunking, retrieval, and evidence policy
- Explainable relevance, accuracy, hallucination, and completeness agents
- Claim-level supported, unsupported, and contradicted classifications
- Configurable weighted verdict with retained component explanations
- Batch evaluation, SQLite history, and dashboard summaries

## Milestone Roadmap

### Milestone 1 — implemented

Foundation, input UI/API, benchmark knowledge base, RAG retrieval, evidence packaging, retrieval validation, and documentation.

### Milestone 2 — implemented

Relevance, accuracy, and hallucination judge agents plus an evaluation orchestrator and validated structured outputs.

### Milestone 3 — implemented

Completeness and verdict agents, explicit weighted policy, persisted runs, batch evaluation, and analytics dashboard.

## System Architecture

```mermaid
flowchart LR
  U[User] --> F[Next.js input]
  F --> A[FastAPI validation]
  A --> E[Evidence Service]
  E --> D[Direct reference]
  E --> S[Temporary source ranking]
  E --> R[Semantic Retriever]
  R --> M[MiniLM embeddings]
  M --> C[(ChromaDB)]
  D --> P[EvidencePackage]
  S --> P
  C --> P
  P --> J[Explainable judge agents]
  J --> V[Weighted verdict]
  V --> S[(SQLite history)]
  V --> O[Results UI]
  S --> D[Dashboard]
```

The complete future architecture and information flow are in [`docs/architecture.md`](docs/architecture.md). A code-aligned explanation of the current API, ingestion pipeline, evidence selection, retrieval behavior, errors, and verification procedure is in [`docs/backend-working-procedure.md`](docs/backend-working-procedure.md).

## Tech Stack

Next.js, TypeScript, Tailwind CSS, Python, FastAPI, Pydantic, Hugging Face Datasets, Sentence Transformers, ChromaDB, NumPy, Pandas, Pytest, and Uvicorn. Selection rationale is documented in [`docs/tech-stack.md`](docs/tech-stack.md).

## Project Structure

```text
.
├── backend/
│   ├── api/evaluation.py
│   ├── core/config.py
│   ├── datasets/{normalizer,squad_loader,truthfulqa_loader}.py
│   ├── models/evaluation.py
│   ├── rag/{cleaner,chunker,embeddings,loader,retriever,vector_store}.py
│   ├── services/evidence_service.py
│   └── main.py
├── frontend/
│   ├── app/
│   ├── components/
│   ├── lib/
│   └── types/
├── scripts/{ingest_datasets,evaluate_retrieval}.py
├── tests/
├── docs/
├── data/
├── .env.example
├── requirements.txt
└── README.md
```

## Installation

Prerequisites: Node.js 20+ and Python 3.11 or 3.12. From the repository root on PowerShell:

```powershell
Copy-Item .env.example .env
uv venv --python 3.11
.\.venv\Scripts\Activate.ps1
uv pip install -r requirements.txt
Set-Location frontend
npm install
Set-Location ..
```

With a preinstalled Python interpreter, `python -m venv .venv` and `python -m pip install -r requirements.txt` are equivalent alternatives.

## Backend Setup

Configuration is loaded from the root `.env`. Start from the repository root with the virtual environment active:

```powershell
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

Health check: `GET http://localhost:8000/health`. Interactive API documentation: `http://localhost:8000/docs`.

## Frontend Setup

For a non-default backend URL, create `frontend/.env.local`:

```text
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
```

Then:

```powershell
Set-Location frontend
npm run dev
```

Open `http://localhost:3000`.

## Netlify Deployment

The root `netlify.toml` deploys the Next.js application from `frontend/` using Node.js 22. When the GitHub repository is linked, the file supplies these settings:

- Base directory: `frontend`
- Build command: `npm run build`
- Publish directory: `out`

The frontend uses Next.js static export mode, so the production build creates `frontend/out/index.html` and deployable assets. This avoids publishing the internal `.next` build directory directly, which can produce a Netlify “Page not found” response when no Next.js runtime adapter is active.

Python is pinned to 3.11 through `.python-version` and `PYTHON_VERSION` to prevent build images from selecting Python 3.14, which can force `pydantic-core` to compile from source. A correct Netlify frontend build does not install `requirements.txt`; the pin is a safe fallback for repository tooling.

The FastAPI, Sentence Transformers, and persistent ChromaDB backend is not deployed by Netlify. Deploy the backend to a persistent Python or container host, set `NEXT_PUBLIC_API_URL` in Netlify to that public HTTPS URL, and trigger a new frontend deployment. `http://127.0.0.1:8000` works only for local development and must not be used in production.

## Dataset Ingestion and Vector Index

The single ingestion command downloads both real benchmark datasets, normalizes and chunks them, generates embeddings, and populates Chroma:

```powershell
python scripts/ingest_datasets.py --reset
```

Omit `--reset` for idempotent upserts into the existing collection. In development mode the configured samples are used. To ingest full validation splits, set `DATASET_MODE=full`; this takes longer and requires more disk/memory.

## Running the Application

1. Run ingestion once.
2. Start the backend from the repository root.
3. Start the frontend from `frontend/`.
4. Submit a question and response. Add a trusted reference and/or source material when available.
5. Inspect the verdict, component explanations, claim classifications, missing aspects, and cited evidence. The Batch and Dashboard tabs expose the Milestone 3 flows.

## API

### `GET /health`

Lightweight liveness response that does not load the embedding model.

### `POST /api/v1/evaluations/prepare`

Request:

```json
{
  "question": "What causes the seasons?",
  "ai_response": "The distance from the Sun changes.",
  "reference_answer": null,
  "source_text": null
}
```

`question` and `ai_response` are required non-blank strings. Optional blank strings normalize to `null`. The response contains status, message, and a provenance-bearing `EvidencePackage`.

### `POST /api/v1/evaluations/evaluate`

Accepts the same request and returns a complete structured evaluation containing the `EvidencePackage`, four dimension results, claim analysis, and weighted verdict.

### `POST /api/v1/evaluations/batch`

Accepts `{"items": [...]}` and returns every evaluation plus calculated averages and verdict counts.

### `GET /api/v1/evaluations/dashboard`

Returns totals, average dimension scores, verdict counts, and recent locally persisted evaluations.

### `GET /api/v1/evaluations/{evaluation_id}`

Returns one saved evaluation or a structured 404 response.

## RAG Pipeline

Benchmark records are loaded into one schema, cleaned, deduplicated, chunked with overlap, embedded in batches, and upserted to Chroma using stable chunk IDs. At request time, a question embedding retrieves Top-K chunks using cosine distance. The API returns both the raw distance and `1 - distance` similarity. Submitted source text follows the same cleaning/chunking/embedding logic but is ranked in memory and never enters the permanent benchmark collection.

Evidence priority is: preserve a supplied reference answer; rank supplied source text; when neither is available, query the benchmark knowledge base. The package has separate fields so direct and retrieved evidence can coexist in future policies.

## Retrieval Evaluation

After ingestion:

```powershell
python scripts/evaluate_retrieval.py --queries 50 --output data/retrieval-evaluation.json
```

The script loads real benchmark questions, retrieves from the actual collection, matches expected document IDs, and computes Hit@1/3/5 and MRR@5. It exits with an error if the index is empty; it never fabricates metrics.

## Testing

```powershell
python -m pytest
Set-Location frontend
npm run build
```

Unit tests isolate external downloads for speed and cover validation, normalization, chunking, retrieval, agent behavior, compatible/conflicting claim details, verdict aggregation, and persistence. Real dataset/model/index behavior is verified by the ingestion and retrieval-evaluation commands.

## Screenshots

Presentation previews and screenshots are generated locally for review before any repository push.

## Current Limitations

- The local judge agents use MiniLM similarity and transparent rules, not a paid external LLM or human fact checker.
- Claim splitting is sentence-level, and contradiction rules are conservative rather than full natural-language inference.
- Batch processing is synchronous and SQLite is intended for local/internship-scale use.
- Netlify hosts only the static frontend. The FastAPI service requires a separate persistent Python/container host and `NEXT_PUBLIC_API_URL` must point to it.

Detailed requirement maps are available in [`docs/milestone-2.md`](docs/milestone-2.md) and [`docs/milestone-3.md`](docs/milestone-3.md).

## Configuration

| Variable | Default | Meaning |
|---|---:|---|
| `BACKEND_HOST` | `127.0.0.1` | Bind host used by the documented command |
| `BACKEND_PORT` | `8000` | API port |
| `FRONTEND_ORIGIN` | `http://localhost:3000` | Allowed browser origin |
| `NEXT_PUBLIC_API_URL` | `http://127.0.0.1:8000` | Browser-visible API base URL |
| `EMBEDDING_MODEL` | `sentence-transformers/all-MiniLM-L6-v2` | Embedding model identifier |
| `HF_CACHE_DIR` | `./data/cache/huggingface` | Ignored local dataset/model cache |
| `CHROMA_PERSIST_DIR` | `./data/chroma` | Local index directory |
| `CHROMA_COLLECTION` | `benchmark_evidence` | Collection name |
| `TOP_K` | `5` | Returned evidence limit |
| `CHUNK_SIZE` | `400` | Approximate whitespace-token window |
| `CHUNK_OVERLAP` | `50` | Overlapping tokens |
| `DATASET_MODE` | `development` | `development` or `full` |
| `SQUAD_SAMPLE_SIZE` | `250` | Development SQuAD records |
| `TRUTHFULQA_SAMPLE_SIZE` | `250` | Development TruthfulQA records |

Chunk parameters are starting values, not universally optimal settings. Tune them with measured retrieval experiments.

## Current Limitations

- Benchmark coverage is limited to sampled SQuAD and TruthfulQA in development mode.
- TruthfulQA evidence consists of benchmark questions and reference answers rather than long source documents.
- Whitespace-token chunking is model-independent but approximate; it does not use the embedding model's exact tokenizer.
- Chroma persistence is local and intended for a single-developer Milestone 1 deployment.
- No PDF upload, authentication, submission history, reranking, or cross-encoder is included.
- First-time ingestion downloads datasets and a model and may be slow on CPU.

## Future Work

Intentionally deferred: all LLM judge calls, relevance/accuracy/hallucination/completeness scoring, verdict aggregation, weighting, orchestration, persisted evaluation history, batch workflows, dashboards, and analytics. Their responsibilities are defined in [`docs/architecture.md`](docs/architecture.md), while research background is in [`docs/research.md`](docs/research.md).
