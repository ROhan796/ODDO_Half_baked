# app/api/v1/rentals.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
import uuid

from app.utils.database import get_read_db, get_db
from app.api.deps import get_current_user, require_permission
from app.models.user import User
from app.models.rental import Rental
from app.schemas.rental import (
    RentalCreate,
    RentalResponse,
    RentalListResponse,
    RentalReturnRequest,
    RentalExtensionRequest,
)
from app.core.permissions import Permission

router = APIRouter()


@router.get("/", response_model=RentalListResponse)
async def list_rentals(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_read_db),
    current_user: User = require_permission(Permission.RENTAL_VIEW_ANY.value),
):
    """List all rentals."""
    query = select(Rental)

    if status:
        query = query.where(Rental.status == status)

    # Portal users can only view their own rentals
    if current_user.role == "portal_user":
        query = query.where(Rental.customer_id == current_user.id)

    # Get total count
    from sqlalchemy import func

    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar()

    # Paginate
    query = query.offset((page - 1) * limit).limit(limit)
    result = await db.execute(query)
    rentals = result.scalars().all()

    return RentalListResponse(
        items=rentals,
        total=total,
        page=page,
        limit=limit,
        has_next=(page * limit) < total,
    )


@router.post("/", response_model=RentalResponse, status_code=201)
async def create_rental(
    data: RentalCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = require_permission(Permission.RENTAL_CREATE_ANY.value),
):
    """Create a new rental."""
    rental = Rental(
        **data.model_dump(),
        daily_rate=0,  # TODO: Calculate from product
        total_amount=0,  # TODO: Calculate
    )
    db.add(rental)
    return rental


@router.get("/{rental_id}", response_model=RentalResponse)
async def get_rental(
    rental_id: uuid.UUID,
    db: AsyncSession = Depends(get_read_db),
    current_user: User = require_permission(Permission.RENTAL_VIEW_ANY.value),
):
    """Get rental by ID."""
    rental = await db.get(Rental, rental_id)
    if not rental:
        raise HTTPException(status_code=404, detail="Rental not found")

    # Portal users can only view their own rentals
    if current_user.role == "portal_user" and rental.customer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    return rental


@router.post("/{rental_id}/return", response_model=RentalResponse)
async def process_return(
    rental_id: uuid.UUID,
    data: RentalReturnRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = require_permission(Permission.RENTAL_RETURN.value),
):
    """Process rental return."""
    rental = await db.get(Rental, rental_id)
    if not rental:
        raise HTTPException(status_code=404, detail="Rental not found")

    # TODO: Process return logic
    rental.status = "returned"
    rental.condition_at_return = data.condition_notes

    return rental


@router.post("/{rental_id}/extend", response_model=RentalResponse)
async def extend_rental(
    rental_id: uuid.UUID,
    data: RentalExtensionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = require_permission(Permission.RENTAL_CREATE_OWN.value),
):
    """Extend rental period."""
    rental = await db.get(Rental, rental_id)
    if not rental:
        raise HTTPException(status_code=404, detail="Rental not found")

    # TODO: Extension logic
    rental.end_date = data.new_end_date

    return rental
