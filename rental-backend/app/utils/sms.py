# app/utils/sms.py
import httpx
from typing import Optional
from app.config import settings


class SMSClient:
    """SMS client using MSG91 API."""

    def __init__(self):
        self.api_key = settings.MSG91_API_KEY
        self.template_id = settings.MSG91_TEMPLATE_ID
        self.base_url = "https://api.msg91.com/api/v5"

    async def send_otp(
        self,
        phone: str,
        otp: str,
    ) -> bool:
        """Send OTP via MSG91."""
        if not self.api_key:
            return False

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/otp",
                headers={
                    "authkey": self.api_key,
                    "Content-Type": "application/json",
                },
                json={
                    "mobile": phone,
                    "otp": otp,
                    "template_id": self.template_id,
                },
            )
            return response.status_code == 200

    async def send_sms(
        self,
        phone: str,
        message: str,
    ) -> bool:
        """Send SMS via MSG91."""
        if not self.api_key:
            return False

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/sms",
                headers={
                    "authkey": self.api_key,
                    "Content-Type": "application/json",
                },
                json={
                    "mobile": phone,
                    "message": message,
                },
            )
            return response.status_code == 200


sms_client = SMSClient()
