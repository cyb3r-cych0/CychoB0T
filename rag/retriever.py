import time
import math
import numpy as np
from rag.vector_store import SQLiteVectorStore
from infra.settings import MEMORY_DECAY_LAMBDA


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    # embeddings are normalized; dot = cosine
    return float(np.dot(a, b))

class Retriever:
    def __init__(self, store: SQLiteVectorStore):
        self.store = store

    def search(
        self,
        query_emb: np.ndarray,
        k: int,
        privacy_mode: str,
        owner: str | None = None
    ):
        scored = []

        for vid, emb, text, meta in self.store.fetch_all():
            scope = meta.get("scope")
            source = meta.get("source")

            #  conversation isolation
            if source == "memory" and meta.get("owner") != owner:
                continue

            # STRICT: public only
            if privacy_mode == "strict" and scope != "public":
                continue

            # STANDARD: public + own private
            if privacy_mode == "standard":
                if scope == "private" and meta.get("owner") != owner:
                    continue

            now = time.time()
            timestamp = meta.get("timestamp")

            # semantic similarity
            cosine_score = float(np.dot(query_emb, emb))

            # time decay (only if timestamp exists)
            if timestamp:
                age = now - timestamp
                time_weight = math.exp(-MEMORY_DECAY_LAMBDA * age)
            else:
                time_weight = 1.0

            score = cosine_score * time_weight
            scored.append((score, text))

        scored.sort(reverse=True)
        return [t for _, t in scored[:k]]
