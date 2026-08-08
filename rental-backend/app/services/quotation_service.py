# app/services/quotation_service.py
from uuid import UUID
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.models.quotation import Quotation, QuotationStatus


class QuotationService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_quotation(self, data: dict, created_by: UUID) -> Quotation:
        quote_number = await self._generate_quote_number()

        subtotal = Decimal("0")
        items = data.get("items", [])
        for item in items:
            qty = Decimal(str(item.get("quantity", 1)))
            price = Decimal(str(item.get("unit_price", 0)))
            subtotal += qty * price

        tax_amount = Decimal(str(data.get("tax_amount", 0)))
        discount_amount = Decimal(str(data.get("discount_amount", 0)))
        total_amount = subtotal + tax_amount - discount_amount
        deposit_amount = Decimal(str(data.get("deposit_amount", 0)))

        quotation = Quotation(
            quote_number=quote_number,
            customer_id=data["customer_id"],
            enterprise_id=data.get("enterprise_id"),
            status=QuotationStatus.DRAFT,
            items=items,
            subtotal=subtotal,
            tax_amount=tax_amount,
            discount_amount=discount_amount,
            total_amount=total_amount,
            deposit_amount=deposit_amount,
            valid_until=data.get(
                "valid_until",
                datetime.now(timezone.utc) + timedelta(days=15),
            ),
            notes=data.get("notes"),
            terms=data.get("terms"),
            created_by=created_by,
        )
        self.db.add(quotation)
        await self.db.flush()
        await self.db.refresh(quotation)
        return quotation

    async def get_quotation(self, quotation_id: UUID) -> Quotation:
        result = await self.db.execute(
            select(Quotation).where(Quotation.id == quotation_id)
        )
        quotation = result.scalar_one_or_none()
        if not quotation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Quotation not found",
            )
        return quotation

    async def list_quotations(
        self,
        page: int = 1,
        limit: int = 20,
        quotation_status: str = None,
        customer_id: UUID = None,
    ) -> dict:
        query = select(Quotation)

        if quotation_status:
            query = query.where(Quotation.status == quotation_status)

        if customer_id:
            query = query.where(Quotation.customer_id == customer_id)

        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()

        query = query.order_by(Quotation.created_at.desc())
        query = query.offset((page - 1) * limit).limit(limit)
        result = await self.db.execute(query)
        quotations = result.scalars().all()

        return {
            "items": quotations,
            "total": total,
            "page": page,
            "limit": limit,
            "pages": (total + limit - 1) // limit,
        }

    async def update_status(
        self, quotation_id: UUID, quotation_status: str
    ) -> Quotation:
        quotation = await self.get_quotation(quotation_id)
        new_status = QuotationStatus(quotation_status)

        status_timestamps = {
            QuotationStatus.SENT: "sent_at",
            QuotationStatus.ACCEPTED: "accepted_at",
            QuotationStatus.REJECTED: "rejected_at",
        }

        quotation.status = new_status
        timestamp_field = status_timestamps.get(new_status)
        if timestamp_field:
            setattr(quotation, timestamp_field, datetime.now(timezone.utc))

        await self.db.flush()
        await self.db.refresh(quotation)
        return quotation

    async def _generate_quote_number(self) -> str:
        today = datetime.now(timezone.utc).strftime("%Y%m%d")
        result = await self.db.execute(
            select(func.count()).select_from(Quotation).where(
                Quotation.quote_number.like(f"QT-{today}-%")
            )
        )
        count = result.scalar() + 1
        return f"QT-{today}-{count:04d}"
