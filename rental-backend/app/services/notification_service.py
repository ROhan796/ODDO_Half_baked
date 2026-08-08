# app/services/notification_service.py
from uuid import UUID
from datetime import datetime, timezone
from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.models.notification import (
    Notification,
    NotificationTemplate,
    NotificationType,
    NotificationChannel,
    NotificationStatus,
)


class NotificationService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_notification(
        self,
        user_id: UUID,
        notification_type: str,
        channel: str,
        title: str,
        message: str,
        data: dict = None,
    ) -> Notification:
        notification = Notification(
            user_id=user_id,
            type=NotificationType(notification_type),
            channel=NotificationChannel(channel),
            title=title,
            message=message,
            data=data or {},
            status=NotificationStatus.PENDING,
        )
        self.db.add(notification)
        await self.db.flush()
        await self.db.refresh(notification)
        return notification

    async def list_notifications(
        self, user_id: UUID, page: int = 1, limit: int = 20
    ) -> dict:
        query = select(Notification).where(Notification.user_id == user_id)

        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()

        unread_result = await self.db.execute(
            select(func.count()).select_from(Notification).where(
                Notification.user_id == user_id,
                Notification.status != NotificationStatus.READ,
            )
        )
        unread_count = unread_result.scalar()

        query = query.order_by(Notification.created_at.desc())
        query = query.offset((page - 1) * limit).limit(limit)
        result = await self.db.execute(query)
        notifications = result.scalars().all()

        return {
            "items": notifications,
            "total": total,
            "unread_count": unread_count,
            "page": page,
            "limit": limit,
            "pages": (total + limit - 1) // limit,
        }

    async def get_unread_count(self, user_id: UUID) -> dict:
        result = await self.db.execute(
            select(func.count()).select_from(Notification).where(
                Notification.user_id == user_id,
                Notification.status != NotificationStatus.READ,
            )
        )
        count = result.scalar()
        return {"unread_count": count}

    async def mark_read(self, notification_id: UUID) -> Notification:
        result = await self.db.execute(
            select(Notification).where(Notification.id == notification_id)
        )
        notification = result.scalar_one_or_none()
        if not notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found",
            )

        notification.status = NotificationStatus.READ
        notification.read_at = datetime.now(timezone.utc)

        await self.db.flush()
        await self.db.refresh(notification)
        return notification

    async def mark_all_read(self, user_id: UUID) -> dict:
        await self.db.execute(
            update(Notification)
            .where(
                Notification.user_id == user_id,
                Notification.status != NotificationStatus.READ,
            )
            .values(
                status=NotificationStatus.READ,
                read_at=datetime.now(timezone.utc),
            )
        )
        await self.db.flush()
        return {"message": "All notifications marked as read"}

    async def create_template(self, data: dict) -> NotificationTemplate:
        existing = await self.db.execute(
            select(NotificationTemplate).where(
                NotificationTemplate.name == data["name"]
            )
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Template with this name already exists",
            )

        template = NotificationTemplate(
            name=data["name"],
            type=NotificationType(data["type"]),
            channel=NotificationChannel(data["channel"]),
            subject=data.get("subject"),
            body_template=data["body_template"],
            variables=data.get("variables", []),
            is_active=data.get("is_active", True),
        )
        self.db.add(template)
        await self.db.flush()
        await self.db.refresh(template)
        return template

    async def list_templates(self, page: int = 1, limit: int = 20) -> dict:
        query = select(NotificationTemplate)

        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()

        query = query.order_by(NotificationTemplate.name)
        query = query.offset((page - 1) * limit).limit(limit)
        result = await self.db.execute(query)
        templates = result.scalars().all()

        return {
            "items": templates,
            "total": total,
            "page": page,
            "limit": limit,
            "pages": (total + limit - 1) // limit,
        }
