# app/utils/email.py
import httpx
from typing import Optional
from app.config import settings


class EmailClient:
    """Email client using Resend API."""

    def __init__(self):
        self.api_key = settings.RESEND_API_KEY
        self.from_email = settings.EMAIL_FROM
        self.base_url = "https://api.resend.com"

    async def send_email(
        self,
        to: str | list[str],
        subject: str,
        html: str,
        text: Optional[str] = None,
    ) -> bool:
        """Send email via Resend."""
        if not self.api_key:
            return False

        recipients = [to] if isinstance(to, str) else to

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/emails",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "from": self.from_email,
                    "to": recipients,
                    "subject": subject,
                    "html": html,
                    "text": text,
                },
            )
            return response.status_code == 200


email_client = EmailClient()
