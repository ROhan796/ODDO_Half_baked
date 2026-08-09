"""
Backfill user roles based on email-to-role mapping.

Run this script to update existing users in the database
with their correct RBAC roles.

Usage:
    python scripts/backfill_roles.py
"""
import asyncio
from sqlalchemy import select

from app.utils.database import PrimarySessionLocal
from app.models.user import User
from app.core.rbac_config import USER_ROLE_MAP


async def backfill_roles():
    """Update existing users with roles from USER_ROLE_MAP."""
    updated = 0
    skipped = 0

    async with PrimarySessionLocal() as db:
        for email, role in USER_ROLE_MAP.items():
            result = await db.execute(
                select(User).where(User.email == email)
            )
            user = result.scalar_one_or_none()

            if user:
                if user.role != role:
                    old_role = user.role
                    user.role = role
                    updated += 1
                    print(f"  Updated: {email} | {old_role} → {role}")
                else:
                    skipped += 1
                    print(f"  Already correct: {email} | {role}")
            else:
                print(f"  Not found in DB: {email} (will be auto-assigned on first login)")

        await db.commit()

    print(f"\nDone: {updated} updated, {skipped} already correct")


if __name__ == "__main__":
    asyncio.run(backfill_roles())
