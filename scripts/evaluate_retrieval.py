"""Calculate retrieval metrics from actual indexed benchmark queries."""

import argparse
import csv
import json
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.core.config import get_settings
from backend.datasets.squad_loader import load_squad
from backend.datasets.truthfulqa_loader import load_truthfulqa
from backend.rag.embeddings import get_embedding_service
from backend.rag.retriever import SemanticRetriever
from backend.rag.vector_store import ChromaVectorStore


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--queries", type=int, default=50, help="Maximum benchmark queries.")
    parser.add_argument("--output", type=Path, help="Optional .json or .csv result file.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    settings = get_settings()
    store = ChromaVectorStore(settings.chroma_persist_dir, settings.chroma_collection)
    if store.count == 0:
        raise SystemExit("The vector index is empty. Run scripts/ingest_datasets.py first.")

    each = max(1, args.queries // 2)
    documents = [*load_squad(each), *load_truthfulqa(each)][: args.queries]
    retriever = SemanticRetriever(get_embedding_service(), store)
    rows = []
    reciprocal_ranks = []
    for document in documents:
        results = retriever.retrieve(document.question, max(5, settings.top_k))
        rank = next(
            (index for index, item in enumerate(results, start=1) if item.document_id == document.document_id),
            None,
        )
        reciprocal_ranks.append(1.0 / rank if rank else 0.0)
        rows.append(
            {
                "dataset": document.dataset,
                "document_id": document.document_id,
                "question": document.question,
                "rank": rank,
                "hit_at_1": bool(rank and rank <= 1),
                "hit_at_3": bool(rank and rank <= 3),
                "hit_at_5": bool(rank and rank <= 5),
            }
        )

    count = len(rows)
    summary = {
        "queries_evaluated": count,
        "hit_at_1": sum(row["hit_at_1"] for row in rows) / count,
        "hit_at_3": sum(row["hit_at_3"] for row in rows) / count,
        "hit_at_5": sum(row["hit_at_5"] for row in rows) / count,
        "mrr_at_5": sum(reciprocal_ranks) / count,
    }
    print(json.dumps(summary, indent=2))

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        if args.output.suffix.lower() == ".csv":
            with args.output.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=rows[0].keys())
                writer.writeheader()
                writer.writerows(rows)
        elif args.output.suffix.lower() == ".json":
            args.output.write_text(
                json.dumps({"summary": summary, "queries": rows}, indent=2), encoding="utf-8"
            )
        else:
            raise SystemExit("--output must end in .json or .csv")


if __name__ == "__main__":
    main()
