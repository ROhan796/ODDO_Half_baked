# app/schemas/upload.py
from pydantic import BaseModel, Field
from datetime import datetime


class PresignedUrlRequest(BaseModel):
    folder: str = Field(..., pattern="^(avatars|documents|inspections|contracts|products)$")
    filename: str
    content_type: str


class PresignedUrlResponse(BaseModel):
    upload_url: str
    file_key: str
    expires_at: str
