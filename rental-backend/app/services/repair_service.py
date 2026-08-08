# app/services/repair_service.py
from uuid import UUID
from datetime import datetime, timezone
from decimal import Decimal
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.models.repair import RepairCase, RepairStatus
from app.models.product import Product, ProductStatus


class RepairService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_repair(self, data: dict, reported_by: UUID) -> RepairCase:
        product = await self.db.get(Product, data["product_id"])
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found",
            )

        repair = RepairCase(
            product_id=data["product_id"],
            rental_id=data.get("rental_id"),
            reported_by=reported_by,
            reported_at=datetime.now(timezone.utc),
            damage_description=data["damage_description"],
            damage_photos=data.get("damage_photos", []),
            estimated_cost=(
                Decimal(str(data["estimated_cost"]))
                if data.get("estimated_cost")
                else None
            ),
            status=RepairStatus.REPORTED,
        )
        self.db.add(repair)

        product.status = ProductStatus.IN_REPAIR
        product.total_damage_reports = (product.total_damage_reports or 0) + 1

        await self.db.flush()
        await self.db.refresh(repair)
        return repair

    async def get_repair(self, repair_id: UUID) -> RepairCase:
        result = await self.db.execute(
            select(RepairCase).where(RepairCase.id == repair_id)
        )
        repair = result.scalar_one_or_none()
        if not repair:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Repair case not found",
            )
        return repair

    async def list_repairs(
        self, page: int = 1, limit: int = 20, repair_status: str = None
    ) -> dict:
        query = select(RepairCase)

        if repair_status:
            query = query.where(RepairCase.status == repair_status)

        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()

        query = query.order_by(RepairCase.created_at.desc())
        query = query.offset((page - 1) * limit).limit(limit)
        result = await self.db.execute(query)
        repairs = result.scalars().all()

        return {
            "items": repairs,
            "total": total,
            "page": page,
            "limit": limit,
            "pages": (total + limit - 1) // limit,
        }

    async def update_repair(self, repair_id: UUID, data: dict) -> RepairCase:
        repair = await self.get_repair(repair_id)

        status_map = {
            "assessed": RepairStatus.ASSESSED,
            "in_progress": RepairStatus.IN_PROGRESS,
            "completed": RepairStatus.COMPLETED,
            "write_off": RepairStatus.WRITE_OFF,
        }

        if "status" in data:
            new_status = status_map.get(data["status"])
            if new_status:
                repair.status = new_status

                if new_status == RepairStatus.IN_PROGRESS:
                    repair.started_at = datetime.now(timezone.utc)
                elif new_status == RepairStatus.COMPLETED:
                    repair.completed_at = datetime.now(timezone.utc)
                    product = await self.db.get(Product, repair.product_id)
                    if product:
                        product.status = ProductStatus.AVAILABLE

        if "assigned_to" in data:
            repair.assigned_to = data["assigned_to"]
        if "vendor_name" in data:
            repair.vendor_name = data["vendor_name"]
        if "vendor_reference" in data:
            repair.vendor_reference = data["vendor_reference"]
        if "actual_cost" in data:
            repair.actual_cost = Decimal(str(data["actual_cost"]))
        if "notes" in data:
            repair.notes = data["notes"]
        if "charged_to_customer" in data:
            repair.charged_to_customer = data["charged_to_customer"]
        if "customer_charge_amount" in data:
            repair.customer_charge_amount = Decimal(str(data["customer_charge_amount"]))

        await self.db.flush()
        await self.db.refresh(repair)
        return repair
