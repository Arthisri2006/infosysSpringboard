import pytest

from backend.datasets.normalizer import NormalizedDocument
from backend.rag.chunker import Chunker


def test_small_document_is_one_chunk() -> None:
    chunks = Chunker(10, 2).chunk_text("A short document.", document_id="one", source="test")
    assert len(chunks) == 1
    assert chunks[0].text == "A short document."


def test_long_document_is_split_with_overlap() -> None:
    chunks = Chunker(5, 2).chunk_text(
        "zero one two three four five six seven eight", document_id="long", source="test"
    )
    assert len(chunks) == 3
    assert chunks[0].text.split()[-2:] == chunks[1].text.split()[:2]
    assert chunks[1].text.split()[-2:] == chunks[2].text.split()[:2]


def test_document_metadata_is_preserved() -> None:
    document = NormalizedDocument(
        dataset="squad",
        document_id="abc",
        question="Question?",
        answer="Answer.",
        context="Context with useful evidence.",
        source="benchmark",
        metadata={"title": "Example"},
    )
    chunk = Chunker(20, 2).chunk_document(document)[0]
    assert chunk.dataset == "squad"
    assert chunk.document_id == "abc"
    assert chunk.metadata["original_question"] == "Question?"
    assert chunk.metadata["reference_answer"] == "Answer."
    assert chunk.metadata["title"] == "Example"


def test_invalid_overlap_is_rejected() -> None:
    with pytest.raises(ValueError):
        Chunker(10, 10)

