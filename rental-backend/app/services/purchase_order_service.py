# app/services/purchase_order_service.py
from uuid import UUID
from datetime import datetime, timezone
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.models.purchase_order import PORequisition, POStatus


class PurchaseOrderService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_po(self, data: dict, enterprise_id: UUID, requested_by: UUID) -> PORequisition:
        po = PORequisition(
            enterprise_id=enterprise_id,
            requested_by=requested_by,
            equipment_name=data["equipment_name"],
            quantity=data.get("quantity", 1),
            daily_rate=data.get("daily_rate"),
            rental_dates=data.get("rental_dates"),
            total_amount=data.get("total_amount"),
            department=data.get("department"),
            status=POStatus.PENDING,
        )
        self.db.add(po)
        await self.db.flush()
        await self.db.refresh(po)
        return po

    async def get_po(self, po_id: UUID) -> PORequisition:
        result = await self.db.execute(
            select(PORequisition).where(PORequisition.id == po_id)
        )
        po = result.scalar_one_or_none()
        if not po:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Purchase order not found",
            )
        return po

    async def list_pos(
        self,
        page: int = 1,
        limit: int = 20,
        enterprise_id: UUID = None,
        po_status: str = None,
    ) -> dict:
        query = select(PORequisition)

        if enterprise_id:
            query = query.where(PORequisition.enterprise_id == enterprise_id)

        if po_status:
            query = query.where(PORequisition.status == po_status)

        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()

        query = query.order_by(PORequisition.created_at.desc())
        query = query.offset((page - 1) * limit).limit(limit)
        result = await self.db.execute(query)
        pos = result.scalars().all()

        return {
            "items": pos,
            "total": total,
            "page": page,
            "limit": limit,
            "has_next": (page * limit) < total,
        }

    async def approve_po(self, po_id: UUID, reviewed_by: UUID, review_notes: str = None) -> PORequisition:
        po = await self.get_po(po_id)

        if po.status != POStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot approve PO in {po.status.value} status",
            )

        po.status = POStatus.APPROVED
        po.reviewed_by = reviewed_by
        po.reviewed_at = datetime.now(timezone.utc)
        po.review_notes = review_notes

        await self.db.flush()
        await self.db.refresh(po)
        return po

    async def reject_po(self, po_id: UUID, reviewed_by: UUID, review_notes: str = None) -> PORequisition:
        po = await self.get_po(po_id)

        if po.status != POStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot reject PO in {po.status.value} status",
            )

        po.status = POStatus.REJECTED
        po.reviewed_by = reviewed_by
        po.reviewed_at = datetime.now(timezone.utc)
        po.review_notes = review_notes

        await self.db.flush()
        await self.db.refresh(po)
        return po
