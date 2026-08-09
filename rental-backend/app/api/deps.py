# app/api/deps.py
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.utils.database import get_read_db, get_db
from app.core.auth import verify_access_token
from app.core.clerk_auth import verify_clerk_token
from app.models.user import User
from app.core.permissions import check_permission

from typing import Optional
from app.config import settings

security = HTTPBearer(auto_error=False)


async def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_read_db),
) -> User:
    """Get current authenticated user.

    Supports dual mode authentication:
    1. Clerk session token (RS256 / HS256) — preferred
    2. Legacy JWT token (HS256) — backward compatible
    3. Development mode fallback when unauthenticated
    """
    token = credentials.credentials if credentials else None

    if token:
        # Try Clerk verification first
        payload = verify_clerk_token(token)

        if payload:
            clerk_user_id = payload.get("sub", "")
            if clerk_user_id:
                result = await db.execute(
                    select(User).where(User.clerk_user_id == clerk_user_id)
                )
                user = result.scalars().first()
                if user:
                    if user.blacklisted:
                        raise HTTPException(
                            status_code=status.HTTP_403_FORBIDDEN,
                            detail="Account is blacklisted",
                        )
                    return user

            email = payload.get("email_address", payload.get("email", ""))
            if email:
                result = await db.execute(
                    select(User).where(User.email.ilike(email.strip()))
                )
                user = result.scalars().first()
                if user:
                    user.clerk_user_id = clerk_user_id
                    await db.commit()
                    if user.blacklisted:
                        raise HTTPException(
                            status_code=status.HTTP_403_FORBIDDEN,
                            detail="Account is blacklisted",
                        )
                    return user

            from app.core.rbac_config import get_role_for_email
            assigned_role = get_role_for_email(email) or "portal_user"

            first_name = payload.get("first_name", "") or ""
            last_name = payload.get("last_name", "") or ""
            name = f"{first_name} {last_name}".strip() or email or "Clerk User"

            new_user = User(
                clerk_user_id=clerk_user_id,
                name=name,
                email=email or f"{clerk_user_id}@clerk.local",
                phone="0000000000",
                role=assigned_role,
                user_type="personal",
                kyc_status="pending",
                trust_score=0,
                trust_tier="unverified",
            )
            db.add(new_user)
            await db.commit()
            return new_user

        # Fallback: Legacy JWT verification
        payload = verify_access_token(token)
        if payload:
            import uuid
            try:
                u_id = uuid.UUID(payload.get("sub", ""))
                user = await db.get(User, u_id)
            except (ValueError, TypeError):
                user = None

            if user:
                if user.blacklisted:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Account is blacklisted",
                    )
                return user

    # Development fallback when unauthenticated — defaults strictly to a portal_user (Customer Renter)
    if settings.DEBUG or settings.APP_ENV == "development":
        result = await db.execute(select(User).where(User.email == "roix107@gmail.com"))
        default_user = result.scalars().first()
        if not default_user:
            result = await db.execute(select(User).where(User.role == "portal_user"))
            default_user = result.scalars().first()
        if default_user:
            return default_user

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or missing authentication token",
    )


def require_role(*roles):
    """Dependency that checks user has required role."""

    async def role_checker(user: User = Depends(get_current_user)):
        if user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role {user.role} not authorized",
            )
        return user

    return Depends(role_checker)


def require_permission(permission: str):
    """Dependency that checks user has specific permission."""

    async def perm_checker(user: User = Depends(get_current_user)):
        if not check_permission(user.role, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission '{permission}' required",
            )
        return user

    return Depends(perm_checker)
