# app/services/invoice_service.py
from uuid import UUID
from datetime import datetime, timezone
from decimal import Decimal
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status

from app.models.invoice import Invoice, InvoiceItem, InvoiceStatus, Payment, PaymentStatus, PaymentMethod


class InvoiceService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_invoice(self, data: dict) -> Invoice:
        invoice_number = await self._generate_invoice_number()

        subtotal = Decimal("0")
        items_data = data.get("items", [])

        invoice = Invoice(
            invoice_number=invoice_number,
            customer_id=data["customer_id"],
            enterprise_id=data.get("enterprise_id"),
            rental_id=data.get("rental_id"),
            status=InvoiceStatus.DRAFT,
            subtotal=Decimal("0"),
            tax_amount=Decimal(str(data.get("tax_amount", 0))),
            discount_amount=Decimal(str(data.get("discount_amount", 0))),
            total_amount=Decimal("0"),
            due_date=data["due_date"],
            notes=data.get("notes"),
            billing_address=data.get("billing_address"),
            shipping_address=data.get("shipping_address"),
        )
        self.db.add(invoice)
        await self.db.flush()

        for item_data in items_data:
            qty = Decimal(str(item_data.get("quantity", 1)))
            price = Decimal(str(item_data.get("unit_price", 0)))
            amount = qty * price
            tax_rate = Decimal(str(item_data.get("tax_rate", 0)))
            item_tax = amount * tax_rate / Decimal("100")

            item = InvoiceItem(
                invoice_id=invoice.id,
                description=item_data["description"],
                quantity=qty,
                unit_price=price,
                amount=amount,
                tax_rate=tax_rate,
                tax_amount=item_tax,
                metadata_=item_data.get("metadata_", {}),
            )
            self.db.add(item)
            subtotal += amount

        invoice.subtotal = subtotal
        invoice.total_amount = (
            subtotal + invoice.tax_amount - invoice.discount_amount
        )

        await self.db.flush()
        await self.db.refresh(invoice)
        return invoice

    async def get_invoice(self, invoice_id: UUID) -> Invoice:
        result = await self.db.execute(
            select(Invoice)
            .options(selectinload(Invoice.items), selectinload(Invoice.payments))
            .where(Invoice.id == invoice_id)
        )
        invoice = result.scalar_one_or_none()
        if not invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invoice not found",
            )
        return invoice

    async def list_invoices(
        self,
        page: int = 1,
        limit: int = 20,
        invoice_status: str = None,
        customer_id: UUID = None,
    ) -> dict:
        query = select(Invoice)

        if invoice_status:
            query = query.where(Invoice.status == invoice_status)

        if customer_id:
            query = query.where(Invoice.customer_id == customer_id)

        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()

        query = query.order_by(Invoice.created_at.desc())
        query = query.offset((page - 1) * limit).limit(limit)
        result = await self.db.execute(query)
        invoices = result.scalars().all()

        return {
            "items": invoices,
            "total": total,
            "page": page,
            "limit": limit,
            "pages": (total + limit - 1) // limit,
        }

    async def record_payment(self, invoice_id: UUID, data: dict) -> Payment:
        invoice = await self.get_invoice(invoice_id)

        payment_number = await self._generate_payment_number()
        amount = Decimal(str(data["amount"]))

        payment = Payment(
            payment_number=payment_number,
            invoice_id=invoice.id,
            customer_id=invoice.customer_id,
            amount=amount,
            status=PaymentStatus.COMPLETED,
            payment_method=PaymentMethod(data["payment_method"]),
            razorpay_order_id=data.get("razorpay_order_id"),
            razorpay_payment_id=data.get("razorpay_payment_id"),
            razorpay_signature=data.get("razorpay_signature"),
            transaction_reference=data.get("transaction_reference"),
            paid_at=datetime.now(timezone.utc),
        )
        self.db.add(payment)

        invoice.paid_amount = (invoice.paid_amount or Decimal("0")) + amount

        if invoice.paid_amount >= invoice.total_amount:
            invoice.status = InvoiceStatus.PAID
            invoice.paid_at = datetime.now(timezone.utc)
        else:
            invoice.status = InvoiceStatus.PARTIALLY_PAID

        await self.db.flush()
        await self.db.refresh(payment)
        return payment

    async def update_status(self, invoice_id: UUID, invoice_status: str) -> Invoice:
        invoice = await self.get_invoice(invoice_id)
        invoice.status = InvoiceStatus(invoice_status)

        if invoice_status == "paid":
            invoice.paid_at = datetime.now(timezone.utc)

        await self.db.flush()
        await self.db.refresh(invoice)
        return invoice

    async def _generate_invoice_number(self) -> str:
        today = datetime.now(timezone.utc).strftime("%Y%m%d")
        result = await self.db.execute(
            select(func.count()).select_from(Invoice).where(
                Invoice.invoice_number.like(f"INV-{today}-%")
            )
        )
        count = result.scalar() + 1
        return f"INV-{today}-{count:04d}"

    async def _generate_payment_number(self) -> str:
        today = datetime.now(timezone.utc).strftime("%Y%m%d")
        result = await self.db.execute(
            select(func.count()).select_from(Payment).where(
                Payment.payment_number.like(f"PAY-{today}-%")
            )
        )
        count = result.scalar() + 1
        return f"PAY-{today}-{count:04d}"
