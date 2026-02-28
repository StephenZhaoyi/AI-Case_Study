# Project Quick Start

This document explains how to run the local chatbot prototype quickly.

## 1) Prerequisites

- Python 3.11.14
- Ollama installed and running

## 2) Install Dependencies

From project root:

```bash
pip install -r requirements.txt
```

## 3) Pull Local Models (Ollama)

```bash
ollama pull qwen2.5:3b
ollama pull all-minilm
```

If you use different model names, update `src/config.py`.

## 4) Start the Apps

```bash
streamlit run src/pages/chat_app.py --server.port 8501
streamlit run src/pages/admin_app.py --server.port 8502
```

Or use Makefile shortcuts:

```bash
make chat
make admin
make run-all
make stop
```

- `make run-all` will stop existing Chat/Admin processes first, then start both in background.
- `make stop` kills Chat/Admin Streamlit processes started for this project.

After startup:
- Open **Chat** at `http://localhost:8501` for user interaction.
- Open **Admin** at `http://localhost:8502` for query statistics.
- In Admin, turn on **Auto Top-K** to hide the slider and enable adaptive retrieval (k starts at 1 and increases only when needed).
- If Auto is off, adjust **Retrieval Top-K** manually (range: 1-6); Chat reads the saved value automatically.

## 5) Current Scope

- ✅ Local LLM chat is available.
- ✅ Session history and clear-chat button are available.
- ✅ Query logging and basic admin dashboard are available.
- ✅ Chat and Admin run as two separate Streamlit web apps.
- ⏳ Full RAG ingestion/retrieval pipeline is scaffolded and can be implemented next.

## 6) Troubleshooting

- If model calls fail, make sure Ollama service is running.
- If import/path issues appear, run commands from the project root.
- If no response appears, check that the configured model exists in Ollama.
