# app/workers/tasks/overdue_detection.py
import logging
from datetime import date, datetime, timezone
from decimal import Decimal

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.rental import Rental, RentalStatus
from app.models.fee import LateFee, LateFeeStatus
from app.models.notification import (
    Notification,
    NotificationType,
    NotificationChannel,
    NotificationStatus,
)

logger = logging.getLogger(__name__)


async def detect_overdue_rentals(ctx: dict):
    session_factory = ctx["session_factory"]
    async with session_factory() as db:
        try:
            today = date.today()

            result = await db.execute(
                select(Rental).where(
                    and_(
                        Rental.status == RentalStatus.ACTIVE,
                        Rental.end_date < today,
                    )
                )
            )
            overdue_rentals = result.scalars().all()

            updated_count = 0
            for rental in overdue_rentals:
                rental.status = RentalStatus.OVERDUE

                days_overdue = (today - rental.end_date).days
                daily_late_fee = rental.daily_rate * Decimal("0.10")
                total_late_fee = daily_late_fee * days_overdue

                existing_fee = await db.execute(
                    select(LateFee).where(
                        and_(
                            LateFee.rental_id == rental.id,
                            LateFee.status != LateFeeStatus.WAIVED,
                        )
                    )
                )
                existing = existing_fee.scalar_one_or_none()

                if not existing:
                    late_fee = LateFee(
                        rental_id=rental.id,
                        customer_id=rental.customer_id,
                        days_overdue=Decimal(str(days_overdue)),
                        daily_rate=daily_late_fee,
                        total_amount=total_late_fee,
                        status=LateFeeStatus.CALCULATED,
                        calculated_at=datetime.now(timezone.utc),
                    )
                    db.add(late_fee)

                notification = Notification(
                    user_id=rental.customer_id,
                    type=NotificationType.RENTAL,
                    channel=NotificationChannel.IN_APP,
                    title="Rental Overdue",
                    message=(
                        f"Your rental for product is overdue by {days_overdue} day(s). "
                        f"Please return the item as soon as possible to avoid additional charges."
                    ),
                    data={
                        "rental_id": str(rental.id),
                        "days_overdue": days_overdue,
                        "late_fee": str(total_late_fee),
                    },
                    status=NotificationStatus.PENDING,
                )
                db.add(notification)

                updated_count += 1

            await db.commit()
            logger.info(f"Detected {updated_count} overdue rentals")
            return {"overdue_count": updated_count}

        except Exception as e:
            await db.rollback()
            logger.error(f"Error detecting overdue rentals: {e}")
            raise
