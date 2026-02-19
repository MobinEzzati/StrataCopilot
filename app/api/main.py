from fastapi import FastAPI
from fastapi import UploadFile, File
import os
from fastapi import HTTPException
from app.Core.parsing import textToPdf
# Create the Flask application instance
app = FastAPI()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.get("/")
def root():
    return {"message": "Consulting Copilot API running"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/ingest")
async def postFile(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)


    try:
        content = await file.read()

        extracted_text =  textToPdf(content)

        with open(file_path, "wb") as f : 
             f.write(content)
        
    
    except Exception as e:
            raise HTTPException(status_code=500, detail=f"There was an error uploading the file: {e}")
    finally:
        await file.close()
    
    return {
    "filename": file.filename,
    "contentSize": len(content),
    "text_len": len(extracted_text),
    "preview": extracted_text[:300]
}

         


