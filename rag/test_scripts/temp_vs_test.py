""" Test all-MiniLM-L6-v2 Sentence Transformers """

# from rag.embeddings import EmbeddingModel
#
# m = EmbeddingModel()
# v = m.embed(["hello world"])
# assert v.shape[0] == 1
# print(v.shape)

""" Test Vector """

# import numpy as np
# from rag.vector_store import SQLiteVectorStore
#
# vs = SQLiteVectorStore()
#
# vs.add(
#     vid="doc1",
#     embedding=np.array([0.1, 0.2, 0.3]),
#     text="Test document",
#     metadata={"source": "unit-test"}
# )
#
# rows = vs.fetch_all()
# assert len(rows) >= 1
# print("Vector store OK:", rows[0][0], rows[0][2])
