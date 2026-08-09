# app/api/v1/addresses.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from app.utils.database import get_read_db, get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.address import (
    AddressCreate,
    AddressUpdate,
    AddressResponse,
    AddressListResponse,
)
from app.services.address_service import AddressService

router = APIRouter()


@router.get("/", response_model=AddressListResponse)
async def list_addresses(
    db: AsyncSession = Depends(get_read_db),
    current_user: User = Depends(get_current_user),
):
    """List current user's addresses."""
    service = AddressService(db)
    result = await service.list_addresses(user_id=current_user.id)
    return AddressListResponse(**result)


@router.post("/", response_model=AddressResponse, status_code=201)
async def create_address(
    data: AddressCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Add a new address for current user."""
    service = AddressService(db)
    return await service.create_address(
        data=data.model_dump(),
        user_id=current_user.id,
    )


@router.put("/{address_id}", response_model=AddressResponse)
async def update_address(
    address_id: uuid.UUID,
    data: AddressUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update an address."""
    service = AddressService(db)
    return await service.update_address(
        address_id=address_id,
        user_id=current_user.id,
        data=data.model_dump(exclude_unset=True),
    )


@router.delete("/{address_id}")
async def delete_address(
    address_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete an address."""
    service = AddressService(db)
    return await service.delete_address(
        address_id=address_id,
        user_id=current_user.id,
    )


@router.put("/{address_id}/default", response_model=AddressResponse)
async def set_default_address(
    address_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Set address as default."""
    service = AddressService(db)
    return await service.set_default(
        address_id=address_id,
        user_id=current_user.id,
    )
