# app/services/user_service.py
from uuid import UUID
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.models.user import User


class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user(self, user_id: UUID) -> User:
        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        return user

    async def list_users(
        self, page: int = 1, limit: int = 20, search: str = None, role: str = None
    ) -> dict:
        query = select(User)

        if search:
            search_filter = or_(
                User.name.ilike(f"%{search}%"),
                User.email.ilike(f"%{search}%"),
                User.phone.ilike(f"%{search}%"),
            )
            query = query.where(search_filter)

        if role:
            query = query.where(User.role == role)

        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()

        query = query.offset((page - 1) * limit).limit(limit)
        result = await self.db.execute(query)
        users = result.scalars().all()

        return {
            "items": users,
            "total": total,
            "page": page,
            "limit": limit,
            "pages": (total + limit - 1) // limit,
        }

    async def update_user(self, user_id: UUID, data: dict) -> User:
        user = await self.get_user(user_id)

        for key, value in data.items():
            if hasattr(user, key) and value is not None:
                setattr(user, key, value)

        await self.db.flush()
        await self.db.refresh(user)
        return user

    async def get_user_profile(self, user_id: UUID) -> dict:
        user = await self.get_user(user_id)
        return {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "phone": user.phone,
            "user_type": user.user_type.value,
            "role": user.role.value,
            "kyc_status": user.kyc_status.value,
            "trust_score": user.trust_score,
            "trust_tier": user.trust_tier,
            "points_balance": user.points_balance,
            "lifetime_rentals": user.lifetime_rentals,
            "profile_photo_url": user.profile_photo_url,
            "notification_preferences": user.notification_preferences,
        }
