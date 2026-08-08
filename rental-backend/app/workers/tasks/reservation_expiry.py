# app/workers/tasks/reservation_expiry.py
import logging
from datetime import datetime, timezone

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.availability import Reservation, ReservationStatus

logger = logging.getLogger(__name__)


async def expire_reservations(ctx: dict):
    session_factory = ctx["session_factory"]
    async with session_factory() as db:
        try:
            now = datetime.now(timezone.utc)

            result = await db.execute(
                select(Reservation).where(
                    and_(
                        Reservation.status.in_([
                            ReservationStatus.PENDING,
                            ReservationStatus.CONFIRMED,
                        ]),
                        Reservation.expires_at < now,
                    )
                )
            )
            expired_reservations = result.scalars().all()

            expired_count = 0
            for reservation in expired_reservations:
                reservation.status = ReservationStatus.EXPIRED
                expired_count += 1

            await db.commit()
            logger.info(f"Expired {expired_count} reservations")
            return {"expired_count": expired_count}

        except Exception as e:
            await db.rollback()
            logger.error(f"Error expiring reservations: {e}")
            raise
