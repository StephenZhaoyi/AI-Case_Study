"""Standalone Admin app entrypoint."""

import sys
from pathlib import Path

import streamlit as st


SRC_DIR = Path(__file__).resolve().parent.parent
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from analytics.logger import get_summary_stats, get_top_questions, init_analytics_db
from config import RELEVANCE_THRESHOLD, RETRIEVAL_TOP_K_MAX
from runtime_settings import load_runtime_settings, save_runtime_settings


@st.cache_resource
def _init_db() -> None:
    """Run once per server session."""
    init_analytics_db()


@st.cache_data(ttl=30)
def _get_stats() -> dict:
    return get_summary_stats()


@st.cache_data(ttl=30)
def _get_top_questions() -> list:
    return get_top_questions(limit=10)


def _load_settings_once() -> None:
    """Read settings from disk only on first run of the session."""
    if "admin_settings_loaded" not in st.session_state:
        s = load_runtime_settings()
        st.session_state.s_top_k = int(s["retrieval_top_k"])
        st.session_state.s_auto_top_k = bool(s.get("auto_top_k", False))
        st.session_state.s_threshold = float(s.get("relevance_threshold", RELEVANCE_THRESHOLD))
        # Snapshot of last-persisted values for change detection in on_change callback
        st.session_state.s_saved_top_k = st.session_state.s_top_k
        st.session_state.s_saved_auto_top_k = st.session_state.s_auto_top_k
        st.session_state.s_saved_threshold = st.session_state.s_threshold
        st.session_state.admin_settings_loaded = True


def _save_settings() -> None:
    """on_change callback: persist to disk only when values actually changed."""
    auto = st.session_state.s_auto_top_k
    # s_top_k may not exist when auto mode is on (slider not rendered)
    top_k = RETRIEVAL_TOP_K_MAX if auto else st.session_state.get("s_top_k", st.session_state.s_saved_top_k)
    threshold = st.session_state.get("s_threshold", st.session_state.s_saved_threshold)

    changed = (
        auto != st.session_state.s_saved_auto_top_k
        or st.session_state.get("s_top_k", st.session_state.s_saved_top_k) != st.session_state.s_saved_top_k
        or st.session_state.get("s_threshold", st.session_state.s_saved_threshold) != st.session_state.s_saved_threshold
    )
    if changed:
        save_runtime_settings(
            retrieval_top_k=top_k,
            auto_top_k=auto,
            relevance_threshold=threshold,
        )
        st.session_state.s_saved_auto_top_k = auto
        st.session_state.s_saved_top_k = st.session_state.get("s_top_k", st.session_state.s_saved_top_k)
        st.session_state.s_saved_threshold = st.session_state.get("s_threshold", st.session_state.s_saved_threshold)


def main() -> None:
    st.set_page_config(page_title="Admin", page_icon="📊", layout="wide")
    st.title("📊 Admin Dashboard")
    st.caption("Monitoring and analytics interface.")

    _init_db()
    _load_settings_once()

    stats = _get_stats()
    col1, col2 = st.columns(2)
    col1.metric("Total Queries", stats["total_queries"])
    col2.metric("Unique Queries", stats["unique_queries"])

    st.subheader("RAG Settings")

    # Use key= to bind widgets directly to session_state.
    # on_change fires AFTER session_state is updated → no double-click issue.
    st.toggle(
        "Auto Top-K",
        key="s_auto_top_k",
        on_change=_save_settings,
        help="Automatically select chunks above the relevance threshold.",
    )

    if st.session_state.s_auto_top_k:
        st.info(
            f"Auto mode: searches all {RETRIEVAL_TOP_K_MAX} chunks and keeps those "
            f"above the relevance threshold. Adjust the threshold below."
        )
        st.slider(
            "Relevance Threshold",
            min_value=0.0,
            max_value=0.5,
            step=0.05,
            key="s_threshold",
            on_change=_save_settings,
            help="Chunks with a similarity score below this value are excluded.",
        )
    else:
        st.slider(
            "Retrieval Top-K",
            min_value=1,
            max_value=RETRIEVAL_TOP_K_MAX,
            key="s_top_k",
            on_change=_save_settings,
            help="How many chunks are retrieved for each user question.",
        )

    st.subheader("Top Asked Questions")
    top_questions = _get_top_questions()
    if not top_questions:
        st.info("No query logs yet.")
    else:
        st.dataframe(top_questions, use_container_width=True, hide_index=True)


if __name__ == "__main__":
    main()
