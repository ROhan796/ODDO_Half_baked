# app/api/v1/software_services.py
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import uuid

from app.api.deps import get_db, get_current_user, require_permission
from app.core.permissions import Permission
from app.schemas.software_service import (
    SoftwareServiceCreate,
    SoftwareServiceUpdate,
    SoftwareServiceResponse,
    SoftwareServiceListResponse,
)
from app.services.software_service import SoftwareServiceService
from app.models.user import User

router = APIRouter()


@router.get("/", response_model=SoftwareServiceListResponse)
async def list_software_services(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    category_id: Optional[uuid.UUID] = None,
    license_type: Optional[str] = None,
    status_filter: Optional[str] = Query(None, alias="status"),
    is_featured: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
):
    service = SoftwareServiceService(db)
    result = await service.list_services(
        page=page,
        limit=limit,
        search=search,
        category_id=category_id,
        license_type=license_type,
        status=status_filter,
        is_featured=is_featured,
    )
    return result


@router.post("/", response_model=SoftwareServiceResponse, status_code=status.HTTP_201_CREATED)
async def create_software_service(
    data: SoftwareServiceCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = require_permission(Permission.PRODUCT_CREATE.value),
):
    service = SoftwareServiceService(db)
    existing = await service.get_service_by_slug(data.slug)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Software service with slug '{data.slug}' already exists",
        )
    return await service.create_service(data)


@router.get("/{service_id}", response_model=SoftwareServiceResponse)
async def get_software_service(
    service_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    service = SoftwareServiceService(db)
    result = await service.get_service(service_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Software service not found",
        )
    return result


@router.put("/{service_id}", response_model=SoftwareServiceResponse)
async def update_software_service(
    service_id: uuid.UUID,
    data: SoftwareServiceUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = require_permission(Permission.PRODUCT_UPDATE.value),
):
    service = SoftwareServiceService(db)
    result = await service.update_service(service_id, data)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Software service not found",
        )
    return result


@router.delete("/{service_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_software_service(
    service_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = require_permission(Permission.PRODUCT_DELETE.value),
):
    service = SoftwareServiceService(db)
    deleted = await service.delete_service(service_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Software service not found",
        )


@router.get("/{service_id}/availability")
async def check_availability(
    service_id: uuid.UUID,
    start_at: str = Query(..., description="ISO datetime"),
    end_at: str = Query(..., description="ISO datetime"),
    db: AsyncSession = Depends(get_db),
):
    from datetime import datetime

    try:
        start = datetime.fromisoformat(start_at.replace("Z", "+00:00"))
        end = datetime.fromisoformat(end_at.replace("Z", "+00:00"))
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid datetime format. Use ISO 8601.",
        )

    service = SoftwareServiceService(db)
    return await service.check_availability(service_id, start, end)
