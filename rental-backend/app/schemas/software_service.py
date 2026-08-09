# app/schemas/software_service.py
from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime
import uuid


class SoftwareServiceCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    slug: str = Field(..., min_length=2, max_length=255)
    category_id: Optional[uuid.UUID] = None
    description: Optional[str] = None
    short_description: Optional[str] = Field(None, max_length=500)
    vendor: Optional[str] = None
    version: Optional[str] = None
    license_type: str = Field(..., pattern="^(saas_subscription|node_locked|floating|cloud_credit|api_quota)$")
    delivery_method: str = Field(..., pattern="^(email_license_key|cloud_access|api_key|download_link)$")
    hourly_rate: Optional[float] = None
    daily_rate: Optional[float] = None
    weekly_rate: Optional[float] = None
    monthly_rate: Optional[float] = None
    annual_rate: Optional[float] = None
    currency: str = "INR"
    max_concurrent_users: int = 1
    max_seats: Optional[int] = None
    requires_vpn: bool = False
    ip_whitelist: List[str] = []
    system_requirements: Optional[str] = None
    api_endpoint: Optional[str] = None
    documentation_url: Optional[str] = None
    support_email: Optional[str] = None
    metadata: dict = {}
    tags: List[str] = []
    images: List[str] = []
    thumbnail_url: Optional[str] = None
    is_featured: bool = False


class SoftwareServiceUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    short_description: Optional[str] = None
    vendor: Optional[str] = None
    version: Optional[str] = None
    hourly_rate: Optional[float] = None
    daily_rate: Optional[float] = None
    weekly_rate: Optional[float] = None
    monthly_rate: Optional[float] = None
    annual_rate: Optional[float] = None
    max_concurrent_users: Optional[int] = None
    max_seats: Optional[int] = None
    requires_vpn: Optional[bool] = None
    ip_whitelist: Optional[List[str]] = None
    system_requirements: Optional[str] = None
    api_endpoint: Optional[str] = None
    documentation_url: Optional[str] = None
    support_email: Optional[str] = None
    metadata: Optional[dict] = None
    tags: Optional[List[str]] = None
    images: Optional[List[str]] = None
    thumbnail_url: Optional[str] = None
    status: Optional[str] = None
    is_featured: Optional[bool] = None


class SoftwareServiceResponse(BaseModel):
    id: uuid.UUID
    name: str
    slug: str
    category_id: Optional[uuid.UUID] = None
    description: Optional[str] = None
    short_description: Optional[str] = None
    vendor: Optional[str] = None
    version: Optional[str] = None
    license_type: str
    delivery_method: str
    hourly_rate: Optional[float] = None
    daily_rate: Optional[float] = None
    weekly_rate: Optional[float] = None
    monthly_rate: Optional[float] = None
    annual_rate: Optional[float] = None
    currency: str
    max_concurrent_users: int
    max_seats: Optional[int] = None
    requires_vpn: bool
    ip_whitelist: List[str] = []
    system_requirements: Optional[str] = None
    api_endpoint: Optional[str] = None
    documentation_url: Optional[str] = None
    support_email: Optional[str] = None
    metadata: dict = {}
    tags: List[str] = []
    images: List[str] = []
    thumbnail_url: Optional[str] = None
    status: str
    is_featured: bool
    created_at: datetime

    class Config:
        from_attributes = True


class SoftwareServiceListResponse(BaseModel):
    items: list[SoftwareServiceResponse]
    total: int
    page: int
    limit: int
    has_next: bool


class SoftwareRentalCreate(BaseModel):
    software_service_id: uuid.UUID
    start_at: datetime
    end_at: datetime
    usage_limit: Optional[float] = None

    @classmethod
    def validate_dates(cls, v, info):
        if "start_at" in info.data and v <= info.data["start_at"]:
            raise ValueError("end_at must be after start_at")
        return v


class SoftwareRentalResponse(BaseModel):
    id: uuid.UUID
    rental_number: str
    customer_id: uuid.UUID
    software_service_id: uuid.UUID
    start_at: datetime
    end_at: datetime
    actual_access_revoked_at: Optional[datetime] = None
    license_key: Optional[str] = None
    license_server_url: Optional[str] = None
    rental_fee: float
    security_deposit_amount: float
    currency: str
    usage_metric: Optional[str] = None
    usage_limit: Optional[float] = None
    usage_current: float
    status: str
    provisioned_at: Optional[datetime] = None
    access_granted_at: Optional[datetime] = None
    access_revoked_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class SoftwareRentalListResponse(BaseModel):
    items: list[SoftwareRentalResponse]
    total: int
    page: int
    limit: int
    has_next: bool


class SoftwareUsageLogResponse(BaseModel):
    id: uuid.UUID
    software_rental_id: uuid.UUID
    metric_type: str
    quantity: float
    metadata: dict = {}
    created_at: datetime

    class Config:
        from_attributes = True
