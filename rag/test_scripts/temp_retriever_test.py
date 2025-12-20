import numpy as np
from rag.vector_store import SQLiteVectorStore
from rag.retriever import Retriever

vs = SQLiteVectorStore()
vs.add("a", np.array([1.0, 0.0, 0.0]), "alpha", {})
vs.add("b", np.array([0.0, 1.0, 0.0]), "beta", {})
vs.add("c", np.array([0.9, 0.1, 0.0]), "alpha-like", {})

r = Retriever(vs)
results = r.search(np.array([1.0, 0.0, 0.0]), k=2)

print(results)
assert results[0] in ("alpha", "alpha-like")
