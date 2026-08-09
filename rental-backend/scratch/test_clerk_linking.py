import asyncio
from sqlalchemy import select
from app.utils.database import PrimarySessionLocal
from app.models.user import User
from app.api.deps import get_current_user
from unittest.mock import MagicMock


async def test_clerk_linking():
    async with PrimarySessionLocal() as db:
        # Simulate a Clerk payload for jetp292@gmail.com
        test_email = "jetp292@gmail.com"
        mock_clerk_id = "user_clerk_test_jet_123"

        res = await db.execute(select(User).where(User.email == test_email))
        user = res.scalars().first()
        print(f"Pre-test: User {user.name} ({user.email}) -> clerk_user_id: {user.clerk_user_id}, role: {user.role}")

        # Link clerk_user_id
        if not user.clerk_user_id:
            user.clerk_user_id = mock_clerk_id
            await db.commit()

        res_after = await db.execute(select(User).where(User.clerk_user_id == mock_clerk_id))
        user_after = res_after.scalars().first()
        print(f"Post-test: Found user by Clerk ID '{mock_clerk_id}': {user_after.name} ({user_after.email}), role: {user_after.role}")


if __name__ == "__main__":
    asyncio.run(test_clerk_linking())
