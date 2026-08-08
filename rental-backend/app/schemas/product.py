# app/schemas/product.py
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date
import uuid


class ProductCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    slug: str = Field(..., min_length=2, max_length=255)
    category_id: uuid.UUID
    description: Optional[str] = None
    short_description: Optional[str] = Field(None, max_length=500)
    serial_number: Optional[str] = None
    sku: Optional[str] = None
    daily_rate: float = Field(..., gt=0)
    deposit_percentage: float = Field(30.0, ge=0, le=100)
    late_fee_rate: Optional[float] = None
    min_rental_duration: int = Field(1, ge=1)
    max_rental_duration: Optional[int] = None
    is_insured: bool = False
    images: List[str] = []
    tags: List[str] = []
    metadata_: Optional[dict] = Field(None, alias="metadata")


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    description: Optional[str] = None
    short_description: Optional[str] = Field(None, max_length=500)
    daily_rate: Optional[float] = Field(None, gt=0)
    deposit_percentage: Optional[float] = Field(None, ge=0, le=100)
    late_fee_rate: Optional[float] = None
    status: Optional[str] = None
    is_insured: Optional[bool] = None
    images: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    is_featured: Optional[bool] = None


class ProductResponse(BaseModel):
    id: uuid.UUID
    name: str
    slug: str
    category_id: uuid.UUID
    description: Optional[str] = None
    short_description: Optional[str] = None
    serial_number: Optional[str] = None
    qr_code: Optional[str] = None
    sku: Optional[str] = None
    status: str
    condition_rating: int
    daily_rate: float
    deposit_percentage: float
    late_fee_rate: Optional[float] = None
    is_insured: bool
    images: List[str] = []
    thumbnail_url: Optional[str] = None
    tags: List[str] = []
    total_rentals: int
    is_featured: bool
    created_at: datetime

    class Config:
        from_attributes = True


class ProductListResponse(BaseModel):
    items: list[ProductResponse]
    total: int
    page: int
    limit: int
    has_next: bool


class CategoryCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    slug: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = None
    parent_id: Optional[uuid.UUID] = None
    icon_url: Optional[str] = None


class CategoryResponse(BaseModel):
    id: uuid.UUID
    name: str
    slug: str
    description: Optional[str] = None
    parent_id: Optional[uuid.UUID] = None
    icon_url: Optional[str] = None
    is_active: bool
    sort_order: int
    created_at: datetime

    class Config:
        from_attributes = True
