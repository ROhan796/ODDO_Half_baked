# app/services/rental_service.py
from uuid import UUID
from datetime import datetime, date, timezone, timedelta
from decimal import Decimal
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status

from app.models.rental import Rental, RentalStatus, RentalExtension
from app.models.product import Product, ProductStatus
from app.models.deposit import SecurityDeposit, DepositStatus
from app.models.availability import AvailabilityBlock, BlockType
from app.models.fee import LateFee, LateFeeStatus


class RentalService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_rental(self, data: dict, created_by: UUID) -> Rental:
        product = await self.db.get(Product, data["product_id"])
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found",
            )

        if product.status != ProductStatus.AVAILABLE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Product is not available for rental",
            )

        daily_rate = Decimal(str(data.get("daily_rate", product.purchase_price or 0)))
        start = data["start_date"]
        end = data["end_date"]
        days = (end - start).days or 1
        total_amount = daily_rate * days

        deposit_pct = product.deposit_percentage / Decimal("100")
        deposit_amount = total_amount * deposit_pct

        rental = Rental(
            customer_id=data["customer_id"],
            product_id=data["product_id"],
            quotation_id=data.get("quotation_id"),
            rental_type=data.get("rental_type", "daily"),
            start_date=start,
            end_date=end,
            daily_rate=daily_rate,
            total_amount=total_amount,
            deposit_amount=deposit_amount,
            insurance_selected=data.get("insurance_selected", False),
            insurance_amount=data.get("insurance_amount", 0),
            delivery_address=data.get("delivery_address"),
            special_requirements=data.get("special_requirements"),
            condition_at_checkout=data.get("condition_at_checkout"),
            checkout_photos=data.get("checkout_photos"),
        )
        self.db.add(rental)
        await self.db.flush()

        deposit = SecurityDeposit(
            rental_id=rental.id,
            customer_id=data["customer_id"],
            amount=deposit_amount,
            status=DepositStatus.PENDING,
        )
        self.db.add(deposit)
        await self.db.flush()

        return rental

    async def get_rental(self, rental_id: UUID) -> Rental:
        result = await self.db.execute(
            select(Rental)
            .options(selectinload(Rental.customer), selectinload(Rental.product))
            .where(Rental.id == rental_id)
        )
        rental = result.scalar_one_or_none()
        if not rental:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Rental not found",
            )
        return rental

    async def list_rentals(
        self,
        page: int = 1,
        limit: int = 20,
        rental_status: str = None,
        customer_id: UUID = None,
    ) -> dict:
        query = select(Rental)

        if rental_status:
            query = query.where(Rental.status == rental_status)

        if customer_id:
            query = query.where(Rental.customer_id == customer_id)

        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()

        query = query.offset((page - 1) * limit).limit(limit)
        result = await self.db.execute(query)
        rentals = result.scalars().all()

        return {
            "items": rentals,
            "total": total,
            "page": page,
            "limit": limit,
            "pages": (total + limit - 1) // limit,
        }

    async def confirm_rental(self, rental_id: UUID, confirmed_by: UUID) -> Rental:
        rental = await self.get_rental(rental_id)

        if rental.status != RentalStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot confirm rental in {rental.status.value} status",
            )

        rental.status = RentalStatus.CONFIRMED
        rental.confirmed_by = confirmed_by
        rental.confirmed_at = datetime.now(timezone.utc)

        block = AvailabilityBlock(
            product_id=rental.product_id,
            block_type=BlockType.RENTAL,
            rental_id=rental.id,
            start_at=rental.start_date,
            end_at=rental.end_date,
            booked_by=rental.customer_id,
        )
        self.db.add(block)

        product = await self.db.get(Product, rental.product_id)
        if product:
            product.status = ProductStatus.RENTED
            product.current_holder_id = rental.customer_id
            product.current_rental_id = rental.id

        await self.db.flush()
        return rental

    async def process_return(
        self,
        rental_id: UUID,
        condition_notes: str = None,
        photos: str = None,
        processed_by: UUID = None,
    ) -> Rental:
        rental = await self.get_rental(rental_id)

        if rental.status not in (RentalStatus.ACTIVE, RentalStatus.OVERDUE):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot return rental in {rental.status.value} status",
            )

        today = date.today()
        rental.actual_return_date = today
        rental.status = RentalStatus.RETURNED
        rental.returned_to = processed_by
        rental.returned_at = datetime.now(timezone.utc)
        rental.condition_at_return = condition_notes
        rental.return_photos = photos

        if today > rental.end_date:
            days_late = (today - rental.end_date).days
            daily_late_fee = rental.daily_rate * Decimal("0.1")
            late_fee = daily_late_fee * days_late
            rental.late_fees = late_fee

            late_fee_record = LateFee(
                rental_id=rental.id,
                customer_id=rental.customer_id,
                days_overdue=days_late,
                daily_rate=daily_late_fee,
                total_amount=late_fee,
                status=LateFeeStatus.CALCULATED,
                calculated_at=datetime.now(timezone.utc),
            )
            self.db.add(late_fee_record)

        product = await self.db.get(Product, rental.product_id)
        if product:
            product.status = ProductStatus.AVAILABLE
            product.current_holder_id = None
            product.current_rental_id = None
            product.total_rentals = (product.total_rentals or 0) + 1

        await self.db.flush()
        return rental

    async def extend_rental(
        self, rental_id: UUID, new_end_date: date, extended_by: UUID
    ) -> RentalExtension:
        rental = await self.get_rental(rental_id)

        if rental.status not in (RentalStatus.CONFIRMED, RentalStatus.ACTIVE):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot extend rental in {rental.status.value} status",
            )

        if new_end_date <= rental.end_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="New end date must be after current end date",
            )

        extension_days = (new_end_date - rental.end_date).days
        additional_amount = rental.daily_rate * extension_days

        extension = RentalExtension(
            rental_id=rental.id,
            original_end_date=rental.end_date,
            new_end_date=new_end_date,
            extension_days=extension_days,
            additional_amount=additional_amount,
            requested_by=extended_by,
        )
        self.db.add(extension)
        await self.db.flush()
        await self.db.refresh(extension)

        return extension
