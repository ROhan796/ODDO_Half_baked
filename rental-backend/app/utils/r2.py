# app/utils/r2.py
import boto3
from botocore.config import Config
from typing import Optional
import uuid
from datetime import datetime, timedelta
from app.config import settings


class R2Storage:
    """Cloudflare R2 storage client."""

    def __init__(self):
        self.s3_client = boto3.client(
            "s3",
            endpoint_url=settings.R2_ENDPOINT_URL,
            aws_access_key_id=settings.R2_ACCESS_KEY_ID,
            aws_secret_access_key=settings.R2_SECRET_ACCESS_KEY,
            config=Config(
                signature_version="s3v4",
                s3={"addressing_style": "path"},
            ),
        )
        self.bucket_name = settings.R2_BUCKET_NAME

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
