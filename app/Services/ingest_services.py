import os
from fastapi import HTTPException
from app.core.parsing import extract_pdf_text
from app.core.chunking import chunk_text
from app.core.store import reset_store, add_chunks, set_embeddings
from app.core.embeddings import embed_texts


async def run_ingest(file, upload_dir: str) -> dict:
    if not file.filename:
        raise HTTPException(status_code=400, detail="file is required")

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported right now")

    file_path = os.path.join(upload_dir, file.filename)

    try:
        content = await file.read()

        with open(file_path, "wb") as f:
            f.write(content)

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