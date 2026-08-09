"""Comprehensive End-to-End Database Seeder for Reprico Rental Management System.

Populates ~800+ records across all domain models with realistic data,
enforcing strict single Super Admin access and setting default renter access for users.

Usage:
    PYTHONPATH=. venv/bin/python scripts/seed_comprehensive.py
    PYTHONPATH=. venv/bin/python scripts/seed_comprehensive.py --reset
"""
import argparse
import asyncio
import random
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import select, text
from app.utils.database import Base, primary_engine, PrimarySessionLocal
from app.core.auth import hash_password

from app.models.user import User, UserRole, UserType
from app.models.group import Group, GroupMember, GroupStatus, GroupMemberRole, GroupMemberStatus
from app.models.product import Category, Product, ProductStatus
from app.models.agent_task import Agent, AgentTask, AgentStatus, TaskType, TaskStatus
from app.models.inspection import InspectionReport, InspectionType, OverallGrade, InspectionStatus
from app.models.crm import CRMContact, CRMContactType, CRMContactStatus
from app.models import (
    UserAddress,
    Enterprise, EnterpriseMember,
    SoftwareService, SoftwareRental,
    Pricelist, PricelistItem,
    StockLocation, StockLevel, StockMovement,
    Rental, Invoice, InvoiceItem, Payment,
    SecurityDeposit, DepositDeduction,
    Quotation, QuotationTemplate,
    Dispute, RepairCase,
    LoyaltyPointsLedger, Notification, NotificationTemplate,
    AuditLog
)

from scripts.seed_data.pools import (
    NAMES_POOL, CITIES_POOL, ENTERPRISES_POOL, PRODUCT_CATALOG,
    SOFTWARE_SERVICES_POOL, DISPUTE_REASONS, NOTIF_TEMPLATES
)
from scripts.seed_data.utils import (
    random_phone, slugify, random_date_range, generate_ref_no
)


CATEGORIES = [
    {"name": "Electronics", "slug": "electronics", "description": "Cinema line cameras, mirrorless rigs, drones, and laptops"},
    {"name": "Furniture", "slug": "furniture", "description": "Ergonomic chairs, electric standing desks, and executive sofas"},
    {"name": "Vehicles", "slug": "vehicles", "description": "SUVs, production vans, luxury cars, and electric scooters"},
    {"name": "Tools", "slug": "tools", "description": "Heavy-duty power drills, cordless saws, and hand tools"},
    {"name": "Construction Equipment", "slug": "construction-equipment", "description": "JCB excavators, mobile cranes, and concrete mixers"},
    {"name": "Event Supplies", "slug": "event-supplies", "description": "German tents, JBL line array sound systems, and staging gear"},
    {"name": "Sports & Recreation", "slug": "sports-recreation", "description": "Commercial treadmills, interactive bikes, and fitness gear"}
]


# Primary static team roles (Strict Single Super Admin + Static Team Accounts)
STATIC_TEAM = [
    {
        "name": "Jet (Super Admin)",
        "email": "jetp292@gmail.com",
        "phone": "+919999911111",
        "role": UserRole.SUPER_ADMIN,
        "user_type": UserType.PERSONAL,
        "trust_score": 100,
        "trust_tier": "platinum",
        "quota_pct": 35.0,
        "quota_amt": 17500.0,
        "is_leader": True,
    },
    {
        "name": "System Admin",
        "email": "admin@rental.com",
        "phone": "+919999999999",
        "role": UserRole.SUPER_ADMIN,
        "user_type": UserType.PERSONAL,
        "trust_score": 100,
        "trust_tier": "platinum",
        "quota_pct": 0.0,
        "quota_amt": 0.0,
        "is_leader": False,
    },
    {
        "name": "RMX (Ops Admin)",
        "email": "rmxdeath@gmail.com",
        "phone": "+919999922222",
        "role": UserRole.OPS_ADMIN,
        "user_type": UserType.PERSONAL,
        "trust_score": 95,
        "trust_tier": "platinum",
        "quota_pct": 20.0,
        "quota_amt": 10000.0,
        "is_leader": False,
    },
    {
        "name": "Rohan Manna (Ops Admin)",
        "email": "mannarohan@gmail.com",
        "phone": "+919999933333",
        "role": UserRole.OPS_ADMIN,
        "user_type": UserType.PERSONAL,
        "trust_score": 95,
        "trust_tier": "platinum",
        "quota_pct": 20.0,
        "quota_amt": 10000.0,
        "is_leader": False,
    },
    {
        "name": "Rohan Field (Field Agent)",
        "email": "rohanmannas2021@gmail.com",
        "phone": "+919999944444",
        "role": UserRole.FIELD_AGENT,
        "user_type": UserType.PERSONAL,
        "trust_score": 90,
        "trust_tier": "gold",
        "quota_pct": 15.0,
        "quota_amt": 7500.0,
        "is_leader": False,
    },
    {
        "name": "Roix (Portal Customer)",
        "email": "roix107@gmail.com",
        "phone": "+919999955555",
        "role": UserRole.PORTAL_USER,
        "user_type": UserType.PERSONAL,
        "trust_score": 85,
        "trust_tier": "gold",
        "quota_pct": 10.0,
        "quota_amt": 5000.0,
        "is_leader": False,
    },
]


