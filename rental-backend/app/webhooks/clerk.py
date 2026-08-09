# app/webhooks/clerk.py
"""Clerk webhook handler — syncs Clerk users to local DB."""
from fastapi import APIRouter, Request, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import hmac
import hashlib
import json

from app.utils.database import PrimarySessionLocal
from app.models.user import User, UserRole, UserType
from app.config import settings
from app.core.rbac_config import get_role_for_email

router = APIRouter()


def _verify_webhook_signature(payload: bytes, signature: str, secret: str) -> bool:
    """Verify Svix webhook signature."""
    if not secret:
        return True  # Skip verification if no secret configured
    try:
        from svix.webhooks import Webhook
        wh = Webhook(secret)
        wh.verify(payload, {"svix-id": signature, "svix-timestamp": "", "svix-signature": ""})
        return True
    except Exception:
        # Fallback: simple HMAC check
        expected = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected, signature)


@router.post("/clerk/webhook")
async def clerk_webhook(request: Request):
    """Handle Clerk webhook events for user sync.

    Supported events:
    - user.created → Create local User record
    - user.updated → Update local User record
    - user.deleted → Soft-delete local User record
    """
    body = await request.body()

    # Verify signature if webhook secret is configured
    signature = request.headers.get("svix-signature", "")
    if settings.CLERK_WEBHOOK_SECRET:
        if not _verify_webhook_signature(body, signature, settings.CLERK_WEBHOOK_SECRET):
            raise HTTPException(status_code=400, detail="Invalid webhook signature")

    event = json.loads(body)
    event_type = event.get("type", "")
    data = event.get("data", {})

    clerk_user_id = data.get("id", "")
    email_addresses = data.get("email_addresses", [])
    primary_email = ""
    for email_obj in email_addresses:
        if email_obj.get("id") == data.get("primary_email_address_id"):
            primary_email = email_obj.get("email_address", "")
            break
    if not primary_email and email_addresses:
        primary_email = email_addresses[0].get("email_address", "")

    phone_numbers = data.get("phone_numbers", [])
    phone = ""
    for phone_obj in phone_numbers:
        if phone_obj.get("id") == data.get("primary_phone_number_id"):
            phone = phone_obj.get("phone_number", "")
            break
    if not phone and phone_numbers:
        phone = phone_numbers[0].get("phone_number", "")

    first_name = data.get("first_name", "")
    last_name = data.get("last_name", "")
    name = f"{first_name} {last_name}".strip() or "New User"
    image_url = data.get("image_url", "")

    async with PrimarySessionLocal() as db:
        if event_type == "user.created":
            # Check if user already exists by clerk_user_id
            result = await db.execute(
                select(User).where(User.clerk_user_id == clerk_user_id)
            )
            existing = result.scalar_one_or_none()

            if not existing:
                # Also check by email to avoid duplicates
                if primary_email:
                    result = await db.execute(
                        select(User).where(User.email == primary_email)
                    )
                    existing = result.scalar_one_or_none()
                    if existing:
                        # Link existing user to Clerk
                        existing.clerk_user_id = clerk_user_id
                        if image_url:
                            existing.profile_photo_url = image_url
                        await db.commit()
                        return {"status": "linked"}

                # Create new user — auto-assign role based on email
                assigned_role = get_role_for_email(primary_email) or UserRole.PORTAL_USER
                user = User(
                    clerk_user_id=clerk_user_id,
                    name=name,
                    email=primary_email or f"{clerk_user_id}@clerk.local",
                    phone=phone or f"0000000000",
                    role=assigned_role,
                    user_type=UserType.PERSONAL,
                    profile_photo_url=image_url or None,
                    kyc_status="pending",
                    trust_score=0,
                    trust_tier="unverified",
                )
                db.add(user)
                await db.commit()
                return {"status": "created", "role": assigned_role}

        elif event_type == "user.updated":
            result = await db.execute(
                select(User).where(User.clerk_user_id == clerk_user_id)
            )
            user = result.scalar_one_or_none()
            if user:
                user.name = name or user.name
                if image_url:
                    user.profile_photo_url = image_url
                await db.commit()
                return {"status": "updated"}

        elif event_type == "user.deleted":
            result = await db.execute(
                select(User).where(User.clerk_user_id == clerk_user_id)
            )
            user = result.scalar_one_or_none()
            if user:
                user.blacklisted = True
                user.blacklist_reason = "Clerk account deleted"
                await db.commit()
                return {"status": "soft_deleted"}

    return {"status": "ignored"}
