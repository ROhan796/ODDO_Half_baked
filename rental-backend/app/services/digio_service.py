# app/services/digio_service.py
"""DigiO KYC/eSign service — sandbox configuration for prototyping.

This is a stub implementation for future DigiO integration.
Configure DIGIO_CLIENT_ID, DIGIO_CLIENT_SECRET, DIGIO_ENVIRONMENT in .env
to activate when ready.
"""
from app.config import settings
from typing import Optional
import httpx


class DigioService:
    """DigiO API client for KYC and eSign operations."""

    SANDBOX_URL = "https://ext.digio.in:444"
    PRODUCTION_URL = "https://api.digio.in"

    def __init__(self):
        self.base_url = settings.DIGIO_BASE_URL or (
            self.SANDBOX_URL if settings.DIGIO_ENVIRONMENT == "sandbox"
            else self.PRODUCTION_URL
        )
        self.client_id = settings.DIGIO_CLIENT_ID
        self.client_secret = settings.DIGIO_CLIENT_SECRET
        self.environment = settings.DIGIO_ENVIRONMENT

    @property
    def is_configured(self) -> bool:
        return bool(self.client_id and self.client_secret)

    async def _request(self, method: str, path: str, **kwargs) -> Optional[dict]:
        """Make an authenticated request to DigiO API."""
        if not self.is_configured:
            return None

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Basic {self._get_auth_token()}",
        }

        async with httpx.AsyncClient(base_url=self.base_url) as client:
            resp = await client.request(method, path, headers=headers, **kwargs)
            resp.raise_for_status()
            return resp.json()

    def _get_auth_token(self) -> str:
        """Generate Basic auth token from client_id:client_secret."""
        import base64
        creds = f"{self.client_id}:{self.client_secret}"
        return base64.b64encode(creds.encode()).decode()

    # ── KYC Endpoints (stubs) ──────────────────────────────────

    async def request_kyc(self, identifier: str, id_type: str = "aadhaar") -> Optional[dict]:
        """Initiate a KYC request for a user.

        Args:
            identifier: Phone number or email for KYC link
            id_type: Type of ID — 'aadhaar', 'pan', 'dl', etc.
        """
        return await self._request("POST", "/v2/kyc/request", json={
            "identifier": identifier,
            "id_type": id_type,
        })

    async def get_kyc_status(self, request_id: str) -> Optional[dict]:
        """Check KYC request status."""
        return await self._request("GET", f"/v2/kyc/request/{request_id}")

    # ── eSign Endpoints (stubs) ────────────────────────────────

    async def request_esign(self, document_url: str, signer_email: str) -> Optional[dict]:
        """Request electronic signature on a document."""
        return await self._request("POST", "/v2/esign/request", json={
            "document_url": document_url,
            "signer_email": signer_email,
        })

    async def get_esign_status(self, request_id: str) -> Optional[dict]:
        """Check eSign request status."""
        return await self._request("GET", f"/v2/esign/request/{request_id}")


# Singleton instance
digio_service = DigioService()
