# app/api/v1/auth.py
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta, timezone

from app.utils.database import get_db, get_read_db
from app.models.user import User, RefreshToken, OTPToken
from app.core.auth import (
    create_access_token,
    create_refresh_token,
    hash_token,
    verify_password,
    hash_password,
    generate_otp,
)
from app.schemas.auth import (
    LoginRequest,
    OTPRequest,
    OTPVerifyRequest,
    RegisterRequest,
    TokenResponse,
    RefreshTokenRequest,
    LogoutRequest,
)
from app.config import settings

router = APIRouter()


# ── Legacy Auth Endpoints (kept for backward compatibility) ─────

@router.post("/register", response_model=TokenResponse)
async def register(data: RegisterRequest, db: AsyncSession = Depends(get_db)):
    """Register a new user (legacy)."""
    existing = await db.execute(
        select(User).where((User.email == data.email) | (User.phone == data.phone))
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="User already exists")

    user = User(
        name=data.name,
        email=data.email,
        phone=data.phone,
        password_hash=hash_password(data.password) if data.password else None,
        role="portal_user",
        user_type=data.user_type,
    )
    db.add(user)
    await db.flush()

    access_token = create_access_token(str(user.id), user.role, user.user_type)
    refresh_token = create_refresh_token()

    token_record = RefreshToken(
        user_id=user.id,
        token_hash=hash_token(refresh_token),
        device_fingerprint="initial",
        expires_at=datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )
    db.add(token_record)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest, db: AsyncSession = Depends(get_read_db)):
    """Login with email/phone and password (legacy)."""
    result = await db.execute(
        select(User).where((User.email == data.identifier) | (User.phone == data.identifier))
    )
    user = result.scalar_one_or_none()

    if not user or not user.password_hash:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if user.blacklisted:
        raise HTTPException(status_code=403, detail="Account is blacklisted")

    access_token = create_access_token(str(user.id), user.role, user.user_type)
    refresh_token = create_refresh_token()

    token_record = RefreshToken(
        user_id=user.id,
        token_hash=hash_token(refresh_token),
        device_fingerprint=data.device_fingerprint,
        expires_at=datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )
    db.add(token_record)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post("/otp/request")
async def request_otp(data: OTPRequest, db: AsyncSession = Depends(get_db)):
    """Request OTP for login/register (legacy)."""
    otp_code = generate_otp()

    otp_record = OTPToken(
        identifier=data.identifier,
        channel=data.channel,
        code=otp_code,
        purpose="login",
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=5),
    )
    db.add(otp_record)

    # TODO: Send OTP via SMS/Email
    # await sms_client.send_otp(data.identifier, otp_code)

    return {"message": "OTP sent successfully"}


@router.post("/otp/verify", response_model=TokenResponse)
async def verify_otp(data: OTPVerifyRequest, db: AsyncSession = Depends(get_db)):
    """Verify OTP and login (legacy)."""
    result = await db.execute(
        select(OTPToken)
        .where(
            OTPToken.identifier == data.identifier,
            OTPToken.code == data.code,
            OTPToken.purpose == data.purpose,
            OTPToken.verified_at.is_(None),
        )
        .order_by(OTPToken.created_at.desc())
    )
    otp_record = result.scalar_one_or_none()

    if not otp_record:
        raise HTTPException(status_code=400, detail="Invalid OTP")

    if otp_record.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="OTP expired")

    if otp_record.attempts >= 3:
        raise HTTPException(status_code=400, detail="OTP attempts exceeded")

    otp_record.verified_at = datetime.now(timezone.utc)

    result = await db.execute(
        select(User).where((User.email == data.identifier) | (User.phone == data.identifier))
    )
    user = result.scalar_one_or_none()

    if not user:
        user = User(
            name="New User",
            email=data.identifier if "@" in data.identifier else f"{data.identifier}@temp.com",
            phone=data.identifier if "@" not in data.identifier else "0000000000",
            role="portal_user",
            user_type="personal",
        )
        db.add(user)
        await db.flush()

    access_token = create_access_token(str(user.id), user.role, user.user_type)
    refresh_token = create_refresh_token()

    token_record = RefreshToken(
        user_id=user.id,
        token_hash=hash_token(refresh_token),
        device_fingerprint="otp-login",
        expires_at=datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )
    db.add(token_record)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(data: RefreshTokenRequest, db: AsyncSession = Depends(get_db)):
    """Refresh access token (legacy)."""
    token_hash = hash_token(data.refresh_token)
    result = await db.execute(
        select(RefreshToken).where(
            RefreshToken.token_hash == token_hash,
            RefreshToken.revoked_at.is_(None),
        )
    )
    token_record = result.scalar_one_or_none()

    if not token_record:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    if token_record.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=401, detail="Refresh token expired")

    user = await db.get(User, token_record.user_id)
    if not user or user.blacklisted:
        raise HTTPException(status_code=401, detail="User not found or blacklisted")

    token_record.revoked_at = datetime.now(timezone.utc)

    access_token = create_access_token(str(user.id), user.role, user.user_type)
    new_refresh_token = create_refresh_token()

    new_token_record = RefreshToken(
        user_id=user.id,
        token_hash=hash_token(new_refresh_token),
        device_fingerprint=data.device_fingerprint,
        expires_at=datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )
    db.add(new_token_record)

    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post("/logout")
async def logout(data: LogoutRequest, db: AsyncSession = Depends(get_db)):
    """Logout and revoke refresh token (legacy)."""
    token_hash = hash_token(data.refresh_token)
    result = await db.execute(
        select(RefreshToken).where(
            RefreshToken.token_hash == token_hash,
            RefreshToken.revoked_at.is_(None),
        )
    )
    token_record = result.scalar_one_or_none()

    if token_record:
        token_record.revoked_at = datetime.now(timezone.utc)

    return {"message": "Logged out successfully"}


# ── Clerk Sync Endpoint ────────────────────────────────────────

@router.post("/me")
async def get_me_clerk(request: Request, db: AsyncSession = Depends(get_read_db)):
    """Get current user info from Clerk token.

    Frontend calls this after Clerk sign-in to sync/get local user data.
    """
    from app.api.deps import get_current_user
    from fastapi import Depends as _Depends

    # This endpoint is called by frontend with Clerk session token
    # The get_current_user dependency handles Clerk JWT verification
    auth_header = request.headers.get("authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing authorization header")

    token = auth_header.split(" ", 1)[1]
    from app.core.clerk_auth import verify_clerk_token
    payload = verify_clerk_token(token)

    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")

    clerk_user_id = payload.get("sub", "")
    result = await db.execute(
        select(User).where(User.clerk_user_id == clerk_user_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found. Please sign up first.")

    from app.schemas.user import UserResponse
    return UserResponse.model_validate(user)
