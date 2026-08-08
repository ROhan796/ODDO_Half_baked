# app/core/auth.py
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.config import settings
import hashlib
import secrets

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(
    user_id: str,
    role: str,
    user_type: str,
    enterprise_id: str | None = None,
) -> str:
    """Create JWT access token (15 min TTL)."""
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload = {
        "sub": user_id,
        "role": role,
        "user_type": user_type,
        "enterprise_id": enterprise_id,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "jti": secrets.token_hex(16),
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def verify_access_token(token: str) -> dict | None:
    """Verify and decode JWT access token."""
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        return payload
    except JWTError:
        return None


def create_refresh_token() -> str:
    """Create opaque refresh token (32 bytes)."""
    return secrets.token_hex(32)


def hash_token(token: str) -> str:
    """Hash token for secure storage."""
    return hashlib.sha256(token.encode()).hexdigest()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash."""
    return pwd_context.verify(plain_password, hashed_password)


def hash_password(password: str) -> str:
    """Hash password."""
    return pwd_context.hash(password)


def generate_otp() -> str:
    """Generate 6-digit OTP."""
    return str(secrets.randbelow(1000000)).zfill(6)
