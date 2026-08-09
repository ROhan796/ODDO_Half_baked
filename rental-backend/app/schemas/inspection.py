# app/schemas/inspection.py
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal
import uuid


class FunctionalCheck(BaseModel):
    power_on: bool = False
    screen_display: bool = False
    buttons_controls: bool = False
    ports_connectivity: bool = False
    audio_speaker_mic: bool = False
    sensor_lens: bool = False


class AccessoryStatusItem(BaseModel):
    accessory_id: Optional[uuid.UUID] = None
    name: str
    present: bool = False
    condition: Optional[str] = None


class InspectionCreate(BaseModel):
    rental_id: uuid.UUID
    product_id: uuid.UUID
    inspection_type: str = Field(..., pattern="^(checkout|return)$")
    functional_check: Optional[FunctionalCheck] = None
    cosmetic_grade: Optional[str] = None
    overall_grade: Optional[str] = Field(None, pattern="^(excellent|good|fair|poor)$")
    accessories_status: Optional[List[AccessoryStatusItem]] = None
    damage_detected: bool = False
    damage_description: Optional[str] = None
    estimated_damage_cost: Optional[float] = None
    photos: List[str] = []
    before_photo: Optional[str] = None
    after_photo: Optional[str] = None


class InspectionResponse(BaseModel):
    id: uuid.UUID
    rental_id: uuid.UUID
    product_id: uuid.UUID
    inspector_id: uuid.UUID
    inspection_type: str
    functional_check: Optional[Dict[str, Any]] = None
    cosmetic_grade: Optional[str] = None
    overall_grade: Optional[str] = None
    accessories_status: Optional[List[Dict[str, Any]]] = None
    damage_detected: bool
    damage_description: Optional[str] = None
    estimated_damage_cost: Optional[float] = None
    photos: List[str] = []
    before_photo: Optional[str] = None
    after_photo: Optional[str] = None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class InspectionListResponse(BaseModel):
    items: List[InspectionResponse]
    total: int
    page: int
    limit: int
    has_next: bool
