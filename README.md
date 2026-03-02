# Automotive Customer Service AI Chatbot — RAG Prototype

A fully local, **Retrieval-Augmented Generation (RAG)** chatbot prototype for automotive customer service.  
All inference runs on-device via **Ollama** — no cloud API keys required.

---

## Features

| Area | What's implemented |
|---|---|
| **RAG Pipeline** | Document ingestion → ChromaDB vector store → semantic retrieval → LLM answer with source citations |
| **Adaptive Top-K** | Auto mode dynamically filters chunks by similarity score; manual slider for fine control |
| **Guardrails** | Input sanitization (prompt-injection patterns redacted) + output inspection for system-prompt leakage |
| **Graceful Fallback** | Returns "I don't know" when no relevant chunks are found, skipping the LLM call entirely |
| **Chat UI** | Streamlit app with session history, source expander, and sidebar controls |
| **Admin Dashboard** | Query log viewer (SQLite), LLM-generated trend summary, CSV/Markdown export |

---

## Prerequisites

| Requirement | Version / Notes |
|---|---|
| Python | 3.11+ |
| [Ollama](https://ollama.ai) | Must be installed and running locally |
| Git | For cloning the repo |

---

## Setup

### 1. Clone & install dependencies

```bash
git clone <your-repo-url>
cd AI-Case_Study
pip install -r requirements.txt
```

### 2. Pull Ollama models

```bash
ollama pull qwen2.5:3b      # chat model
ollama pull all-minilm       # embedding model
```

> If you want to use different models, update `OLLAMA_CHAT_MODEL` and `OLLAMA_EMBEDDING_MODEL` in `src/config.py`.

### 3. Ingest the knowledge base

Run this **once** to chunk the documents and populate the ChromaDB vector store:

```bash
python -c "
from src.ingestion.loader import load_documents
from src.ingestion.chunker import chunk_documents
from src.retrieval.vectorstore import init_vectorstore, add_documents_to_vectorstore
docs = load_documents()
chunks = chunk_documents(docs)
vs = init_vectorstore()
add_documents_to_vectorstore(vs, chunks)
print(f'Ingested {len(chunks)} chunks.')
"
```

The vector store is persisted at `data/vectorstore/` and survives restarts — no need to re-run after the first time.

---

## Running the Apps

### Option A — Makefile (recommended)

```bash
make chat       # User chat UI    → http://localhost:8501
make admin      # Admin dashboard → http://localhost:8502
make run-all    # Start both apps in the background
make stop       # Stop background apps
```

`make run-all` stops any existing instances first, then starts both apps in the background.

### Option B — Direct Streamlit commands

```bash
streamlit run src/pages/chat_app.py  --server.port 8501
streamlit run src/pages/admin_app.py --server.port 8502
```

---

## Usage

### Chat App (`localhost:8501`)

- Type a question in the input box and press **Enter**.
- The answer includes **source document citations** in a collapsible expander.
- **Sidebar controls:**
  - **Retrieval Mode** toggle — *Manual* (use the Top-K slider) or *Auto* (adaptive threshold-based filtering).
  - **Top-K slider** — number of chunks to retrieve (disabled in Auto mode).
  - **Similarity threshold** — minimum score for a chunk to be included (Auto mode only).
  - **Clear chat** button — resets the current session history.

### Admin Dashboard (`localhost:8502`)

- **Query Log** — table of all past queries with timestamps, chunk counts, and source documents.
- **Trend Summary** — click **Generate Summary** to have the LLM analyse the most frequent questions.
- **Export** — download the FAQ summary as CSV or Markdown.

---

## Project Structure

```
AI-Case_Study/
├── Makefile                          # Shortcuts: make chat / admin / run-all / stop
├── requirements.txt
├── data/
│   ├── knowledge_base/               # 6 source documents (.txt)
│   ├── vectorstore/                  # ChromaDB persistence (auto-created)
│   └── analytics/
│       ├── chat_logs.db              # SQLite query log (auto-created)
│       └── runtime_settings.json    # Persisted sidebar settings
└── src/
    ├── config.py                     # Global config (models, paths, thresholds)
    ├── runtime_settings.py           # Load / save sidebar settings to JSON
    ├── pages/
    │   ├── chat_app.py               # User chat interface
    │   └── admin_app.py             # Admin dashboard
    ├── ingestion/
    │   ├── loader.py                 # TextLoader for knowledge_base/
    │   └── chunker.py               # RecursiveCharacterTextSplitter
    ├── retrieval/
    │   ├── vectorstore.py            # ChromaDB init & similarity search
    │   └── adaptive_topk.py         # Score-threshold chunk filtering
    ├── generation/
    │   ├── chain.py                  # RAG chain: retrieve → augment → generate
    │   ├── prompts.py               # System prompt templates
    │   └── guardrails.py            # Input sanitization + output inspection
    └── analytics/
        ├── logger.py                # Write query entries to SQLite
        └── summarizer.py           # LLM trend summary generation
```

---

## Configuration

All tunable parameters live in [`src/config.py`](../src/config.py):

| Parameter | Default | Description |
|---|---|---|
| `OLLAMA_CHAT_MODEL` | `qwen2.5:3b` | Chat model served by Ollama |
| `OLLAMA_EMBEDDING_MODEL` | `all-minilm` | Embedding model served by Ollama |
| `CHUNK_SIZE` | `300` | Token chunk size for document splitting |
| `CHUNK_OVERLAP` | `50` | Overlap between adjacent chunks |
| `RETRIEVAL_TOP_K` | `4` | Default manual Top-K |
| `RETRIEVAL_TOP_K_MAX` | `30` | Maximum candidates fetched in Auto mode |
| `RELEVANCE_THRESHOLD` | `0.1` | Minimum similarity score in Auto mode |
| `MAX_INPUT_CHARS` | `500` | Hard cap on user input length |
| `MAX_HISTORY_MESSAGES` | `8` | Number of history turns passed to the model |

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `Connection refused` from Ollama | Make sure `ollama serve` is running |
| `Model not found` error | Run `ollama pull <model-name>` for the model in `config.py` |
| Empty answers / no chunks retrieved | Re-run the ingestion step; check `data/vectorstore/` exists |
| Import errors | Run all commands from the **project root** directory |
