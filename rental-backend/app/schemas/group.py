# app/schemas/group.py
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import uuid


class GroupCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    description: Optional[str] = None
    max_members: int = Field(20, ge=2, le=20)
    joint_liability: bool = True


class GroupUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    description: Optional[str] = None
    status: Optional[str] = None


class GroupResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: Optional[str] = None
    leader_id: uuid.UUID
    trust_score: float
    trust_tier: str
    status: str
    max_members: int
    current_member_count: int
    joint_liability: bool
    created_at: datetime

    class Config:
        from_attributes = True


class GroupMemberAdd(BaseModel):
    user_id: uuid.UUID
    deposit_share_pct: float = Field(0, ge=0, le=100)


class GroupMemberResponse(BaseModel):
    id: uuid.UUID
    group_id: uuid.UUID
    user_id: uuid.UUID
    role: str
    status: str
    deposit_share_pct: float
    deposit_share_amount: float
    joined_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class GroupVoteCreate(BaseModel):
    rental_id: Optional[uuid.UUID] = None
    vote_type: str = Field(..., pattern="^(extension|dispute|dissolve)$")
    reason: Optional[str] = None


class GroupVoteResponse(BaseModel):
    id: uuid.UUID
    group_id: uuid.UUID
    vote_type: str
    requested_by: uuid.UUID
    status: str
    votes_for: int
    votes_against: int
    expires_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True


class GroupVoteCast(BaseModel):
    vote: str = Field(..., pattern="^(approve|reject)$")
