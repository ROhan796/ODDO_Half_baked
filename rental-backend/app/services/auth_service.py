# app/services/auth_service.py
from datetime import datetime, timedelta, timezone
from uuid import UUID
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.models.user import User, RefreshToken, OTPToken, OTPChannel, OTPPurpose
from app.core.auth import (
    create_access_token,
    create_refresh_token,
    hash_token,
    verify_password,
    hash_password,
    generate_otp,
)
from app.config import settings


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def register_user(self, data: dict) -> dict:
        existing = await self.db.execute(
            select(User).where(
                (User.email == data["email"]) | (User.phone == data["phone"])
            )
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this email or phone already exists",
            )

        user = User(
            name=data["name"],
            email=data["email"],
            phone=data["phone"],
            role=data.get("role", "portal_user"),
            user_type=data.get("user_type", "personal"),
            enterprise_id=data.get("enterprise_id"),
            referral_code=data.get("referral_code"),
        )
        if data.get("password"):
            user.password_hash = hash_password(data["password"])

        self.db.add(user)
        await self.db.flush()

        tokens = await self._generate_tokens(user, data.get("device_fingerprint", ""))
        return {"user": user, **tokens}

    async def login_user(self, identifier: str, password: str, fingerprint: str) -> dict:
        result = await self.db.execute(
            select(User).where(
                (User.email == identifier) | (User.phone == identifier)
            )
        )
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
            )

        if user.blacklisted:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is blacklisted",
            )

        if user.password_hash and password:
            if not verify_password(password, user.password_hash):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid credentials",
                )

        tokens = await self._generate_tokens(user, fingerprint)
        return {"user": user, **tokens}

    async def refresh_tokens(self, refresh_token: str, fingerprint: str) -> dict:
        token_hash = hash_token(refresh_token)
        result = await self.db.execute(
            select(RefreshToken).where(
                and_(
                    RefreshToken.token_hash == token_hash,
                    RefreshToken.revoked_at.is_(None),
                    RefreshToken.expires_at > datetime.now(timezone.utc),
                )
            )
        )
        stored_token = result.scalar_one_or_none()
        if not stored_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token",
            )

        user = await self.db.get(User, stored_token.user_id)
        if not user or user.blacklisted:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or blacklisted",
            )

        stored_token.revoked_at = datetime.now(timezone.utc)
        await self.db.flush()

        tokens = await self._generate_tokens(user, fingerprint)
        return tokens

    async def logout_user(self, refresh_token: str) -> None:
        token_hash = hash_token(refresh_token)
        result = await self.db.execute(
            select(RefreshToken).where(RefreshToken.token_hash == token_hash)
        )
        stored_token = result.scalar_one_or_none()
        if stored_token:
            stored_token.revoked_at = datetime.now(timezone.utc)
            await self.db.flush()

    async def request_otp(self, identifier: str, channel: str) -> dict:
        otp_code = generate_otp()
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)

        otp = OTPToken(
            identifier=identifier,
            channel=OTPChannel(channel),
            code=otp_code,
            purpose=OTPPurpose.LOGIN,
            expires_at=expires_at,
        )
        self.db.add(otp)
        await self.db.flush()

        return {
            "identifier": identifier,
            "channel": channel,
            "expires_at": expires_at.isoformat(),
            "otp_code": otp_code if settings.DEBUG else None,
        }

    async def verify_otp(self, identifier: str, code: str, purpose: str) -> dict:
        result = await self.db.execute(
            select(OTPToken).where(
                and_(
                    OTPToken.identifier == identifier,
                    OTPToken.purpose == purpose,
                    OTPToken.expires_at > datetime.now(timezone.utc),
                    OTPToken.verified_at.is_(None),
                )
            ).order_by(OTPToken.created_at.desc())
        )
        otp_record = result.scalar_one_or_none()

        if not otp_record:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired OTP",
            )

        if otp_record.attempts >= 5:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many attempts. Please request a new OTP.",
            )

        otp_record.attempts += 1

        if otp_record.code != code:
            await self.db.flush()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid OTP code",
            )

        otp_record.verified_at = datetime.now(timezone.utc)
        await self.db.flush()

        user_result = await self.db.execute(
            select(User).where(
                (User.email == identifier) | (User.phone == identifier)
            )
        )
        user = user_result.scalar_one_or_none()

        if user:
            tokens = await self._generate_tokens(user, "")
            return {"user": user, **tokens}

        return {"verified": True, "identifier": identifier, "purpose": purpose}

    async def _generate_tokens(self, user: User, fingerprint: str) -> dict:
        access_token = create_access_token(
            str(user.id), user.role.value, user.user_type.value,
            str(user.enterprise_id) if user.enterprise_id else None,
        )
        refresh_token = create_refresh_token()

        db_refresh = RefreshToken(
            user_id=user.id,
            token_hash=hash_token(refresh_token),
            device_fingerprint=fingerprint or "unknown",
            expires_at=datetime.now(timezone.utc)
            + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        )
        self.db.add(db_refresh)
        await self.db.flush()

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        }
