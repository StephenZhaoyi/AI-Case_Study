"""Global configuration for the local chatbot prototype."""

from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
KNOWLEDGE_BASE_DIR = DATA_DIR / "knowledge_base"
VECTORSTORE_DIR = DATA_DIR / "vectorstore"
ANALYTICS_DIR = DATA_DIR / "analytics"
ANALYTICS_DB_PATH = ANALYTICS_DIR / "chat_logs.db"

OLLAMA_CHAT_MODEL = "qwen2.5:3b"
OLLAMA_EMBEDDING_MODEL = "all-minilm"

CHROMA_COLLECTION_NAME = "knowledge_base_chunks"
RETRIEVAL_TOP_K = 4
RETRIEVAL_TOP_K_MAX = 30
RELEVANCE_THRESHOLD = 0.4
CHUNK_SIZE = 300
CHUNK_OVERLAP = 50

MAX_INPUT_CHARS = 500
MAX_HISTORY_MESSAGES = 8
