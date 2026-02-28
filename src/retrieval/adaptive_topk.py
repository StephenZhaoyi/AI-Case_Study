"""Adaptive Top-K selection logic."""


def select_adaptive_topk(similarity_scores: list[float], threshold: float = 0.4, max_k: int = 10) -> int:
    """Return how many chunks should be kept based on a score threshold."""
    valid_scores = [score for score in similarity_scores[:max_k] if score >= threshold]
    return len(valid_scores)
