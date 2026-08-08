# app/services/recovery_service.py
from uuid import UUID
from datetime import datetime, timezone
from decimal import Decimal
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.models.recovery import RecoveryCase, RecoveryStatus


class RecoveryService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_recovery(self, data: dict, initiated_by: UUID) -> RecoveryCase:
        recovery = RecoveryCase(
            rental_id=data["rental_id"],
            customer_id=data["customer_id"],
            product_id=data["product_id"],
            initiated_by=initiated_by,
            initiated_at=datetime.now(timezone.utc),
            reason=data["reason"],
            amount_outstanding=Decimal(str(data["amount_outstanding"])),
            status=RecoveryStatus.INITIATED,
            recovery_agent=data.get("recovery_agent"),
            notes=data.get("notes"),
        )
        self.db.add(recovery)
        await self.db.flush()
        await self.db.refresh(recovery)
        return recovery

    async def get_recovery(self, recovery_id: UUID) -> RecoveryCase:
        result = await self.db.execute(
            select(RecoveryCase).where(RecoveryCase.id == recovery_id)
        )
        recovery = result.scalar_one_or_none()
        if not recovery:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Recovery case not found",
            )
        return recovery

    async def list_recoveries(
        self, page: int = 1, limit: int = 20, recovery_status: str = None
    ) -> dict:
        query = select(RecoveryCase)

        if recovery_status:
            query = query.where(RecoveryCase.status == recovery_status)

        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()

        query = query.order_by(RecoveryCase.created_at.desc())
        query = query.offset((page - 1) * limit).limit(limit)
        result = await self.db.execute(query)
        recoveries = result.scalars().all()

        return {
            "items": recoveries,
            "total": total,
            "page": page,
            "limit": limit,
            "pages": (total + limit - 1) // limit,
        }

    async def update_recovery(self, recovery_id: UUID, data: dict) -> RecoveryCase:
        recovery = await self.get_recovery(recovery_id)

        status_map = {
            "in_progress": RecoveryStatus.IN_PROGRESS,
            "successful": RecoveryStatus.SUCCESSFUL,
            "partial": RecoveryStatus.PARTIAL,
            "failed": RecoveryStatus.FAILED,
            "legal": RecoveryStatus.LEGAL,
        }

        if "status" in data:
            new_status = status_map.get(data["status"])
            if new_status:
                recovery.status = new_status

                if new_status == RecoveryStatus.SUCCESSFUL:
                    recovery.recovered_at = datetime.now(timezone.utc)
                elif new_status == RecoveryStatus.LEGAL:
                    recovery.escalated_to_legal = True

        if "recovery_agent" in data:
            recovery.recovery_agent = data["recovery_agent"]
        if "notes" in data:
            recovery.notes = data["notes"]
        if "recovered_amount" in data:
            recovery.recovered_amount = Decimal(str(data["recovered_amount"]))
        if "product_recovered" in data:
            recovery.product_recovered = data["product_recovered"]
            if data["product_recovered"]:
                recovery.product_recovered_at = datetime.now(timezone.utc)
        if "next_action_at" in data:
            recovery.next_action_at = data["next_action_at"]
        if "next_action_description" in data:
            recovery.next_action_description = data["next_action_description"]
        if "legal_reference" in data:
            recovery.legal_reference = data["legal_reference"]
        if "contact_attempts" in data:
            contact = data["contact_attempts"]
            if isinstance(contact, list):
                recovery.contact_attempts = (recovery.contact_attempts or []) + contact
            else:
                recovery.contact_attempts = (recovery.contact_attempts or []) + [contact]
            recovery.last_contact_at = datetime.now(timezone.utc)

        await self.db.flush()
        await self.db.refresh(recovery)
        return recovery
