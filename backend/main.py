from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.evaluation import router as evaluation_router
from backend.core.config import get_settings


settings = get_settings()
app = FastAPI(
    title="Explainable Multi-Agent LLM Response Evaluator",
    version="4.0.0",
    description="Evaluates grounded responses, aggregates batches, and exports explainable reports.",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
app.include_router(evaluation_router)


@app.get("/health", tags=["system"])
def health() -> dict[str, str]:
    return {"status": "ok", "milestone": "4"}
