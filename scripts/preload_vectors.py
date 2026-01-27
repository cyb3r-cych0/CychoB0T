from rag.vector_store import SQLiteVectorStore
from rag.embeddings import EmbeddingModel

docs = [
    "keyloggers scans user's keystrokes on the keyboard",
    "python is a good programming language to make keylogger scripts"
]

vs = SQLiteVectorStore()
em = EmbeddingModel()

for i, d in enumerate(docs):
    vs.add(
        vid=f"public-{i}",
        embedding=em.embed([d])[0],
        text=d,
        metadata={
            "scope": "public",
            "source": "docs"
        }
    )

print("Vector preload complete.")
