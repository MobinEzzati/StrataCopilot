from typing import List
import numpy as np
from sentence_transformers import SentenceTransformer

_model = None


def get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


def embed_texts(texts: List[str]) -> np.ndarray:
    model = get_model()
    vectors = model.encode(texts, normalize_embeddings=True)
    return np.asarray(vectors, dtype="float32")


def embed_query(text: str) -> np.ndarray:
    model = get_model()
    vector = model.encode([text], normalize_embeddings=True)
    return np.asarray(vector, dtype="float32")