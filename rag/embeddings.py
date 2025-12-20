from sentence_transformers import SentenceTransformer
import numpy as np
from pathlib import Path
from infra.settings import SENTENCE_TRANSFORMERS_MODEL

model_path = Path(SENTENCE_TRANSFORMERS_MODEL)

class EmbeddingModel:
    def __init__(self):
        if not model_path.exists():
            raise RuntimeError(
                "Embedding model not found locally. "
                "Download it before running in offline mode."
            )
        self.model = SentenceTransformer(str(model_path))

    def embed(self, texts: list[str]) -> np.ndarray:
        return self.model.encode(texts, normalize_embeddings=True)
