# app/schemas/loyalty.py
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import uuid


class LoyaltyPointsResponse(BaseModel):
    balance: int
    lifetime_earned: int
    lifetime_redeemed: int


class LoyaltyPointsLedgerResponse(BaseModel):
    id: uuid.UUID
    transaction_type: str
    points: int
    balance_after: int
    description: Optional[str] = None
    reference_type: Optional[str] = None
    reference_id: Optional[uuid.UUID] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ReferralResponse(BaseModel):
    id: uuid.UUID
    referral_code: str
    status: str
    referrer_bonus_points: int
    referred_bonus_points: int
    completed_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class RedeemPointsRequest(BaseModel):
    points: int = Field(..., gt=0)
    reference_type: str
    reference_id: uuid.UUID
