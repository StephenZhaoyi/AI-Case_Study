"""Document loading utilities."""

from pathlib import Path

from langchain_community.document_loaders import TextLoader
from langchain_core.documents import Document


def load_text_documents(directory: Path) -> list[Document]:
    """Load .txt documents from a directory into LangChain documents."""
    if not directory.exists():
        return []

    documents: list[Document] = []
    for file_path in sorted(directory.glob("*.txt")):
        loader = TextLoader(str(file_path), encoding="utf-8")
        loaded_documents = loader.load()
        for document in loaded_documents:
            document.metadata["source"] = file_path.name
            documents.append(document)
    return documents
