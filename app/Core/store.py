from typing import Any, Dict, List
import numpy as np

CHUNKS: List[Dict[str, Any]] = []
LAST_DOC: Dict[str, Any] = {}
EMBEDDINGS = None  # np.ndarray


def reset_store(doc_meta: Dict[str, Any]) -> None:
    global EMBEDDINGS
    CHUNKS.clear()
    LAST_DOC.clear()
    LAST_DOC.update(doc_meta)
    EMBEDDINGS = None


def add_chunks(source_file: str, chunks: List[str]) -> None:
    for idx, text in enumerate(chunks):
        CHUNKS.append(
            {
                "chunk_id": f"{source_file}-{idx}",
                "chunk_index": idx,
                "source_file": source_file,
                "text": text,
            }
        )


def set_embeddings(vectors: np.ndarray) -> None:
    global EMBEDDINGS
    EMBEDDINGS = vectors