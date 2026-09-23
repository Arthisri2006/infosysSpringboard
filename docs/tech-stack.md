# Technology Stack

| Technology | Purpose | Reason selected |
|---|---|---|
| Next.js | Browser application and production build | Mature React framework with routing, optimized builds, and straightforward local development. |
| TypeScript | Frontend data contracts | Catches drift between UI state and API evidence structures before runtime. |
| Tailwind CSS | Interface styling | Enables a consistent, responsive research UI without a heavy component dependency. |
| Python | Data/RAG backend | Strong ecosystem for NLP, datasets, vector search, and evaluation research. |
| FastAPI | HTTP API | Type-driven routing, automatic OpenAPI documentation, and concise error handling. |
| Pydantic / pydantic-settings | Request schemas and configuration | Validates external input and environment configuration using one typed model system. |
| Hugging Face `datasets` | SQuAD and TruthfulQA acquisition | Reproducible access to named dataset configurations and splits without custom scrapers. |
| Sentence Transformers | Local semantic embedding | Efficient, replaceable embedding runtime without a paid API dependency. |
| `all-MiniLM-L6-v2` | Default embedding model | Compact 384-dimensional general semantic model suitable for local development. |
| ChromaDB | Persistent vector index | Simple local persistence, metadata storage, upsert support, and cosine search. |
| NumPy | In-memory source-text ranking | Reliable vector math for temporary evidence without contaminating the permanent collection. |
| Pandas | Future tabular analysis/export support | Standard tool for inspecting benchmark and metric outputs; included for the stated project stack. |
| Pytest | Automated backend verification | Clear fixtures/assertions and strong FastAPI ecosystem support. |
| HTTPX | FastAPI test client transport | Tests endpoint behavior without starting an external server. |
| Uvicorn | ASGI server | Standard lightweight server for local FastAPI development. |
| JSON/CSV | Retrieval metric export | Portable, inspectable output without adding analytics infrastructure in Milestone 1. |

SQLite is intentionally not used yet: Milestone 1 has no requirement to persist submissions, and Chroma provides the required vector persistence. It can be added later for evaluation runs without coupling it to retrieval.

