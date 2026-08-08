# app/api/v1/disputes.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid

from app.utils.database import get_read_db, get_db
from app.api.deps import get_current_user, require_permission
from app.models.user import User
from app.models.dispute import Dispute
from app.schemas.dispute import DisputeCreate, DisputeResponse, DisputeListResponse
from app.core.permissions import Permission

router = APIRouter()


@router.get("/", response_model=DisputeListResponse)
async def list_disputes(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_read_db),
    current_user: User = Depends(get_current_user),
):
    """List disputes."""
    query = select(Dispute)

    if current_user.role == "portal_user":
        query = query.where(Dispute.customer_id == current_user.id)

    if status:
        query = query.where(Dispute.status == status)

    from sqlalchemy import func

    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar()

    query = query.offset((page - 1) * limit).limit(limit)
    result = await db.execute(query)
    disputes = result.scalars().all()

    return DisputeListResponse(
        items=disputes,
        total=total,
        page=page,
        limit=limit,
        has_next=(page * limit) < total,
    )


@router.post("/", response_model=DisputeResponse, status_code=201)
async def create_dispute(
    data: DisputeCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new dispute."""
    dispute = Dispute(
        rental_id=data.rental_id,
        customer_id=current_user.id,
        filed_by=current_user.id,
        dispute_type=data.dispute_type,
        amount_disputed=data.amount_disputed,
        description=data.description,
        evidence_urls=data.evidence_urls,
    )
    db.add(dispute)
    return dispute


@router.get("/{dispute_id}", response_model=DisputeResponse)
async def get_dispute(
    dispute_id: uuid.UUID,
    db: AsyncSession = Depends(get_read_db),
    current_user: User = Depends(get_current_user),
):
    """Get dispute by ID."""
    dispute = await db.get(Dispute, dispute_id)
    if not dispute:
        raise HTTPException(status_code=404, detail="Dispute not found")
    return dispute
