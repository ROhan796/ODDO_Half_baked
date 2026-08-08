# app/api/v1/recovery.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from app.utils.database import get_read_db, get_db
from app.api.deps import get_current_user, require_permission
from app.models.user import User
from app.models.recovery import RecoveryCase
from app.schemas.recovery import RecoveryCaseCreate, RecoveryCaseResponse
from app.core.permissions import Permission

router = APIRouter()


@router.get("/", response_model=list[RecoveryCaseResponse])
async def list_recovery_cases(
    db: AsyncSession = Depends(get_read_db),
    current_user: User = require_permission(Permission.RECOVERY_MANAGE.value),
):
    """List recovery cases."""
    from sqlalchemy import select

    result = await db.execute(select(RecoveryCase))
    return result.scalars().all()


@router.post("/", response_model=RecoveryCaseResponse, status_code=201)
async def create_recovery_case(
    data: RecoveryCaseCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = require_permission(Permission.RECOVERY_MANAGE.value),
):
    """Create a new recovery case."""
    # TODO: Get rental and product details
    recovery = RecoveryCase(
        rental_id=data.rental_id,
        customer_id=current_user.id,
        product_id=uuid.uuid4(),  # TODO: Get from rental
        initiated_by=current_user.id,
        reason=data.reason,
        amount_outstanding=data.amount_outstanding,
    )
    db.add(recovery)
    return recovery


@router.get("/{recovery_id}", response_model=RecoveryCaseResponse)
async def get_recovery_case(
    recovery_id: uuid.UUID,
    db: AsyncSession = Depends(get_read_db),
    current_user: User = require_permission(Permission.RECOVERY_MANAGE.value),
):
    """Get recovery case by ID."""
    recovery = await db.get(RecoveryCase, recovery_id)
    if not recovery:
        raise HTTPException(status_code=404, detail="Recovery case not found")
    return recovery
