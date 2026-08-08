# app/services/loyalty_service.py
from uuid import UUID
from datetime import datetime, timezone, timedelta
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.models.loyalty import LoyaltyPointsLedger, Referral, PointsTransactionType
from app.models.user import User


class LoyaltyService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_points_balance(self, user_id: UUID) -> dict:
        user = await self.db.get(User, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        return {
            "user_id": user_id,
            "balance": user.points_balance or 0,
        }

    async def get_points_ledger(
        self, user_id: UUID, page: int = 1, limit: int = 20
    ) -> dict:
        query = select(LoyaltyPointsLedger).where(
            LoyaltyPointsLedger.user_id == user_id
        )

        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()

        query = query.order_by(LoyaltyPointsLedger.created_at.desc())
        query = query.offset((page - 1) * limit).limit(limit)
        result = await self.db.execute(query)
        transactions = result.scalars().all()

        return {
            "items": transactions,
            "total": total,
            "page": page,
            "limit": limit,
            "pages": (total + limit - 1) // limit,
        }

    async def redeem_points(
        self,
        user_id: UUID,
        points: int,
        reference_type: str,
        reference_id: UUID,
    ) -> LoyaltyPointsLedger:
        user = await self.db.get(User, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        if (user.points_balance or 0) < points:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Insufficient points balance",
            )

        user.points_balance = (user.points_balance or 0) - points
        new_balance = user.points_balance

        ledger = LoyaltyPointsLedger(
            user_id=user_id,
            transaction_type=PointsTransactionType.REDEEMED,
            points=points,
            balance_after=new_balance,
            reference_type=reference_type,
            reference_id=reference_id,
            description=f"Redeemed {points} points for {reference_type}",
        )
        self.db.add(ledger)
        await self.db.flush()
        await self.db.refresh(ledger)
        return ledger

    async def get_referrals(self, user_id: UUID) -> list:
        result = await self.db.execute(
            select(Referral).where(Referral.referrer_id == user_id)
        )
        referrals = result.scalars().all()
        return referrals

    async def validate_referral_code(self, code: str) -> dict:
        result = await self.db.execute(
            select(User).where(User.referral_code == code)
        )
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invalid referral code",
            )

        return {
            "valid": True,
            "referrer_id": user.id,
            "referrer_name": user.name,
        }

    async def award_referral_bonus(
        self, referrer_id: UUID, referred_id: UUID
    ) -> dict:
        referrer = await self.db.get(User, referrer_id)
        referred = await self.db.get(User, referred_id)

        if not referrer or not referred:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        referrer_bonus = 500
        referred_bonus = 250

        referrer.points_balance = (referrer.points_balance or 0) + referrer_bonus
        referred.points_balance = (referred.points_balance or 0) + referred_bonus

        referrer_ledger = LoyaltyPointsLedger(
            user_id=referrer_id,
            transaction_type=PointsTransactionType.REFERRAL,
            points=referrer_bonus,
            balance_after=referrer.points_balance,
            reference_type="referral",
            reference_id=referred_id,
            description=f"Referral bonus for referring {referred.name}",
        )
        self.db.add(referrer_ledger)

        referred_ledger = LoyaltyPointsLedger(
            user_id=referred_id,
            transaction_type=PointsTransactionType.REFERRAL,
            points=referred_bonus,
            balance_after=referred.points_balance,
            reference_type="referral",
            reference_id=referrer_id,
            description=f"Welcome bonus via referral from {referrer.name}",
        )
        self.db.add(referred_ledger)

        referral_record = await self.db.execute(
            select(Referral).where(
                Referral.referrer_id == referrer_id,
                Referral.referred_id == referred_id,
            )
        )
        referral = referral_record.scalar_one_or_none()
        if referral:
            referral.status = "completed"
            referral.referrer_bonus_points = referrer_bonus
            referral.referred_bonus_points = referred_bonus
            referral.completed_at = datetime.now(timezone.utc)

        await self.db.flush()

        return {
            "referrer_bonus": referrer_bonus,
            "referred_bonus": referred_bonus,
            "referrer_new_balance": referrer.points_balance,
            "referred_new_balance": referred.points_balance,
        }
