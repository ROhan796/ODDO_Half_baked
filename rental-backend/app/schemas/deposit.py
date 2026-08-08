# app/schemas/deposit.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid


class DepositResponse(BaseModel):
    id: uuid.UUID
    rental_id: uuid.UUID
    customer_id: uuid.UUID
    amount: float
    status: str
    refund_amount: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True


class DepositDeductionCreate(BaseModel):
    amount: float
    reason: str
    deduction_type: str
    documentation_url: Optional[str] = None


class DepositDeductionResponse(BaseModel):
    id: uuid.UUID
    deposit_id: uuid.UUID
    amount: float
    reason: str
    deduction_type: str
    documented_by: uuid.UUID
    created_at: datetime

    class Config:
        from_attributes = True
