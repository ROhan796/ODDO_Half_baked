# app/schemas/rental.py
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime, date
import uuid


class RentalCreate(BaseModel):
    customer_id: uuid.UUID
    product_id: uuid.UUID
    start_date: date
    end_date: date
    rental_type: str = Field(..., pattern="^(daily|weekly|monthly)$")
    delivery_address: Optional[str] = None
    special_requirements: Optional[str] = None
    insurance_selected: bool = False

    @field_validator("end_date")
    @classmethod
    def end_date_after_start(cls, v, info):
        if "start_date" in info.data and v <= info.data["start_date"]:
            raise ValueError("end_date must be after start_date")
        return v


class RentalUpdate(BaseModel):
    status: Optional[str] = None
    delivery_address: Optional[str] = None
    special_requirements: Optional[str] = None


class RentalResponse(BaseModel):
    id: uuid.UUID
    status: str
    customer_id: uuid.UUID
    product_id: uuid.UUID
    rental_type: str
    start_date: date
    end_date: date
    actual_return_date: Optional[date] = None
    daily_rate: float
    total_amount: float
    deposit_amount: float
    late_fees: float
    damage_charges: float
    insurance_selected: bool
    created_at: datetime

    class Config:
        from_attributes = True


class RentalListResponse(BaseModel):
    items: list[RentalResponse]
    total: int
    page: int
    limit: int
    has_next: bool


class RentalReturnRequest(BaseModel):
    condition_notes: str = Field(..., min_length=10, max_length=1000)
    photos: List[str] = []
    late_fees_waived: bool = False
    waiver_reason: Optional[str] = None


class RentalExtensionRequest(BaseModel):
    new_end_date: date
    reason: Optional[str] = None


class AvailabilityCheckRequest(BaseModel):
    product_id: uuid.UUID
    start_date: date
    end_date: date


class AvailabilityCheckResponse(BaseModel):
    available: bool
    conflicts: List[dict] = []
    suggestions: List[dict] = []
