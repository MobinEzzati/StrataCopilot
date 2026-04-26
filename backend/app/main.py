from fastapi import FastAPI, UploadFile, File
from app.schemas.ask import AskRequest
from app.Services.ask_services import run_ask
from app.Services.ingest_services import run_ingest
from app.Services.rate_limit_service import check_and_increment_request_limit
from app.core import store

app = FastAPI()

@app.get("/")
def root():
    return {"message": "PE Copilot API running"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/documents")
def list_documents():
    return {
        "total_documents": len(store.get_sources()),
        "total_chunks": len(store.CHUNKS),
        "sources": store.get_sources(),
        "embeddings_shape": list(store.EMBEDDINGS.shape) if store.EMBEDDINGS is not None else None
    }

@app.delete("/documents")
def clear_documents():
    store.reset_store()
    return {"message": "All documents cleared from memory"}

@app.post("/ingest")
async def upload_s3(file: UploadFile = File(...)):
    result = await run_ingest(file, "/tmp")
    return {"message": "Uploaded and indexed successfully", **result}

@app.post("/ask")
def ask_question(payload: AskRequest):
    check_and_increment_request_limit()
    return run_ask(payload.question, payload.k)
