# app/schemas/invoice.py
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import uuid


class InvoiceItemCreate(BaseModel):
    description: str
    quantity: float = Field(..., gt=0)
    unit_price: float = Field(..., gt=0)
    tax_rate: float = Field(0, ge=0, le=100)


class InvoiceCreate(BaseModel):
    customer_id: uuid.UUID
    rental_id: Optional[uuid.UUID] = None
    items: List[InvoiceItemCreate]
    notes: Optional[str] = None
    due_days: int = Field(30, ge=1, le=90)


class InvoiceResponse(BaseModel):
    id: uuid.UUID
    invoice_number: str
    customer_id: uuid.UUID
    status: str
    subtotal: float
    tax_amount: float
    discount_amount: float
    total_amount: float
    paid_amount: float
    due_date: datetime
    paid_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class InvoiceListResponse(BaseModel):
    items: list[InvoiceResponse]
    total: int
    page: int
    limit: int
    has_next: bool


class PaymentCreate(BaseModel):
    invoice_id: uuid.UUID
    amount: float = Field(..., gt=0)
    payment_method: str = Field(..., pattern="^(razorpay|cash|bank_transfer|credit)$")


class PaymentResponse(BaseModel):
    id: uuid.UUID
    payment_number: str
    invoice_id: uuid.UUID
    amount: float
    status: str
    payment_method: str
    razorpay_order_id: Optional[str] = None
    paid_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True
