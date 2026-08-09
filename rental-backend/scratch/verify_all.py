import asyncio
from sqlalchemy import select
from app.utils.database import PrimarySessionLocal
from app.models.user import User
from app.models.group import Group, GroupMember
from app.api.v1.auth import normalize_phone


async def verify():
    async with PrimarySessionLocal() as db:
        # 1. Verify Users
        users_res = await db.execute(select(User))
        users = users_res.scalars().all()
        print(f"Total Users in DB: {len(users)}")
        for u in users:
            print(f" - User: {u.name} | Email: {u.email} | Phone: {u.phone} | Role: {u.role}")

        # 2. Verify Club / Group
        groups_res = await db.execute(select(Group))
        groups = groups_res.scalars().all()
        print(f"\nTotal Groups/Clubs in DB: {len(groups)}")
        for g in groups:
            print(f" - Group: '{g.name}' | Leader ID: {g.leader_id} | Status: {g.status} | Members Count: {g.current_member_count}")

            # 3. Verify Members & Quotas
            members_res = await db.execute(
                select(GroupMember, User).join(User, GroupMember.user_id == User.id).where(GroupMember.group_id == g.id)
            )
            members = members_res.all()
            print(f"   Members in '{g.name}' ({len(members)} found):")
            for m, u in members:
                print(f"    * Member: {u.name} ({u.email}) | Club Role: {m.role} | Quota Share: {m.deposit_share_pct}% ({m.deposit_share_amount} INR) | User Role: {u.role}")

        # 4. Test Phone Normalization
        test_phones = ["+91 98765 43210", "9876543210", "+91-98765-43210", "rahul.sharma@example.com"]
        print("\nPhone Normalization Verification:")
        for tp in test_phones:
            print(f"   '{tp}' -> '{normalize_phone(tp)}'")


if __name__ == "__main__":
    asyncio.run(verify())
