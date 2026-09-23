from collections.abc import Iterable

from backend.core.config import configure_huggingface_cache
from backend.datasets.normalizer import NormalizedDocument, normalize_truthfulqa


def load_truthfulqa(limit: int | None = None) -> list[NormalizedDocument]:
    """Load and normalize the TruthfulQA generation validation split."""
    try:
        configure_huggingface_cache()
        from datasets import load_dataset

        split = f"validation[:{limit}]" if limit else "validation"
        records: Iterable[dict] = load_dataset(
            "truthful_qa",
            "generation",
            split=split,
        )
        return [normalize_truthfulqa(record, index) for index, record in enumerate(records)]
    except Exception as exc:
        raise RuntimeError(f"Unable to load TruthfulQA from Hugging Face: {exc}") from exc
