# app/services/software_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from typing import Optional
from datetime import datetime
import uuid
import secrets

from app.models.software_service import (
    SoftwareService as SoftwareServiceModel,
    SoftwareRental as SoftwareRentalModel,
    SoftwareUsageLog,
    SoftwareServiceStatus,
    SoftwareRentalStatus,
)
from app.schemas.software_service import (
    SoftwareServiceCreate,
    SoftwareServiceUpdate,
    SoftwareRentalCreate,
)


class SoftwareServiceService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_service(self, data: SoftwareServiceCreate) -> SoftwareServiceModel:
        service = SoftwareServiceModel(**data.model_dump())
        self.db.add(service)
        await self.db.flush()
        await self.db.refresh(service)
        return service

    async def get_service(self, service_id: uuid.UUID) -> Optional[SoftwareServiceModel]:
        result = await self.db.execute(
            select(SoftwareServiceModel).where(SoftwareServiceModel.id == service_id)
        )
        return result.scalar_one_or_none()

    async def get_service_by_slug(self, slug: str) -> Optional[SoftwareServiceModel]:
        result = await self.db.execute(
            select(SoftwareServiceModel).where(SoftwareServiceModel.slug == slug)
        )
        return result.scalar_one_or_none()

    async def list_services(
        self,
        page: int = 1,
        limit: int = 20,
        search: Optional[str] = None,
        category_id: Optional[uuid.UUID] = None,
        license_type: Optional[str] = None,
        status: Optional[str] = None,
        is_featured: Optional[bool] = None,
    ) -> dict:
        query = select(SoftwareServiceModel)

        if search:
            query = query.where(
                SoftwareServiceModel.name.ilike(f"%{search}%")
                | SoftwareServiceModel.vendor.ilike(f"%{search}%")
                | SoftwareServiceModel.description.ilike(f"%{search}%")
            )
        if category_id:
            query = query.where(SoftwareServiceModel.category_id == category_id)
        if license_type:
            query = query.where(SoftwareServiceModel.license_type == license_type)
        if status:
            query = query.where(SoftwareServiceModel.status == status)
        if is_featured is not None:
            query = query.where(SoftwareServiceModel.is_featured == is_featured)

        count_query = select(func.count()).select_from(query.subquery())
        total = (await self.db.execute(count_query)).scalar()

        query = query.order_by(SoftwareServiceModel.created_at.desc())
        query = query.offset((page - 1) * limit).limit(limit)

        result = await self.db.execute(query)
        items = result.scalars().all()

        return {
            "items": items,
            "total": total,
            "page": page,
            "limit": limit,
            "has_next": (page * limit) < total,
        }

    async def update_service(
        self, service_id: uuid.UUID, data: SoftwareServiceUpdate
    ) -> Optional[SoftwareServiceModel]:
        service = await self.get_service(service_id)
        if not service:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(service, field, value)

        await self.db.flush()
        await self.db.refresh(service)
        return service

    async def delete_service(self, service_id: uuid.UUID) -> bool:
        service = await self.get_service(service_id)
        if not service:
            return False
        service.status = SoftwareServiceStatus.INACTIVE
        await self.db.flush()
        return True

    async def check_availability(
        self, service_id: uuid.UUID, start_at: datetime, end_at: datetime
    ) -> dict:
        service = await self.get_service(service_id)
        if not service:
            return {"available": False, "reason": "Service not found"}

        if service.status != SoftwareServiceStatus.AVAILABLE:
            return {"available": False, "reason": f"Service status: {service.status}"}

        # Check concurrent license limit
        active_rentals = await self.db.execute(
            select(func.count()).select_from(SoftwareRentalModel).where(
                SoftwareRentalModel.software_service_id == service_id,
                SoftwareRentalModel.status == SoftwareRentalStatus.ACTIVE,
                SoftwareRentalModel.start_at <= end_at,
                SoftwareRentalModel.end_at >= start_at,
            )
        )
        active_count = active_rentals.scalar()

        if service.max_seats and active_count >= service.max_seats:
            return {
                "available": False,
                "reason": f"All {service.max_seats} seats are occupied",
                "active_seats": active_count,
            }

        return {
            "available": True,
            "active_seats": active_count,
            "max_seats": service.max_seats,
        }


