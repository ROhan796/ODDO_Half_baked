# app/models/department.py
import uuid
from sqlalchemy import (
    Column, String, Boolean, ForeignKey, Integer
)
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class Department(BaseModel):
    __tablename__ = "departments"

    enterprise_id = Column(UUID(as_uuid=True), ForeignKey("enterprises.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(String(500), nullable=True)
    head_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    member_ids = Column(ARRAY(UUID), default=[])
    budget_limit = Column(Integer, nullable=True)
    is_active = Column(Boolean, default=True)

    enterprise = relationship("Enterprise", foreign_keys=[enterprise_id])
    head = relationship("User", foreign_keys=[head_user_id])
