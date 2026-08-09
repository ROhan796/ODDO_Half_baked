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

security = HTTPBearer()


async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_read_db),
) -> User:
    """Get current authenticated user.

    Supports two auth methods (dual mode during transition):
    1. Clerk session token (RS256 / HS256) — preferred
    2. Legacy JWT token (HS256) — backward compatible
    """
    token = credentials.credentials

    # Try Clerk verification first
    payload = verify_clerk_token(token)

    if payload:
        # Clerk token — extract user ID from 'sub' claim
        clerk_user_id = payload.get("sub", "")
        if clerk_user_id:
            result = await db.execute(
                select(User).where(User.clerk_user_id == clerk_user_id)
            )
            user = result.scalar_one_or_none()
            if user:
                if user.blacklisted:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Account is blacklisted",
                    )
                return user

            # Clerk user not in local DB yet — create a stub
            # (will be fully synced via webhook, but handle edge case)
            email = payload.get("email_address", payload.get("email", ""))
            name = payload.get("first_name", "") + " " + payload.get("last_name", "")
            name = name.strip() or email or "Clerk User"

            new_user = User(
                clerk_user_id=clerk_user_id,
                name=name,
                email=email or f"{clerk_user_id}@clerk.local",
                phone="0000000000",
                role="portal_user",
                user_type="personal",
                kyc_status="pending",
                trust_score=0,
                trust_tier="unverified",
            )
            db.add(new_user)
            await db.flush()
            return new_user

    # Fallback: Legacy JWT verification
    payload = verify_access_token(token)
    if payload:
        user = await db.get(User, payload["sub"])
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
            )
        if user.blacklisted:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is blacklisted",
            )
        return user

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token",
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
