# app/api/v1/departments.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import List
import uuid

from app.utils.database import get_read_db, get_db
from app.api.deps import get_current_user, require_permission
from app.models.user import User
from app.schemas.department import (
    DepartmentCreate,
    DepartmentUpdate,
    DepartmentMemberUpdate,
    DepartmentResponse,
    DepartmentListResponse,
)
from app.core.permissions import Permission
from app.services.department_service import DepartmentService

router = APIRouter()


@router.get("/", response_model=DepartmentListResponse)
async def list_departments(
    enterprise_id: uuid.UUID,
    db: AsyncSession = Depends(get_read_db),
    current_user: User = Depends(get_current_user),
):
    """List departments for an enterprise."""
    service = DepartmentService(db)
    result = await service.list_departments(enterprise_id=enterprise_id)
    return DepartmentListResponse(**result)


@router.post("/", response_model=DepartmentResponse, status_code=201)
async def create_department(
    enterprise_id: uuid.UUID,
    data: DepartmentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = require_permission(Permission.ADMIN_DASHBOARD.value),
):
    """Create a new department."""
    service = DepartmentService(db)
    return await service.create_department(
        data=data.model_dump(),
        enterprise_id=enterprise_id,
    )


@router.get("/{department_id}", response_model=DepartmentResponse)
async def get_department(
    department_id: uuid.UUID,
    db: AsyncSession = Depends(get_read_db),
    current_user: User = Depends(get_current_user),
):
    """Get department by ID."""
    service = DepartmentService(db)
    return await service.get_department(department_id)


@router.put("/{department_id}", response_model=DepartmentResponse)
async def update_department(
    department_id: uuid.UUID,
    data: DepartmentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = require_permission(Permission.ADMIN_DASHBOARD.value),
):
    """Update department details."""
    service = DepartmentService(db)
    return await service.update_department(
        department_id=department_id,
        data=data.model_dump(exclude_unset=True),
    )


@router.put("/{department_id}/members", response_model=DepartmentResponse)
async def update_department_members(
    department_id: uuid.UUID,
    data: DepartmentMemberUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = require_permission(Permission.ADMIN_DASHBOARD.value),
):
    """Add or remove members from a department."""
    service = DepartmentService(db)
    return await service.update_members(
        department_id=department_id,
        add_members=data.add_members,
        remove_members=data.remove_members,
    )
