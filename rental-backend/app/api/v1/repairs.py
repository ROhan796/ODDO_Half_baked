# app/api/v1/repairs.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from app.utils.database import get_read_db, get_db
from app.api.deps import get_current_user, require_permission
from app.models.user import User
from app.models.repair import RepairCase
from app.schemas.repair import RepairCaseCreate, RepairCaseResponse
from app.core.permissions import Permission

router = APIRouter()


@router.get("/", response_model=list[RepairCaseResponse])
async def list_repairs(
    db: AsyncSession = Depends(get_read_db),
    current_user: User = require_permission(Permission.REPAIR_MANAGE.value),
):
    """List repair cases."""
    from sqlalchemy import select

    result = await db.execute(select(RepairCase))
    return result.scalars().all()


@router.post("/", response_model=RepairCaseResponse, status_code=201)
async def create_repair(
    data: RepairCaseCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = require_permission(Permission.REPAIR_MANAGE.value),
):
    """Create a new repair case."""
    repair = RepairCase(
        **data.model_dump(),
        reported_by=current_user.id,
    )
    db.add(repair)
    return repair


@router.get("/{repair_id}", response_model=RepairCaseResponse)
async def get_repair(
    repair_id: uuid.UUID,
    db: AsyncSession = Depends(get_read_db),
    current_user: User = require_permission(Permission.REPAIR_MANAGE.value),
):
    """Get repair case by ID."""
    repair = await db.get(RepairCase, repair_id)
    if not repair:
        raise HTTPException(status_code=404, detail="Repair case not found")
    return repair
