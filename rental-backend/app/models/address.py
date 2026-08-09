# app/models/address.py
import uuid
from sqlalchemy import (
    Column, String, Boolean, Text, ForeignKey
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class UserAddress(BaseModel):
    __tablename__ = "user_addresses"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    label = Column(String(50), nullable=False, default="Home")
    street = Column(Text, nullable=False)
    city = Column(String(100), nullable=False)
    state = Column(String(100), nullable=False)
    pincode = Column(String(10), nullable=False)
    country = Column(String(100), nullable=False, default="India")
    is_default = Column(Boolean, default=False)
    contact_name = Column(String(255), nullable=True)
    contact_phone = Column(String(15), nullable=True)

    user = relationship("User", foreign_keys=[user_id])
