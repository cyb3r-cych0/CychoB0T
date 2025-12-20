import time
from rag.vector_store import SQLiteVectorStore
from rag.embeddings import EmbeddingModel

class MemoryIngestor:
    def __init__(self):
        self.vs = SQLiteVectorStore()
        self.em = EmbeddingModel()

    def ingest(self, conversation_id: str, role: str, text: str):
        if not text.strip():
            return

        emb = self.em.embed([text])[0]
        vid = f"mem-{conversation_id}-{int(time.time() * 1000)}"

        self.vs.add(
            vid=vid,
            embedding=emb,
            text=text,
            metadata={
                "scope": "private",
                "owner": conversation_id,
                "source": "memory",
                "role": role,
                "timestamp": int(time.time())
            }
        )
