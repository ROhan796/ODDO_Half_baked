# app/services/stock_service.py
from uuid import UUID
from datetime import datetime, timezone
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.models.stock import StockLocation, StockMovement, StockLevel, MovementType


class StockService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_location(self, data: dict) -> StockLocation:
        existing = await self.db.execute(
            select(StockLocation).where(StockLocation.code == data["code"])
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Location with this code already exists",
            )

        location = StockLocation(
            name=data["name"],
            code=data["code"],
            address=data.get("address"),
            city=data.get("city"),
            state=data.get("state"),
            pincode=data.get("pincode"),
            contact_person=data.get("contact_person"),
            contact_phone=data.get("contact_phone"),
            is_active=data.get("is_active", True),
            is_warehouse=data.get("is_warehouse", False),
            capacity=data.get("capacity"),
        )
        self.db.add(location)
        await self.db.flush()
        await self.db.refresh(location)
        return location

    async def get_location(self, location_id: UUID) -> StockLocation:
        result = await self.db.execute(
            select(StockLocation).where(StockLocation.id == location_id)
        )
        location = result.scalar_one_or_none()
        if not location:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Location not found",
            )
        return location

    async def list_locations(self, page: int = 1, limit: int = 20) -> dict:
        query = select(StockLocation)

        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()

        query = query.order_by(StockLocation.name)
        query = query.offset((page - 1) * limit).limit(limit)
        result = await self.db.execute(query)
        locations = result.scalars().all()

        return {
            "items": locations,
            "total": total,
            "page": page,
            "limit": limit,
            "pages": (total + limit - 1) // limit,
        }

    async def create_movement(self, data: dict, performed_by: UUID) -> StockMovement:
        movement = StockMovement(
            product_id=data["product_id"],
            from_location_id=data.get("from_location_id"),
            to_location_id=data.get("to_location_id"),
            movement_type=MovementType(data["movement_type"]),
            quantity=data["quantity"],
            reference_type=data.get("reference_type"),
            reference_id=data.get("reference_id"),
            notes=data.get("notes"),
            performed_by=performed_by,
        )
        self.db.add(movement)

        if data.get("to_location_id"):
            await self._update_stock_level(
                data["product_id"],
                data["to_location_id"],
                data["quantity"],
                MovementType(data["movement_type"]),
            )

        if data.get("from_location_id"):
            await self._update_stock_level(
                data["product_id"],
                data["from_location_id"],
                -data["quantity"],
                MovementType(data["movement_type"]),
            )

        await self.db.flush()
        await self.db.refresh(movement)
        return movement

    async def list_movements(
        self, page: int = 1, limit: int = 20, product_id: UUID = None
    ) -> dict:
        query = select(StockMovement)

        if product_id:
            query = query.where(StockMovement.product_id == product_id)

        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()

        query = query.order_by(StockMovement.created_at.desc())
        query = query.offset((page - 1) * limit).limit(limit)
        result = await self.db.execute(query)
        movements = result.scalars().all()

        return {
            "items": movements,
            "total": total,
            "page": page,
            "limit": limit,
            "pages": (total + limit - 1) // limit,
        }

    async def get_stock_level(
        self, product_id: UUID, location_id: UUID
    ) -> StockLevel:
        result = await self.db.execute(
            select(StockLevel).where(
                and_(
                    StockLevel.product_id == product_id,
                    StockLevel.location_id == location_id,
                )
            )
        )
        level = result.scalar_one_or_none()
        if not level:
            return StockLevel(
                product_id=product_id,
                location_id=location_id,
                quantity=0,
                reserved=0,
                available=0,
            )
        return level

    async def _update_stock_level(
        self,
        product_id: UUID,
        location_id: UUID,
        quantity_change: int,
        movement_type: MovementType,
    ) -> None:
        result = await self.db.execute(
            select(StockLevel).where(
                and_(
                    StockLevel.product_id == product_id,
                    StockLevel.location_id == location_id,
                )
            )
        )
        level = result.scalar_one_or_none()

        if not level:
            level = StockLevel(
                product_id=product_id,
                location_id=location_id,
                quantity=0,
                reserved=0,
                available=0,
            )
            self.db.add(level)

        level.quantity = max(level.quantity + quantity_change, 0)
        level.available = max(level.quantity - level.reserved, 0)

        if movement_type == MovementType.IN:
            level.last_received_at = datetime.now(timezone.utc)
        elif movement_type == MovementType.ADJUSTMENT:
            level.last_counted_at = datetime.now(timezone.utc)
