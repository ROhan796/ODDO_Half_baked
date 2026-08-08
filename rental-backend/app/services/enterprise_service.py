# app/services/enterprise_service.py
from uuid import UUID
from datetime import datetime, timezone
from decimal import Decimal
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.models.enterprise import Enterprise, EnterpriseMember, EnterpriseSubRole
from app.models.user import User


class EnterpriseService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_enterprise(self, data: dict) -> Enterprise:
        enterprise = Enterprise(
            name=data["name"],
            legal_entity_type=data["legal_entity_type"],
            gst_number=data.get("gst_number"),
            pan=data["pan"],
            cin=data.get("cin"),
            registered_address=data["registered_address"],
            office_address=data.get("office_address"),
            contact_person_name=data["contact_person_name"],
            contact_person_email=data["contact_person_email"],
            contact_person_phone=data["contact_person_phone"],
            credit_line_enabled=data.get("credit_line_enabled", False),
            credit_limit_inr=(
                Decimal(str(data["credit_limit_inr"]))
                if data.get("credit_limit_inr")
                else None
            ),
            credit_days=data.get("credit_days", 30),
        )
        self.db.add(enterprise)
        await self.db.flush()
        await self.db.refresh(enterprise)
        return enterprise

    async def get_enterprise(self, enterprise_id: UUID) -> Enterprise:
        result = await self.db.execute(
            select(Enterprise).where(Enterprise.id == enterprise_id)
        )
        enterprise = result.scalar_one_or_none()
        if not enterprise:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Enterprise not found",
            )
        return enterprise

    async def list_enterprises(self, page: int = 1, limit: int = 20) -> dict:
        query = select(Enterprise)

        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()

        query = query.order_by(Enterprise.created_at.desc())
        query = query.offset((page - 1) * limit).limit(limit)
        result = await self.db.execute(query)
        enterprises = result.scalars().all()

        return {
            "items": enterprises,
            "total": total,
            "page": page,
            "limit": limit,
            "pages": (total + limit - 1) // limit,
        }

    async def add_member(
        self, enterprise_id: UUID, data: dict, invited_by: UUID
    ) -> EnterpriseMember:
        enterprise = await self.get_enterprise(enterprise_id)

        existing = await self.db.execute(
            select(EnterpriseMember).where(
                EnterpriseMember.enterprise_id == enterprise_id,
                EnterpriseMember.user_id == data["user_id"],
            )
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User is already a member of this enterprise",
            )

        user = await self.db.get(User, data["user_id"])
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        member = EnterpriseMember(
            enterprise_id=enterprise_id,
            user_id=data["user_id"],
            sub_role=EnterpriseSubRole(data.get("sub_role", "department_user")),
            department=data.get("department"),
            designation=data.get("designation"),
            spending_limit_inr=(
                Decimal(str(data["spending_limit_inr"]))
                if data.get("spending_limit_inr")
                else None
            ),
            monthly_limit_inr=(
                Decimal(str(data["monthly_limit_inr"]))
                if data.get("monthly_limit_inr")
                else None
            ),
            can_approve_rentals=data.get("can_approve_rentals", False),
            invited_by=invited_by,
            invited_at=datetime.now(timezone.utc),
        )
        self.db.add(member)

        user.enterprise_id = enterprise_id
        user.user_type = "enterprise_sub"

        await self.db.flush()
        await self.db.refresh(member)
        return member

    async def list_members(self, enterprise_id: UUID) -> list:
        await self.get_enterprise(enterprise_id)

        result = await self.db.execute(
            select(EnterpriseMember).where(
                EnterpriseMember.enterprise_id == enterprise_id
            )
        )
        members = result.scalars().all()
        return members
