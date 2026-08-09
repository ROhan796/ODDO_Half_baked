"""Seed the database with sample data."""
import asyncio
import uuid
from datetime import datetime, timezone

from app.utils.database import Base, primary_engine, PrimarySessionLocal
from app.models import *  # noqa: ensure all models are imported
from app.models.user import User, UserRole, UserType
from app.models.product import Category, Product, ProductStatus
from app.core.auth import hash_password


CATEGORIES = [
    {"name": "Electronics", "slug": "electronics", "description": "Electronic devices and gadgets"},
    {"name": "Furniture", "slug": "furniture", "description": "Home and office furniture"},
    {"name": "Vehicles", "slug": "vehicles", "description": "Cars, bikes, and commercial vehicles"},
    {"name": "Tools", "slug": "tools", "description": "Power tools and hand tools"},
    {"name": "Construction Equipment", "slug": "construction-equipment", "description": "Heavy machinery and construction tools"},
    {"name": "Event Supplies", "slug": "event-supplies", "description": "Tents, chairs, stages, and event gear"},
    {"name": "Sports & Recreation", "slug": "sports-recreation", "description": "Sports equipment and recreational gear"},
    {"name": "Industrial Machinery", "slug": "industrial-machinery", "description": "Factory and warehouse machinery"},
]

PRODUCTS = [
    # Electronics
    {"name": "MacBook Pro 16-inch M3 Max", "slug": "macbook-pro-16-m3", "category_slug": "electronics", "daily_rate": 1500, "purchase_price": 249990, "deposit_pct": 30},
    {"name": "Sony A7R V Camera", "slug": "sony-a7rv", "category_slug": "electronics", "daily_rate": 800, "purchase_price": 349990, "deposit_pct": 25},
    {"name": "DJI Mavic 3 Pro Drone", "slug": "dji-mavic-3-pro", "category_slug": "electronics", "daily_rate": 600, "purchase_price": 164990, "deposit_pct": 30},
    {"name": "Samsung Galaxy S24 Ultra", "slug": "samsung-s24-ultra", "category_slug": "electronics", "daily_rate": 300, "purchase_price": 134990, "deposit_pct": 25},

    # Furniture
    {"name": "Herman Miller Aeron Chair", "slug": "herman-miller-aeron", "category_slug": "furniture", "daily_rate": 150, "purchase_price": 125000, "deposit_pct": 20},
    {"name": "Standing Desk - Electric", "slug": "standing-desk-electric", "category_slug": "furniture", "daily_rate": 100, "purchase_price": 45000, "deposit_pct": 20},
    {"name": "3-Seater Sofa - Fabric", "slug": "sofa-3-seater", "category_slug": "furniture", "daily_rate": 200, "purchase_price": 65000, "deposit_pct": 25},

    # Vehicles
    {"name": "Toyota Innova Crysta", "slug": "toyota-innova", "category_slug": "vehicles", "daily_rate": 2500, "purchase_price": 1900000, "deposit_pct": 15},
    {"name": "Honda Activa 6G", "slug": "honda-activa", "category_slug": "vehicles", "daily_rate": 400, "purchase_price": 75000, "deposit_pct": 20},

    # Tools
    {"name": "Bosch Hammer Drill", "slug": "bosch-hammer-drill", "category_slug": "tools", "daily_rate": 80, "purchase_price": 8500, "deposit_pct": 30},
    {"name": "DeWalt Circular Saw", "slug": "dewalt-circular-saw", "category_slug": "tools", "daily_rate": 100, "purchase_price": 12000, "deposit_pct": 30},

    # Construction
    {"name": "JCB 3DX Backhoe Loader", "slug": "jcb-3dx", "category_slug": "construction-equipment", "daily_rate": 5000, "purchase_price": 3500000, "deposit_pct": 10},
    {"name": "Concrete Mixer 10/7", "slug": "concrete-mixer", "category_slug": "construction-equipment", "daily_rate": 500, "purchase_price": 85000, "deposit_pct": 20},

    # Event Supplies
    {"name": "20x30ft Event Tent", "slug": "event-tent-20x30", "category_slug": "event-supplies", "daily_rate": 1500, "purchase_price": 120000, "deposit_pct": 20},
    {"name": "50x Plastic Chairs Set", "slug": "plastic-chairs-50", "category_slug": "event-supplies", "daily_rate": 300, "purchase_price": 25000, "deposit_pct": 25},

    # Sports
    {"name": "Treadmill - Commercial", "slug": "treadmill-commercial", "category_slug": "sports-recreation", "daily_rate": 250, "purchase_price": 180000, "deposit_pct": 15},
    {"name": "Cricket Kit - Full Set", "slug": "cricket-kit-full", "category_slug": "sports-recreation", "daily_rate": 150, "purchase_price": 25000, "deposit_pct": 30},
]


async def seed():
    async with primary_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with PrimarySessionLocal() as db:
        # Create admin user
        admin = User(
            id=uuid.uuid4(),
            name="System Admin",
            email="admin@rental.com",
            phone="9999999999",
            password_hash=hash_password("Admin@123"),
            role=UserRole.SUPER_ADMIN,
            user_type=UserType.PERSONAL,
            kyc_status="verified",
            trust_score=100,
            trust_tier="platinum",
        )
        db.add(admin)

        # Create categories
        category_map = {}
        for cat_data in CATEGORIES:
            cat = Category(
                id=uuid.uuid4(),
                name=cat_data["name"],
                slug=cat_data["slug"],
                description=cat_data["description"],
                is_active=True,
            )
            db.add(cat)
            category_map[cat_data["slug"]] = cat

        await db.flush()

        # Create products
        for prod_data in PRODUCTS:
            cat = category_map[prod_data["category_slug"]]
            product = Product(
                id=uuid.uuid4(),
                name=prod_data["name"],
                slug=prod_data["slug"],
                category_id=cat.id,
                status=ProductStatus.AVAILABLE,
                daily_rate=prod_data["daily_rate"],
                purchase_price=prod_data["purchase_price"],
                current_value=prod_data["purchase_price"],
                deposit_percentage=prod_data["deposit_pct"],
                late_fee_rate=prod_data["daily_rate"] * 0.1,
                condition_rating=5,
            )
            db.add(product)

        await db.commit()
        print("Seed data created successfully!")


if __name__ == "__main__":
    asyncio.run(seed())
