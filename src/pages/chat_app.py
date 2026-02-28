"""Standalone Chat app entrypoint."""

import sys
from pathlib import Path

import streamlit as st


SRC_DIR = Path(__file__).resolve().parent.parent
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from analytics.logger import init_analytics_db, log_chat_interaction
from config import RELEVANCE_THRESHOLD, RETRIEVAL_TOP_K, RETRIEVAL_TOP_K_MAX
from generation.chain import generate_chat_response
from runtime_settings import load_runtime_settings


@st.cache_resource
def _init_db() -> None:
    init_analytics_db()


@st.cache_data(ttl=5)
def _load_settings() -> dict:
    """Cache settings for 5 s to avoid per-render disk reads."""
    return load_runtime_settings()


def _render_sources(sources: list[str], num_chunks: int = 0) -> None:
    if not sources:
        return

    st.markdown(f"**Sources** — {num_chunks} chunk(s) retrieved from {len(sources)} file(s)")
    for source in sources:
        st.markdown(f"- {source}")


def _render_message(message: dict) -> None:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        sources = message.get("sources", [])
        num_chunks = message.get("num_chunks", 0)
        _render_sources(sources, num_chunks)


def main() -> None:
    st.set_page_config(page_title="Chat", page_icon="💬", layout="centered")
    st.markdown(
        """
        <style>
        [data-testid="stAppViewContainer"] .main .block-container {
            padding-bottom: 8rem;
        }
        [data-testid="stChatMessageContainer"] {
            overflow-y: auto;
            -webkit-overflow-scrolling: touch;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.title("💬 User Chat")
    st.caption("Customer-facing chat interface.")

    _init_db()

    with st.sidebar:
        st.subheader("Session")
        if st.button("Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

    if "messages" not in st.session_state:
        st.session_state.messages = []

    runtime_settings = _load_settings()
    retrieval_top_k = int(runtime_settings.get("retrieval_top_k", RETRIEVAL_TOP_K))
    auto_top_k = bool(runtime_settings.get("auto_top_k", False))
    relevance_threshold = float(runtime_settings.get("relevance_threshold", RELEVANCE_THRESHOLD))
    if auto_top_k:
        retrieval_top_k = RETRIEVAL_TOP_K_MAX

    for message in st.session_state.messages:
        _render_message(message)

    if prompt := st.chat_input("Type your question..."):
        user_message = {"role": "user", "content": prompt}
        st.session_state.messages.append(user_message)
        _render_message(user_message)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                answer, sources, num_chunks = generate_chat_response(
                    prompt,
                    st.session_state.messages,
                    top_k=retrieval_top_k,
                    auto_top_k=auto_top_k,
                    relevance_threshold=relevance_threshold,
                )
            st.markdown(answer)
            _render_sources(sources, num_chunks)

        assistant_message = {"role": "assistant", "content": answer, "sources": sources, "num_chunks": num_chunks}
        st.session_state.messages.append(assistant_message)
        log_chat_interaction(query=prompt, answer=answer)


if __name__ == "__main__":
    main()
