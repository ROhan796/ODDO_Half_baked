# Data Seeder Plan & Architecture

## Overview

The Data Seeder is a comprehensive script that generates realistic, interconnected test data matching Reprico's system architecture. It populates 300-600 records across all tables, maintaining referential integrity and business logic constraints.

## Goals

1. Generate **300-600 records** across all entities
2. Maintain **referential integrity** (foreign keys always valid)
3. Follow **business logic** (status transitions, date ranges, amounts)
4. Create **edge cases** (overdue rentals, disputed invoices, low stock)
5. Seed data that exercises **all API endpoints** and **frontend flows**

## Data Volume Targets

| Entity | Count | Notes |
|--------|-------|-------|
| Users | 50 | 5 admins, 10 enterprise, 35 customers |
| Enterprises | 5 | With members and credit lines |
| Groups | 10 | 3-15 members each |
| Categories | 8 | All existing categories |
| Products | 100 | Across all categories |
| Rentals | 80 | Various statuses (active, completed, overdue, disputed) |
| Invoices | 70 | Linked to rentals, various payment states |
| Payments | 60 | Paid, pending, failed, refunded |
| Quotations | 40 | Draft, accepted, rejected, expired |
| Deposits | 50 | Active, refunded, partially deducted |
| Disputes | 15 | Open, resolved, escalated |
| Repairs | 20 | Pending, in-progress, completed |
| Notifications | 100 | Various types and read states |
| Audit Logs | 200 | Across all operations |
| CRM Contacts | 30 | With interactions and tags |
| Stock Movements | 60 | Inbound, outbound, transfers |
| Loyalty Entries | 40 | Points earned and redeemed |
| Inspection Reports | 25 | Pre/post rental inspections |
| Agent Tasks | 20 | Various statuses |
| Software Services | 5 | With rental records |

**Total: ~900 records**

## Entity Relationship Flow

```
Users ──┬── Enterprises (members)
        ├── Groups (members)
        ├── Rentals ──┬── Invoices ── Payments
        │             ├── Quotations
        │             ├── Deposits ── Deductions
        │             ├── Custody Events
        │             └── Disputes ── Resolution
        ├── CRM Contacts ── Interactions
        ├── Loyalty Ledger
        ├── Notifications
        └── Addresses

Products ──┬── Categories
           ├── Accessories
           ├── Stock Levels
           ├── Stock Movements
           └── Availability Blocks

Agents ──┬── Tasks
         └── Inspection Reports

Software Services ── Software Rentals ── Usage Logs
```

## Implementation Plan

### Phase 1: Core User & Product Data

```python
# scripts/seed_comprehensive.py
import asyncio
import uuid
import random
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from app.utils.database import Base, primary_engine, PrimarySessionLocal
from app.models import *  # noqa
from app.core.auth import hash_password


class DataSeeder:
    def __init__(self, db):
        self.db = db
        self.user_ids = []
        self.product_ids = []
        self.category_ids = []
        self.enterprise_ids = []
        self.group_ids = []

    async def seed_all(self):
        """Master seed method."""
        await self.seed_users()
        await self.seed_enterprises()
        await self.seed_groups()
        await self.seed_categories()
        await self.seed_products()
        await self.seed_stock()
        await self.seed_rentals()
        await self.seed_invoices()
        await self.seed_deposits()
        await self.seed_quotations()
        await self.seed_disputes()
        await self.seed_repairs()
        await self.seed_notifications()
        await self.seed_crm()
        await self.seed_loyalty()
        await self.seed_inspections()
        await self.seed_agent_tasks()
        await self.seed_software_services()
        await self.seed_audit_logs()

        await self.db.commit()
        print(f"Seeded {self.count_all()} records successfully!")
```

### Phase 2: Realistic Name & Data Generation

```python
# Data pools for realistic generation
FIRST_NAMES = [
    "Aarav", "Vivaan", "Aditya", "Arjun", "Sai",
    "Ananya", "Diya", "Priya", "Kavya", "Meera",
    "Rahul", "Vikram", "Sanjay", "Deepak", "Amit",
    "Neha", "Pooja", "Ritu", "Sonia", "Tanvi",
]

LAST_NAMES = [
    "Sharma", "Patel", "Kumar", "Singh", "Gupta",
    "Reddy", "Nair", "Iyer", "Mukherjee", "Das",
    "Joshi", "Verma", "Choudhary", "Tiwari", "Mishra",
]

CITIES = [
    "Mumbai", "Delhi", "Bangalore", "Hyderabad", "Chennai",
    "Pune", "Kolkata", "Ahmedabad", "Jaipur", "Lucknow",
]

PRODUCT_NAMES = {
    "electronics": [
        "MacBook Pro 16\" M3 Max", "Sony A7R V Camera",
        "DJI Mavic 3 Pro", "Samsung Galaxy S24 Ultra",
        "iPad Pro 12.9\"", "Canon EOS R5", "GoPro Hero 12",
    ],
    "furniture": [
        "Herman Miller Aeron", "Standing Desk Electric",
        "3-Seater Sofa", "Ergonomic Office Chair",
        "Conference Table", "Bookshelf 6-Tier",
    ],
    "vehicles": [
        "Toyota Innova Crysta", "Honda Activa 6G",
        "Mahindra Thar", "Tata Nexon EV", "Force Traveller",
    ],
    "tools": [
        "Bosch Hammer Drill", "DeWalt Circular Saw",
        "Makita Impact Driver", "Stanley Tool Kit",
    ],
    "construction-equipment": [
        "JCB 3DX", "Concrete Mixer", "Tower Light Set",
        "Portable Welding Machine", "Compactor Plate",
    ],
    "event-supplies": [
        "20x30ft Event Tent", "50x Plastic Chairs",
        "LED Stage Light Set", "Sound System 500W",
    ],
    "sports-recreation": [
        "Commercial Treadmill", "Cricket Kit Full",
        "Badminton Court Set", "Gym Dumbbell Set",
    ],
    "industrial-machinery": [
        "Lathe Machine", "CNC Router", "Air Compressor 50L",
        "Hydraulic Press", "Plate Bender",
    ],
}
```

