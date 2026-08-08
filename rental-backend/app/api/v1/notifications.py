# app/api/v1/notifications.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update
from typing import Optional
import uuid
from datetime import datetime, timezone

from app.utils.database import get_read_db, get_db
from app.api.deps import get_current_user, require_permission
from app.models.user import User
from app.models.notification import (
    Notification,
    NotificationTemplate,
    NotificationStatus,
)
from app.schemas.notification import (
    NotificationResponse,
    NotificationListResponse,
    NotificationTemplateCreate,
    NotificationTemplateResponse,
)
from app.core.permissions import Permission

router = APIRouter()


@router.get("/", response_model=NotificationListResponse)
async def list_notifications(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_read_db),
    current_user: User = Depends(get_current_user),
):
    """List notifications for current user."""
    query = select(Notification).where(Notification.user_id == current_user.id)

    if status:
        query = query.where(Notification.status == status)

    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar()

    unread_result = await db.execute(
        select(func.count()).select_from(
            select(Notification).where(
                Notification.user_id == current_user.id,
                Notification.status != NotificationStatus.READ,
            ).subquery()
        )
    )
    unread_count = unread_result.scalar()

    query = query.order_by(Notification.created_at.desc())
    query = query.offset((page - 1) * limit).limit(limit)

    result = await db.execute(query)
    notifications = result.scalars().all()

    return NotificationListResponse(
        items=notifications,
        total=total,
        unread_count=unread_count,
    )


@router.get("/unread-count")
async def get_unread_count(
    db: AsyncSession = Depends(get_read_db),
    current_user: User = Depends(get_current_user),
):
    """Get unread notification count."""
    result = await db.execute(
        select(func.count()).select_from(
            select(Notification).where(
                Notification.user_id == current_user.id,
                Notification.status != NotificationStatus.READ,
            ).subquery()
        )
    )
    count = result.scalar()
    return {"unread_count": count}


@router.put("/{notification_id}/read")
async def mark_as_read(
    notification_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mark a notification as read."""
    notification = await db.get(Notification, notification_id)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")

    if notification.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    notification.status = NotificationStatus.READ
    notification.read_at = datetime.now(timezone.utc)

    return {"message": "Notification marked as read"}


@router.put("/read-all")
async def mark_all_as_read(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mark all notifications as read."""
    now = datetime.now(timezone.utc)
    await db.execute(
        update(Notification)
        .where(
            Notification.user_id == current_user.id,
            Notification.status != NotificationStatus.READ,
        )
        .values(status=NotificationStatus.READ, read_at=now)
    )

    return {"message": "All notifications marked as read"}


@router.get("/templates", response_model=list[NotificationTemplateResponse])
async def list_notification_templates(
    db: AsyncSession = Depends(get_read_db),
    current_user: User = require_permission(Permission.ADMIN_SETTINGS.value),
):
    """List notification templates (admin only)."""
    result = await db.execute(select(NotificationTemplate).order_by(NotificationTemplate.name))
    return result.scalars().all()


@router.post("/templates", response_model=NotificationTemplateResponse, status_code=201)
async def create_notification_template(
    data: NotificationTemplateCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = require_permission(Permission.ADMIN_SETTINGS.value),
):
    """Create a notification template (admin only)."""
    existing = await db.execute(
        select(NotificationTemplate).where(NotificationTemplate.name == data.name)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Template name already exists")

    template = NotificationTemplate(**data.model_dump())
    db.add(template)
    return template
