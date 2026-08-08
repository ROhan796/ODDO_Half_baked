# app/api/v1/quotations.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
import uuid

from app.utils.database import get_read_db, get_db
from app.api.deps import get_current_user, require_permission
from app.models.user import User
from app.models.quotation import Quotation
from app.schemas.quotation import QuotationCreate, QuotationResponse, QuotationListResponse
from app.core.permissions import Permission

router = APIRouter()


@router.get("/", response_model=QuotationListResponse)
async def list_quotations(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_read_db),
    current_user: User = Depends(get_current_user),
):
    """List quotations."""
    query = select(Quotation)

    if current_user.role == "portal_user":
        query = query.where(Quotation.customer_id == current_user.id)

    if status:
        query = query.where(Quotation.status == status)

    from sqlalchemy import func

    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar()

    query = query.offset((page - 1) * limit).limit(limit)
    result = await db.execute(query)
    quotations = result.scalars().all()

    return QuotationListResponse(
        items=quotations,
        total=total,
        page=page,
        limit=limit,
        has_next=(page * limit) < total,
    )


@router.post("/", response_model=QuotationResponse, status_code=201)
async def create_quotation(
    data: QuotationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new quotation."""
    quotation = Quotation(
        quote_number=f"Q-{uuid.uuid4().hex[:8].upper()}",
        customer_id=data.customer_id,
        items=[item.model_dump() for item in data.items],
        subtotal=sum(item.amount for item in data.items),
        total_amount=sum(item.amount for item in data.items),
        created_by=current_user.id,
    )
    db.add(quotation)
    return quotation


@router.get("/{quotation_id}", response_model=QuotationResponse)
async def get_quotation(
    quotation_id: uuid.UUID,
    db: AsyncSession = Depends(get_read_db),
    current_user: User = Depends(get_current_user),
):
    """Get quotation by ID."""
    quotation = await db.get(Quotation, quotation_id)
    if not quotation:
        raise HTTPException(status_code=404, detail="Quotation not found")

    if current_user.role == "portal_user" and quotation.customer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    return quotation
