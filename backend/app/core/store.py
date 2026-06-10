from typing import Any, Dict, List, Optional
import numpy as np

CHUNKS: List[Dict[str, Any]] = []
EMBEDDINGS = None  # np.ndarray

def add_document(source_file: str, chunks: List[str]) -> None:
    """Add chunks from a new document WITHOUT clearing existing ones"""
    start_index = len(CHUNKS)
    for idx, text in enumerate(chunks):
        CHUNKS.append({
            "chunk_id": f"{source_file}-{idx}",
            "chunk_index": start_index + idx,
            "source_file": source_file,
            "text": text,
        })

def set_embeddings(vectors: np.ndarray) -> None:
    """Stack new embeddings onto existing ones"""
    global EMBEDDINGS
    if EMBEDDINGS is None:
        EMBEDDINGS = vectors
    else:
        EMBEDDINGS = np.vstack([EMBEDDINGS, vectors])

def get_sources() -> List[str]:
    """List all ingested document names"""
    return list(set(c["source_file"] for c in CHUNKS))

def document_exists(source_file: str) -> bool:
    """Check if a document is already ingested"""
    return source_file in get_sources()

def reset_store() -> None:
    """Wipe everything — use carefully"""
    global EMBEDDINGS
    CHUNKS.clear()
    EMBEDDINGS = None
