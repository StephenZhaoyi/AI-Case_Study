"""SQLite logging utilities for chat queries."""

import sqlite3
from datetime import datetime

from config import ANALYTICS_DB_PATH, ANALYTICS_DIR


def init_analytics_db() -> None:
    """Create database and table if they do not exist."""
    ANALYTICS_DIR.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(ANALYTICS_DB_PATH) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS chat_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query TEXT NOT NULL,
                answer TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.commit()


def log_chat_interaction(query: str, answer: str) -> None:
    """Insert one chat interaction row."""
    now = datetime.utcnow().isoformat()
    with sqlite3.connect(ANALYTICS_DB_PATH) as conn:
        conn.execute(
            "INSERT INTO chat_logs (query, answer, created_at) VALUES (?, ?, ?)",
            (query, answer, now),
        )
        conn.commit()


def get_summary_stats() -> dict[str, int]:
    """Return total and unique query counts."""
    with sqlite3.connect(ANALYTICS_DB_PATH) as conn:
        total_queries = conn.execute("SELECT COUNT(*) FROM chat_logs").fetchone()[0]
        unique_queries = conn.execute("SELECT COUNT(DISTINCT query) FROM chat_logs").fetchone()[0]
    return {"total_queries": total_queries, "unique_queries": unique_queries}


def get_top_questions(limit: int = 10) -> list[dict[str, int | str]]:
    """Return top repeated questions by exact match."""
    with sqlite3.connect(ANALYTICS_DB_PATH) as conn:
        rows = conn.execute(
            """
            SELECT query, COUNT(*) AS ask_count
            FROM chat_logs
            GROUP BY query
            ORDER BY ask_count DESC, query ASC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
    return [{"query": row[0], "ask_count": row[1]} for row in rows]
