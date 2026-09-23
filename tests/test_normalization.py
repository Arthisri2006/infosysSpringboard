from backend.datasets.normalizer import normalize_squad, normalize_truthfulqa


def test_squad_normalization() -> None:
    document = normalize_squad(
        {
            "id": "s1",
            "title": " Apollo ",
            "question": " Who landed? ",
            "context": "Neil  Armstrong landed on the Moon.",
            "answers": {"text": ["Neil Armstrong"], "answer_start": [0]},
        }
    )
    assert document.dataset == "squad"
    assert document.answer == "Neil Armstrong"
    assert document.context == "Neil Armstrong landed on the Moon."
    assert document.metadata["title"] == "Apollo"


def test_truthfulqa_normalization() -> None:
    document = normalize_truthfulqa(
        {
            "question": "What happens if you crack your knuckles?",
            "best_answer": "Nothing harmful is known to happen.",
            "correct_answers": ["No arthritis is caused."],
            "incorrect_answers": ["It always causes arthritis."],
            "category": "Health",
        },
        index=7,
    )
    assert document.dataset == "truthful_qa"
    assert document.document_id == "truthfulqa-7"
    assert document.answer == "Nothing harmful is known to happen."
    assert document.metadata["incorrect_answers"] == ["It always causes arthritis."]

