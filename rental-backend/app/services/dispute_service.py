# app/services/dispute_service.py
from uuid import UUID
from datetime import datetime, timezone
from decimal import Decimal
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.models.dispute import Dispute, DisputeStatus, DisputeResolution


class DisputeService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_dispute(self, data: dict, filed_by: UUID) -> Dispute:
        dispute = Dispute(
            rental_id=data["rental_id"],
            customer_id=data["customer_id"],
            filed_by=filed_by,
            dispute_type=data["dispute_type"],
            amount_disputed=Decimal(str(data["amount_disputed"])),
            description=data["description"],
            evidence_urls=data.get("evidence_urls", []),
            status=DisputeStatus.OPEN,
            assigned_to=data.get("assigned_to"),
            deadline=data.get("deadline"),
        )
        self.db.add(dispute)
        await self.db.flush()
        await self.db.refresh(dispute)
        return dispute

    async def get_dispute(self, dispute_id: UUID) -> Dispute:
        result = await self.db.execute(
            select(Dispute).where(Dispute.id == dispute_id)
        )
        dispute = result.scalar_one_or_none()
        if not dispute:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dispute not found",
            )
        return dispute

    async def list_disputes(
        self,
        page: int = 1,
        limit: int = 20,
        dispute_status: str = None,
        customer_id: UUID = None,
    ) -> dict:
        query = select(Dispute)

        if dispute_status:
            query = query.where(Dispute.status == dispute_status)

        if customer_id:
            query = query.where(Dispute.customer_id == customer_id)

        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()

        query = query.order_by(Dispute.created_at.desc())
        query = query.offset((page - 1) * limit).limit(limit)
        result = await self.db.execute(query)
        disputes = result.scalars().all()

        return {
            "items": disputes,
            "total": total,
            "page": page,
            "limit": limit,
            "pages": (total + limit - 1) // limit,
        }

    async def resolve_dispute(
        self, dispute_id: UUID, data: dict, resolved_by: UUID
    ) -> Dispute:
        dispute = await self.get_dispute(dispute_id)

        if dispute.status == DisputeStatus.RESOLVED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Dispute is already resolved",
            )

        dispute.status = DisputeStatus.RESOLVED
        dispute.resolution = DisputeResolution(data["resolution"])
        dispute.resolution_amount = (
            Decimal(str(data["resolution_amount"]))
            if data.get("resolution_amount")
            else None
        )
        dispute.resolution_notes = data.get("resolution_notes")
        dispute.resolved_by = resolved_by
        dispute.resolved_at = datetime.now(timezone.utc)

        await self.db.flush()
        await self.db.refresh(dispute)
        return dispute
