# app/schemas/quotation.py
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import uuid


class QuotationItem(BaseModel):
    product_id: uuid.UUID
    product_name: str
    rental_type: str
    duration: int
    unit_price: float
    quantity: int = 1
    amount: float


class QuotationCreate(BaseModel):
    customer_id: uuid.UUID
    items: List[QuotationItem]
    notes: Optional[str] = None
    terms: Optional[str] = None
    valid_days: int = Field(30, ge=1, le=90)


class QuotationUpdate(BaseModel):
    status: Optional[str] = None
    notes: Optional[str] = None
    terms: Optional[str] = None


class QuotationResponse(BaseModel):
    id: uuid.UUID
    quote_number: str
    customer_id: uuid.UUID
    status: str
    items: List[QuotationItem]
    subtotal: float
    tax_amount: float
    discount_amount: float
    total_amount: float
    deposit_amount: float
    valid_until: datetime
    notes: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class QuotationListResponse(BaseModel):
    items: list[QuotationResponse]
    total: int
    page: int
    limit: int
    has_next: bool
