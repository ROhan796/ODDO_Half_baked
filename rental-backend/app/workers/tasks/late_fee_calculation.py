# app/workers/tasks/late_fee_calculation.py
import logging
from datetime import date, datetime, timezone
from decimal import Decimal

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.rental import Rental, RentalStatus
from app.models.fee import LateFee, LateFeeStatus
from app.models.product import Product

logger = logging.getLogger(__name__)


async def calculate_late_fees(ctx: dict):
    session_factory = ctx["session_factory"]
    async with session_factory() as db:
        try:
            today = date.today()

            result = await db.execute(
                select(Rental).where(
                    and_(
                        Rental.status == RentalStatus.OVERDUE,
                        Rental.end_date < today,
                    )
                )
            )
            overdue_rentals = result.scalars().all()

            calculated_count = 0
            for rental in overdue_rentals:
                days_overdue = (today - rental.end_date).days

                product_result = await db.execute(
                    select(Product).where(Product.id == rental.product_id)
                )
                product = product_result.scalar_one_or_none()

                if product and product.late_fee_rate:
                    daily_late_fee = product.late_fee_rate
                else:
                    daily_late_fee = rental.daily_rate * Decimal("0.10")

                existing_result = await db.execute(
                    select(LateFee).where(
                        and_(
                            LateFee.rental_id == rental.id,
                            LateFee.status.in_([
                                LateFeeStatus.CALCULATED,
                                LateFeeStatus.APPLIED,
                            ]),
                        )
                    )
                )
                existing_fee = existing_result.scalar_one_or_none()

                if existing_fee:
                    existing_fee.days_overdue = Decimal(str(days_overdue))
                    existing_fee.daily_rate = daily_late_fee
                    existing_fee.total_amount = daily_late_fee * days_overdue
                    existing_fee.calculated_at = datetime.now(timezone.utc)
                else:
                    late_fee = LateFee(
                        rental_id=rental.id,
                        customer_id=rental.customer_id,
                        days_overdue=Decimal(str(days_overdue)),
                        daily_rate=daily_late_fee,
                        total_amount=daily_late_fee * days_overdue,
                        status=LateFeeStatus.CALCULATED,
                        calculated_at=datetime.now(timezone.utc),
                    )
                    db.add(late_fee)

                rental.late_fees = daily_late_fee * days_overdue
                calculated_count += 1

            await db.commit()
            logger.info(f"Calculated late fees for {calculated_count} rentals")
            return {"calculated_count": calculated_count}

        except Exception as e:
            await db.rollback()
            logger.error(f"Error calculating late fees: {e}")
            raise
