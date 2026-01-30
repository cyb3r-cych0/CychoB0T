"""
Chosen Solution: Per-Request SQLite Connections
Rule:
- Never share SQLite connections across threads.

Instead:
- Create a new connection per operation
- Let SQLite handle locking
- Keep it simple and safe

This is standard practice for FastAPI + SQLite.
Why:
- Each request gets its own connection
- Thread-safe
- No shared state
- Works with Uvicorn workers
- Production-accepted pattern

Retention Policy (Configurable, Enforced)
Policy (v1)

Default retention: 30 days

Manual purge function

No background jobs yet
"""

import sqlite3
from datetime import datetime
from pathlib import Path
from datetime import timedelta
from infra.settings import DB_PATH
from rag.memory_ingest import MemoryIngestor
import time

db_path = Path(DB_PATH)

_memory_ingestor = MemoryIngestor()


class SQLiteMemoryStore:
    def __init__(self):
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    @staticmethod
    def _get_conn():
        return sqlite3.connect(
            db_path,
            check_same_thread=False
        )

    def _init_db(self):
        conn = self._get_conn()
        cur = conn.cursor()

        # Conversations table (canonical schema)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                conversation_id TEXT PRIMARY KEY,
                model_profile_id TEXT NOT NULL,
                created_at DATETIME
            )
        """)

        # Messages table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                engine TEXT,
                timestamp DATETIME
            )
        """)

        conn.commit()
        conn.close()

    def ensure_conversation(self, conversation_id: str, model_profile_id: str):
        conn = self._get_conn()
        cur = conn.cursor()

        # Check if conversation already exists
        cur.execute(
            "SELECT model_profile_id FROM conversations WHERE conversation_id = ?",
            (conversation_id,)
        )
        row = cur.fetchone()

        if row is None:
            # Create new conversation with bound model profile
            cur.execute(
                """
                INSERT INTO conversations (
                    conversation_id,
                    model_profile_id,
                    created_at
                )
                VALUES (?, ?, ?)
                """,
                (conversation_id, model_profile_id, datetime.now())
            )

        # If it exists, do NOTHING (model_profile_id is immutable)

        conn.commit()
        conn.close()

    def conversation_exists(self, conversation_id: str) -> bool:
        conn = self._get_conn()
        cur = conn.cursor()

        cur.execute(
            "SELECT 1 FROM conversations WHERE conversation_id = ?",
            (conversation_id,)
        )
        exists = cur.fetchone() is not None

        conn.close()
        return exists

    def add_message(self, conversation_id: str, role: str, content: str, engine: str):
        conn = self._get_conn()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO messages (conversation_id, role, content, engine, timestamp) VALUES (?, ?, ?, ?, ?)",
            (conversation_id, role, content, engine, time.time())
        )
        conn.commit()
        conn.close()

        # MEMORY → VECTOR INGESTION
        try:
            _memory_ingestor.ingest(
                conversation_id=conversation_id,
                role=role,
                text=content
            )
        except Exception:
            pass

    def purge_older_than(self, days: int = 30):
        cutoff = datetime.now() - timedelta(days=days)
        conn = self._get_conn()
        cur = conn.cursor()
        cur.execute(
            "DELETE FROM messages WHERE timestamp < ?",
            (cutoff,)
        )
        conn.commit()
        conn.close()

    def get_model_profile_id(self, conversation_id: str) -> str:
        conn = self._get_conn()
        cur = conn.cursor()
        cur.execute(
            "SELECT model_profile_id FROM conversations WHERE conversation_id = ?",
            (conversation_id,)
        )
        row = cur.fetchone()
        if not row:
            raise KeyError(f"Conversation not found: {conversation_id}")
        return row[0]
