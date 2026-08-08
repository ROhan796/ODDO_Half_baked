# app/schemas/recovery.py
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import uuid


class RecoveryCaseCreate(BaseModel):
    rental_id: uuid.UUID
    reason: str = Field(..., min_length=5, max_length=255)
    amount_outstanding: float = Field(..., gt=0)


class RecoveryCaseUpdate(BaseModel):
    status: Optional[str] = None
    recovery_agent: Optional[str] = None
    notes: Optional[str] = None
    recovered_amount: Optional[float] = None
    product_recovered: Optional[bool] = None
    escalated_to_legal: Optional[bool] = None
    legal_reference: Optional[str] = None


class RecoveryCaseResponse(BaseModel):
    id: uuid.UUID
    rental_id: uuid.UUID
    customer_id: uuid.UUID
    product_id: uuid.UUID
    reason: str
    amount_outstanding: float
    status: str
    recovered_amount: float
    product_recovered: bool
    escalated_to_legal: bool
    created_at: datetime

    class Config:
        from_attributes = True