### Phase 3: Business Logic Constraints

```python
# Status transition rules
RENTAL_STATUS_FLOW = {
    "pending": ["confirmed", "cancelled"],
    "confirmed": ["active", "cancelled"],
    "active": ["returned", "overdue", "extended"],
    "overdue": ["returned", "disputed"],
    "extended": ["returned", "overdue"],
    "returned": ["completed", "disputed"],
    "disputed": ["resolved", "escalated"],
    "completed": [],
    "cancelled": [],
}

# Date logic
def generate_rental_dates():
    """Generate realistic rental date ranges."""
    today = datetime.now(timezone.utc)
    start_offset = random.randint(-90, 30)  # -90 to +30 days from today
    start_date = today + timedelta(days=start_offset)
    duration = random.randint(1, 30)  # 1-30 days
    end_date = start_date + timedelta(days=duration)
    return start_date, end_date

# Amount logic
def calculate_rental_amount(daily_rate: int, days: int, deposit_pct: int):
    """Calculate realistic amounts."""
    rental_amount = Decimal(str(daily_rate * days))
    deposit_amount = rental_amount * Decimal(str(deposit_pct)) / 100
    total = rental_amount + deposit_amount
    return {
        "daily_rate": daily_rate,
        "rental_amount": rental_amount,
        "deposit_amount": deposit_amount,
        "total_amount": total,
    }
```

### Phase 4: Edge Case Generation

```python
# Edge cases to include
EDGE_CASES = {
    "overdue_rentals": 5,      # Rentals past end_date
    "disputed_invoices": 3,     # Invoices under dispute
    "low_stock_products": 4,    # Products with stock < 3
    "blacklisted_users": 2,     # Users on blacklist
    "expired_quotations": 5,    # Quotations past validity
    "partial_deposits": 3,      # Partially refunded deposits
    "failed_payments": 4,       # Failed payment attempts
    "empty_groups": 2,          # Groups with no active members
    "new_users_no_kyc": 5,      # Users with pending KYC
    "high_value_rentals": 3,    # Rentals > ₹1,00,000
}
```

## Running the Seeder

```bash
cd rental-backend

# Full seed
python scripts/seed_comprehensive.py

# With specific count
python scripts/seed_comprehensive.py --count 500

# Reset and re-seed
python scripts/seed_comprehensive.py --reset

# Dry run (no DB writes)
python scripts/seed_comprehensive.py --dry-run
```

## Output Example

```
Seeding Users...         50 records ✓
Seeding Enterprises...    5 records ✓
Seeding Groups...        10 records ✓
Seeding Categories...     8 records ✓
Seeding Products...      100 records ✓
Seeding Stock...         60 records ✓
Seeding Rentals...        80 records ✓
Seeding Invoices...       70 records ✓
Seeding Deposits...       50 records ✓
Seeding Quotations...     40 records ✓
Seeding Disputes...       15 records ✓
Seeding Repairs...        20 records ✓
Seeding Notifications... 100 records ✓
Seeding CRM...           30 records ✓
Seeding Loyalty...        40 records ✓
Seeding Inspections...    25 records ✓
Seeding Agent Tasks...    20 records ✓
Seeding Software...       15 records ✓
Seeding Audit Logs...    200 records ✓

Total: 938 records seeded in 12.3s
```

## File Structure

```
scripts/
├── seed_comprehensive.py      # Main seeder (Phase 1-4)
├── seed_data.py               # Existing simple seeder
├── seed_factories/            # Factory classes
│   ├── __init__.py
│   ├── user_factory.py
│   ├── product_factory.py
│   ├── rental_factory.py
│   ├── invoice_factory.py
│   └── ...
├── seed_data/                 # Static data pools
│   ├── names.py
│   ├── products.py
│   └── addresses.py
└── seed_utils/                # Helper functions
    ├── date_utils.py
    ├── amount_utils.py
    └── status_utils.py
```

## Integration with Testing

The seeder can also be used in test fixtures:

```python
# tests/conftest.py
@pytest.fixture
async def seeded_db(db_session):
    """Seed test database with comprehensive data."""
    seeder = DataSeeder(db_session)
    await seeder.seed_all()
    return db_session
```

## Future Enhancements

1. **Performance Testing** → Generate 10K+ records
2. **Time Travel** → Seed data with historical timestamps
3. **Correlation** → Link related entities (same user across rentals)
4. **Distribution** → Realistic distribution (80/20 rule for revenue)
5. **CLI Interface** → `python -m seed --profile=full|minimal|performance`
