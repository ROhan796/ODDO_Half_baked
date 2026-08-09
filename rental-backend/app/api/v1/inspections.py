# app/api/v1/inspections.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import uuid

from app.utils.database import get_read_db, get_db
from app.api.deps import get_current_user, require_permission
from app.models.user import User
from app.schemas.inspection import (
    InspectionCreate,
    InspectionResponse,
    InspectionListResponse,
)
from app.core.permissions import Permission
from app.services.inspection_service import InspectionService

router = APIRouter()


@router.get("/", response_model=InspectionListResponse)
async def list_inspections(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    rental_id: Optional[uuid.UUID] = None,
    inspection_type: Optional[str] = None,
    db: AsyncSession = Depends(get_read_db),
    current_user: User = require_permission(Permission.INSPECTION_PERFORM.value),
):
    """List inspection reports with optional filters."""
    service = InspectionService(db)
    result = await service.list_inspections(
        page=page,
        limit=limit,
        rental_id=rental_id,
        inspection_type=inspection_type,
    )
    return InspectionListResponse(**result)


@router.post("/", response_model=InspectionResponse, status_code=201)
async def create_inspection(
    data: InspectionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = require_permission(Permission.INSPECTION_PERFORM.value),
):
    """Create a new inspection report."""
    service = InspectionService(db)
    report = await service.create_inspection(
        data=data.model_dump(),
        inspector_id=current_user.id,
    )
    return report


@router.get("/{inspection_id}", response_model=InspectionResponse)
async def get_inspection(
    inspection_id: uuid.UUID,
    db: AsyncSession = Depends(get_read_db),
    current_user: User = require_permission(Permission.INSPECTION_PERFORM.value),
):
    """Get inspection report by ID."""
    service = InspectionService(db)
    return await service.get_inspection(inspection_id)
