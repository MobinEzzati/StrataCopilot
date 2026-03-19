from fastapi import FastAPI, UploadFile, File, HTTPException, Body
import os

from app.core.parsing import extract_pdf_text
from app.core.chunking import chunk_text
from app.core.store import reset_store, add_chunks, set_embeddings, CHUNKS
from app.core.embeddings import embed_texts
from app.core.Retrieval.Faiss_Retriver import faiss_query
from app.core.llm import generate_answer
import time

MAX_REQUESTS_PER_HOUR = 20
request_count = 0
window_start = time.time()


app = FastAPI()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.get("/")
def root():
    return {"message": "Consulting Copilot API running"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/ask")
def ask_question(payload: dict = Body(...)):
    global request_count, window_start

    current_time = time.time()

# Reset every hour
    if current_time - window_start > 3600:
        request_count = 0
        window_start = current_time

# Block if limit reached
    if request_count >= MAX_REQUESTS_PER_HOUR:
        raise HTTPException(
            status_code=429,
            detail="Demo limit reached. Please try again later."
         )

    request_count += 1


    question = str(payload.get("question", "")).strip()
    k = int(payload.get("k", 3))

    if not question:
        raise HTTPException(status_code=400, detail="question is required")

    if k < 1 or k > 10:
        raise HTTPException(status_code=400, detail="k must be between 1 and 10")

    if not CHUNKS:
        raise HTTPException(status_code=400, detail="No document has been ingested yet")

    # Step 1: Retrieval
    retrieval_results = faiss_query(question, k=k)

    if not retrieval_results:
        return {
            "question": question,
            "k": k,
            "num_hits": 0,
            "evidence": [],
            "answer": "No relevant information found in the documents."
        }

    # Step 2: Build context
    context_parts = [item["text"] for item in retrieval_results]
    context = "\n\n".join(context_parts[:2])

    # Step 3: LLM generation
    try:
        llm_response = generate_answer(question, context)

    except Exception as e:
        print("Bedrock error:", e)

        # fallback to retrieval-based answer
        llm_response = context
      

    return {
        "question": question,
        "k": k,
        "num_hits": len(retrieval_results),
        "evidence": retrieval_results,
        "answer": llm_response,
    }

@app.post("/ingest")
async def ingest(file: UploadFile = File(...)):

    ## make sure it exist 
    if not file.filename:
        raise HTTPException(status_code=400, detail="file is required")

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported right now")

    file_path = os.path.join(UPLOAD_DIR, file.filename)

    try:
        content = await file.read()

        with open(file_path, "wb") as f:
            f.write(content)

       ## chunkign operation  and text exratction 
        extracted_text = extract_pdf_text(file_path)
        chunks = chunk_text(extracted_text, chunk_size=500, overlap=100)

        reset_store({"source_file": file.filename, "saved_path": file_path})
        add_chunks(file.filename, chunks)

        chunk_vectors = embed_texts(chunks)
        set_embeddings(chunk_vectors)

        return {
            "filename": file.filename,
            "saved_to": file_path,
            "content_size_bytes": len(content),
            "text_len": len(extracted_text),
            "preview": extracted_text[:300],
            "num_chunks": len(chunks),
            "first_chunk_preview": chunks[0][:200] if chunks else "",
            "embedding_shape": list(chunk_vectors.shape),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"There was an error uploading the file: {e}")

    finally:
        await file.close()