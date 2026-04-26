import os
from fastapi import UploadFile, HTTPException
from app.core.parsing import extract_pdf_text
from app.core.chunking import chunk_text
from app.core.store import add_document, set_embeddings, get_sources, document_exists
from app.core.embeddings import embed_texts
from app.Services.s3_service import StorageService

async def run_ingest(file: UploadFile, upload_dir: str) -> dict:
    if not file.filename:
        raise HTTPException(400, "file is required")
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(400, "Only PDF files are supported")

    try:
        content = await file.read()

        # Skip if already ingested
        if document_exists(file.filename):
            return {
                "filename": file.filename,
                "message": "Document already ingested — skipped",
                "total_sources": get_sources()
            }

        # Step 1: Upload to S3
        await file.seek(0)
        service = StorageService()
        s3_result = await service.upload(file, folder="Documents")
        print(f"✅ Saved to S3: {s3_result['key']}")

        # Step 2: Save temporarily for PDF parsing
        tmp_path = f"/tmp/{file.filename}"
        with open(tmp_path, "wb") as f:
            f.write(content)

        # Step 3: RAG pipeline — ADD not replace
        extracted_text = extract_pdf_text(tmp_path)
        chunks = chunk_text(extracted_text, chunk_size=500, overlap=100)

        add_document(file.filename, chunks)
        chunk_vectors = embed_texts(chunks)
        set_embeddings(chunk_vectors)

        print(f"✅ Added '{file.filename}' — total sources: {get_sources()}")

        return {
            "filename": file.filename,
            "s3_key": s3_result["key"],
            "num_chunks": len(chunks),
            "embedding_shape": list(chunk_vectors.shape),
            "total_sources": get_sources(),
        }

    except Exception as e:
        raise HTTPException(500, detail=f"Error during ingestion: {e}")
    finally:
        await file.close()
