from rag.vector_store import SQLiteVectorStore
from rag.embeddings import EmbeddingModel

vs = SQLiteVectorStore()
em = EmbeddingModel()

texts = [
    "Ransomware encrypts files",
    "Attackers demand payment for decryption"
]

for i, t in enumerate(texts):
    vs.add(
        vid=f"doc{i}",
        embedding=em.embed([t])[0],
        text=t,
        metadata={}
    )
