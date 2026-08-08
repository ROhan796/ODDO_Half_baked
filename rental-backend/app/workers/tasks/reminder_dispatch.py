# app/workers/tasks/reminder_dispatch.py
import logging
from datetime import date, datetime, timezone, timedelta

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.rental import Rental, RentalStatus
from app.models.invoice import Invoice, InvoiceStatus
from app.models.notification import (
    Notification,
    NotificationType,
    NotificationChannel,
    NotificationStatus,
)

logger = logging.getLogger(__name__)


async def send_rental_reminders(ctx: dict):
    session_factory = ctx["session_factory"]
    async with session_factory() as db:
        try:
            today = date.today()
            reminder_date = today + timedelta(days=3)

            result = await db.execute(
                select(Rental).where(
                    and_(
                        Rental.status.in_([
                            RentalStatus.CONFIRMED,
                            RentalStatus.ACTIVE,
                        ]),
                        Rental.end_date == reminder_date,
                    )
                )
            )
            rentals_ending_soon = result.scalars().all()

            sent_count = 0
            for rental in rentals_ending_soon:
                days_remaining = (rental.end_date - today).days

                notification = Notification(
                    user_id=rental.customer_id,
                    type=NotificationType.REMINDER,
                    channel=NotificationChannel.IN_APP,
                    title="Rental Ending Soon",
                    message=(
                        f"Your rental is ending in {days_remaining} day(s) on "
                        f"{rental.end_date}. Please ensure timely return."
                    ),
                    data={
                        "rental_id": str(rental.id),
                        "end_date": rental.end_date.isoformat(),
                        "days_remaining": days_remaining,
                    },
                    status=NotificationStatus.PENDING,
                )
                db.add(notification)
                sent_count += 1

            await db.commit()
            logger.info(f"Sent {sent_count} rental reminders")
            return {"reminders_sent": sent_count}

        except Exception as e:
            await db.rollback()
            logger.error(f"Error sending rental reminders: {e}")
            raise


async def send_payment_reminders(ctx: dict):
    session_factory = ctx["session_factory"]
    async with session_factory() as db:
        try:
            today = date.today()

            result = await db.execute(
                select(Invoice).where(
                    and_(
                        Invoice.status.in_([
                            InvoiceStatus.PENDING,
                            InvoiceStatus.OVERDUE,
                        ]),
                        Invoice.due_date <= datetime.now(timezone.utc),
                    )
                )
            )
            overdue_invoices = result.scalars().all()

            sent_count = 0
            for invoice in overdue_invoices:
                if invoice.status != InvoiceStatus.OVERDUE:
                    invoice.status = InvoiceStatus.OVERDUE

                notification = Notification(
                    user_id=invoice.customer_id,
                    type=NotificationType.PAYMENT,
                    channel=NotificationChannel.IN_APP,
                    title="Payment Overdue",
                    message=(
                        f"Invoice {invoice.invoice_number} for "
                        f"₹{invoice.total_amount} is overdue. "
                        f"Please make payment to avoid late fees."
                    ),
                    data={
                        "invoice_id": str(invoice.id),
                        "invoice_number": invoice.invoice_number,
                        "amount": str(invoice.total_amount),
                        "due_date": invoice.due_date.isoformat(),
                    },
                    status=NotificationStatus.PENDING,
                )
                db.add(notification)
                sent_count += 1

            await db.commit()
            logger.info(f"Sent {sent_count} payment reminders")
            return {"payment_reminders_sent": sent_count}

        except Exception as e:
            await db.rollback()
            logger.error(f"Error sending payment reminders: {e}")
            raise
