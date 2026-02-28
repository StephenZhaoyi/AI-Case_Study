"""Vector store wrappers with Chroma + Ollama embeddings."""

import shutil

from langchain_core.documents import Document
from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaEmbeddings

from config import (
    CHROMA_COLLECTION_NAME,
    CHUNK_OVERLAP,
    CHUNK_SIZE,
    KNOWLEDGE_BASE_DIR,
    OLLAMA_EMBEDDING_MODEL,
    RETRIEVAL_TOP_K_MAX,
    VECTORSTORE_DIR,
)
from ingestion.chunker import chunk_documents
from ingestion.loader import load_text_documents
from retrieval.adaptive_topk import select_adaptive_topk


def _get_embeddings() -> OllamaEmbeddings:
    """Return Ollama embeddings client."""
    return OllamaEmbeddings(model=OLLAMA_EMBEDDING_MODEL)


def initialize_vectorstore() -> Chroma:
    """Initialize and return persistent Chroma vector store."""
    VECTORSTORE_DIR.mkdir(parents=True, exist_ok=True)
    return Chroma(
        collection_name=CHROMA_COLLECTION_NAME,
        embedding_function=_get_embeddings(),
        persist_directory=str(VECTORSTORE_DIR),
    )


def _load_and_chunk_knowledge_base() -> list[Document]:
    """Load knowledge base files and split into chunks."""
    documents = load_text_documents(KNOWLEDGE_BASE_DIR)
    return chunk_documents(documents, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP)


def upsert_documents_to_vectorstore(documents: list[Document], reset_collection: bool = False) -> Chroma:
    """Embed and upsert LangChain documents to Chroma."""
    if reset_collection and VECTORSTORE_DIR.exists():
        shutil.rmtree(VECTORSTORE_DIR)

    vectorstore = initialize_vectorstore()
    if documents:
        vectorstore.add_documents(documents)
    return vectorstore


def ensure_vectorstore_indexed() -> Chroma:
    """Ensure the persistent vector store contains indexed chunks."""
    vectorstore = initialize_vectorstore()
    if vectorstore._collection.count() > 0:
        return vectorstore

    chunks = _load_and_chunk_knowledge_base()
    return upsert_documents_to_vectorstore(chunks)


def query_vectorstore(query: str, top_k: int) -> list[Document]:
    """Run similarity search against vector store."""
    if top_k <= 0:
        return []

    vectorstore = ensure_vectorstore_indexed()
    return vectorstore.similarity_search(query, k=top_k)


def query_vectorstore_adaptive(
    query: str,
    max_top_k: int,
    relevance_threshold: float = 0.4,
) -> list[Document]:
    """Fetch up to max_top_k chunks and return those above the relevance threshold."""
    if max_top_k <= 0:
        return []

    vectorstore = ensure_vectorstore_indexed()
    bounded_max_k = max(1, min(RETRIEVAL_TOP_K_MAX, max_top_k))

    scored = vectorstore.similarity_search_with_relevance_scores(query, k=bounded_max_k)
    if not scored:
        return []

    scores = [score for _, score in scored]
    adaptive_k = select_adaptive_topk(
        similarity_scores=scores,
        threshold=relevance_threshold,
        max_k=bounded_max_k,
    )

    return [document for document, _ in scored[:adaptive_k]]
