from functools import lru_cache
import os
from pathlib import Path
from typing import Literal

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    """Validated application settings loaded from environment variables."""

    backend_host: str = "127.0.0.1"
    backend_port: int = Field(8000, ge=1, le=65535)
    frontend_origin: str = "http://localhost:3000"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    hf_cache_dir: Path = PROJECT_ROOT / "data" / "cache" / "huggingface"
    chroma_persist_dir: Path = PROJECT_ROOT / "data" / "chroma"
    chroma_collection: str = "benchmark_evidence"
    top_k: int = Field(5, ge=1, le=100)
    chunk_size: int = Field(400, ge=10)
    chunk_overlap: int = Field(50, ge=0)
    dataset_mode: Literal["development", "full"] = "development"
    squad_sample_size: int = Field(250, ge=1)
    truthfulqa_sample_size: int = Field(250, ge=1)

    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env", env_file_encoding="utf-8", extra="ignore"
    )

    @model_validator(mode="after")
    def validate_chunking(self) -> "Settings":
        if self.chunk_overlap >= self.chunk_size:
            raise ValueError("CHUNK_OVERLAP must be smaller than CHUNK_SIZE")
        for field_name in ("hf_cache_dir", "chroma_persist_dir"):
            path = getattr(self, field_name)
            if not path.is_absolute():
                setattr(self, field_name, (PROJECT_ROOT / path).resolve())
        return self

    @property
    def cors_origins(self) -> list[str]:
        """Allow both common local frontend hostnames during development."""
        origins = [self.frontend_origin.rstrip("/")]
        if self.frontend_origin in {"http://localhost:3000", "http://127.0.0.1:3000"}:
            origins.extend(["http://localhost:3000", "http://127.0.0.1:3000"])
        return list(dict.fromkeys(origins))


@lru_cache
def get_settings() -> Settings:
    return Settings()


def configure_huggingface_cache(settings: Settings | None = None) -> Path:
    """Keep model and dataset downloads in the configured ignored project cache."""
    cache_dir = (settings or get_settings()).hf_cache_dir
    cache_dir.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("HF_HOME", str(cache_dir))
    return cache_dir