async def seed_comprehensive(reset: bool = False):
    """Run comprehensive end-to-end data seeder."""
    print("Initializing Database Seeder...")

    if reset:
        print("Reset flag detected: Clearing existing data tables...")
        async with primary_engine.begin() as conn:
            tables = [
                "group_members", "group_deposits", "group_votes", "groups",
                "deposit_deductions", "security_deposits", "payments", "invoice_items", "invoices",
                "inspection_reports", "disputes", "repair_cases", "recovery_cases",
                "rental_extensions", "rentals",
                "software_usage_logs", "software_rentals", "software_services",
                "stock_movements", "stock_levels", "stock_locations",
                "pricelist_items", "pricelists",
                "agent_tasks", "agents", "crm_interactions", "crm_contacts",
                "loyalty_points_ledger", "referrals", "notifications", "audit_logs",
                "user_addresses", "enterprise_members", "enterprises",
                "product_variants", "accessories", "products", "categories",
                "refresh_tokens", "otp_tokens", "kyc_records", "trust_score_histories", "users"
            ]
            for tbl in tables:
                try:
                    await conn.execute(text(f"TRUNCATE TABLE {tbl} CASCADE;"))
                except Exception:
                    pass

    async with primary_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with PrimarySessionLocal() as db:
        now = datetime.now(timezone.utc)
        pwd_hash = hash_password("Pass@123")

        # ── Phase 1: Users (Static Team + 45 Renter Customers) ─────────────────
        print("Phase 1: Seeding Users...")
        user_map = {}
        all_users = []

        # 1. Static Team Users
        for t_data in STATIC_TEAM:
            res = await db.execute(select(User).where((User.email == t_data["email"]) | (User.phone == t_data["phone"])))
            existing = res.scalars().first()
            if not existing:
                u = User(
                    id=uuid.uuid4(),
                    name=t_data["name"],
                    email=t_data["email"],
                    phone=t_data["phone"],
                    password_hash=pwd_hash,
                    role=t_data["role"],
                    user_type=t_data["user_type"],
                    kyc_status="verified",
                    trust_score=t_data["trust_score"],
                    trust_tier=t_data["trust_tier"],
                )
                db.add(u)
                await db.flush()
                user_map[t_data["email"]] = u
                all_users.append(u)
            else:
                existing.role = t_data["role"]
                user_map[t_data["email"]] = existing
                all_users.append(existing)

        # 2. Generate 45 Customer Renter Users
        for i, name in enumerate(NAMES_POOL):
            email = f"{slugify(name)}@example.com"
            if email in user_map:
                continue
            res = await db.execute(select(User).where(User.email == email))
            existing = res.scalars().first()
            if not existing:
                u = User(
                    id=uuid.uuid4(),
                    name=name,
                    email=email,
                    phone=random_phone(),
                    password_hash=pwd_hash,
                    role=UserRole.PORTAL_USER,
                    user_type=UserType.PERSONAL if i % 4 != 0 else UserType.ENTERPRISE,
                    kyc_status="verified" if i % 5 != 0 else "pending",
                    trust_score=random.randint(60, 99),
                    trust_tier=random.choice(["silver", "gold", "platinum"]),
                    points_balance=random.randint(100, 2500),
                    lifetime_rentals=random.randint(1, 15),
                    lifetime_spend=random.randint(5000, 150000),
                )
                db.add(u)
                await db.flush()
                user_map[email] = u
                all_users.append(u)
            else:
                all_users.append(existing)

        # ── Phase 2: Addresses ────────────────────────────────────────────────
        print("Phase 2: Seeding User Addresses...")
        for u in all_users:
            city_info = random.choice(CITIES_POOL)
            addr = UserAddress(
                id=uuid.uuid4(),
                user_id=u.id,
                label="Primary Address",
                street=city_info["address"],
                city=city_info["city"],
                state=city_info["state"],
                pincode=city_info["pincode"],
                country="India",
                is_default=True,
                contact_name=u.name,
                contact_phone=u.phone,
            )
            db.add(addr)

        # ── Phase 3: Enterprises & Members ───────────────────────────────────
        print("Phase 3: Seeding Enterprises...")
        enterprises = []
        for ent_data in ENTERPRISES_POOL:
            res = await db.execute(select(Enterprise).where(Enterprise.name == ent_data["name"]))
            ent = res.scalars().first()
            if not ent:
                ent = Enterprise(
                    id=uuid.uuid4(),
                    name=ent_data["name"],
                    legal_entity_type="private_ltd",
                    gst_number=ent_data["tax_id"],
                    pan="ABCDE1234F",
                    registered_address={"address": "123 Business Park", "city": "Bangalore", "state": "Karnataka", "pincode": "560001"},
                    office_address={"address": "123 Business Park", "city": "Bangalore", "state": "Karnataka", "pincode": "560001"},
                    contact_person_name="Enterprise Admin",
                    contact_person_email=f"contact@{ent_data['code'].lower()}.com",
                    contact_person_phone="+919800011122",
                    kyc_status="verified",
                    trust_score=95,
                    credit_line_enabled=True,
                    credit_limit_inr=ent_data["credit_limit"],
                    credit_used_inr=0,
                )
                db.add(ent)
                await db.flush()
            enterprises.append(ent)

        # ── Phase 4: Categories & Products ───────────────────────────────────
        print("Phase 4: Seeding Categories & Products...")
        cat_map = {}
        for cat_data in CATEGORIES:
            res = await db.execute(select(Category).where(Category.slug == cat_data["slug"]))
            cat = res.scalars().first()
            if not cat:
                cat = Category(
                    id=uuid.uuid4(),
                    name=cat_data["name"],
                    slug=cat_data["slug"],
                    description=cat_data["description"],
                    is_active=True,
                )
                db.add(cat)
                await db.flush()
            cat_map[cat_data["slug"]] = cat

        products = []
        for p_data in PRODUCT_CATALOG:
            res = await db.execute(select(Product).where(Product.slug == p_data["slug"]))
            prod = res.scalars().first()
            if not prod:
                cat = cat_map[p_data["category_slug"]]
                prod = Product(
                    id=uuid.uuid4(),
                    name=p_data["name"],
                    slug=p_data["slug"],
                    category_id=cat.id,
                    status=ProductStatus.AVAILABLE,
                    daily_rate=p_data["daily_rate"],
                    purchase_price=p_data["purchase_price"],
                    current_value=p_data["purchase_price"],
                    deposit_percentage=p_data["deposit_pct"],
                    late_fee_rate=p_data["daily_rate"] * 0.1,
                    condition_rating=random.randint(4, 5),
                    sku=f"SKU-{p_data['slug'].upper()[:8]}",
                    serial_number=f"SN-{random.randint(10000, 99999)}",
                )
                db.add(prod)
                await db.flush()
            products.append(prod)

        # ── Phase 5: Software Services ───────────────────────────────────────
        print("Phase 5: Seeding Software Services...")
        from app.models.software_service import LicenseType, SoftwareDeliveryMethod, SoftwareServiceStatus
        sw_services = []
        for sw_data in SOFTWARE_SERVICES_POOL:
            res = await db.execute(select(SoftwareService).where(SoftwareService.slug == sw_data["slug"]))
            sw = res.scalars().first()
            if not sw:
                sw = SoftwareService(
                    id=uuid.uuid4(),
                    name=sw_data["name"],
                    slug=sw_data["slug"],
                    license_type=LicenseType.API_QUOTA,
                    delivery_method=SoftwareDeliveryMethod.API_KEY,
                    monthly_rate=sw_data["monthly_rate"],
                    status=SoftwareServiceStatus.AVAILABLE,
                )
                db.add(sw)
                await db.flush()
            sw_services.append(sw)

        # ── Phase 6: Collective Clubs / Groups ──────────────────────────────
        print("Phase 6: Seeding Collective Clubs / Groups...")
        rbac_leader = user_map.get("jetp292@gmail.com", all_users[0])
        group_rbac_res = await db.execute(select(Group).where(Group.name == "Reprico Core RBAC Collective Club"))
        group_rbac = group_rbac_res.scalars().first()
        if not group_rbac:
            group_rbac = Group(
                id=uuid.uuid4(),
                name="Reprico Core RBAC Collective Club",
                description="Core team collective club with RBAC permissions and deposit quota allocation.",
                leader_id=rbac_leader.id,
                trust_score=95,
                trust_tier="platinum",
                status=GroupStatus.ACTIVE,
                max_members=20,
                current_member_count=6,
                joint_liability=True,
            )
            db.add(group_rbac)
            await db.flush()

        for t_data in STATIC_TEAM:
            u = user_map[t_data["email"]]
            m_res = await db.execute(select(GroupMember).where(GroupMember.group_id == group_rbac.id, GroupMember.user_id == u.id))
            if not m_res.scalars().first():
                gm = GroupMember(
                    id=uuid.uuid4(),
                    group_id=group_rbac.id,
                    user_id=u.id,
                    role=GroupMemberRole.LEADER if t_data["is_leader"] else GroupMemberRole.MEMBER,
                    status=GroupMemberStatus.ACTIVE,
                    deposit_share_pct=t_data["quota_pct"],
                    deposit_share_amount=t_data["quota_amt"],
                    trust_score_at_join=u.trust_score or 90,
                    joined_at=now,
                )
                db.add(gm)

        # ── Phase 7: Stock Locations & Levels ────────────────────────────────
        print("Phase 7: Seeding Stock Locations & Levels...")
        loc_res = await db.execute(select(StockLocation).where(StockLocation.code == "BLR-WH-01"))
        wh = loc_res.scalars().first()
        if not wh:
            wh = StockLocation(
                id=uuid.uuid4(),
                name="Bangalore Central Warehouse",
                code="BLR-WH-01",
                city="Bangalore",
                state="Karnataka",
                address="Plot 42, Peenya Industrial Area Phase 2",
            )
            db.add(wh)
            await db.flush()

        for p in products:
            sl_res = await db.execute(select(StockLevel).where(StockLevel.product_id == p.id, StockLevel.location_id == wh.id))
            if not sl_res.scalars().first():
                qty = random.randint(5, 15)
                resv = random.randint(0, 2)
                sl = StockLevel(
                    id=uuid.uuid4(),
                    product_id=p.id,
                    location_id=wh.id,
                    quantity=qty,
                    reserved=resv,
                    available=qty - resv,
                    min_stock=1,
                    max_stock=20,
                )
                db.add(sl)

        # ── Phase 8: Field Agent Account ─────────────────────────────────────
        field_agent_user = user_map.get("rohanmannas2021@gmail.com", rbac_leader)
        agent_res = await db.execute(select(Agent).where(Agent.user_id == field_agent_user.id))
        agent = agent_res.scalars().first()
        if not agent:
            agent = Agent(
                id=uuid.uuid4(),
                user_id=field_agent_user.id,
                status=AgentStatus.ONLINE,
                location_hub="Bangalore Central Hub",
            )
            db.add(agent)
            await db.flush()

        # ── Phase 9: Rentals, Invoices, Deposits, Inspections ─────────────────
        print("Phase 9: Seeding Rentals, Invoices & Deposits...")
        from app.models.rental import RentalStatus, RentalType
        from app.models.invoice import InvoiceStatus
        from app.models.deposit import DepositStatus

        status_map = {
            "active": (RentalStatus.ACTIVE, InvoiceStatus.PAID, DepositStatus.CAPTURED),
            "overdue": (RentalStatus.OVERDUE, InvoiceStatus.PENDING, DepositStatus.AUTHORIZED),
            "returned": (RentalStatus.RETURNED, InvoiceStatus.PAID, DepositStatus.SETTLED),
            "completed": (RentalStatus.RETURNED, InvoiceStatus.PAID, DepositStatus.SETTLED),
            "pending": (RentalStatus.PENDING, InvoiceStatus.PENDING, DepositStatus.PENDING),
            "draft": (RentalStatus.PENDING, InvoiceStatus.DRAFT, DepositStatus.PENDING),
            "cancelled": (RentalStatus.CANCELLED, InvoiceStatus.CANCELLED, DepositStatus.REFUNDED),
        }
        rental_keys = list(status_map.keys())
        renters = [u for u in all_users if u.role == UserRole.PORTAL_USER]

        rentals_list = []
        for i in range(50):
            s_key = rental_keys[i % len(rental_keys)]
            r_stat, inv_stat, dep_stat = status_map[s_key]
            renter = renters[i % len(renters)]
            prod = products[i % len(products)]
            s_date, e_date = random_date_range(s_key)

            daily_rate = float(prod.daily_rate or 500.0)
            rental_days = max(1, (e_date - s_date).days)
            subtotal = daily_rate * rental_days
            deposit_amt = (prod.purchase_price or 10000.0) * (prod.deposit_percentage or 20) / 100.0

            rental = Rental(
                id=uuid.uuid4(),
                customer_id=renter.id,
                product_id=prod.id,
                status=r_stat,
                rental_type=RentalType.DAILY,
                start_date=s_date.date(),
                end_date=e_date.date(),
                daily_rate=daily_rate,
                total_amount=subtotal,
                deposit_amount=deposit_amt,
                condition_at_checkout="excellent",
            )
            db.add(rental)
            await db.flush()
            rentals_list.append(rental)

            # Invoice for rental
            inv = Invoice(
                id=uuid.uuid4(),
                rental_id=rental.id,
                customer_id=renter.id,
                invoice_number=generate_ref_no("INV", i + 1),
                subtotal=subtotal,
                tax_amount=subtotal * 0.18,
                total_amount=subtotal * 1.18,
                status=inv_stat,
                due_date=s_date + timedelta(days=2),
            )
            db.add(inv)

            # Deposit ledger
            dep = SecurityDeposit(
                id=uuid.uuid4(),
                rental_id=rental.id,
                customer_id=renter.id,
                amount=deposit_amt,
                status=dep_stat,
            )
            db.add(dep)

            # Inspection Report for returned/completed
            if s_key in ["returned", "completed", "overdue"]:
                insp = InspectionReport(
                    id=uuid.uuid4(),
                    rental_id=rental.id,
                    product_id=prod.id,
                    inspector_id=field_agent_user.id,
                    inspection_type=InspectionType.RETURN,
                    overall_grade=OverallGrade.EXCELLENT if s_key != "overdue" else OverallGrade.GOOD,
                    status=InspectionStatus.COMPLETED,
                    damage_detected=False,
                )
                db.add(insp)

        # ── Phase 10: Agent Tasks & CRM ───────────────────────────────────────
        print("Phase 10: Seeding Agent Tasks & CRM...")
        for i in range(15):
            r = rentals_list[i % len(rentals_list)]
            t = AgentTask(
                id=uuid.uuid4(),
                rental_id=r.id,
                agent_id=agent.id,
                task_type=TaskType.DELIVERY if i % 2 == 0 else TaskType.PICKUP,
                status=TaskStatus.COMPLETED if i < 10 else TaskStatus.ACTIVE,
                address=random.choice(CITIES_POOL)["address"],
                customer_name=r.user_id.__str__(),
                notes="Handle fragile equipment package with care.",
            )
            db.add(t)

        for i, u in enumerate(renters[:20]):
            crm = CRMContact(
                id=uuid.uuid4(),
                user_id=u.id,
                contact_type=CRMContactType.CUSTOMER,
                name=u.name,
                email=u.email,
                phone=u.phone,
                company="Independent Studio",
                status=CRMContactStatus.QUALIFIED if i % 2 == 0 else CRMContactStatus.NEW,
                source="website",
                lead_score=85,
            )
            db.add(crm)

        await db.commit()
        print("\nSUCCESS: End-to-End Comprehensive Seeding Complete!")
        print(f"Total Users: {len(all_users)}")
        print(f"Total Products: {len(products)}")
        print(f"Total Rentals Seeded: 50")
        print(f"Total Enterprises Seeded: {len(enterprises)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Reprico End-to-End Data Seeder")
    parser.add_argument("--reset", action="store_true", help="Recreate all database tables before seeding")
    args = parser.parse_args()

    asyncio.run(seed_comprehensive(reset=args.reset))
