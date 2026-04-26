from typing import Any, Dict, List
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from app.core.embeddings import embed_query
from app.core.store import CHUNKS, EMBEDDINGS


def text_retrieval(question: str, k: int = 3) -> List[Dict[str, Any]]:
    question = (question or "").strip()
    if not question:
        return []

    if not CHUNKS or EMBEDDINGS is None:
        return []

    if k < 1:
        return []

    query_vector = embed_query(question)  # shape: (1, dim)
    similarities = cosine_similarity(query_vector, EMBEDDINGS)[0]

    top_k_indices = np.argsort(similarities)[::-1][: min(k, len(CHUNKS))]

    results: List[Dict[str, Any]] = []
    for rank, idx in enumerate(top_k_indices, start=1):
        chunk = CHUNKS[int(idx)]
        results.append(
            {
                "rank": rank,
                "chunk_index": chunk["chunk_index"],
                "chunk_id": chunk["chunk_id"],
                "source_file": chunk["source_file"],
                "text": chunk["text"],
                "score": float(similarities[idx]),
            }
        )

    return results