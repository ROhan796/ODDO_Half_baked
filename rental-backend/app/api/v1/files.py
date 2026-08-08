# app/api/v1/files.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.utils.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.upload import PresignedUrlRequest, PresignedUrlResponse
from app.utils.r2 import storage

router = APIRouter()


@router.post("/presigned-url", response_model=PresignedUrlResponse)
async def get_presigned_url(
    data: PresignedUrlRequest,
    current_user: User = Depends(get_current_user),
):
    """Get pre-signed URL for file upload."""
    try:
        result = await storage.generate_presigned_upload_url(
            folder=data.folder,
            filename=data.filename,
            content_type=data.content_type,
        )
        return PresignedUrlResponse(
            upload_url=result["upload_url"],
            file_key=result["file_key"],
            expires_at=result["expires_at"],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate upload URL: {str(e)}")


@router.delete("/{file_key}")
async def delete_file(
    file_key: str,
    current_user: User = Depends(get_current_user),
):
    """Delete a file from storage."""
    deleted = await storage.delete_file(file_key)
    if not deleted:
        raise HTTPException(status_code=500, detail="Failed to delete file")

    return {"message": "File deleted successfully"}
