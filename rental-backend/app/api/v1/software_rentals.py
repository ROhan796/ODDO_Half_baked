# app/api/v1/software_rentals.py
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import uuid

from app.api.deps import get_db, get_current_user
from app.schemas.software_service import (
    SoftwareRentalCreate,
    SoftwareRentalResponse,
    SoftwareRentalListResponse,
    SoftwareUsageLogResponse,
)
from app.services.software_service import SoftwareRentalService
from app.models.user import User

router = APIRouter()


@router.get("/", response_model=SoftwareRentalListResponse)
async def list_software_rentals(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status_filter: Optional[str] = Query(None, alias="status"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = SoftwareRentalService(db)
    customer_id = current_user.id
    result = await service.list_rentals(
        page=page,
        limit=limit,
        customer_id=customer_id,
        status=status_filter,
    )
    return result


@router.post("/", response_model=SoftwareRentalResponse, status_code=status.HTTP_201_CREATED)
async def create_software_rental(
    data: SoftwareRentalCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = SoftwareRentalService(db)
    try:
        return await service.create_rental(data, current_user.id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/{rental_id}", response_model=SoftwareRentalResponse)
async def get_software_rental(
    rental_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = SoftwareRentalService(db)
    result = await service.get_rental(rental_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Software rental not found",
        )
    if result.customer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )
    return result


@router.post("/{rental_id}/activate", response_model=SoftwareRentalResponse)
async def activate_software_rental(
    rental_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = SoftwareRentalService(db)
    result = await service.activate_rental(rental_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Software rental not found",
        )
    return result


@router.post("/{rental_id}/deactivate", response_model=SoftwareRentalResponse)
async def deactivate_software_rental(
    rental_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = SoftwareRentalService(db)
    result = await service.deactivate_rental(rental_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Software rental not found",
        )
    return result


@router.post("/{rental_id}/usage", response_model=SoftwareUsageLogResponse)
async def log_software_usage(
    rental_id: uuid.UUID,
    metric_type: str = Query(...),
    quantity: float = Query(..., gt=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = SoftwareRentalService(db)
    result = await service.log_usage(rental_id, metric_type, quantity)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot log usage for this rental",
        )
    return result


@router.get("/{rental_id}/usage")
async def get_software_usage(
    rental_id: uuid.UUID,
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = SoftwareRentalService(db)
    return await service.get_usage_logs(rental_id, page, limit)
