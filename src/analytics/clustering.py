"""Semantic clustering placeholder for FAQ grouping."""


def cluster_questions(questions: list[str]) -> list[dict[str, str | int]]:
    """Placeholder clustering implementation.

    This will be replaced with embedding-based clustering in a later step.
    """
    return [{"cluster_id": idx, "representative_question": question} for idx, question in enumerate(questions)]
