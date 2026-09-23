from collections.abc import Iterable

from backend.core.config import configure_huggingface_cache
from backend.datasets.normalizer import NormalizedDocument, normalize_squad


def load_squad(limit: int | None = None) -> list[NormalizedDocument]:
    """Load and normalize the SQuAD validation split from Hugging Face."""
    try:
        configure_huggingface_cache()
        from datasets import load_dataset

        split = f"validation[:{limit}]" if limit else "validation"
        records: Iterable[dict] = load_dataset("rajpurkar/squad", split=split)
        return [normalize_squad(record) for record in records]
    except Exception as exc:
        raise RuntimeError(f"Unable to load SQuAD from Hugging Face: {exc}") from exc
