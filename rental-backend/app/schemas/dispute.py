# app/schemas/dispute.py
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import uuid


class DisputeCreate(BaseModel):
    rental_id: uuid.UUID
    dispute_type: str = Field(..., pattern="^(late_fee|damage|deposit|charge|other)$")
    amount_disputed: float = Field(..., gt=0)
    description: str = Field(..., min_length=10, max_length=2000)
    evidence_urls: List[str] = []


class DisputeUpdate(BaseModel):
    status: Optional[str] = None
    resolution: Optional[str] = None
    resolution_amount: Optional[float] = None
    resolution_notes: Optional[str] = None


class DisputeResponse(BaseModel):
    id: uuid.UUID
    rental_id: uuid.UUID
    customer_id: uuid.UUID
    dispute_type: str
    amount_disputed: float
    description: str
    evidence_urls: List[str]
    status: str
    resolution: Optional[str] = None
    resolution_amount: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True


class DisputeListResponse(BaseModel):
    items: list[DisputeResponse]
    total: int
    page: int
    limit: int
    has_next: bool
