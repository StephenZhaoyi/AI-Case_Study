"""RAG generation pipeline with Chroma retrieval."""

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_ollama import ChatOllama

from config import (
    OLLAMA_CHAT_MODEL,
    RELEVANCE_THRESHOLD,
    RETRIEVAL_TOP_K,
    RETRIEVAL_TOP_K_MAX,
)
from generation.guardrails import inspect_output, safe_fallback_response, sanitize_user_input
from generation.prompts import build_user_prompt, get_system_prompt
from retrieval.vectorstore import query_vectorstore, query_vectorstore_adaptive



def _invoke_chat_model(*, system_prompt: str, user_prompt: str) -> str:
    """Invoke chat model and return guarded text content."""
    model = ChatOllama(model=OLLAMA_CHAT_MODEL, temperature=0.2)
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt),
    ]
    result = model.invoke(messages)
    content = result.content if isinstance(result.content, str) else str(result.content)
    return inspect_output(content)


def _format_context_for_prompt(retrieved_documents: list) -> str:
    """Format retrieved chunks for prompt context."""
    formatted_chunks: list[str] = []
    for index, document in enumerate(retrieved_documents, start=1):
        source = document.metadata.get("source", "unknown")
        formatted_chunks.append(f"[{index}] Source: {source}\n{document.page_content}")
    return "\n\n".join(formatted_chunks)


def _extract_sources(retrieved_documents: list) -> list[str]:
    """Extract unique sources from retrieved documents."""
    unique_sources: list[str] = []
    for document in retrieved_documents:
        source = document.metadata.get("source", "unknown")
        if source not in unique_sources:
            unique_sources.append(source)
    return unique_sources


def generate_chat_response(
    user_text: str,
    history: list[dict[str, str]],
    top_k: int | None = None,
    auto_top_k: bool = False,
    relevance_threshold: float = RELEVANCE_THRESHOLD,
) -> tuple[str, list[str], int]:
    """Generate a RAG answer from local Ollama model and retrieved context.

    Returns:
        (answer, unique_sources, num_chunks_retrieved)
    """
    _ = history
    sanitized_input = sanitize_user_input(user_text)
    if not sanitized_input:
        return safe_fallback_response(), [], 0

    retrieval_k = top_k if top_k is not None else RETRIEVAL_TOP_K
    if auto_top_k:
        retrieval_k = RETRIEVAL_TOP_K_MAX
    try:
        if auto_top_k:
            retrieved_documents = query_vectorstore_adaptive(
                sanitized_input,
                max_top_k=retrieval_k,
                relevance_threshold=relevance_threshold,
            )
        else:
            retrieved_documents = query_vectorstore(sanitized_input, top_k=retrieval_k)

        if not retrieved_documents:
            no_context_prompt = build_user_prompt(question=sanitized_input, context="")
            no_context_answer = _invoke_chat_model(
                system_prompt=get_system_prompt(),
                user_prompt=no_context_prompt,
            )
            return no_context_answer or safe_fallback_response(), [], 0

        context = _format_context_for_prompt(retrieved_documents)
        user_prompt = build_user_prompt(question=sanitized_input, context=context)
        answer = _invoke_chat_model(
            system_prompt=get_system_prompt(),
            user_prompt=user_prompt,
        )
        return answer, _extract_sources(retrieved_documents), len(retrieved_documents)
    except Exception:
        return "LLM call failed. Please ensure Ollama is running and the model is available.", [], 0
