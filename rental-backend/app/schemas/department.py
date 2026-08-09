# app/schemas/department.py
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import uuid


class DepartmentCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    description: Optional[str] = Field(None, max_length=500)
    head_user_id: Optional[uuid.UUID] = None
    budget_limit: Optional[int] = None


class DepartmentUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    description: Optional[str] = Field(None, max_length=500)
    head_user_id: Optional[uuid.UUID] = None
    budget_limit: Optional[int] = None
    is_active: Optional[bool] = None


class DepartmentMemberUpdate(BaseModel):
    add_members: List[uuid.UUID] = []
    remove_members: List[uuid.UUID] = []


class DepartmentResponse(BaseModel):
    id: uuid.UUID
    enterprise_id: uuid.UUID
    name: str
    description: Optional[str] = None
    head_user_id: Optional[uuid.UUID] = None
    member_ids: List[uuid.UUID] = []
    budget_limit: Optional[int] = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class DepartmentListResponse(BaseModel):
    items: List[DepartmentResponse]
    total: int
