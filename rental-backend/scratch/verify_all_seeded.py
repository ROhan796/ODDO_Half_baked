"""Verification script for seeded data and API endpoints."""
import asyncio
from sqlalchemy import select, func
from app.utils.database import PrimarySessionLocal, primary_engine
from app.models.user import User, UserRole
from app.models.group import Group, GroupMember
from app.models.product import Product
from app.models.rental import Rental
from app.models.enterprise import Enterprise
from app.models.agent_task import AgentTask
from app.models.crm import CRMContact

async def verify():
    async with PrimarySessionLocal() as db:
        # Check users count
        res_users = await db.execute(select(func.count(User.id)))
        users_count = res_users.scalar()

        # Check super admins count
        res_sa = await db.execute(select(User).where(User.role == UserRole.SUPER_ADMIN))
        super_admins = res_sa.scalars().all()

        # Check portal users count
        res_pu = await db.execute(select(func.count(User.id)).where(User.role == UserRole.PORTAL_USER))
        portal_users_count = res_pu.scalar()

        # Check products
        res_prods = await db.execute(select(func.count(Product.id)))
        prods_count = res_prods.scalar()

        # Check rentals
        res_rentals = await db.execute(select(func.count(Rental.id)))
        rentals_count = res_rentals.scalar()

        # Check groups
        res_groups = await db.execute(select(func.count(Group.id)))
        groups_count = res_groups.scalar()

        print("=== DATABASE SEEDING VERIFICATION ===")
        print(f"Total Users: {users_count}")
        print(f"Super Admins ({len(super_admins)}): {[u.email for u in super_admins]}")
        print(f"Customer Renters (Portal Users): {portal_users_count}")
        print(f"Total Products: {prods_count}")
        print(f"Total Rentals: {rentals_count}")
        print(f"Total Groups/Clubs: {groups_count}")

if __name__ == "__main__":
    asyncio.run(verify())
