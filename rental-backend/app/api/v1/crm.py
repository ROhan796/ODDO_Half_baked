# app/api/v1/crm.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
import uuid

from app.utils.database import get_read_db, get_db
from app.api.deps import get_current_user, require_permission
from app.models.user import User
from app.models.crm import CRMContact, CRMInteraction
from app.schemas.crm import (
    CRMContactCreate,
    CRMContactUpdate,
    CRMContactResponse,
    CRMContactListResponse,
    CRMInteractionCreate,
    CRMInteractionResponse,
)
from app.core.permissions import Permission

router = APIRouter()


@router.get("/contacts", response_model=CRMContactListResponse)
async def list_contacts(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    contact_type: Optional[str] = None,
    db: AsyncSession = Depends(get_read_db),
    current_user: User = require_permission(Permission.CRM_VIEW.value),
):
    """List CRM contacts."""
    query = select(CRMContact)

    if search:
        query = query.where(
            (CRMContact.name.ilike(f"%{search}%"))
            | (CRMContact.email.ilike(f"%{search}%"))
        )

    if contact_type:
        query = query.where(CRMContact.contact_type == contact_type)

    from sqlalchemy import func

    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar()

    query = query.offset((page - 1) * limit).limit(limit)
    result = await db.execute(query)
    contacts = result.scalars().all()

    return CRMContactListResponse(
        items=contacts,
        total=total,
        page=page,
        limit=limit,
        has_next=(page * limit) < total,
    )


@router.post("/contacts", response_model=CRMContactResponse, status_code=201)
async def create_contact(
    data: CRMContactCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = require_permission(Permission.CRM_MANAGE.value),
):
    """Create a new CRM contact."""
    contact = CRMContact(**data.model_dump())
    db.add(contact)
    return contact


@router.get("/contacts/{contact_id}", response_model=CRMContactResponse)
async def get_contact(
    contact_id: uuid.UUID,
    db: AsyncSession = Depends(get_read_db),
    current_user: User = require_permission(Permission.CRM_VIEW.value),
):
    """Get CRM contact by ID."""
    contact = await db.get(CRMContact, contact_id)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact


@router.put("/contacts/{contact_id}", response_model=CRMContactResponse)
async def update_contact(
    contact_id: uuid.UUID,
    data: CRMContactUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = require_permission(Permission.CRM_MANAGE.value),
):
    """Update CRM contact."""
    contact = await db.get(CRMContact, contact_id)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(contact, field, value)

    return contact


@router.post("/interactions", response_model=CRMInteractionResponse, status_code=201)
async def create_interaction(
    data: CRMInteractionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = require_permission(Permission.CRM_MANAGE.value),
):
    """Create a new CRM interaction."""
    interaction = CRMInteraction(
        **data.model_dump(),
        performed_by=current_user.id,
    )
    db.add(interaction)
    return interaction
