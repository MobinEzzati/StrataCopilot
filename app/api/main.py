from fastapi import FastAPI, UploadFile, File
import os

from app.schemas.ask import AskRequest
from app.Services.ask_services import run_ask
from app.Services.ingest_services import run_ingest
from app.Services.rate_limit_service import check_and_increment_request_limit

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
def ask_question(payload: AskRequest):
    check_and_increment_request_limit()
    return run_ask(payload.question, payload.k)


@app.post("/ingest")
async def ingest(file: UploadFile = File(...)):
    return await run_ingest(file, UPLOAD_DIR)