class SoftwareRentalService:
    def __init__(self, db: AsyncSession):
        self.db = db

    def _generate_rental_number(self) -> str:
        now = datetime.utcnow()
        return f"SWR-{now.strftime('%Y%m%d')}-{secrets.randbelow(9999):04d}"

    async def create_rental(
        self, data: SoftwareRentalCreate, created_by: uuid.UUID
    ) -> SoftwareRentalModel:
        # Verify service exists and is available
        service_result = await self.db.execute(
            select(SoftwareServiceModel).where(
                SoftwareServiceModel.id == data.software_service_id
            )
        )
        service = service_result.scalar_one_or_none()
        if not service:
            raise ValueError("Software service not found")

        if service.status != SoftwareServiceStatus.AVAILABLE:
            raise ValueError(f"Software service is not available: {service.status}")

        # Calculate rental fee based on duration
        duration_days = (data.end_at - data.start_at).days
        if duration_days <= 0:
            raise ValueError("Rental duration must be at least 1 day")

        if service.daily_rate:
            rental_fee = float(service.daily_rate) * duration_days
        elif service.monthly_rate:
            rental_fee = float(service.monthly_rate) * max(1, duration_days // 30)
        elif service.weekly_rate:
            rental_fee = float(service.weekly_rate) * max(1, duration_days // 7)
        else:
            rental_fee = float(service.hourly_rate or 0) * duration_days * 24

        # Determine usage metric based on license type
        usage_metric = None
        if service.license_type.value == "api_quota":
            usage_metric = "api_calls"
        elif service.license_type.value == "cloud_credit":
            usage_metric = "compute_hours"

        rental = SoftwareRentalModel(
            rental_number=self._generate_rental_number(),
            customer_id=created_by,
            software_service_id=data.software_service_id,
            start_at=data.start_at,
            end_at=data.end_at,
            rental_fee=rental_fee,
            security_deposit_amount=0,
            currency=service.currency,
            usage_metric=usage_metric,
            usage_limit=data.usage_limit,
            usage_current=0,
            status=SoftwareRentalStatus.PENDING,
            created_by=created_by,
        )
        self.db.add(rental)
        await self.db.flush()
        await self.db.refresh(rental)
        return rental

    async def get_rental(self, rental_id: uuid.UUID) -> Optional[SoftwareRentalModel]:
        result = await self.db.execute(
            select(SoftwareRentalModel)
            .options(selectinload(SoftwareRentalModel.software_service))
            .where(SoftwareRentalModel.id == rental_id)
        )
        return result.scalar_one_or_none()

    async def list_rentals(
        self,
        page: int = 1,
        limit: int = 20,
        customer_id: Optional[uuid.UUID] = None,
        status: Optional[str] = None,
    ) -> dict:
        query = select(SoftwareRentalModel).options(
            selectinload(SoftwareRentalModel.software_service)
        )

        if customer_id:
            query = query.where(SoftwareRentalModel.customer_id == customer_id)
        if status:
            query = query.where(SoftwareRentalModel.status == status)

        count_query = select(func.count()).select_from(query.subquery())
        total = (await self.db.execute(count_query)).scalar()

        query = query.order_by(SoftwareRentalModel.created_at.desc())
        query = query.offset((page - 1) * limit).limit(limit)

        result = await self.db.execute(query)
        items = result.scalars().all()

        return {
            "items": items,
            "total": total,
            "page": page,
            "limit": limit,
            "has_next": (page * limit) < total,
        }

    async def activate_rental(self, rental_id: uuid.UUID) -> Optional[SoftwareRentalModel]:
        rental = await self.get_rental(rental_id)
        if not rental:
            return None

        if rental.status != SoftwareRentalStatus.PENDING:
            raise ValueError(f"Cannot activate rental in status: {rental.status}")

        # Generate license key for applicable types
        service = rental.software_service
        if service.license_type.value in ("node_locked", "floating"):
            rental.license_key = f"LIC-{secrets.token_hex(16).upper()}"
        if service.license_type.value == "floating":
            rental.license_server_url = f"https://license.reprico.in/{rental.rental_number}"

        rental.status = SoftwareRentalStatus.ACTIVE
        rental.provisioned_at = datetime.utcnow()
        rental.access_granted_at = datetime.utcnow()

        await self.db.flush()
        await self.db.refresh(rental)
        return rental

    async def deactivate_rental(self, rental_id: uuid.UUID) -> Optional[SoftwareRentalModel]:
        rental = await self.get_rental(rental_id)
        if not rental:
            return None

        rental.status = SoftwareRentalStatus.EXPIRED
        rental.access_revoked_at = datetime.utcnow()
        rental.actual_access_revoked_at = datetime.utcnow()

        await self.db.flush()
        await self.db.refresh(rental)
        return rental

    async def log_usage(
        self,
        rental_id: uuid.UUID,
        metric_type: str,
        quantity: float,
        metadata: dict = None,
    ) -> Optional[SoftwareUsageLog]:
        rental = await self.get_rental(rental_id)
        if not rental or rental.status != SoftwareRentalStatus.ACTIVE:
            return None

        log = SoftwareUsageLog(
            software_rental_id=rental_id,
            metric_type=metric_type,
            quantity=quantity,
            metadata_=metadata or {},
        )
        self.db.add(log)

        # Update usage counter
        rental.usage_current = float(rental.usage_current or 0) + quantity

        # Check if limit exceeded
        if rental.usage_limit and rental.usage_current > rental.usage_limit:
            rental.status = SoftwareRentalStatus.SUSPENDED

        await self.db.flush()
        await self.db.refresh(log)
        return log

    async def get_usage_logs(
        self, rental_id: uuid.UUID, page: int = 1, limit: int = 50
    ) -> dict:
        query = select(SoftwareUsageLog).where(
            SoftwareUsageLog.software_rental_id == rental_id
        )

        count_query = select(func.count()).select_from(query.subquery())
        total = (await self.db.execute(count_query)).scalar()

        query = query.order_by(SoftwareUsageLog.created_at.desc())
        query = query.offset((page - 1) * limit).limit(limit)

        result = await self.db.execute(query)
        items = result.scalars().all()

        return {
            "items": items,
            "total": total,
            "page": page,
            "limit": limit,
            "has_next": (page * limit) < total,
        }
