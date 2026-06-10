import faiss
from app.core import store
from app.core.embeddings import embed_query

## Using Faiss as retriver 
def faiss_query(question: str, k: int = 2):
    question = (question or "").strip()
    if not question:
        return []

    if not store.CHUNKS or store.EMBEDDINGS is None:
        return []

    query_embedding = embed_query(question)

    dimension = store.EMBEDDINGS.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(store.EMBEDDINGS)

    distances, indices = index.search(query_embedding, k)

    results = []
    for rank, idx in enumerate(indices[0]):
        chunk = store.CHUNKS[int(idx)]
        results.append(
            {
                "rank": rank + 1,
                "chunk_index": chunk["chunk_index"],
                "chunk_id": chunk["chunk_id"],
                "source_file": chunk["source_file"],
                "text": chunk["text"],
                "score": float(distances[0][rank]),
            }
        )

    return results

