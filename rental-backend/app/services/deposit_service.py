# app/services/deposit_service.py
from uuid import UUID
from datetime import datetime, timezone
from decimal import Decimal
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.models.deposit import SecurityDeposit, DepositDeduction, DepositStatus


class DepositService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_deposit(
        self, rental_id: UUID, customer_id: UUID, amount: Decimal
    ) -> SecurityDeposit:
        existing = await self.db.execute(
            select(SecurityDeposit).where(SecurityDeposit.rental_id == rental_id)
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Deposit already exists for this rental",
            )

        deposit = SecurityDeposit(
            rental_id=rental_id,
            customer_id=customer_id,
            amount=amount,
            status=DepositStatus.PENDING,
        )
        self.db.add(deposit)
        await self.db.flush()
        await self.db.refresh(deposit)
        return deposit

    async def get_deposit(self, rental_id: UUID) -> SecurityDeposit:
        result = await self.db.execute(
            select(SecurityDeposit).where(SecurityDeposit.rental_id == rental_id)
        )
        deposit = result.scalar_one_or_none()
        if not deposit:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Deposit not found for this rental",
            )
        return deposit

    async def settle_deposit(self, deposit_id: UUID) -> SecurityDeposit:
        result = await self.db.execute(
            select(SecurityDeposit).where(SecurityDeposit.id == deposit_id)
        )
        deposit = result.scalar_one_or_none()
        if not deposit:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Deposit not found",
            )

        deduction_result = await self.db.execute(
            select(DepositDeduction).where(DepositDeduction.deposit_id == deposit_id)
        )
        deductions = deduction_result.scalars().all()

        total_deductions = sum(d.amount for d in deductions)
        refund_amount = deposit.amount - total_deductions

        deposit.refund_amount = max(refund_amount, Decimal("0"))
        deposit.settled_at = datetime.now(timezone.utc)

        if total_deductions > 0:
            deposit.status = DepositStatus.PARTIALLY_DEDUCTED
        else:
            deposit.status = DepositStatus.REFUNDED

        deposit.refund_at = datetime.now(timezone.utc)

        await self.db.flush()
        await self.db.refresh(deposit)
        return deposit

    async def add_deduction(self, deposit_id: UUID, data: dict) -> DepositDeduction:
        result = await self.db.execute(
            select(SecurityDeposit).where(SecurityDeposit.id == deposit_id)
        )
        deposit = result.scalar_one_or_none()
        if not deposit:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Deposit not found",
            )

        deduction = DepositDeduction(
            deposit_id=deposit_id,
            amount=Decimal(str(data["amount"])),
            reason=data["reason"],
            deduction_type=data["deduction_type"],
            documented_by=data["documented_by"],
            documentation_url=data.get("documentation_url"),
        )
        self.db.add(deduction)
        await self.db.flush()
        await self.db.refresh(deduction)
        return deduction
