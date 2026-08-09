# app/services/department_service.py
from uuid import UUID
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.models.department import Department


class DepartmentService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_department(self, data: dict, enterprise_id: UUID) -> Department:
        department = Department(
            enterprise_id=enterprise_id,
            name=data["name"],
            description=data.get("description"),
            head_user_id=data.get("head_user_id"),
            member_ids=data.get("member_ids", []),
            budget_limit=data.get("budget_limit"),
        )
        self.db.add(department)
        await self.db.flush()
        await self.db.refresh(department)
        return department

    async def get_department(self, department_id: UUID) -> Department:
        result = await self.db.execute(
            select(Department).where(Department.id == department_id)
        )
        department = result.scalar_one_or_none()
        if not department:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Department not found",
            )
        return department

    async def list_departments(self, enterprise_id: UUID) -> dict:
        query = select(Department).where(Department.enterprise_id == enterprise_id)

        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()

        query = query.order_by(Department.name)
        result = await self.db.execute(query)
        departments = result.scalars().all()

        return {
            "items": departments,
            "total": total,
        }

    async def update_department(self, department_id: UUID, data: dict) -> Department:
        department = await self.get_department(department_id)

        for key, value in data.items():
            if hasattr(department, key) and value is not None:
                setattr(department, key, value)

        await self.db.flush()
        await self.db.refresh(department)
        return department

    async def update_members(
        self, department_id: UUID, add_members: list, remove_members: list
    ) -> Department:
        department = await self.get_department(department_id)

        current_members = list(department.member_ids or [])

        for member_id in add_members:
            if member_id not in current_members:
                current_members.append(member_id)

        for member_id in remove_members:
            if member_id in current_members:
                current_members.remove(member_id)

        department.member_ids = current_members
        await self.db.flush()
        await self.db.refresh(department)
        return department
