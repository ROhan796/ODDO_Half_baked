# app/api/v1/stock.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional
import uuid
from datetime import datetime, timezone

from app.utils.database import get_read_db, get_db
from app.api.deps import get_current_user, require_permission
from app.models.user import User
from app.models.stock import StockLocation, StockMovement, StockLevel, MovementType
from app.schemas.stock import (
    StockLocationCreate,
    StockLocationResponse,
    StockMovementCreate,
    StockMovementResponse,
    StockLevelResponse,
)
from app.core.permissions import Permission

router = APIRouter()


@router.get("/", response_model=list[StockMovementResponse])
async def list_stock_movements(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    product_id: Optional[uuid.UUID] = None,
    movement_type: Optional[str] = None,
    location_id: Optional[uuid.UUID] = None,
    db: AsyncSession = Depends(get_read_db),
    current_user: User = require_permission(Permission.STOCK_VIEW.value),
):
    """List stock movements with pagination."""
    query = select(StockMovement)

    if product_id:
        query = query.where(StockMovement.product_id == product_id)

    if movement_type:
        query = query.where(StockMovement.movement_type == movement_type)

    if location_id:
        query = query.where(
            (StockMovement.from_location_id == location_id)
            | (StockMovement.to_location_id == location_id)
        )

    query = query.order_by(StockMovement.created_at.desc())
    query = query.offset((page - 1) * limit).limit(limit)

    result = await db.execute(query)
    return result.scalars().all()


@router.post("/locations", response_model=StockLocationResponse, status_code=201)
async def create_stock_location(
    data: StockLocationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = require_permission(Permission.STOCK_MANAGE.value),
):
    """Create a new stock location."""
    existing = await db.execute(
        select(StockLocation).where(StockLocation.code == data.code)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Location code already exists")

    location = StockLocation(**data.model_dump())
    db.add(location)
    return location


@router.get("/locations", response_model=list[StockLocationResponse])
async def list_stock_locations(
    is_active: Optional[bool] = None,
    db: AsyncSession = Depends(get_read_db),
    current_user: User = require_permission(Permission.STOCK_VIEW.value),
):
    """List all stock locations."""
    query = select(StockLocation)

    if is_active is not None:
        query = query.where(StockLocation.is_active == is_active)

    query = query.order_by(StockLocation.name)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/locations/{location_id}", response_model=StockLocationResponse)
async def get_stock_location(
    location_id: uuid.UUID,
    db: AsyncSession = Depends(get_read_db),
    current_user: User = require_permission(Permission.STOCK_VIEW.value),
):
    """Get stock location by ID."""
    location = await db.get(StockLocation, location_id)
    if not location:
        raise HTTPException(status_code=404, detail="Stock location not found")
    return location


@router.post("/movements", response_model=StockMovementResponse, status_code=201)
async def create_stock_movement(
    data: StockMovementCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = require_permission(Permission.STOCK_MANAGE.value),
):
    """Create a new stock movement."""
    from_location = None
    to_location = None

    if data.from_location_id:
        from_location = await db.get(StockLocation, data.from_location_id)
        if not from_location:
            raise HTTPException(status_code=404, detail="Source location not found")

    if data.to_location_id:
        to_location = await db.get(StockLocation, data.to_location_id)
        if not to_location:
            raise HTTPException(status_code=404, detail="Destination location not found")

    if data.movement_type in ("out", "transfer") and data.from_location_id:
        level_result = await db.execute(
            select(StockLevel).where(
                StockLevel.product_id == data.product_id,
                StockLevel.location_id == data.from_location_id,
            )
        )
        source_level = level_result.scalar_one_or_none()
        if source_level and source_level.available < data.quantity:
            raise HTTPException(status_code=400, detail="Insufficient stock at source location")

    movement = StockMovement(
        **data.model_dump(),
        performed_by=current_user.id,
    )
    db.add(movement)

    if data.to_location_id:
        to_level_result = await db.execute(
            select(StockLevel).where(
                StockLevel.product_id == data.product_id,
                StockLevel.location_id == data.to_location_id,
            )
        )
        to_level = to_level_result.scalar_one_or_none()
        if to_level:
            to_level.quantity += data.quantity
            to_level.available += data.quantity
            to_level.last_received_at = datetime.now(timezone.utc)
        else:
            to_level = StockLevel(
                product_id=data.product_id,
                location_id=data.to_location_id,
                quantity=data.quantity,
                available=data.quantity,
            )
            db.add(to_level)

    if data.from_location_id and data.movement_type in ("out", "transfer"):
        from_level_result = await db.execute(
            select(StockLevel).where(
                StockLevel.product_id == data.product_id,
                StockLevel.location_id == data.from_location_id,
            )
        )
        from_level = from_level_result.scalar_one_or_none()
        if from_level:
            from_level.quantity -= data.quantity
            from_level.available -= data.quantity

    return movement


@router.get("/movements", response_model=list[StockMovementResponse])
async def list_movements(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    product_id: Optional[uuid.UUID] = None,
    movement_type: Optional[str] = None,
    db: AsyncSession = Depends(get_read_db),
    current_user: User = require_permission(Permission.STOCK_VIEW.value),
):
    """List stock movements."""
    query = select(StockMovement)

    if product_id:
        query = query.where(StockMovement.product_id == product_id)

    if movement_type:
        query = query.where(StockMovement.movement_type == movement_type)

    query = query.order_by(StockMovement.created_at.desc())
    query = query.offset((page - 1) * limit).limit(limit)

    result = await db.execute(query)
    return result.scalars().all()


@router.get("/levels", response_model=list[StockLevelResponse])
async def list_stock_levels(
    product_id: Optional[uuid.UUID] = None,
    location_id: Optional[uuid.UUID] = None,
    db: AsyncSession = Depends(get_read_db),
    current_user: User = require_permission(Permission.STOCK_VIEW.value),
):
    """List stock levels for products."""
    query = select(StockLevel)

    if product_id:
        query = query.where(StockLevel.product_id == product_id)

    if location_id:
        query = query.where(StockLevel.location_id == location_id)

    result = await db.execute(query)
    return result.scalars().all()
