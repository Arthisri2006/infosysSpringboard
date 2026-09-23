import re
import unicodedata


def clean_text(value: str | None) -> str:
    """Normalize Unicode and whitespace while preserving natural language."""
    if value is None:
        return ""
    normalized = unicodedata.normalize("NFKC", str(value))
    return re.sub(r"\s+", " ", normalized).strip()


def deduplicate_documents(documents):
    """Keep the first document for each dataset/document identifier pair."""
    seen: set[tuple[str, str]] = set()
    result = []
    for document in documents:
        key = (document.dataset, document.document_id)
        if key not in seen and document.context:
            seen.add(key)
            result.append(document)
    return result

