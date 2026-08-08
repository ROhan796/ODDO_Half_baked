# app/workers/tasks/trust_score_recalculation.py
import logging
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, TrustScoreHistory
from app.models.rental import Rental, RentalStatus

logger = logging.getLogger(__name__)


def calculate_trust_score(
    total_rentals: int,
    on_time_returns: int,
    total_late_fees: float,
    disputes_filed: int,
    disputes_won: int,
) -> int:
    score = 50

    if total_rentals > 0:
        on_time_ratio = on_time_returns / total_rentals
        score += int(on_time_ratio * 30)

    if total_rentals >= 3:
        score += 5
    if total_rentals >= 10:
        score += 5
    if total_rentals >= 25:
        score += 5

    if total_late_fees > 0:
        penalty = min(int(total_late_fees / 100), 20)
        score -= penalty

    if disputes_filed > 0:
        if disputes_won > 0:
            win_ratio = disputes_won / disputes_filed
            score += int(win_ratio * 5)
        else:
            score -= min(disputes_filed * 3, 15)

    return max(0, min(100, score))


def trust_tier_from_score(score: int) -> str:
    if score >= 80:
        return "platinum"
    elif score >= 60:
        return "gold"
    elif score >= 40:
        return "silver"
    elif score >= 20:
        return "bronze"
    return "unverified"


async def recalculate_trust_scores(ctx: dict):
    session_factory = ctx["session_factory"]
    async with session_factory() as db:
        try:
            result = await db.execute(
                select(User).where(User.blacklisted == False)
            )
            users = result.scalars().all()

            updated_count = 0
            for user in users:
                rental_result = await db.execute(
                    select(
                        func.count(Rental.id).label("total"),
                        func.count(Rental.id).filter(
                            Rental.status == RentalStatus.RETURNED,
                            Rental.actual_return_date <= Rental.end_date,
                        ).label("on_time"),
                        func.coalesce(
                            func.sum(Rental.late_fees), 0
                        ).label("total_late_fees"),
                    ).where(Rental.customer_id == user.id)
                )
                rental_stats = rental_result.one()

                total_rentals = rental_stats.total or 0
                on_time_returns = rental_stats.on_time or 0
                total_late_fees = float(rental_stats.total_late_fees or 0)

                new_score = calculate_trust_score(
                    total_rentals=total_rentals,
                    on_time_returns=on_time_returns,
                    total_late_fees=total_late_fees,
                    disputes_filed=0,
                    disputes_won=0,
                )
                new_tier = trust_tier_from_score(new_score)

                if user.trust_score != new_score or user.trust_tier != new_tier:
                    history = TrustScoreHistory(
                        user_id=user.id,
                        previous_score=user.trust_score or 0,
                        new_score=new_score,
                        change_amount=new_score - (user.trust_score or 0),
                        reason="scheduled_recalculation",
                    )
                    db.add(history)

                    user.trust_score = new_score
                    user.trust_tier = new_tier
                    updated_count += 1

            await db.commit()
            logger.info(f"Recalculated trust scores for {updated_count} users")
            return {"updated_count": updated_count}

        except Exception as e:
            await db.rollback()
            logger.error(f"Error recalculating trust scores: {e}")
            raise
