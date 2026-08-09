# app/services/address_service.py
from uuid import UUID
from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.models.address import UserAddress


class AddressService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_address(self, data: dict, user_id: UUID) -> UserAddress:
        if data.get("is_default"):
            await self._clear_default(user_id)

        address = UserAddress(
            user_id=user_id,
            label=data.get("label", "Home"),
            street=data["street"],
            city=data["city"],
            state=data["state"],
            pincode=data["pincode"],
            country=data.get("country", "India"),
            is_default=data.get("is_default", False),
            contact_name=data.get("contact_name"),
            contact_phone=data.get("contact_phone"),
        )
        self.db.add(address)
        await self.db.flush()
        await self.db.refresh(address)
        return address

    async def get_address(self, address_id: UUID, user_id: UUID) -> UserAddress:
        result = await self.db.execute(
            select(UserAddress).where(
                UserAddress.id == address_id,
                UserAddress.user_id == user_id,
            )
        )
        address = result.scalar_one_or_none()
        if not address:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Address not found",
            )
        return address

    async def list_addresses(self, user_id: UUID) -> dict:
        query = select(UserAddress).where(UserAddress.user_id == user_id)

        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()

        query = query.order_by(UserAddress.is_default.desc(), UserAddress.created_at.desc())
        result = await self.db.execute(query)
        addresses = result.scalars().all()

        return {
            "items": addresses,
            "total": total,
        }

    async def update_address(self, address_id: UUID, user_id: UUID, data: dict) -> UserAddress:
        address = await self.get_address(address_id, user_id)

        if data.get("is_default"):
            await self._clear_default(user_id)

        for key, value in data.items():
            if hasattr(address, key) and value is not None:
                setattr(address, key, value)

        await self.db.flush()
        await self.db.refresh(address)
        return address

    async def delete_address(self, address_id: UUID, user_id: UUID) -> dict:
        address = await self.get_address(address_id, user_id)
        await self.db.delete(address)
        return {"message": "Address deleted successfully"}

    async def set_default(self, address_id: UUID, user_id: UUID) -> UserAddress:
        address = await self.get_address(address_id, user_id)
        await self._clear_default(user_id)
        address.is_default = True
        await self.db.flush()
        await self.db.refresh(address)
        return address

    async def _clear_default(self, user_id: UUID):
        await self.db.execute(
            update(UserAddress)
            .where(UserAddress.user_id == user_id, UserAddress.is_default == True)
            .values(is_default=False)
        )
