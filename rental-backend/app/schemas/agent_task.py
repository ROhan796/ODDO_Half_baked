# app/schemas/agent_task.py
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
import uuid


class AgentTaskCreate(BaseModel):
    rental_id: uuid.UUID
    agent_id: Optional[uuid.UUID] = None
    task_type: str = Field(..., pattern="^(delivery|pickup|inspection|return)$")
    address: Optional[str] = None
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    product_name: Optional[str] = None
    gps_lat: Optional[float] = None
    gps_lng: Optional[float] = None
    notes: Optional[str] = None


class AgentTaskUpdate(BaseModel):
    agent_id: Optional[uuid.UUID] = None
    status: Optional[str] = Field(None, pattern="^(pending|confirmed|active|overdue|completed)$")
    address: Optional[str] = None
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    notes: Optional[str] = None
    gps_lat: Optional[float] = None
    gps_lng: Optional[float] = None


class AgentTaskResponse(BaseModel):
    id: uuid.UUID
    rental_id: uuid.UUID
    agent_id: Optional[uuid.UUID] = None
    task_type: str
    status: str
    address: Optional[str] = None
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    product_name: Optional[str] = None
    gps_lat: Optional[float] = None
    gps_lng: Optional[float] = None
    notes: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class AgentTaskListResponse(BaseModel):
    items: List[AgentTaskResponse]
    total: int
    page: int
    limit: int
    has_next: bool


class AgentCreate(BaseModel):
    user_id: uuid.UUID
    location_hub: Optional[str] = None


class AgentResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    status: str
    location_hub: Optional[str] = None
    active_task_id: Optional[uuid.UUID] = None
    created_at: datetime

    class Config:
        from_attributes = True
