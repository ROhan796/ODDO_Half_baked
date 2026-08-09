# app/api/v1/enterprise.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field
from typing import Optional
import uuid

from app.utils.database import get_read_db, get_db
from app.api.deps import get_current_user, require_permission
from app.models.user import User
from app.models.enterprise import Enterprise, EnterpriseMember, EnterpriseCreditTransaction
from app.schemas.enterprise import EnterpriseCreate, EnterpriseResponse, EnterpriseMemberCreate, EnterpriseMemberResponse
from app.core.permissions import Permission

router = APIRouter()


class CreditRequestCreate(BaseModel):
    requested_limit: float = Field(..., gt=0)
    reason: str = Field(..., min_length=10, max_length=1000)
    department: Optional[str] = None
    urgency: str = Field("normal", pattern="^(low|normal|high|critical)$")


class CreditRequestResponse(BaseModel):
    id: uuid.UUID
    enterprise_id: uuid.UUID
    requested_by: uuid.UUID
    requested_limit: float
    reason: str
    department: Optional[str] = None
    urgency: str
    status: str
    created_at: str


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


@router.post("/{enterprise_id}/credit-request", status_code=201)
async def create_credit_request(
    enterprise_id: uuid.UUID,
    data: CreditRequestCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Request credit limit expansion for enterprise."""
    enterprise = await db.get(Enterprise, enterprise_id)
    if not enterprise:
        raise HTTPException(status_code=404, detail="Enterprise not found")

    credit_txn = EnterpriseCreditTransaction(
        enterprise_id=enterprise_id,
        type="credit_adjusted",
        amount=data.requested_limit,
        reference=f"Credit request: {data.reason}",
        created_by=current_user.id,
    )
    db.add(credit_txn)

    return {
        "id": str(credit_txn.id),
        "enterprise_id": str(enterprise_id),
        "requested_by": str(current_user.id),
        "requested_limit": data.requested_limit,
        "reason": data.reason,
        "department": data.department,
        "urgency": data.urgency,
        "status": "pending",
        "created_at": str(credit_txn.created_at) if credit_txn.created_at else "",
    }
