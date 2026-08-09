# app/schemas/address.py
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import uuid


class AddressCreate(BaseModel):
    label: str = Field("Home", max_length=50)
    street: str = Field(..., min_length=5)
    city: str = Field(..., min_length=2, max_length=100)
    state: str = Field(..., min_length=2, max_length=100)
    pincode: str = Field(..., min_length=4, max_length=10)
    country: str = Field("India", max_length=100)
    is_default: bool = False
    contact_name: Optional[str] = None
    contact_phone: Optional[str] = None


class AddressUpdate(BaseModel):
    label: Optional[str] = Field(None, max_length=50)
    street: Optional[str] = Field(None, min_length=5)
    city: Optional[str] = Field(None, min_length=2, max_length=100)
    state: Optional[str] = Field(None, min_length=2, max_length=100)
    pincode: Optional[str] = Field(None, min_length=4, max_length=10)
    country: Optional[str] = Field(None, max_length=100)
    is_default: Optional[bool] = None
    contact_name: Optional[str] = None
    contact_phone: Optional[str] = None


class AddressResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    label: str
    street: str
    city: str
    state: str
    pincode: str
    country: str
    is_default: bool
    contact_name: Optional[str] = None
    contact_phone: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class AddressListResponse(BaseModel):
    items: list[AddressResponse]
    total: int
