# app/api/v1/enterprise.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from app.utils.database import get_read_db, get_db
from app.api.deps import get_current_user, require_permission
from app.models.user import User
from app.models.enterprise import Enterprise, EnterpriseMember
from app.schemas.enterprise import EnterpriseCreate, EnterpriseResponse, EnterpriseMemberCreate, EnterpriseMemberResponse

router = APIRouter()


@router.get("/", response_model=list[EnterpriseResponse])
async def list_enterprises(
    db: AsyncSession = Depends(get_read_db),
    current_user: User = require_permission(Permission.ADMIN_DASHBOARD.value),
):
    """List all enterprises."""
    from sqlalchemy import select

    result = await db.execute(select(Enterprise))
    return result.scalars().all()


@router.post("/", response_model=EnterpriseResponse, status_code=201)
async def create_enterprise(
    data: EnterpriseCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new enterprise."""
    enterprise = Enterprise(**data.model_dump())
    db.add(enterprise)
    return enterprise


@router.get("/{enterprise_id}", response_model=EnterpriseResponse)
async def get_enterprise(
    enterprise_id: uuid.UUID,
    db: AsyncSession = Depends(get_read_db),
    current_user: User = Depends(get_current_user),
):
    """Get enterprise by ID."""
    enterprise = await db.get(Enterprise, enterprise_id)
    if not enterprise:
        raise HTTPException(status_code=404, detail="Enterprise not found")
    return enterprise


@router.post("/{enterprise_id}/members", response_model=EnterpriseMemberResponse)
async def add_member(
    enterprise_id: uuid.UUID,
    data: EnterpriseMemberCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Add member to enterprise."""
    member = EnterpriseMember(
        enterprise_id=enterprise_id,
        user_id=data.user_id,
        sub_role=data.sub_role,
        department=data.department,
        designation=data.designation,
        spending_limit_inr=data.spending_limit_inr,
        monthly_limit_inr=data.monthly_limit_inr,
        can_approve_rentals=data.can_approve_rentals,
        invited_by=current_user.id,
    )
    db.add(member)
    return member
