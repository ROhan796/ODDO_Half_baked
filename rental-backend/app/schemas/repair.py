# app/schemas/repair.py
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import uuid


class RepairCaseCreate(BaseModel):
    product_id: uuid.UUID
    rental_id: Optional[uuid.UUID] = None
    damage_description: str = Field(..., min_length=10, max_length=2000)
    damage_photos: List[str] = []


class RepairCaseUpdate(BaseModel):
    status: Optional[str] = None
    estimated_cost: Optional[float] = None
    actual_cost: Optional[float] = None
    vendor_name: Optional[str] = None
    notes: Optional[str] = None
    charged_to_customer: Optional[bool] = None
    customer_charge_amount: Optional[float] = None


class RepairCaseResponse(BaseModel):
    id: uuid.UUID
    product_id: uuid.UUID
    rental_id: Optional[uuid.UUID] = None
    damage_description: str
    damage_photos: List[str]
    estimated_cost: Optional[float] = None
    actual_cost: Optional[float] = None
    status: str
    charged_to_customer: bool
    customer_charge_amount: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True
