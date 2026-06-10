from fastapi import UploadFile, HTTPException
from app.Services.s3_repository import S3Repository

ALLOWED_TYPES = {"application/pdf", "image/jpeg", "image/png", "image/webp"}
MAX_SIZE_MB = 10

class StorageService:
    def __init__(self):
        self.repo = S3Repository()

    async def upload(self, file: UploadFile, folder: str = "uploads") -> dict:
        if file.content_type not in ALLOWED_TYPES:
            raise HTTPException(400, f"File type not allowed: {file.content_type}")

        contents = await file.read()
        if len(contents) > MAX_SIZE_MB * 1024 * 1024:
            raise HTTPException(400, f"File exceeds {MAX_SIZE_MB}MB limit")
        await file.seek(0)

        key = f"{folder}/{file.filename}"
        self.repo.upload(file.file, key, file.content_type)
        return {"key": key, "filename": file.filename}

    def delete(self, key: str):
        self.repo.delete(key)

    def list_files(self, prefix: str = "") -> list:
        return self.repo.list_objects(prefix)

    def get_download_url(self, key: str, expiry: int = 3600) -> str:
        return self.repo.generate_presigned_url(key, expiry)
