# app/services/file_service.py
from app.utils.r2 import storage


class FileService:
    def __init__(self, db=None):
        self.db = db

    async def get_presigned_upload_url(
        self, folder: str, filename: str, content_type: str
    ) -> dict:
        """Get a pre-signed URL for uploading a file to R2."""
        result = await storage.generate_presigned_upload_url(
            folder=folder,
            filename=filename,
            content_type=content_type,
        )
        return result

    async def get_presigned_download_url(self, file_key: str) -> str:
        """Get a pre-signed URL for downloading a file from R2."""
        url = await storage.generate_presigned_download_url(file_key=file_key)
        return url

    async def delete_file(self, file_key: str) -> bool:
        """Delete a file from R2 storage."""
        deleted = await storage.delete_file(file_key=file_key)
        return deleted
