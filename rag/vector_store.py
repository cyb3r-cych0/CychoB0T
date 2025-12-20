import sqlite3
import json
from pathlib import Path
import numpy as np
from typing import Dict, List, Tuple
from infra.settings import VECTOR_DB_PATH

vector_db_path = Path(VECTOR_DB_PATH)

class SQLiteVectorStore:
    def __init__(self):
        vector_db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _conn(self):
        return sqlite3.connect(vector_db_path)

    def _init_db(self):
        conn = self._conn()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS vectors (
                id TEXT PRIMARY KEY,
                embedding TEXT NOT NULL,
                text TEXT NOT NULL,
                metadata TEXT
            )
        """)
        conn.commit()
        conn.close()

    def add(self, vid: str, embedding: np.ndarray, text: str, metadata: Dict):
        if "scope" not in metadata:
            raise ValueError("Vector metadata must include 'scope'")
        if metadata["scope"] not in ("public", "private"):
            raise ValueError("Invalid scope value")

        conn = self._conn()
        cur = conn.cursor()
        cur.execute(
            "INSERT OR REPLACE INTO vectors (id, embedding, text, metadata) VALUES (?, ?, ?, ?)",
            (vid, json.dumps(embedding.tolist()), text, json.dumps(metadata))
        )
        conn.commit()
        conn.close()

    def fetch_all(self) -> List[Tuple[str, np.ndarray, str, Dict]]:
        conn = self._conn()
        cur = conn.cursor()
        rows = cur.execute(
            "SELECT id, embedding, text, metadata FROM vectors"
        ).fetchall()
        conn.close()

        results = []
        for vid, emb_json, text, meta_json in rows:
            emb = np.array(json.loads(emb_json), dtype=float)
            meta = json.loads(meta_json) if meta_json else {}
            results.append((vid, emb, text, meta))
        return results
