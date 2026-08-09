# app/services/inspection_service.py
from uuid import UUID
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.models.inspection import InspectionReport, InspectionStatus


class InspectionService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_inspection(self, data: dict, inspector_id: UUID) -> InspectionReport:
        report = InspectionReport(
            rental_id=data["rental_id"],
            product_id=data["product_id"],
            inspector_id=inspector_id,
            inspection_type=data["inspection_type"],
            functional_check=data.get("functional_check"),
            cosmetic_grade=data.get("cosmetic_grade"),
            overall_grade=data.get("overall_grade"),
            accessories_status=data.get("accessories_status"),
            damage_detected=data.get("damage_detected", False),
            damage_description=data.get("damage_description"),
            estimated_damage_cost=data.get("estimated_damage_cost"),
            photos=data.get("photos", []),
            before_photo=data.get("before_photo"),
            after_photo=data.get("after_photo"),
            status=InspectionStatus.PENDING,
        )
        self.db.add(report)
        await self.db.flush()
        await self.db.refresh(report)
        return report

    async def get_inspection(self, inspection_id: UUID) -> InspectionReport:
        result = await self.db.execute(
            select(InspectionReport).where(InspectionReport.id == inspection_id)
        )
        report = result.scalar_one_or_none()
        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Inspection report not found",
            )
        return report

    async def list_inspections(
        self,
        page: int = 1,
        limit: int = 20,
        rental_id: UUID = None,
        inspection_type: str = None,
    ) -> dict:
        query = select(InspectionReport)

        if rental_id:
            query = query.where(InspectionReport.rental_id == rental_id)

        if inspection_type:
            query = query.where(InspectionReport.inspection_type == inspection_type)

        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()

        query = query.order_by(InspectionReport.created_at.desc())
        query = query.offset((page - 1) * limit).limit(limit)
        result = await self.db.execute(query)
        reports = result.scalars().all()

        return {
            "items": reports,
            "total": total,
            "page": page,
            "limit": limit,
            "has_next": (page * limit) < total,
        }

    async def update_inspection(self, inspection_id: UUID, data: dict) -> InspectionReport:
        report = await self.get_inspection(inspection_id)

        for key, value in data.items():
            if hasattr(report, key) and value is not None:
                setattr(report, key, value)

        await self.db.flush()
        await self.db.refresh(report)
        return report

    async def complete_inspection(self, inspection_id: UUID) -> InspectionReport:
        report = await self.get_inspection(inspection_id)

        if report.status == InspectionStatus.COMPLETED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inspection already completed",
            )

        report.status = InspectionStatus.COMPLETED
        await self.db.flush()
        await self.db.refresh(report)
        return report
