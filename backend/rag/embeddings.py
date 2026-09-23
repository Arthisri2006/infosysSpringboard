from functools import lru_cache
from typing import Protocol, Sequence

import numpy as np

from backend.core.config import configure_huggingface_cache, get_settings


class EmbeddingProvider(Protocol):
    def embed_documents(self, texts: Sequence[str]) -> list[list[float]]: ...
    def embed_query(self, text: str) -> list[float]: ...


class SentenceTransformerEmbeddingService:
    """Centralized, reusable Sentence Transformers embedding adapter."""

    def __init__(self, model_name: str, cache_dir: str | None = None) -> None:
        try:
            configure_huggingface_cache()
            from sentence_transformers import SentenceTransformer

            try:
                # Prefer an already downloaded model so normal local startup never
                # waits on Hub freshness checks. First-time setup still falls back
                # to the online download path with a clear error if that fails.
                self._model = SentenceTransformer(
                    model_name,
                    cache_folder=cache_dir,
                    local_files_only=True,
                )
            except Exception:
                self._model = SentenceTransformer(model_name, cache_folder=cache_dir)
        except Exception as exc:
            raise RuntimeError(f"Unable to initialize embedding model '{model_name}': {exc}") from exc

    def embed_documents(self, texts: Sequence[str]) -> list[list[float]]:
        if not texts:
            return []
        try:
            vectors = self._model.encode(
                list(texts), batch_size=32, show_progress_bar=False, normalize_embeddings=True
            )
            return np.asarray(vectors).tolist()
        except Exception as exc:
            raise RuntimeError(f"Document embedding failed: {exc}") from exc

    def embed_query(self, text: str) -> list[float]:
        if not text.strip():
            raise ValueError("Query text cannot be empty")
        return self.embed_documents([text])[0]


@lru_cache(maxsize=1)
def get_embedding_service() -> SentenceTransformerEmbeddingService:
    settings = get_settings()
    return SentenceTransformerEmbeddingService(
        settings.embedding_model, str(settings.hf_cache_dir / "hub")
    )
