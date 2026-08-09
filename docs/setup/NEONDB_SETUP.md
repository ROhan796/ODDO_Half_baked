# NeonDB PostgreSQL Setup Guide

## Overview

Reprico uses **NeonDB** (serverless PostgreSQL) with a **multi-database architecture** for separation of concerns. All databases live under a single NeonDB project.

## Database Architecture

```
┌─────────────────────────────────────────────────┐
│              NEONDB PROJECT                      │
│                                                  │
│  ┌──────────────┐  ┌──────────────┐             │
│  │  rental_db    │  │  rental_db   │             │
│  │  (Primary)    │  │  (Read       │             │
│  │  Writes       │  │   Replica)   │             │
│  │               │  │   Reads      │             │
│  └──────┬───────┘  └──────────────┘             │
│         │                                        │
│  ┌──────▼───────────────────────────────────┐    │
│  │          SCHEMA SEPARATION               │    │
│  │                                          │    │
│  │  public     → Operational tables         │    │
│  │  audit      → Immutable audit logs       │    │
│  │  analytics  → Materialized views         │    │
│  │  archive    → Historical data            │    │
│  └──────────────────────────────────────────┘    │
└─────────────────────────────────────────────────┘
```

## Step 1: Create NeonDB Account

1. Go to [https://neon.tech](https://neon.tech)
2. Sign up with GitHub or email
3. Create a new project:
   - **Project name:** `reprico-production` (or `reprico-staging`, `reprico-dev`)
   - **Region:** Choose closest to your users (e.g., `us-east-2` for AWS)
   - **PostgreSQL version:** 16

## Step 2: Get Connection Strings

After project creation, NeonDB provides:

### Primary Connection (for writes)
```
postgresql://neondb_owner:password@ep-xxx.us-east-2.aws.neon.tech/rental_db?sslmode=require
```

### Read Replica Connection (for reads)
```
postgresql://neondb_owner:password@ep-yyy.us-east-2.aws.neon.tech/rental_db?sslmode=require
```

### Convert to Async (for SQLAlchemy)
Add `+asyncpg` to the protocol:
```
postgresql+asyncpg://neondb_owner:password@ep-xxx.us-east-2.aws.neon.tech/rental_db?sslmode=require
```

## Step 3: Configure Environment Variables

```bash
# rental-backend/.env

# Primary (writes) - Use the primary endpoint
DATABASE_URL=postgresql+asyncpg://neondb_owner:xxxx@ep-xxx.us-east-2.aws.neon.tech/rental_db?sslmode=require

# Read Replica (reads) - Use the read-only endpoint
DATABASE_READ_URL=postgresql+asyncpg://neondb_owner:xxxx@ep-yyy.us-east-2.aws.neon.tech/rental_db?sslmode=require

# Connection Pool Settings (optimized for NeonDB serverless)
DATABASE_POOL_SIZE=10
DATABASE_MAX_OVERFLOW=20
DATABASE_POOL_TIMEOUT=30
```

## Step 4: Connection Pooling (NeonDB Built-in)

NeonDB provides built-in connection pooling via PgBouncer. Configure in the NeonDB console:

- **Pool mode:** Transaction (recommended for async)
- **Default pool size:** 10-20
- **Max client connections:** 100+

### Pool Settings in Code

```python
# app/utils/database.py
primary_engine = create_async_engine(
    settings.DATABASE_URL,
    pool_size=10,          # NeonDB handles pooling server-side
    max_overflow=20,       # Burst capacity
    pool_timeout=30,       # Wait time before timeout
    pool_pre_ping=True,    # Validate connections before use
    echo=settings.DEBUG,   # SQL logging in dev
)
```

### NeonDB-Specific Optimizations

```python
# Add to DATABASE_URL for NeonDB serverless:
?sslmode=require&prepared_statement_cache_size=0
```

## Step 5: Schema Separation

Create separate schemas for different concerns:

```sql
-- Run in NeonDB SQL Editor
CREATE SCHEMA IF NOT EXISTS audit;
CREATE SCHEMA IF NOT EXISTS analytics;
CREATE SCHEMA IF NOT EXISTS archive;
```

Update models to use schemas:

```python
# In models that need schema separation
class AuditLog(Base):
    __tablename__ = "audit_logs"
    __table_args__ = {"schema": "audit"}
```

## Step 6: Run Migrations

```bash
cd rental-backend

# Initialize Alembic (already done)
alembic init alembic

# Run all migrations
alembic upgrade head

# Create a new migration
alembic revision --autogenerate -m "description"
```

## Step 7: NeonDB Settings to Configure

In the NeonDB Console:

| Setting | Value | Reason |
|---------|-------|--------|
| **Compute size** | Free tier or 0.25 CU | Dev; scale for prod |
| **Auto-suspend** | 5 min | Save costs in dev |
| **Autosuspend** | Disabled | Keep always-on for prod |
| **IP Allow** | Your server IPs | Security |
| **Logical replication** | Enable if needed | For analytics sync |

## Step 8: Read Replica Setup

NeonDB supports read replicas natively:

1. In NeonDB Console → **Branching** → Create read replica
2. The replica gets its own endpoint (`ep-yyy...`)
3. Set `DATABASE_READ_URL` to the replica endpoint
4. Code automatically routes reads to replica, writes to primary

```python
# Writes → primary_engine → DATABASE_URL
# Reads  → read_engine    → DATABASE_READ_URL
```

## Performance Tuning

### Indexes

```sql
-- High-impact indexes for the rental system
CREATE INDEX CONCURRENTLY idx_users_email ON users(email);
CREATE INDEX CONCURRENTLY idx_users_phone ON users(phone);
CREATE INDEX CONCURRENTLY idx_users_role ON users(role);
CREATE INDEX CONCURRENTLY idx_products_category ON products(category_id);
CREATE INDEX CONCURRENTLY idx_products_status ON products(status);
CREATE INDEX CONCURRENTLY idx_rentals_user ON rentals(user_id);
CREATE INDEX CONCURRENTLY idx_rentals_status ON rentals(status);
CREATE INDEX CONCURRENTLY idx_rentals_dates ON rentals(start_date, end_date);
CREATE INDEX CONCURRENTLY idx_invoices_rental ON invoices(rental_id);
CREATE INDEX ON audit.audit_logs(created_at);
```

### Materialized Views

```sql
-- Dashboard stats (refreshed by ARQ worker)
CREATE MATERIALIZED ANALYTICS.mv_dashboard_stats AS
SELECT
    DATE_TRUNC('day', r.created_at) AS date,
    COUNT(*) AS total_rentals,
    SUM(r.total_amount) AS revenue,
    AVG(r.total_amount) AS avg_order_value
FROM public.rentals r
GROUP BY 1;

CREATE UNIQUE INDEX ON analytics.mv_dashboard_stats(date);
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Connection timeout | NeonDB auto-suspends; check compute status |
| SSL errors | Ensure `sslmode=require` in connection string |
| Pool exhausted | Increase `DATABASE_POOL_SIZE` or `max_overflow` |
| Read lag | Read replicas may lag 1-5s; critical reads use primary |
| Migration fails | Ensure `DATABASE_URL` points to primary, not replica |

## Cost Optimization

- **Free tier:** 0.5 GB storage, 24/7 compute (0.25 CU)
- **Pro:** Pay per compute hour + storage
- **Tip:** Use auto-suspend for dev environments
- **Tip:** Use connection pooling to reduce compute wake-ups
