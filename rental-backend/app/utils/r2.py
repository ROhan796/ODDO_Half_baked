# app/utils/r2.py
# S3-compatible object storage client (Backblaze B2 / Cloudflare R2 / AWS S3)
import boto3
from botocore.config import Config
from typing import Optional
import uuid
from datetime import datetime, timedelta
from app.config import settings


class R2Storage:
    """S3-compatible storage client."""

    def __init__(self):
        self._s3_client = None
        self.bucket_name = settings.STORAGE_BUCKET_NAME

    @property
    def s3_client(self):
        if self._s3_client is None:
            self._s3_client = boto3.client(
                "s3",
                endpoint_url=settings.STORAGE_ENDPOINT_URL,
                aws_access_key_id=settings.STORAGE_ACCESS_KEY_ID,
                aws_secret_access_key=settings.STORAGE_SECRET_ACCESS_KEY,
                config=Config(
                    signature_version="s3v4",
                    s3={"addressing_style": "path"},
                ),
            )
        return self._s3_client

    async def generate_presigned_upload_url(
        self,
        folder: str,
        filename: str,
        content_type: str,
        expires_in: int = 3600,
    ) -> dict:
        """Generate pre-signed URL for upload."""
        ext = filename.rsplit(".", 1)[1] if "." in filename else ""
        key = f"{folder}/{uuid.uuid4().hex}.{ext}"

        presigned_url = self.s3_client.generate_presigned_url(
            "put_object",
            Params={
                "Bucket": self.bucket_name,
                "Key": key,
                "ContentType": content_type,
            },
            ExpiresIn=expires_in,
        )

        return {
            "upload_url": presigned_url,
            "file_key": key,
            "public_url": f"{settings.STORAGE_PUBLIC_URL}/{key}",
            "expires_at": (datetime.utcnow() + timedelta(seconds=expires_in)).isoformat(),
        }

    async def generate_presigned_download_url(
        self,
        file_key: str,
        expires_in: int = 3600,
    ) -> str:
        """Generate pre-signed URL for download."""
        presigned_url = self.s3_client.generate_presigned_url(
            "get_object",
            Params={
                "Bucket": self.bucket_name,
                "Key": file_key,
            },
            ExpiresIn=expires_in,
        )
        return presigned_url

    async def get_public_url(self, file_key: str) -> str:
        """Get public URL for a file (no expiry)."""
        return f"{settings.STORAGE_PUBLIC_URL}/{file_key}"

    async def delete_file(self, file_key: str) -> bool:
        """Delete file from storage."""
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=file_key,
            )
            return True
        except Exception:
            return False


storage = R2Storage()
