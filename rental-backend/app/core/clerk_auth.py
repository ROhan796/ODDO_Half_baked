# app/core/clerk_auth.py
"""Clerk JWT verification for FastAPI."""
import jwt
import httpx
from functools import lru_cache
from typing import Optional
from app.config import settings

JWKS_URL = "https://originating-tuna-85.clerk.accounts.dev/.well-known/jwks.json"


@lru_cache()
def _get_jwks() -> dict:
    """Fetch Clerk's JWKS (cached)."""
    resp = httpx.get(JWKS_URL, timeout=10)
    resp.raise_for_status()
    return resp.json()


def verify_clerk_token(token: str) -> Optional[dict]:
    """Verify a Clerk session token and return the decoded payload.

    Tries RS256 verification with Clerk's JWKS first.
    Falls back to HS256 verification with CLERK_SECRET_KEY for backend tokens.
    Returns None if verification fails.
    """
    # Try RS256 (Clerk session tokens signed with JWKS)
    try:
        jwks = _get_jwks()
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get("kid")

        if kid:
            key_data = next((k for k in jwks.get("keys", []) if k["kid"] == kid), None)
            if key_data:
                from jwt.algorithms import RSAAlgorithm
                public_key = RSAAlgorithm.from_jwk(key_data)
                payload = jwt.decode(
                    token,
                    public_key,
                    algorithms=["RS256"],
                    options={"verify_aud": False},
                )
                return payload
    except Exception:
        pass

    # Fallback: HS256 with Clerk secret key (for backend API tokens)
    if settings.CLERK_SECRET_KEY:
        try:
            payload = jwt.decode(
                token,
                settings.CLERK_SECRET_KEY,
                algorithms=["HS256"],
                options={"verify_aud": False},
            )
            return payload
        except Exception:
            pass

    return None
