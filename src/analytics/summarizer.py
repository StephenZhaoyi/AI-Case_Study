"""LLM-powered analytics summariser for chat logs."""

import sys
from pathlib import Path

_SRC_DIR = Path(__file__).resolve().parents[1]
if str(_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_SRC_DIR))

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_ollama import ChatOllama

from config import OLLAMA_CHAT_MODEL
from generation.prompts import build_summary_user_prompt, get_summary_system_prompt


def summarize_chat_logs(queries: list[str]) -> str:
    """Call the LLM to produce an automotive service-improvement summary.

    Non-automotive queries (small talk, off-topic, crisis, injection attempts)
    are filtered out by the LLM itself via the system prompt.

    Args:
        queries: All raw query strings retrieved from the chat_logs table.

    Returns:
        A markdown-formatted summary string, or an error/no-data message.
    """
    if not queries:
        return "No chat logs found. Ask some questions in the chat first."

    system_prompt = get_summary_system_prompt()
    user_prompt = build_summary_user_prompt(queries)

    try:
        model = ChatOllama(model=OLLAMA_CHAT_MODEL, temperature=0.2)
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt),
        ]
        result = model.invoke(messages)
        content = result.content if isinstance(result.content, str) else str(result.content)
        return content.strip() or "The model returned an empty response."
    except Exception as exc:
        return f"LLM call failed: {exc}\n\nPlease make sure Ollama is running and the model is available."
