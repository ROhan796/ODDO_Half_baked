# app/schemas/stock.py
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import uuid


class StockLocationCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    code: str = Field(..., min_length=2, max_length=50)
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    contact_person: Optional[str] = None
    contact_phone: Optional[str] = None
    is_warehouse: bool = False


class StockLocationResponse(BaseModel):
    id: uuid.UUID
    name: str
    code: str
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    is_active: bool
    is_warehouse: bool
    created_at: datetime

    class Config:
        from_attributes = True


class StockMovementCreate(BaseModel):
    product_id: uuid.UUID
    from_location_id: Optional[uuid.UUID] = None
    to_location_id: Optional[uuid.UUID] = None
    movement_type: str = Field(..., pattern="^(in|out|transfer|adjustment|return)$")
    quantity: int = Field(..., gt=0)
    reference_type: Optional[str] = None
    reference_id: Optional[uuid.UUID] = None
    notes: Optional[str] = None


class StockMovementResponse(BaseModel):
    id: uuid.UUID
    product_id: uuid.UUID
    from_location_id: Optional[uuid.UUID] = None
    to_location_id: Optional[uuid.UUID] = None
    movement_type: str
    quantity: int
    performed_by: uuid.UUID
    created_at: datetime

    class Config:
        from_attributes = True


class StockLevelResponse(BaseModel):
    id: uuid.UUID
    product_id: uuid.UUID
    location_id: uuid.UUID
    quantity: int
    reserved: int
    available: int
    min_stock: int
    last_counted_at: Optional[datetime] = None

    class Config:
        from_attributes = True
