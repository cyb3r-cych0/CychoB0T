from pathlib import Path
from infra.settings import SENTENCE_TRANSFORMERS_MODEL

EMBED_MODEL_DIR = Path(SENTENCE_TRANSFORMERS_MODEL)

def verify_models():
    if not EMBED_MODEL_DIR.exists():
        raise RuntimeError(
            "Embedding model missing. Preload models before startup."
        )
