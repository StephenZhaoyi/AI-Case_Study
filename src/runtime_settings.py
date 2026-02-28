"""Runtime settings persistence shared by standalone Streamlit apps."""

import json
from pathlib import Path

from config import ANALYTICS_DIR, RELEVANCE_THRESHOLD, RETRIEVAL_TOP_K, RETRIEVAL_TOP_K_MAX


SETTINGS_PATH = ANALYTICS_DIR / "runtime_settings.json"


def _default_settings() -> dict[str, int | bool | float]:
    return {"retrieval_top_k": RETRIEVAL_TOP_K, "auto_top_k": False, "relevance_threshold": RELEVANCE_THRESHOLD}


def load_runtime_settings() -> dict[str, int | bool]:
    """Load persisted runtime settings with safe defaults."""
    if not SETTINGS_PATH.exists():
        return _default_settings()

    try:
        data = json.loads(SETTINGS_PATH.read_text(encoding="utf-8"))
        value = int(data.get("retrieval_top_k", RETRIEVAL_TOP_K))
        value = max(1, min(RETRIEVAL_TOP_K_MAX, value))
        auto_top_k = bool(data.get("auto_top_k", False))
        threshold = float(data.get("relevance_threshold", RELEVANCE_THRESHOLD))
        threshold = max(0.0, min(0.5, threshold))
        return {"retrieval_top_k": value, "auto_top_k": auto_top_k, "relevance_threshold": threshold}
    except Exception:
        return _default_settings()


def save_runtime_settings(
    *,
    retrieval_top_k: int,
    auto_top_k: bool = False,
    relevance_threshold: float = RELEVANCE_THRESHOLD,
) -> None:
    """Persist runtime settings for cross-app usage."""
    ANALYTICS_DIR.mkdir(parents=True, exist_ok=True)
    value = max(1, min(RETRIEVAL_TOP_K_MAX, int(retrieval_top_k)))
    threshold = max(0.0, min(0.5, float(relevance_threshold)))
    SETTINGS_PATH.write_text(
        json.dumps(
            {"retrieval_top_k": value, "auto_top_k": bool(auto_top_k), "relevance_threshold": threshold},
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
