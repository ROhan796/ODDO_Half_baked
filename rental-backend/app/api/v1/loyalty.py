# app/api/v1/loyalty.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional
import uuid
from datetime import datetime, timezone

from app.utils.database import get_read_db, get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.loyalty import LoyaltyPointsLedger, Referral, PointsTransactionType
from app.schemas.loyalty import (
    LoyaltyPointsResponse,
    LoyaltyPointsLedgerResponse,
    ReferralResponse,
    RedeemPointsRequest,
)

router = APIRouter()


@router.get("/points", response_model=LoyaltyPointsResponse)
async def get_points_balance(
    db: AsyncSession = Depends(get_read_db),
    current_user: User = Depends(get_current_user),
):
    """Get current user's points balance."""
    earned_result = await db.execute(
        select(func.coalesce(func.sum(LoyaltyPointsLedger.points), 0)).where(
            LoyaltyPointsLedger.user_id == current_user.id,
            LoyaltyPointsLedger.transaction_type.in_([
                PointsTransactionType.EARNED,
                PointsTransactionType.ADJUSTED,
                PointsTransactionType.REFERRAL,
            ]),
        )
    )
    lifetime_earned = earned_result.scalar()

    redeemed_result = await db.execute(
        select(func.coalesce(func.abs(func.sum(LoyaltyPointsLedger.points)), 0)).where(
            LoyaltyPointsLedger.user_id == current_user.id,
            LoyaltyPointsLedger.transaction_type == PointsTransactionType.REDEEMED,
        )
    )
    lifetime_redeemed = redeemed_result.scalar()

    return LoyaltyPointsResponse(
        balance=current_user.points_balance or 0,
        lifetime_earned=lifetime_earned,
        lifetime_redeemed=lifetime_redeemed,
    )


@router.get("/points/ledger", response_model=list[LoyaltyPointsLedgerResponse])
async def get_points_ledger(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_read_db),
    current_user: User = Depends(get_current_user),
):
    """Get points transaction history."""
    query = (
        select(LoyaltyPointsLedger)
        .where(LoyaltyPointsLedger.user_id == current_user.id)
        .order_by(LoyaltyPointsLedger.created_at.desc())
        .offset((page - 1) * limit)
        .limit(limit)
    )

    result = await db.execute(query)
    return result.scalars().all()


@router.post("/points/redeem")
async def redeem_points(
    data: RedeemPointsRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Redeem loyalty points."""
    if (current_user.points_balance or 0) < data.points:
        raise HTTPException(status_code=400, detail="Insufficient points balance")

    new_balance = current_user.points_balance - data.points
    current_user.points_balance = new_balance

    ledger_entry = LoyaltyPointsLedger(
        user_id=current_user.id,
        transaction_type=PointsTransactionType.REDEEMED,
        points=-data.points,
        balance_after=new_balance,
        reference_type=data.reference_type,
        reference_id=data.reference_id,
        description=f"Redeemed {data.points} points",
    )
    db.add(ledger_entry)

    return {"message": "Points redeemed successfully", "new_balance": new_balance}


@router.get("/referrals", response_model=list[ReferralResponse])
async def get_referrals(
    db: AsyncSession = Depends(get_read_db),
    current_user: User = Depends(get_current_user),
):
    """Get user's referrals."""
    query = (
        select(Referral)
        .where(Referral.referrer_id == current_user.id)
        .order_by(Referral.created_at.desc())
    )
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/referrals/{code}/validate")
async def validate_referral_code(
    code: str,
    db: AsyncSession = Depends(get_read_db),
    current_user: User = Depends(get_current_user),
):
    """Validate a referral code."""
    query = select(Referral).where(Referral.referral_code == code)
    result = await db.execute(query)
    referral = result.scalar_one_or_none()

    if not referral:
        raise HTTPException(status_code=404, detail="Invalid referral code")

    if referral.referrer_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot use your own referral code")

    if referral.status == "completed":
        raise HTTPException(status_code=400, detail="Referral code already used")

    if referral.expires_at and referral.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Referral code has expired")

    return {"valid": True, "referral_code": code, "referrer_id": referral.referrer_id}
