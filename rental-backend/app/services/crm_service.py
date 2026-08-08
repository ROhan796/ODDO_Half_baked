# app/services/crm_service.py
from uuid import UUID
from datetime import datetime, timezone
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.models.crm import CRMContact, CRMInteraction, CRMContactType, CRMInteractionType


class CRMService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_contact(self, data: dict) -> CRMContact:
        contact = CRMContact(
            user_id=data.get("user_id"),
            contact_type=CRMContactType(data["contact_type"]),
            name=data["name"],
            email=data.get("email"),
            phone=data.get("phone"),
            company=data.get("company"),
            designation=data.get("designation"),
            source=data.get("source"),
            notes=data.get("notes"),
            tags=data.get("tags", []),
            assigned_to=data.get("assigned_to"),
        )
        self.db.add(contact)
        await self.db.flush()
        await self.db.refresh(contact)
        return contact

    async def get_contact(self, contact_id: UUID) -> CRMContact:
        result = await self.db.execute(
            select(CRMContact).where(CRMContact.id == contact_id)
        )
        contact = result.scalar_one_or_none()
        if not contact:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Contact not found",
            )
        return contact

    async def list_contacts(
        self,
        page: int = 1,
        limit: int = 20,
        search: str = None,
        contact_type: str = None,
    ) -> dict:
        query = select(CRMContact)

        if search:
            search_filter = or_(
                CRMContact.name.ilike(f"%{search}%"),
                CRMContact.email.ilike(f"%{search}%"),
                CRMContact.phone.ilike(f"%{search}%"),
                CRMContact.company.ilike(f"%{search}%"),
            )
            query = query.where(search_filter)

        if contact_type:
            query = query.where(CRMContact.contact_type == contact_type)

        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()

        query = query.order_by(CRMContact.created_at.desc())
        query = query.offset((page - 1) * limit).limit(limit)
        result = await self.db.execute(query)
        contacts = result.scalars().all()

        return {
            "items": contacts,
            "total": total,
            "page": page,
            "limit": limit,
            "pages": (total + limit - 1) // limit,
        }

    async def update_contact(self, contact_id: UUID, data: dict) -> CRMContact:
        contact = await self.get_contact(contact_id)

        for key, value in data.items():
            if hasattr(contact, key) and value is not None:
                if key == "contact_type":
                    contact.contact_type = CRMContactType(value)
                else:
                    setattr(contact, key, value)

        await self.db.flush()
        await self.db.refresh(contact)
        return contact

    async def create_interaction(
        self, data: dict, performed_by: UUID
    ) -> CRMInteraction:
        contact = await self.get_contact(data["contact_id"])

        interaction = CRMInteraction(
            contact_id=data["contact_id"],
            interaction_type=CRMInteractionType(data["interaction_type"]),
            direction=data["direction"],
            subject=data.get("subject"),
            content=data.get("content"),
            duration_minutes=data.get("duration_minutes"),
            outcome=data.get("outcome"),
            next_action=data.get("next_action"),
            next_action_at=data.get("next_action_at"),
            performed_by=performed_by,
            attachment_urls=data.get("attachment_urls", []),
        )
        self.db.add(interaction)

        contact.last_contact_at = datetime.now(timezone.utc)

        await self.db.flush()
        await self.db.refresh(interaction)
        return interaction

    async def list_interactions(self, contact_id: UUID) -> list:
        await self.get_contact(contact_id)

        result = await self.db.execute(
            select(CRMInteraction)
            .where(CRMInteraction.contact_id == contact_id)
            .order_by(CRMInteraction.created_at.desc())
        )
        interactions = result.scalars().all()
        return interactions
