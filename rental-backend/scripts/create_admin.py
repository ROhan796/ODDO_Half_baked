"""Create a super_admin user from the command line."""
import argparse
import asyncio
import sys
from app.utils.database import primary_engine, PrimarySessionLocal, Base
from app.models import *  # noqa: ensure all models are imported
from app.models.user import User, UserRole, UserType
from app.core.auth import hash_password


async def create_admin(name: str, email: str, phone: str, password: str):
    async with primary_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with PrimarySessionLocal() as db:
        from sqlalchemy import select

        existing = await db.execute(
            select(User).where((User.email == email) | (User.phone == phone))
        )
        if existing.scalar_one_or_none():
            print(f"Error: User with email '{email}' or phone '{phone}' already exists.")
            return

        admin = User(
            name=name,
            email=email,
            phone=phone,
            password_hash=hash_password(password),
            role=UserRole.SUPER_ADMIN,
            user_type=UserType.PERSONAL,
            kyc_status="verified",
            trust_score=100,
            trust_tier="platinum",
        )
        db.add(admin)
        await db.commit()
        print(f"Super admin '{name}' created successfully! (email={email})")


def main():
    parser = argparse.ArgumentParser(description="Create a super_admin user")
    parser.add_argument("--name", required=True, help="Full name of the admin")
    parser.add_argument("--email", required=True, help="Email address")
    parser.add_argument("--phone", required=True, help="Phone number (10 digits)")
    parser.add_argument("--password", required=True, help="Password (min 8 chars)")
    args = parser.parse_args()

    if len(args.password) < 8:
        print("Error: Password must be at least 8 characters.")
        sys.exit(1)
    if len(args.phone) != 10 or not args.phone.isdigit():
        print("Error: Phone must be a 10-digit number.")
        sys.exit(1)

    asyncio.run(create_admin(args.name, args.email, args.phone, args.password))


if __name__ == "__main__":
    main()
