# app/api/v1/deposits.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid

from app.utils.database import get_read_db, get_db
from app.api.deps import get_current_user, require_permission
from app.models.user import User
from app.models.deposit import SecurityDeposit
from app.schemas.deposit import DepositResponse
from app.core.permissions import Permission

router = APIRouter()


@router.get("/", response_model=list[DepositResponse])
async def list_deposits(
    db: AsyncSession = Depends(get_read_db),
    current_user: User = require_permission(Permission.DEPOSIT_VIEW.value),
):
    """List deposits."""
    query = select(SecurityDeposit)

    if current_user.role == "portal_user":
        query = query.where(SecurityDeposit.customer_id == current_user.id)

    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{deposit_id}", response_model=DepositResponse)
async def get_deposit(
    deposit_id: uuid.UUID,
    db: AsyncSession = Depends(get_read_db),
    current_user: User = require_permission(Permission.DEPOSIT_VIEW.value),
):
    """Get deposit by ID."""
    deposit = await db.get(SecurityDeposit, deposit_id)
    if not deposit:
        raise HTTPException(status_code=404, detail="Deposit not found")
    return deposit


@router.post("/{deposit_id}/settle")
async def settle_deposit(
    deposit_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = require_permission(Permission.DEPOSIT_SETTLE.value),
):
    """Settle a deposit."""
    deposit = await db.get(SecurityDeposit, deposit_id)
    if not deposit:
        raise HTTPException(status_code=404, detail="Deposit not found")

    deposit.status = "settled"
    return {"message": "Deposit settled successfully"}
