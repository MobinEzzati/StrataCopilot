from fastapi import HTTPException
from app.core.store import CHUNKS
from app.core.Retrieval.Faiss_Retriver import faiss_query
from app.core.llm import generate_answer


def run_ask(question: str, k: int) -> dict:
    question = question.strip()

    if not question:
        raise HTTPException(status_code=400, detail="question is required")

    if k < 1 or k > 10:
        raise HTTPException(status_code=400, detail="k must be between 1 and 10")

    if not CHUNKS:
        raise HTTPException(status_code=400, detail="No document has been ingested yet")

    retrieval_results = faiss_query(question, k=k)

    if not retrieval_results:
        return {
            "question": question,
            "k": k,
            "num_hits": 0,
            "evidence": [],
            "answer": "No relevant information found in the documents."
        }

    context_parts = [item["text"] for item in retrieval_results]
    context = "\n\n".join(context_parts[:2])

    try:
        llm_response = generate_answer(question, context)
    except Exception:
        llm_response = context

    return {
        "question": question,
        "k": k,
        "num_hits": len(retrieval_results),
        "evidence": retrieval_results,
        "answer": llm_response,
    }