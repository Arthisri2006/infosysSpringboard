# LLM Response Evaluation System

## Overview

Milestone 1 of an explainable, multi-agent, RAG-based system for evaluating AI-generated responses. The implemented application accepts a question and AI response, prepares direct or retrieved evidence with provenance, and returns a stable `EvidencePackage` for future judge agents.

This milestone **prepares evidence only**. It does not produce relevance, accuracy, hallucination, completeness, or verdict scores.

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

## Milestone Roadmap

### Milestone 1 — implemented

Foundation, input UI/API, benchmark knowledge base, RAG retrieval, evidence packaging, retrieval validation, and documentation.

### Milestone 2 — planned, not implemented

Relevance, accuracy, and hallucination judge agents plus an evaluation orchestrator and validated structured outputs.

### Milestone 3 — planned, not implemented

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
  P --> J[Judge agents<br/>Future M2/M3]
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
- Publish directory: `.next`

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
5. Inspect the evidence package. No evaluation verdict is produced in this milestone.

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

Unit tests isolate external downloads for speed. Real dataset/model/index behavior is verified by the ingestion and retrieval-evaluation commands.

## Screenshots

Screenshots are intentionally not checked in yet. Run the frontend to view the submission and evidence-inspection screens; repository screenshots can be added after the mentor-approved visual review without committing generated build artifacts.

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
