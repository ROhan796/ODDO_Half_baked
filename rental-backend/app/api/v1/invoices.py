# app/api/v1/invoices.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
import uuid

from app.utils.database import get_read_db, get_db
from app.api.deps import get_current_user, require_permission
from app.models.user import User
from app.models.invoice import Invoice, Payment
from app.schemas.invoice import InvoiceCreate, InvoiceResponse, PaymentCreate, PaymentResponse
from app.core.permissions import Permission

router = APIRouter()


@router.get("/", response_model=list[InvoiceResponse])
async def list_invoices(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_read_db),
    current_user: User = require_permission(Permission.INVOICE_VIEW.value),
):
    """List invoices."""
    query = select(Invoice)

    if current_user.role == "portal_user":
        query = query.where(Invoice.customer_id == current_user.id)

    if status:
        query = query.where(Invoice.status == status)

    query = query.offset((page - 1) * limit).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/", response_model=InvoiceResponse, status_code=201)
async def create_invoice(
    data: InvoiceCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = require_permission(Permission.INVOICE_CREATE.value),
):
    """Create a new invoice."""
    subtotal = sum(item.quantity * item.unit_price for item in data.items)
    invoice = Invoice(
        invoice_number=f"INV-{uuid.uuid4().hex[:8].upper()}",
        customer_id=data.customer_id,
        rental_id=data.rental_id,
        subtotal=subtotal,
        total_amount=subtotal,
        notes=data.notes,
    )
    db.add(invoice)
    return invoice


@router.get("/{invoice_id}", response_model=InvoiceResponse)
async def get_invoice(
    invoice_id: uuid.UUID,
    db: AsyncSession = Depends(get_read_db),
    current_user: User = require_permission(Permission.INVOICE_VIEW.value),
):
    """Get invoice by ID."""
    invoice = await db.get(Invoice, invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return invoice


@router.post("/payments", response_model=PaymentResponse, status_code=201)
async def create_payment(
    data: PaymentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a payment."""
    payment = Payment(
        payment_number=f"PMT-{uuid.uuid4().hex[:8].upper()}",
        invoice_id=data.invoice_id,
        customer_id=current_user.id,
        amount=data.amount,
        payment_method=data.payment_method,
    )
    db.add(payment)
    return payment
