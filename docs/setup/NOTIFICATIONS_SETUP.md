# Notification Services Setup (Resend + MSG91)

## Overview

Reprico uses two notification services:
- **Resend** → Transactional emails (invoices, OTPs, notifications)
- **MSG91** → SMS/OTP delivery (Indian phone numbers)

## Email - Resend Setup

### Step 1: Create Resend Account

1. Go to [https://resend.com](https://resend.com)
2. Sign up with GitHub or email
3. Free tier: 3,000 emails/month, 100/day

### Step 2: Add & Verify Domain

1. Resend Dashboard → **Domains** → **Add Domain**
2. Enter your domain: `yourdomain.com`
3. Add DNS records (provided by Resend):

```
Type: TXT
Name: resend._domainkey
Value: p=MIGfMA...

Type: CNAME
Name: resend
Value: feedback-smtp.yourdomain.com

Type: MX
Name: mail.yourdomain.com
Value: feedback-smtp.com
Priority: 10
```

4. Wait for DNS propagation (5-60 minutes)
5. Click **Verify**

### Step 3: Get API Key

1. Resend Dashboard → **API Keys**
2. Click **"Create API Key"**

| Setting | Value |
|---------|-------|
| **Name** | `reprico-backend` |
| **Permission** | Full access |
| **Domain** | Your verified domain |

Copy the API key: `re_xxxxxxxxxxxxxxxx`

### Step 4: Configure Environment Variables

```bash
# rental-backend/.env

RESEND_API_KEY=re_xxxxxxxxxxxxxxxx
EMAIL_FROM=noreply@yourdomain.com
```

### Step 5: Email Client Implementation

Already implemented in `app/utils/email.py`:

```python
import httpx
from typing import Optional
from app.config import settings


class EmailClient:
    def __init__(self):
        self.api_key = settings.RESEND_API_KEY
        self.from_email = settings.EMAIL_FROM
        self.base_url = "https://api.resend.com"

    async def send_email(
        self, to: str | list[str], subject: str, html: str, text: Optional[str] = None
    ) -> bool:
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
```

### Step 6: Email Templates

Create HTML templates for common emails:

```python
# app/templates/emails/
# ├── welcome.html
# ├── otp.html
# ├── invoice.html
# ├── payment_confirmation.html
# ├── rental_reminder.html
# └── base.html (layout)
```

Example usage:

```python
from app.utils.email import email_client

await email_client.send_email(
    to="user@example.com",
    subject="Your Invoice #INV-2024-001",
    html=render_template("invoice.html", {
        "user_name": "John",
        "invoice_number": "INV-2024-001",
        "amount": "₹15,000",
    }),
)
```

---

## SMS - MSG91 Setup

### Step 1: Create MSG91 Account

1. Go to [https://msg91.com](https://msg91.com)
2. Sign up and verify your phone number
3. Complete business verification (for transactional SMS)

### Step 2: Create SMS Template

1. MSG91 Dashboard → **SMS** → **Templates**
2. Click **"Create Template"**

| Setting | Value |
|---------|-------|
| **Template Name** | `OTP Verification` |
| **Type** | Transactional |
| **Template** | `Your OTP for Reprico is {{1}}. Valid for 5 minutes. Do not share.` |

3. Submit for approval (takes 2-24 hours)

### Step 3: Get API Key

1. MSG91 Dashboard → **Settings** → **API Keys**
2. Copy your **Auth Key**

### Step 4: Configure Environment Variables

```bash
# rental-backend/.env

MSG91_API_KEY=your_auth_key
MSG91_TEMPLATE_ID=your_template_id
```

### Step 5: SMS Client Implementation

Already implemented in `app/utils/sms.py`:

```python
import httpx
from app.config import settings


class SMSClient:
    def __init__(self):
        self.api_key = settings.MSG91_API_KEY
        self.template_id = settings.MSG91_TEMPLATE_ID
        self.base_url = "https://api.msg91.com/api/v5"

    async def send_otp(self, phone: str, otp: str) -> bool:
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

    async def send_sms(self, phone: str, message: str) -> bool:
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
```

### Step 6: OTP Flow

```python
# app/services/auth_service.py
import random
import string
from app.utils.sms import sms_client
from app.utils.redis import get_redis


async def request_otp(phone: str) -> str:
    """Generate and send OTP."""
    otp = "".join(random.choices(string.digits, k=6))

    # Store in Redis with 5-minute TTL
    redis = await get_redis()
    await redis.set(f"otp:{phone}", otp, ex=300)

    # Send via MSG91
    await sms_client.send_otp(phone, otp)

    return otp


async def verify_otp(phone: str, otp: str) -> bool:
    """Verify OTP from Redis."""
    redis = await get_redis()
    stored_otp = await redis.get(f"otp:{phone}")

    if stored_otp and stored_otp == otp:
        await redis.delete(f"otp:{phone}")
        return True
    return False
```

---

## Environment Variables Summary

```bash
# Email (Resend)
RESEND_API_KEY=re_xxxxx
EMAIL_FROM=noreply@yourdomain.com

# SMS (MSG91)
MSG91_API_KEY=your_auth_key
MSG91_TEMPLATE_ID=your_template_id
```

## Cost Comparison

| Service | Free Tier | Paid |
|---------|-----------|------|
| Resend | 3,000/month | $20/month for 50K |
| MSG91 | 100 SMS/day | ₹0.15-0.20 per SMS |

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Emails not received | Check spam, verify domain DNS |
| 422 error (Resend) | Domain not verified or wrong `from` address |
| OTP not received | Check MSG91 template approval, phone format (+91) |
| SMS delayed | MSG91 queue, check dashboard for delivery status |
| Rate limit hit | Resend: 100/day on free; MSG91: depends on plan |
