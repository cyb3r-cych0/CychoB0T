from rag.vector_store import SQLiteVectorStore
from rag.embeddings import EmbeddingModel

vs = SQLiteVectorStore()
em = EmbeddingModel()
vs.add("doc1", em.embed(["Ransomware encrypts files"])[0], "Ransomware encrypts files", {})
