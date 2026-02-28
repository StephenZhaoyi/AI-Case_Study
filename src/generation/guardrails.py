"""Input and output guardrails for minimal prompt-injection resistance."""

import re

from config import MAX_INPUT_CHARS


SUSPICIOUS_PATTERNS = [
    r"ignore\s+previous\s+instructions",
    r"reveal\s+system\s+prompt",
    r"you\s+are\s+now",
    r"act\s+as",
    r"developer\s+message",
]


def sanitize_user_input(user_text: str) -> str:
    """Trim length and redact common prompt-injection phrases."""
    cleaned = user_text.strip()[:MAX_INPUT_CHARS]
    for pattern in SUSPICIOUS_PATTERNS:
        cleaned = re.sub(pattern, "[REDACTED]", cleaned, flags=re.IGNORECASE)
    return cleaned


def safe_fallback_response() -> str:
    """Return default fallback response."""
    return "I don't know based on the available information."


def inspect_output(output_text: str) -> str:
    """Replace suspicious model output with a safe fallback."""
    lower_output = output_text.lower()
    if "system prompt" in lower_output or "developer message" in lower_output:
        return safe_fallback_response()
    return output_text.strip() or safe_fallback_response()
