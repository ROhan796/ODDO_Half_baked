# app/api/v1/custody.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional
import uuid

from app.utils.database import get_read_db, get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.custody import CustodyEvent

router = APIRouter()


@router.get("/events")
async def list_custody_events(
    rental_id: uuid.UUID = Query(...),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_read_db),
    current_user: User = Depends(get_current_user),
):
    """List custody events for a rental."""
    query = select(CustodyEvent).where(CustodyEvent.rental_id == rental_id)

    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    query = query.order_by(CustodyEvent.created_at.desc())
    query = query.offset((page - 1) * limit).limit(limit)
    result = await db.execute(query)
    events = result.scalars().all()

    return {
        "items": [
            {
                "id": str(e.id),
                "rental_id": str(e.rental_id),
                "product_id": str(e.product_id),
                "event_type": e.event_type.value if hasattr(e.event_type, 'value') else e.event_type,
                "from_user_id": str(e.from_user_id) if e.from_user_id else None,
                "to_user_id": str(e.to_user_id) if e.to_user_id else None,
                "condition_rating": e.condition_rating,
                "condition_notes": e.condition_notes,
                "photos": e.photos,
                "performed_by": str(e.performed_by),
                "created_at": e.created_at.isoformat() if e.created_at else None,
            }
            for e in events
        ],
        "total": total,
        "page": page,
        "limit": limit,
        "has_next": (page * limit) < total,
    }


@router.post("/events", status_code=201)
async def create_custody_event(
    rental_id: uuid.UUID,
    product_id: uuid.UUID,
    event_type: str,
    performed_by: uuid.UUID,
    from_user_id: Optional[uuid.UUID] = None,
    to_user_id: Optional[uuid.UUID] = None,
    condition_rating: Optional[int] = None,
    condition_notes: Optional[str] = None,
    photos: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new custody event."""
    event = CustodyEvent(
        rental_id=rental_id,
        product_id=product_id,
        event_type=event_type,
        from_user_id=from_user_id,
        to_user_id=to_user_id,
        condition_rating=condition_rating,
        condition_notes=condition_notes,
        photos=photos,
        performed_by=performed_by,
    )
    db.add(event)
    await db.flush()
    await db.refresh(event)

    return {
        "id": str(event.id),
        "rental_id": str(event.rental_id),
        "product_id": str(event.product_id),
        "event_type": event.event_type.value if hasattr(event.event_type, 'value') else event.event_type,
        "from_user_id": str(event.from_user_id) if event.from_user_id else None,
        "to_user_id": str(event.to_user_id) if event.to_user_id else None,
        "condition_rating": event.condition_rating,
        "condition_notes": event.condition_notes,
        "photos": event.photos,
        "performed_by": str(event.performed_by),
        "created_at": event.created_at.isoformat() if event.created_at else None,
    }


@router.get("/events/{event_id}")
async def get_custody_event(
    event_id: uuid.UUID,
    db: AsyncSession = Depends(get_read_db),
    current_user: User = Depends(get_current_user),
):
    """Get a custody event by ID."""
    event = await db.get(CustodyEvent, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Custody event not found")

    return {
        "id": str(event.id),
        "rental_id": str(event.rental_id),
        "product_id": str(event.product_id),
        "event_type": event.event_type.value if hasattr(event.event_type, 'value') else event.event_type,
        "from_user_id": str(event.from_user_id) if event.from_user_id else None,
        "to_user_id": str(event.to_user_id) if event.to_user_id else None,
        "condition_rating": event.condition_rating,
        "condition_notes": event.condition_notes,
        "photos": event.photos,
        "performed_by": str(event.performed_by),
        "created_at": event.created_at.isoformat() if event.created_at else None,
    }
