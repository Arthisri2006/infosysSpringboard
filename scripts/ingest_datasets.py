"""Load benchmark datasets, normalize/chunk them, and build the Chroma index."""

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.core.config import get_settings
from backend.datasets.squad_loader import load_squad
from backend.datasets.truthfulqa_loader import load_truthfulqa
from backend.rag.chunker import Chunker
from backend.rag.embeddings import get_embedding_service
from backend.rag.loader import KnowledgeBaseLoader
from backend.rag.vector_store import ChromaVectorStore


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--reset", action="store_true", help="Rebuild the configured collection before ingestion."
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    settings = get_settings()
    limit_squad = settings.squad_sample_size if settings.dataset_mode == "development" else None
    limit_truthfulqa = (
        settings.truthfulqa_sample_size if settings.dataset_mode == "development" else None
    )

    print(f"Loading SQuAD ({settings.dataset_mode} mode)...")
    squad = load_squad(limit_squad)
    print(f"Loading TruthfulQA ({settings.dataset_mode} mode)...")
    truthfulqa = load_truthfulqa(limit_truthfulqa)

    store = ChromaVectorStore(settings.chroma_persist_dir, settings.chroma_collection)
    if args.reset:
        store.reset()
    loader = KnowledgeBaseLoader(
        Chunker(settings.chunk_size, settings.chunk_overlap),
        get_embedding_service(),
        store,
    )
    summary = loader.ingest([*squad, *truthfulqa])
    summary.update({"squad_records": len(squad), "truthfulqa_records": len(truthfulqa)})
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
