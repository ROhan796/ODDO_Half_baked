# app/schemas/purchase_order.py
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime, date
from decimal import Decimal
import uuid


class PORentalDates(BaseModel):
    start_date: Optional[date] = None
    end_date: Optional[date] = None


class PORequisitionCreate(BaseModel):
    equipment_name: str = Field(..., min_length=2, max_length=255)
    quantity: int = Field(1, ge=1)
    daily_rate: Optional[float] = None
    rental_dates: Optional[PORentalDates] = None
    total_amount: Optional[float] = None
    department: Optional[str] = None


class PORequisitionResponse(BaseModel):
    id: uuid.UUID
    enterprise_id: uuid.UUID
    requested_by: uuid.UUID
    equipment_name: str
    quantity: int
    daily_rate: Optional[float] = None
    rental_dates: Optional[Dict[str, Any]] = None
    total_amount: Optional[float] = None
    department: Optional[str] = None
    status: str
    reviewed_by: Optional[uuid.UUID] = None
    reviewed_at: Optional[datetime] = None
    review_notes: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class PORequisitionListResponse(BaseModel):
    items: List[PORequisitionResponse]
    total: int
    page: int
    limit: int
    has_next: bool


class POReviewRequest(BaseModel):
    review_notes: Optional[str] = None


class CreditRequestCreate(BaseModel):
    requested_limit: float = Field(..., gt=0)
    reason: str = Field(..., min_length=10, max_length=1000)
    department: Optional[str] = None
    urgency: str = Field("normal", pattern="^(low|normal|high|critical)$")
