# RENTAL MANAGEMENT SYSTEM — BACKEND IMPLEMENTATION GUIDE
## The Complete Technical Reference
### Version 3.0 | 2026

---

# TABLE OF CONTENTS

1. [Architecture Overview](#1-architecture-overview)
2. [Project Structure Map](#2-project-structure-map)
3. [Core Layer — Deep Dive](#3-core-layer--deep-dive)
4. [Database Layer — All Models & Schemas](#4-database-layer--all-models--schemas)
5. [API Layer — Every Endpoint Explained](#5-api-layer--every-endpoint-explained)
6. [Service Layer — Business Logic & Algorithms](#6-service-layer--business-logic--algorithms)
7. [WebSocket Layer — Real-Time Architecture](#7-websocket-layer--real-time-architecture)
8. [Middleware Layer — Request Pipeline](#8-middleware-layer--request-pipeline)
9. [Background Workers — Scheduled Tasks](#9-background-workers--scheduled-tasks)
10. [Infrastructure — Docker, Testing, Scripts](#10-infrastructure--docker-testing-scripts)
11. [Data Flow Diagrams](#11-data-flow-diagrams)
11. [API Reference Tables](#12-api-reference-tables)

---

# 1. ARCHITECTURE OVERVIEW

## 1.1 What Is This System?

This is a **full-stack rental management backend** for a platform that rents out physical products (equipment, vehicles, furniture, tools, etc.) to individual customers, enterprise clients, and groups. Think of it as an "Airbnb for physical goods" — but with enterprise-grade features like KYC verification, security deposits, trust scoring, late fee escalation, group voting, and CRM.

## 1.2 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                                │
│  (Next.js Frontend, Mobile App, Third-party Integrations)           │
└──────────────────────────┬──────────────────────────────────────────┘
                           │ HTTP / WebSocket
┌──────────────────────────▼──────────────────────────────────────────┐
│                     NGINX REVERSE PROXY                             │
│  - SSL Termination    - Rate Limiting    - Load Balancing            │
│  - Gzip Compression  - Security Headers  - WebSocket Upgrade        │
└──────────────────────────┬──────────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────────────┐
│                    FASTAPI APPLICATION                               │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │ MIDDLEWARE PIPELINE                                            │ │
│  │ RequestID → RateLimiter → Audit → Compression → CORS          │ │
│  └────────────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │ API ROUTER (20 routers, 80+ endpoints)                        │ │
│  │ auth users products rentals quotations invoices deposits       │ │
│  │ disputes repairs recovery groups enterprise crm stock loyalty  │ │
│  │ notifications admin files dashboard categories                 │ │
│  └────────────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │ SERVICE LAYER (20 services)                                    │ │
│  │ Business logic, validation, orchestration                      │ │
│  └────────────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │ DATA LAYER                                                     │ │
│  │ SQLAlchemy ORM → asyncpg → PostgreSQL (NeonDB)                │ │
│  │ Redis Cache → Upstash                                         │ │
│  └────────────────────────────────────────────────────────────────┘ │
└──────────────────────────┬──────────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────────────┐
│                    BACKGROUND WORKERS (ARQ)                          │
│  - Overdue Detection    - Late Fee Calculation                      │
│  - Reminder Dispatch    - Trust Score Recalculation                 │
│  - Reservation Expiry   - PDF Generation                            │
│  - Email/SMS Dispatch   - Materialized View Refresh                 │
└─────────────────────────────────────────────────────────────────────┘
```

## 1.3 Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Framework** | FastAPI 0.115.0 | Async Python web framework |
| **ORM** | SQLAlchemy 2.0.35 (async) | Database object-relational mapping |
| **Database** | PostgreSQL (NeonDB) | Primary data store |
| **Cache** | Redis (Upstash) | Caching, sessions, rate limiting |
| **Auth** | JWT (python-jose) + bcrypt | Authentication & authorization |
| **File Storage** | Cloudflare R2 (S3-compatible) | File uploads, images, documents |
| **Payments** | Razorpay | Payment processing, deposits |
| **Background Jobs** | ARQ | Async task queue with cron support |
| **WebSockets** | FastAPI native | Real-time notifications |
| **Containerization** | Docker + Nginx | Deployment & reverse proxy |
| **Testing** | pytest + httpx | Unit, integration, system tests |

## 1.4 Design Principles

1. **Async-First**: Every I/O operation is async (database, HTTP, Redis, file storage)
2. **Layered Architecture**: API → Service → Model (never skip layers)
3. **Repository Pattern**: Services handle all database queries (no raw SQL in routes)
4. **Dependency Injection**: FastAPI's DI system for DB sessions, auth, permissions
5. **RBAC**: Role-Based Access Control with 4 roles and 30+ granular permissions
6. **Separation of Concerns**: Each file does exactly one thing
7. **Fail Gracefully**: Custom exceptions return proper HTTP status codes

---

# 2. PROJECT STRUCTURE MAP

## 2.1 Complete File Tree

```
rental-backend/
│
├── app/                              # MAIN APPLICATION PACKAGE
│   ├── __init__.py                   # Package marker (empty)
│   ├── main.py                       # FastAPI app entry point, middleware, routes
│   ├── config.py                     # Pydantic Settings class (env vars)
│   │
│   ├── core/                         # CORE BUSINESS LOGIC
│   │   ├── __init__.py
│   │   ├── auth.py                   # JWT creation/verification, password hashing, OTP
│   │   ├── permissions.py            # RBAC: Role enum, Permission enum, permission matrix
│   │   ├── security.py               # Re-exports from auth.py (facade pattern)
│   │   ├── cache.py                  # Redis cache manager with decorator
│   │   ├── websocket.py              # WebSocket ConnectionManager (rooms, broadcast)
│   │   ├── events.py                 # WebSocket event type definitions
│   │   └── exceptions.py             # Custom HTTP exception classes
│   │
│   ├── middleware/                    # REQUEST PIPELINE MIDDLEWARE
│   │   ├── __init__.py
│   │   ├── request_id.py             # UUID4 injection into every request
│   │   ├── rate_limiter.py           # Token bucket rate limiting
│   │   ├── audit.py                  # Request logging (method, path, duration)
│   │   └── compression.py            # Gzip response compression
│   │
│   ├── models/                       # SQLALCHEMY ORM MODELS (22 files)
│   │   ├── __init__.py               # Imports all models, defines __all__
│   │   ├── base.py                   # BaseModel with UUID PK + timestamps
│   │   ├── user.py                   # User, RefreshToken, OTPToken, KYCRecord, TrustScoreHistory
│   │   ├── enterprise.py             # Enterprise, EnterpriseMember, CreditTransaction
│   │   ├── group.py                  # Group, GroupMember, GroupDeposit, GroupVote, VoteRecord
│   │   ├── product.py                # Category, Product, ProductVariant, Accessory
│   │   ├── availability.py           # AvailabilityBlock, BlackoutDate, Reservation
│   │   ├── rental.py                 # Rental, RentalExtension
│   │   ├── quotation.py              # Quotation, QuotationTemplate
│   │   ├── invoice.py                # Invoice, InvoiceItem, Payment
│   │   ├── deposit.py                # SecurityDeposit, DepositDeduction
│   │   ├── custody.py                # CustodyEvent, AccessoryCheck
│   │   ├── fee.py                    # LateFee
│   │   ├── dispute.py                # Dispute
│   │   ├── repair.py                 # RepairCase
│   │   ├── recovery.py               # RecoveryCase
│   │   ├── blacklist.py              # Blacklist
│   │   ├── notification.py           # Notification, NotificationTemplate
│   │   ├── pricelist.py              # Pricelist, PricelistItem
│   │   ├── crm.py                    # CRMContact, CRMInteraction, CRMTag
│   │   ├── stock.py                  # StockLocation, StockMovement, StockLevel
│   │   ├── loyalty.py                # LoyaltyPointsLedger, Referral
│   │   └── audit.py                  # AuditLog
│   │
│   ├── schemas/                      # PYDANTIC V2 VALIDATION SCHEMAS (22 files)
│   │   ├── __init__.py
│   │   ├── auth.py                   # LoginRequest, OTPRequest, TokenResponse, etc.
│   │   ├── user.py                   # UserCreate, UserUpdate, UserResponse
│   │   ├── product.py                # ProductCreate, ProductResponse, CategoryCreate
│   │   ├── rental.py                 # RentalCreate, RentalResponse, RentalReturnRequest
│   │   ├── enterprise.py             # EnterpriseCreate, EnterpriseMemberCreate
│   │   ├── group.py                  # GroupCreate, GroupMemberAdd, GroupVoteCreate
│   │   ├── stock.py                  # StockLocationCreate, StockMovementCreate
│   │   ├── invoice.py                # InvoiceCreate, PaymentCreate, InvoiceResponse
│   │   ├── quotation.py              # QuotationCreate, QuotationItem
│   │   ├── deposit.py                # DepositResponse, DepositDeductionCreate
│   │   ├── loyalty.py                # LoyaltyPointsResponse, RedeemPointsRequest
│   │   ├── crm.py                    # CRMContactCreate, CRMInteractionCreate
│   │   ├── notification.py           # NotificationResponse, NotificationTemplateCreate
│   │   ├── dispute.py                # DisputeCreate, DisputeUpdate
│   │   ├── repair.py                 # RepairCaseCreate, RepairCaseUpdate
│   │   ├── recovery.py               # RecoveryCaseCreate, RecoveryCaseUpdate
│   │   ├── upload.py                 # PresignedUrlRequest, PresignedUrlResponse
│   │   ├── websocket.py              # WSMessage, WSPing, WSPong
│   │   ├── dashboard.py              # DashboardStats, RevenueChart, RentalChart
│   │   └── common.py                 # PaginatedResponse, MessageResponse, ErrorResponse
│   │
│   ├── api/                          # API ROUTE HANDLERS
│   │   ├── __init__.py
│   │   ├── deps.py                   # get_current_user, require_permission, require_role
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── router.py             # Main v1 router (includes all sub-routers)
│   │       ├── auth.py               # /auth/register, /auth/login, /auth/otp/*, /auth/refresh
│   │       ├── users.py              # /users/me, /users/, /users/{id}
│   │       ├── products.py           # CRUD for products
│   │       ├── categories.py         # CRUD for categories
│   │       ├── rentals.py            # Rental lifecycle endpoints
│   │       ├── quotations.py         # Quotation CRUD
│   │       ├── invoices.py           # Invoice + payment endpoints
│   │       ├── deposits.py           # Deposit management
│   │       ├── disputes.py           # Dispute filing & resolution
│   │       ├── repairs.py            # Repair case management
│   │       ├── recovery.py           # Recovery case management
│   │       ├── groups.py             # Group CRUD + voting
│   │       ├── enterprise.py         # Enterprise CRUD + members
│   │       ├── crm.py                # CRM contacts + interactions
│   │       ├── stock.py              # Stock locations + movements
│   │       ├── loyalty.py            # Points, referrals, redemption
│   │       ├── notifications.py      # Notification CRUD + read status
│   │       ├── admin.py              # Admin dashboard, blacklist, audit logs
│   │       ├── files.py              # Pre-signed URL generation
│   │       └── dashboard.py          # Dashboard stats + charts
│   │
│   ├── services/                     # BUSINESS LOGIC LAYER (20 files)
│   │   ├── __init__.py
│   │   ├── auth_service.py           # Registration, login, OTP, token refresh
│   │   ├── user_service.py           # User CRUD, profile management
│   │   ├── product_service.py        # Product CRUD, availability
│   │   ├── rental_service.py         # Rental lifecycle, late fees, extensions
│   │   ├── quotation_service.py      # Quotation creation, status management
│   │   ├── invoice_service.py        # Invoice generation, payment recording
│   │   ├── deposit_service.py        # Deposit creation, settlement, deductions
│   │   ├── dispute_service.py        # Dispute filing, resolution
│   │   ├── repair_service.py         # Repair case tracking
│   │   ├── recovery_service.py       # Recovery case management
│   │   ├── group_service.py          # Group management, voting algorithm
│   │   ├── enterprise_service.py     # Enterprise CRUD, member management
│   │   ├── crm_service.py            # CRM contacts, interactions
│   │   ├── stock_service.py          # Stock locations, movements, levels
│   │   ├── loyalty_service.py        # Points, referrals, redemption
│   │   ├── notification_service.py   # Notification CRUD, templates
│   │   ├── pdf_service.py            # PDF generation (placeholder)
│   │   ├── payment_service.py        # Razorpay integration (placeholder)
│   │   └── file_service.py           # R2 file operations
│   │
│   ├── websockets/                   # WEBSOCKET HANDLERS
│   │   ├── __init__.py
│   │   └── handlers.py               # /ws/{token} endpoint with JWT auth
│   │
│   ├── workers/                      # ARQ BACKGROUND JOBS
│   │   ├── __init__.py
│   │   ├── settings.py               # WorkerSettings class
│   │   ├── schedules.py              # Cron schedule definitions
│   │   └── tasks/
│   │       ├── __init__.py
│   │       ├── overdue_detection.py   # Mark overdue rentals
│   │       ├── late_fee_calculation.py # Calculate daily late fees
│   │       ├── reminder_dispatch.py   # Send rental & payment reminders
│   │       ├── reservation_expiry.py  # Expire old reservations
│   │       ├── trust_score_recalculation.py # Recalculate user trust
│   │       ├── pdf_generation.py      # Generate PDFs
│   │       ├── email_dispatch.py      # Send pending emails
│   │       ├── sms_dispatch.py        # Send pending SMS
│   │       ├── materialized_view_refresh.py # Refresh analytics views
│   │       └── audit_archive.py       # Archive old audit logs
│   │
│   └── utils/                        # SHARED UTILITIES
│       ├── __init__.py
│       ├── database.py               # Async engine, session factories, get_db()
│       ├── redis.py                  # Redis connection pool
│       ├── r2.py                     # Cloudflare R2 storage client
│       ├── email.py                  # Resend email client
│       ├── sms.py                    # MSG91 SMS client
│       ├── qr.py                     # QR code generation
│       └── validators.py             # Indian validators (phone, PAN, Aadhaar, GST)
│
├── alembic/                          # DATABASE MIGRATIONS
│   ├── env.py                        # Async migration configuration
│   ├── script.py.mako                # Migration template
│   └── versions/
│       └── 001_initial.py            # Creates all 40+ tables
│
├── tests/                            # TEST SUITE
│   ├── __init__.py
│   ├── conftest.py                   # Fixtures: client, db_session, auth_headers
│   ├── unit/
│   │   ├── __init__.py
│   │   ├── test_auth.py              # JWT, password, OTP tests
│   │   ├── test_permissions.py       # RBAC permission tests
│   │   └── test_validators.py        # Indian ID validation tests
│   ├── integration/
│   │   ├── __init__.py
│   │   └── test_rentals.py           # Rental flow integration tests
│   └── system/
│       ├── __init__.py
│       └── test_api_endpoints.py     # Health, register, login tests
│
├── scripts/                          # UTILITY SCRIPTS
│   ├── __init__.py
│   ├── seed_data.py                  # Seed categories, products, admin user
│   └── create_admin.py               # Create super admin via CLI
│
├── docker/                           # DOCKER CONFIGURATION
│   ├── Dockerfile                    # API server image
│   ├── Dockerfile.worker             # Background worker image
│   ├── docker-compose.yml            # Full stack: api, worker, redis, nginx
│   └── nginx.conf                    # Reverse proxy config
│
├── .env                              # Environment variables (local dev)
├── .env.example                      # Environment template
├── .gitignore                        # Git ignore rules
├── requirements.txt                  # Python dependencies
├── pyproject.toml                    # Project configuration
├── gunicorn.conf.py                  # Gunicorn production config
├── run.bat                           # Windows one-click start
├── run.sh                            # Mac/Linux one-click start
└── alembic.ini                       # Alembic configuration
```

## 2.2 Module Dependency Flow

```
Request Flow:
  Client → Nginx → FastAPI App → Middleware Pipeline → Router → Service → Model → Database

Dependency Flow:
  API Routes → Services → Models
                  ↓          ↓
              Utils    External APIs
              (Redis, R2, Email, SMS)

No circular dependencies. Each layer only imports from layers below it.
```

---

# 3. CORE LAYER — DEEP DIVE

## 3.1 Authentication System (`app/core/auth.py`)

### Algorithm: JWT Access Token Creation

```
FUNCTION create_access_token(user_id, role, user_type, enterprise_id):
    1. Calculate expiry = now + ACCESS_TOKEN_EXPIRE_MINUTES (15 min)
    2. Build payload dict:
       - sub: user_id          (subject - who the token belongs to)
       - role: role            (user's RBAC role)
       - user_type: user_type  (personal/enterprise)
       - enterprise_id: id     (if enterprise user)
       - exp: expiry           (expiration timestamp)
       - iat: now              (issued-at timestamp)
       - jti: random_hex_16    (unique token ID for revocation)
    3. Encode with HS256 algorithm using JWT_SECRET_KEY
    4. Return encoded string
```

### Algorithm: JWT Token Verification

```
FUNCTION verify_access_token(token):
    1. Try to decode with jwt.decode(token, secret, algorithms=[HS256])
    2. If JWTError → return None (invalid/expired)
    3. If success → return payload dict
```

### Algorithm: Refresh Token Rotation

```
FUNCTION refresh_tokens(refresh_token, fingerprint):
    1. Hash the refresh_token with SHA-256
    2. Query refresh_tokens table for matching hash (not revoked, not expired)
    3. If not found → raise 401 Unauthorized
    4. Get the user from user_id in the token record
    5. If user blacklisted → raise 401
    6. Revoke old token (set revoked_at = now)
    7. Generate new access_token (15 min TTL)
    8. Generate new refresh_token (32-byte random hex)
    9. Store new refresh_token hash in database (30-day TTL)
    10. Return both tokens
```

### Algorithm: Password Security

```
Hash Password:
    1. Use bcrypt algorithm with random salt
    2. bcrypt.hash(password) → $2b$12$hashed_string
    3. Store hash in database (never plain text)

Verify Password:
    1. bcrypt.verify(plain_password, stored_hash)
    2. Return True/False
```

### Algorithm: OTP Generation

```
FUNCTION generate_otp():
    1. Generate random number 0-999999
    2. Pad with leading zeros to ensure 6 digits
    3. Return string "048291" format
```

## 3.2 Permission System (`app/core/permissions.py`)

### Data Structure: Role Enum

```
Roles:
    super_admin  → Full access to everything
    ops_admin    → Operations team (most features, no system settings)
    field_agent  → On-ground staff (view + inspections only)
    portal_user  → End customers (own data only)
```

### Data Structure: Permission Enum (30+ permissions)

```
Products:    product:view, product:create, product:update, product:delete
Rentals:     rental:create_own, rental:create_any, rental:view_own, rental:view_any,
             rental:confirm, rental:return, rental:cancel
Customers:   customer:view, customer:create, customer:update, customer:blacklist
Finance:     deposit:view, deposit:settle, deposit:deduct, invoice:view, invoice:create
Operations:  inspection:perform, repair:manage, recovery:manage
Admin:       admin:dashboard, admin:settings, admin:audit, admin:blacklist
CRM:         crm:view, crm:manage
Stock:       stock:view, stock:manage
```

### Algorithm: Permission Check

```
FUNCTION check_permission(role, permission):
    1. Look up ROLE_PERMISSIONS[role] → list of allowed permissions
    2. Check if permission is in the list
    3. Return True/False

Example:
    check_permission("portal_user", "product:view")      → True
    check_permission("portal_user", "rental:create_any") → False
    check_permission("super_admin", "admin:settings")     → True
```

### Permission Matrix

```
┌──────────────────┬──────────┬──────────┬──────────┬──────────┐
│ Permission       │ Super    │ Ops      │ Field    │ Portal   │
│                  │ Admin    │ Admin    │ Agent    │ User     │
├──────────────────┼──────────┼──────────┼──────────┼──────────┤
│ product:view     │    ✓     │    ✓     │    ✓     │    ✓     │
│ product:create   │    ✓     │    ✓     │    ✗     │    ✗     │
│ rental:create    │    ✓     │    ✓     │    ✗     │    ✓(own)│
│ rental:view      │    ✓     │    ✓     │    ✓     │    ✓(own)│
│ rental:confirm   │    ✓     │    ✓     │    ✗     │    ✗     │
│ rental:return    │    ✓     │    ✓     │    ✗     │    ✗     │
│ customer:blacklist│   ✓     │    ✗     │    ✗     │    ✗     │
│ admin:settings   │    ✓     │    ✗     │    ✗     │    ✗     │
│ stock:manage     │    ✓     │    ✓     │    ✗     │    ✗     │
│ crm:manage       │    ✓     │    ✓     │    ✗     │    ✗     │
└──────────────────┴──────────┴──────────┴──────────┴──────────┘
```

## 3.3 Cache System (`app/core/cache.py`)

### Algorithm: Cache Key Generation

```
FUNCTION _make_key(prefix, *args, **kwargs):
    1. Serialize args and kwargs to JSON
    2. Hash with MD5, take first 12 hex chars
    3. Return "prefix:hash12chars"
    Example: "product:a1b2c3d4e5f6"
```

### Algorithm: Cache-Aside Pattern (get_or_set)

```
FUNCTION get_or_set(key, factory_function, ttl=3600):
    1. Try to get value from Redis
    2. If found → return cached value (cache hit)
    3. If not found → call factory_function() (cache miss)
    4. Store result in Redis with TTL
    5. Return the computed value
```

### Algorithm: Pattern-Based Invalidation

```
FUNCTION invalidate_pattern(pattern):
    1. Use Redis KEYS command to find all matching keys
    2. Delete all found keys in one operation
    Example: invalidate_pattern("product:*") → deletes all product caches
```

### Cache Decorator Usage

```python
@cached(prefix="product", ttl=1800)  # Cache for 30 minutes
async def get_product(product_id: str):
    # This result is automatically cached
    ...
```

## 3.4 WebSocket System (`app/core/websocket.py`)

### Data Structure: ConnectionManager

```
active_connections: Dict[str, List[WebSocket]]
    → Maps user_id to list of their WebSocket connections
    → One user can have multiple tabs/devices

rooms: Dict[str, Set[str]]
    → Maps room name to set of user_ids in that room
    → Example: {"user:abc123": {"abc123"}, "admin:dashboard": {"admin1", "admin2"}}
```

### Algorithm: Connection Management

```
CONNECT:
    1. Accept WebSocket connection
    2. Add to active_connections[user_id]
    3. For each room, add user_id to rooms[room]

DISCONNECT:
    1. Remove from active_connections[user_id]
    2. For each room, remove user_id from rooms[room]
    3. Clean up empty rooms

SEND PERSONAL MESSAGE:
    1. Get all connections for user_id
    2. For each connection, try to send_json
    3. Silently ignore failed connections

BROADCAST TO ROOM:
    1. Get all user_ids in the room
    2. For each user (except excluded), send personal message
```

---

# 4. DATABASE LAYER — ALL MODELS & SCHEMAS

## 4.1 Base Model (`app/models/base.py`)

Every model inherits from this:

```
BaseModel:
    id: UUID (primary key, auto-generated)
    created_at: DateTime (server default: now())
    updated_at: DateTime (server default: now(), auto-updates)
```

## 4.2 User Model (`app/models/user.py`)

### Fields

```
User Table:
    id                UUID (PK)
    user_type         Enum: personal | enterprise | enterprise_sub
    role              Enum: super_admin | ops_admin | field_agent | portal_user
    phone             String(15) UNIQUE, NOT NULL, INDEXED
    email             String(255) UNIQUE, NOT NULL, INDEXED
    password_hash     String(255) (nullable - OTP-only users have none)
    name              String(255) NOT NULL
    dob               Date
    profile_photo_url Text
    kyc_status        Enum: pending | in_progress | verified | rejected
    kyc_completed_at  DateTime
    trust_score       SmallInteger (0-100)
    trust_tier        String(20): unverified | bronze | silver | gold | platinum
    enterprise_id     UUID FK → enterprises.id
    blacklisted       Boolean (default: false)
    blacklisted_at    DateTime
    blacklisted_by    UUID FK → users.id
    blacklist_reason  Text
    device_fingerprints  Text[] (array of device IDs)
    notification_preferences  JSONB: {sms: true, email: true, push: true}
    points_balance    Integer (loyalty points)
    lifetime_rentals  Integer
    lifetime_spend    Numeric(14,2)
    last_rental_at    DateTime
    referral_code     String(20) UNIQUE
    referred_by       UUID FK → users.id
```

### Indexes

```
idx_users_phone        → UNIQUE on phone
idx_users_email        → UNIQUE on email
idx_users_trust_tier   → on trust_tier
idx_users_blacklisted  → on blacklisted WHERE blacklisted = true
idx_users_enterprise_id → on enterprise_id
```

### Related Tables

```
RefreshToken:
    user_id, token_hash, device_fingerprint, user_agent,
    ip_address, expires_at, revoked_at

OTPToken:
    identifier (phone/email), channel (sms/email),
    code (6 digits), purpose, attempts, expires_at, verified_at

KYCRecord:
    user_id, step (7-step KYC), id_type, id_number,
    id_doc_url, selfie_url, face_match_score, status

TrustScoreHistory:
    user_id, previous_score, new_score, change_amount, reason
```

## 4.3 Product Model (`app/models/product.py`)

### Fields

```
Product Table:
    id                UUID (PK)
    name              String(255) NOT NULL
    slug              String(255) UNIQUE
    category_id       UUID FK → categories.id
    description       Text
    serial_number     String(100) UNIQUE
    qr_code           String(255) UNIQUE
    sku               String(100) UNIQUE
    status            Enum: available | rented | in_repair | inactive | archived
    current_holder_id UUID FK → users.id (who currently has it)
    current_rental_id UUID FK → rentals.id (active rental)
    condition_rating  SmallInteger (1-5)
    daily_rate        Numeric(10,2) NOT NULL
    deposit_percentage Numeric(5,2) default 30.00
    late_fee_rate     Numeric(10,2)
    late_fee_mode     Enum: hourly | daily | weekly | monthly
    images            Text[]
    thumbnail_url     Text
    tags              Text[]
    total_rentals     Integer (lifetime counter)
    total_revenue     Numeric(14,2)
    is_featured       Boolean
    is_insured        Boolean
    min_rental_duration  Integer
    max_rental_duration  Integer
```

## 4.4 Rental Model (`app/models/rental.py`)

### Fields

```
Rental Table:
    id                UUID (PK)
    customer_id       UUID FK → users.id
    product_id        UUID FK → products.id
    quotation_id      UUID FK → quotations.id
    status            Enum: pending | confirmed | active | returned | overdue | cancelled
    rental_type       Enum: daily | weekly | monthly
    start_date        Date NOT NULL
    end_date          Date NOT NULL
    actual_return_date Date
    daily_rate        Numeric(10,2) NOT NULL
    total_amount      Numeric(12,2) NOT NULL
    deposit_amount    Numeric(12,2)
    late_fees         Numeric(12,2)
    damage_charges    Numeric(12,2)
    insurance_selected Boolean
    delivery_address  Text
    condition_at_checkout Text
    condition_at_return  Text
    checkout_photos   Text
    return_photos     Text
    confirmed_by      UUID FK → users.id
    confirmed_at      DateTime
    returned_to       UUID FK → users.id
    returned_at       DateTime
```

### Rental Status Flow

```
                  ┌──────────┐
                  │ PENDING  │
                  └────┬─────┘
                       │ confirm_rental()
                       ▼
                  ┌──────────┐
                  │CONFIRMED │
                  └────┬─────┘
                       │ start_date arrives → background worker activates
                       ▼
                  ┌──────────┐
                  │  ACTIVE  │←────┐
                  └──┬───┬───┘     │ extend_rental()
                     │   │         │
                     │   └─────────┘
                     │
     process_return()│
                     ▼
              ┌──────────┐    ┌──────────┐
              │ RETURNED │    │ OVERDUE  │ (auto-detected by worker)
              └──────────┘    └──────────┘

     cancel_rental() → CANCELLED (from pending/confirmed only)
```

## 4.5 Invoice Model (`app/models/invoice.py`)

### Fields

```
Invoice Table:
    invoice_number    String(50) UNIQUE (format: INV-YYYYMMDD-0001)
    customer_id       UUID FK → users.id
    enterprise_id     UUID FK → enterprises.id
    rental_id         UUID FK → rentals.id
    status            Enum: draft | pending | paid | partially_paid | overdue | cancelled | refunded
    subtotal          Numeric(12,2)
    tax_amount        Numeric(12,2)
    discount_amount   Numeric(12,2)
    total_amount      Numeric(12,2)
    paid_amount       Numeric(12,2)
    due_date          DateTime
    paid_at           DateTime
    notes             Text
    billing_address   JSONB

InvoiceItem Table:
    invoice_id        UUID FK → invoices.id
    description       String(255)
    quantity          Numeric(10,2)
    unit_price        Numeric(10,2)
    amount            Numeric(12,2) = quantity × unit_price
    tax_rate          Numeric(5,2)
    tax_amount        Numeric(10,2) = amount × tax_rate / 100

Payment Table:
    payment_number    String(50) UNIQUE (format: PAY-YYYYMMDD-0001)
    invoice_id        UUID FK → invoices.id
    customer_id       UUID FK → users.id
    amount            Numeric(12,2)
    status            Enum: pending | processing | completed | failed | refunded
    payment_method    Enum: razorpay | cash | bank_transfer | credit
    razorpay_order_id String(255)
    razorpay_payment_id String(255)
    paid_at           DateTime
```

## 4.6 All Other Models (Summary)

```
Enterprise:
    name, legal_entity_type, gst_number, pan, cin,
    registered_address (JSONB), trust_score,
    credit_line_enabled, credit_limit_inr, credit_used_inr

Group:
    name, leader_id, trust_score, status,
    max_members, joint_liability

GroupMember:
    group_id, user_id, role (leader/member),
    status (invited/active/removed), deposit_share_pct

GroupVote:
    group_id, rental_id, vote_type, requested_by,
    status (pending/approved/rejected/expired),
    votes_for, votes_against, expires_at

SecurityDeposit:
    rental_id, customer_id, amount,
    status (pending/authorized/captured/settled/refunded),
    refund_amount, refund_at

DepositDeduction:
    deposit_id, amount, reason,
    deduction_type (late_fee/damage/missing_item/other)

AvailabilityBlock:
    product_id, block_type (rental/maintenance/reservation),
    rental_id, start_at, end_at, status

CustodyEvent:
    rental_id, product_id, event_type (checkout/checkin/transfer/inspection),
    from_user_id, to_user_id, condition_rating, photos

LateFee:
    rental_id, customer_id, days_overdue, daily_rate,
    total_amount, waived_amount, status

Dispute:
    rental_id, customer_id, dispute_type, amount_disputed,
    description, evidence_urls, status, resolution

RecoveryCase:
    rental_id, customer_id, product_id, reason,
    amount_outstanding, status, recovered_amount

Blacklist:
    user_id, reason, description, evidence_urls,
    added_by, expires_at, is_permanent

Notification:
    user_id, type, channel, title, message, data (JSONB),
    status (pending/sent/delivered/failed/read)

CRMContact:
    contact_type (lead/customer/partner/vendor), name, email,
    phone, company, status, lead_score, lifetime_value

StockLocation:
    name, code, address, city, state, is_warehouse, capacity

StockMovement:
    product_id, from_location_id, to_location_id,
    movement_type (in/out/transfer/adjustment/return), quantity

StockLevel:
    product_id, location_id, quantity, reserved, available, min_stock

LoyaltyPointsLedger:
    user_id, transaction_type (earned/redeemed/referral/expired),
    points, balance_after, reference_type, reference_id

AuditLog:
    user_id, action, resource_type, resource_id,
    old_value (JSONB), new_value (JSONB), ip_address
```

---

# 5. API LAYER — EVERY ENDPOINT EXPLAINED

## 5.1 Authentication Endpoints (`app/api/v1/auth.py`)

### POST `/api/v1/auth/register`

```
Purpose: Register a new user account
Request Body: {name, email, phone, password, user_type, referral_code?}
Algorithm:
    1. Check if email or phone already exists → 409 Conflict
    2. Create User record with hashed password
    3. Generate JWT access token (15 min)
    4. Generate refresh token (30 days)
    5. Store refresh token hash in database
    6. Return {access_token, refresh_token, expires_in}
```

### POST `/api/v1/auth/login`

```
Purpose: Login with email/phone + password
Request Body: {identifier, password, device_fingerprint}
Algorithm:
    1. Find user by email OR phone
    2. If not found → 401 Unauthorized
    3. If blacklisted → 403 Forbidden
    4. Verify password against bcrypt hash
    5. Generate token pair
    6. Store refresh token
    7. Return tokens
```

### POST `/api/v1/auth/otp/request`

```
Purpose: Request OTP for passwordless login
Request Body: {identifier (phone/email), channel (sms/email)}
Algorithm:
    1. Generate 6-digit OTP
    2. Store in otp_tokens table with 5-min expiry
    3. Send via SMS/Email (placeholder)
    4. In DEBUG mode, return OTP in response for testing
```

### POST `/api/v1/auth/otp/verify`

```
Purpose: Verify OTP and login
Request Body: {identifier, code, purpose}
Algorithm:
    1. Find latest unverified OTP for identifier+purpose
    2. Check expiry (5 min) → 400 if expired
    3. Check attempts (< 5) → 429 if exceeded
    4. Increment attempts counter
    5. Compare code → 400 if wrong
    6. Mark as verified
    7. Find or create user
    8. Generate tokens
    9. Return tokens
```

### POST `/api/v1/auth/refresh`

```
Purpose: Refresh expired access token
Request Body: {refresh_token, device_fingerprint}
Algorithm:
    1. Hash refresh_token with SHA-256
    2. Find matching unexpired, unrevoked token
    3. Revoke old token
    4. Generate new token pair
    5. Store new refresh token
    6. Return new tokens
```

### POST `/api/v1/auth/logout`

```
Purpose: Logout and revoke refresh token
Request Body: {refresh_token, device_fingerprint}
Algorithm:
    1. Find refresh token by hash
    2. Set revoked_at = now
    3. Return success message
```

## 5.2 User Endpoints (`app/api/v1/users.py`)

### GET `/api/v1/users/me`
```
Purpose: Get current user's profile
Auth: Any authenticated user
Returns: UserResponse with all profile fields
```

### PUT `/api/v1/users/me`
```
Purpose: Update current user's profile
Auth: Any authenticated user
Body: {name?, email?, phone?, dob?, profile_photo_url?, notification_preferences?}
Algorithm: Update only provided fields (partial update)
```

### GET `/api/v1/users/`
```
Purpose: List all users (admin only)
Auth: permission: customer:view
Query: page, limit, search, role
Algorithm:
    1. Build query with optional filters
    2. Count total records
    3. Paginate with offset/limit
    4. Return paginated response
```

## 5.3 Product Endpoints (`app/api/v1/products.py`)

### GET `/api/v1/products/`
```
Purpose: List products (public, with filters)
Query: page, limit, search, category_id, status
Algorithm:
    1. Build base query
    2. Apply search filter (name OR description LIKE)
    3. Apply category_id filter
    4. Apply status filter
    5. Count total
    6. Paginate
```

### POST `/api/v1/products/`
```
Purpose: Create new product
Auth: permission: product:create
Body: ProductCreate schema
Algorithm:
    1. Validate all fields with Pydantic
    2. Create Product record
    3. Auto-generate slug, QR code, serial number
    4. Return created product
```

### GET/PUT/DELETE `/api/v1/products/{id}`
```
Standard CRUD with permission checks:
    GET: permission: product:view
    PUT: permission: product:update
    DELETE: permission: product:delete
```

## 5.4 Rental Endpoints (`app/api/v1/rentals.py`)

### POST `/api/v1/rentals/`
```
Purpose: Create a new rental
Auth: permission: rental:create_any (ops_admin) or rental:create_own (portal_user)
Body: RentalCreate
Algorithm:
    1. Verify product exists and is available
    2. Calculate total = daily_rate × number_of_days
    3. Calculate deposit = total × (deposit_percentage / 100)
    4. Create Rental record with status PENDING
    5. Create SecurityDeposit record with status PENDING
    6. Return created rental
```

### POST `/api/v1/rentals/{id}/return`
```
Purpose: Process rental return
Auth: permission: rental:return
Body: {condition_notes, photos, late_fees_waived, waiver_reason}
Algorithm:
    1. Verify rental is ACTIVE or OVERDUE
    2. Set actual_return_date = today
    3. Set status = RETURNED
    4. If today > end_date:
       a. Calculate days_late = today - end_date
       b. Calculate daily_late_fee = daily_rate × 0.1 (10%)
       c. Calculate total_late_fee = daily_late_fee × days_late
       d. Create LateFee record
       e. Update rental.late_fees
    5. Reset product status to AVAILABLE
    6. Clear product.current_holder_id and current_rental_id
    7. Increment product.total_rentals
    8. Return rental
```

### POST `/api/v1/rentals/{id}/extend`
```
Purpose: Extend rental period
Auth: permission: rental:create_own
Body: {new_end_date, reason}
Algorithm:
    1. Verify rental is CONFIRMED or ACTIVE
    2. Verify new_end_date > current end_date
    3. Calculate extension_days = new_end_date - current end_date
    4. Calculate additional_amount = daily_rate × extension_days
    5. Create RentalExtension record with status PENDING
    6. Return extension record
```

## 5.5 Invoice Endpoints (`app/api/v1/invoices.py`)

### POST `/api/v1/invoices/`
```
Purpose: Create invoice with line items
Auth: permission: invoice:create
Algorithm:
    1. Generate invoice_number: INV-YYYYMMDD-NNNN
    2. Create Invoice record with status DRAFT
    3. For each item:
       a. Calculate amount = quantity × unit_price
       b. Calculate tax = amount × tax_rate / 100
       c. Create InvoiceItem record
       d. Add to subtotal
    4. total_amount = subtotal + tax_amount - discount
    5. Return invoice with items
```

### POST `/api/v1/invoices/{id}/payments`
```
Purpose: Record a payment against an invoice
Auth: permission: invoice:create
Algorithm:
    1. Generate payment_number: PAY-YYYYMMDD-NNNN
    2. Create Payment record with status COMPLETED
    3. Update invoice.paid_amount += payment.amount
    4. If paid_amount >= total_amount → status = PAID
    5. Else → status = PARTIALLY_PAID
    6. Return payment record
```

## 5.6 Group Voting Algorithm (`app/services/group_service.py`)

### Algorithm: Cast Vote

```
FUNCTION cast_vote(vote_id, vote_choice, user_id):
    1. Get the vote record
    2. Verify vote.status == PENDING
    3. Verify vote.expires_at > now (not expired)
    4. Verify user is ACTIVE member of the group
    5. Verify user hasn't already voted (prevent double-voting)
    6. Create GroupVoteRecord with the choice
    7. Increment votes_for or votes_against
    8. Return vote record
```

### Algorithm: Resolve Vote

```
FUNCTION resolve_vote(vote_id):
    1. Get the vote record
    2. Count total active members in the group
    3. Calculate total_votes = votes_for + votes_against
    4. Quorum check: if total_votes < total_members / 2:
       → status = EXPIRED (not enough participation)
    5. Majority check: if votes_for > votes_against:
       → status = APPROVED
    6. Otherwise:
       → status = REJECTED
    7. Set resolved_at = now
    8. Return vote

Example:
    Group has 10 active members
    Quorum = 10 / 2 = 5 votes needed
    If 6 vote: 4 approve, 2 reject
    → 4 > 2 → APPROVED
```

## 5.7 Deposit Settlement Algorithm (`app/services/deposit_service.py`)

```
FUNCTION settle_deposit(deposit_id):
    1. Get deposit record
    2. Get all deductions for this deposit
    3. Calculate total_deductions = sum(deduction.amount)
    4. Calculate refund_amount = deposit.amount - total_deductions
    5. If refund_amount < 0 → refund_amount = 0
    6. If total_deductions > 0:
       → status = PARTIALLY_DEDUCTED
    7. Else:
       → status = REFUNDED (full refund)
    8. Set refund_amount, settled_at, refund_at
    9. Return deposit

Example:
    Deposit = ₹10,000
    Deductions: late_fee ₹500, damage ₹1,000
    total_deductions = ₹1,500
    refund_amount = ₹10,000 - ₹1,500 = ₹8,500
    → status = PARTIALLY_DEDUCTED
```

## 5.8 Invoice Number Generation Algorithm

```
FUNCTION _generate_invoice_number():
    1. Get today's date as YYYYMMDD (e.g., "20260808")
    2. Count existing invoices starting with "INV-20260808-"
    3. Increment by 1
    4. Format as 4-digit zero-padded string
    5. Return "INV-20260808-0001"

Same algorithm for payment numbers:
    "PAY-20260808-0001"
```

## 5.9 Loyalty Points Algorithm (`app/services/loyalty_service.py`)

```
Redeem Points:
    1. Get user's current points_balance
    2. If balance < requested points → 400 Bad Request
    3. Subtract points from balance
    4. Create LoyaltyPointsLedger entry (type: REDEEMED)
    5. Return ledger entry with new balance

Referral Bonus:
    1. Referrer gets 500 points
    2. Referred user gets 250 points
    3. Both get LoyaltyPointsLedger entries (type: REFERRAL)
    4. Update Referral record status to "completed"
```

---

# 6. SERVICE LAYER — BUSINESS LOGIC & ALGORITHMS

## 6.1 Service Architecture Pattern

Every service follows this pattern:

```python
class SomeService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: dict) -> Model:
        # 1. Validate input
        # 2. Check business rules
        # 3. Create database record
        # 4. Flush (write to DB but don't commit yet)
        # 5. Return created record

    async def get(self, id: UUID) -> Model:
        # 1. Query by ID
        # 2. If not found → raise HTTPException(404)
        # 3. Return record

    async def list(self, page, limit, filters) -> dict:
        # 1. Build base query
        # 2. Apply filters
        # 3. Count total
        # 4. Paginate with offset/limit
        # 5. Return {items, total, page, limit, pages}
```

## 6.2 Database Query Pattern (Offset Pagination)

```
FUNCTION list_with_pagination(query, page, limit):
    1. Create count_query = SELECT COUNT(*) FROM (query)
    2. Execute count_query → total
    3. Apply offset/limit: query.offset((page-1) * limit).limit(limit)
    4. Execute query → items
    5. Calculate pages = ceil(total / limit)
    6. Return {items, total, page, limit, pages}
```

## 6.3 Eager Loading (N+1 Prevention)

```python
# BAD: N+1 query problem
rentals = await db.execute(select(Rental))
for rental in rentals:
    customer = await db.get(User, rental.customer_id)  # N extra queries!
    product = await db.get(Product, rental.product_id)  # N more queries!

# GOOD: Eager loading
result = await db.execute(
    select(Rental)
    .options(
        selectinload(Rental.customer),  # JOIN in single query
        selectinload(Rental.product),   # JOIN in single query
    )
)
```

## 6.4 Late Fee Calculation Algorithm

```
Background Worker runs daily at midnight:
    1. Find all ACTIVE rentals where end_date < today
    2. For each overdue rental:
       a. Update status to OVERDUE
       b. Get product's late_fee_rate
       c. Calculate daily_late_fee = daily_rate × late_fee_rate
       d. Create LateFee record
       e. Send WebSocket notification to customer

At Return Time:
    1. If actual_return_date > end_date:
       a. days_late = actual_return_date - end_date
       b. total_late_fee = daily_late_fee × days_late
       c. Add to rental.late_fees
       d. Create LateFee record
    2. Late fee can be waived by admin (waiver_reason required)
```

---

# 7. WEBSOCKET LAYER — REAL-TIME ARCHITECTURE

## 7.1 Connection Flow

```
1. Client connects to: ws://localhost:8000/ws/{jwt_token}
2. Server extracts JWT from URL path
3. Decodes JWT to get user_id
4. Accepts connection
5. Adds to active_connections[user_id]
6. User joins default rooms:
   - "user:{user_id}" (personal notifications)
   - "admin:dashboard" (if super_admin/ops_admin)
   - "customer:{customer_id}" (if customer)
7. Listens for messages in a loop
```

## 7.2 Message Protocol

```json
// Client → Server: Ping
{"type": "ping"}

// Server → Client: Pong
{"type": "pong", "timestamp": "2026-08-08T12:00:00Z"}

// Client → Server: Subscribe to room
{"type": "subscribe", "room": "rental:abc123"}

// Server → Client: Subscription confirmed
{"type": "subscribed", "room": "rental:abc123"}

// Server → Client: New notification
{
    "type": "notification:new",
    "data": {
        "title": "Rental Ending Soon",
        "message": "Your rental ends in 3 days",
        "rental_id": "abc123"
    }
}
```

## 7.3 Event Types

```
RENTAL_EVENTS:    rental:created, rental:updated, rental:returned, rental:extended
PAYMENT_EVENTS:   payment:received, payment:failed, invoice:generated
STOCK_EVENTS:     stock:low, stock:updated, product:available
NOTIFICATION:     notification:new, notification:read
CRM_EVENTS:       crm:follow_up, crm:interaction
SYSTEM:           system:maintenance, system:alert
```

---

# 8. MIDDLEWARE LAYER — REQUEST PIPELINE

## 8.1 Middleware Execution Order

```
Request arrives at FastAPI:
    ┌─────────────────────────────────┐
    │ 1. CORSMiddleware               │  ← Handles CORS headers
    │ 2. RequestIDMiddleware          │  ← Generates UUID, sets X-Request-ID
    │ 3. RateLimiterMiddleware        │  ← Checks token bucket, returns 429 if exceeded
    │ 4. AuditMiddleware              │  ← Logs method, path, timing
    │ 5. CompressionMiddleware        │  ← Gzip-compresses large responses
    └─────────────────────────────────┘
    ↓
    Router → Endpoint → Service → Model → Database
    ↓
    Response flows back through middleware in REVERSE order
```

## 8.2 Rate Limiter Algorithm (Token Bucket)

```
Token Bucket Algorithm:
    Capacity: 200 tokens (general) or 5 tokens (auth)
    Refill rate: capacity tokens per 60 seconds

    For each request:
    1. Calculate elapsed_time = now - last_refill
    2. Refill tokens = elapsed_time × refill_rate
    3. Cap at capacity
    4. If tokens >= 1:
       a. Consume 1 token
       b. Allow request
    5. Else:
       a. Return 429 Too Many Requests
       b. Set Retry-After header

Auth endpoints (5/min) are MUCH stricter than general endpoints (200/min).
```

## 8.3 Compression Algorithm

```
CompressionMiddleware:
    1. Check if client accepts gzip (Accept-Encoding header)
    2. Check if response is compressible (text/json/javascript/xml)
    3. Read entire response body
    4. If body <= 1KB → skip compression (not worth it)
    5. If body > 1KB:
       a. Compress with gzip (level 6)
       b. Set Content-Encoding: gzip
       c. Update Content-Length
       d. Return compressed response
```

## 8.4 Audit Logging

```
For every request:
    1. Record start_time = time.monotonic()
    2. Process request
    3. Calculate duration_ms = (now - start_time) × 1000
    4. Log: {method, path, status_code, duration_ms, client_ip, request_id}
    5. Use structlog if available, else stdlib logging
    6. Status-based log level:
       - 2xx → INFO
       - 4xx → WARNING
       - 5xx → ERROR
```

---

# 9. BACKGROUND WORKERS — SCHEDULED TASKS

## 9.1 ARQ Worker Configuration

```
WorkerSettings:
    max_jobs: 4 (concurrent jobs)
    max_tries: 3 (retry on failure)
    job_timeout: 300 seconds (5 min max per job)
    keep_result: 3600 seconds (1 hour)
    redis_settings: from ARQ_REDIS_URL or REDIS_URL
```

## 9.2 Scheduled Tasks (Cron Jobs)

```
┌─────────────────────────────┬──────────┬──────────────────────────────────┐
│ Task                        │ Schedule │ Purpose                          │
├─────────────────────────────┼──────────┼──────────────────────────────────┤
│ overdue_detection           │ 00:00    │ Mark overdue rentals             │
│ late_fee_calculation        │ 01:00    │ Calculate daily late fees        │
│ reminder_dispatch           │ 09:00    │ Send rental reminders            │
│ reservation_expiry          │ Every 5m │ Expire old reservations          │
│ trust_score_recalculation   │ 02:00    │ Recalculate all trust scores     │
│ pdf_generation              │ 03:00    │ Generate pending PDFs            │
│ email_dispatch              │ Every 5m │ Send pending emails              │
│ sms_dispatch                │ Every 5m │ Send pending SMS                 │
│ materialized_view_refresh   │ 04:00    │ Refresh analytics views          │
│ audit_archive               │ Sunday   │ Archive old audit logs           │
│ payment_reminder            │ 09:30    │ Send overdue invoice reminders   │
│ stock_check                 │ 08:00    │ Check low stock alerts           │
└─────────────────────────────┴──────────┴──────────────────────────────────┘
```

## 9.3 Task Algorithms

### Overdue Detection

```
1. Query: SELECT * FROM rentals WHERE status = 'active' AND end_date < NOW()
2. For each rental:
   a. UPDATE status = 'overdue'
   b. Create LateFee record
   c. Send WebSocket notification to customer
   d. Send email notification
```

### Trust Score Recalculation

```
1. For each user with rentals:
   a. Count total_rentals
   b. Count on_time_returns (actual_return_date <= end_date)
   c. Count late_returns
   d. Count disputes_filed
   e. Count disputes_won
   f. Calculate score:
      - Base: 50 points
      - +5 per on-time return (max +50)
      - -10 per late return
      - -5 per dispute filed
      - +10 per dispute won
      - Clamp to 0-100 range
   g. Determine tier:
      - 0-20: unverified
      - 21-40: bronze
      - 41-60: silver
      - 61-80: gold
      - 81-100: platinum
   h. Update user.trust_score and user.trust_tier
```

---

# 10. INFRASTRUCTURE — DOCKER, TESTING, SCRIPTS

## 10.1 Docker Architecture

```
┌─────────────────────────────────────────┐
│ docker-compose.yml                       │
│                                          │
│  ┌──────────┐  ┌──────────┐             │
│  │   API    │  │  Worker  │             │
│  │ :8000    │  │  (ARQ)   │             │
│  └────┬─────┘  └────┬─────┘             │
│       │              │                   │
│  ┌────▼──────────────▼─────┐            │
│  │       Redis :6379       │            │
│  └─────────────────────────┘            │
│                                          │
│  ┌─────────────────────────┐            │
│  │   Nginx :80/:443        │            │
│  │   (reverse proxy)       │            │
│  └─────────────────────────┘            │
└─────────────────────────────────────────┘
```

## 10.2 Nginx Configuration

```
Rate Limiting Zones:
    api zone: 10 requests/second, 10MB shared memory
    auth zone: 5 requests/minute, 10MB shared memory

Proxy Configuration:
    /api/ → http://api:8000 (with rate limiting, burst=20)
    /ws/  → http://api:8000 (WebSocket upgrade, 86400s timeout)
    /health → http://api:8000

Security Headers:
    Strict-Transport-Security: max-age=31536000
    X-Content-Type-Options: nosniff
    X-Frame-Options: DENY
    X-XSS-Protection: 1; mode=block
```

## 10.3 Gunicorn Configuration

```
workers: 4 (CPU count × 2 + 1 recommended)
worker_class: uvicorn.workers.UvicornWorker (async worker)
bind: 0.0.0.0:8000
timeout: 120 seconds
keepalive: 5 seconds
errorlog: stdout
accesslog: stdout
```

## 10.4 Test Structure

```
tests/
├── conftest.py                 # Shared fixtures
│   event_loop                  # Async event loop for entire test session
│   client                      # httpx.AsyncClient with test app
│   db_session                  # Fresh DB session per test (with rollback)
│   auth_headers                # JWT headers for authenticated requests
│
├── unit/                       # Isolated function tests (no DB)
│   test_auth.py                # JWT creation/verification, password hashing
│   test_permissions.py         # RBAC permission checks
│   test_validators.py          # Indian ID validators (phone, PAN, Aadhaar)
│
├── integration/                # Multi-component tests (with DB)
│   test_rentals.py             # Rental create/list/get flow
│
└── system/                     # Full API endpoint tests
    test_api_endpoints.py       # Health check, register, login
```

## 10.5 Seed Data Script

```
scripts/seed_data.py creates:
    Categories: Electronics, Furniture, Vehicles, Tools, Sports,
                Event Equipment, Construction, Medical Equipment
    Products: 17 sample products across categories
    Admin User: super_admin with email admin@rental.com
```

## 10.6 Run Scripts

### Windows (run.bat)

```batch
@echo off
echo Starting Rental Management System Backend...
if not exist "venv" (python -m venv venv)
call venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
pause
```

### Mac/Linux (run.sh)

```bash
#!/bin/bash
echo "Starting Rental Management System Backend..."
if [ ! -d "venv" ]; then python3 -m venv venv; fi
source venv/bin/activate
pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

---

# 11. DATA FLOW DIAGRAMS

## 11.1 User Registration Flow

```
┌─────────┐     POST /auth/register      ┌─────────┐
│ Client  │ ──────────────────────────────▶│  API    │
└─────────┘                               └────┬────┘
                                               │
                    ┌──────────────────────────┤
                    ▼                          ▼
            ┌──────────────┐          ┌──────────────┐
            │ Validate     │          │ Check Unique │
            │ Pydantic     │          │ email/phone  │
            │ Schema       │          │ in DB        │
            └──────┬───────┘          └──────┬───────┘
                   │                          │
                   ▼                          ▼
            ┌──────────────┐          ┌──────────────┐
            │ Hash         │          │ Create User  │
            │ Password     │          │ Record       │
            └──────┬───────┘          └──────┬───────┘
                   │                          │
                   ▼                          ▼
            ┌──────────────┐          ┌──────────────┐
            │ Generate JWT │          │ Store Refresh│
            │ Access Token │          │ Token Hash   │
            └──────┬───────┘          └──────┬───────┘
                   │                          │
                   ▼                          ▼
            ┌─────────────────────────────────────┐
            │ Return {access_token, refresh_token} │
            └─────────────────────────────────────┘
```

## 11.2 Rental Lifecycle Flow

```
┌────────────────────────────────────────────────────────────┐
│                    RENTAL LIFECYCLE                          │
│                                                              │
│  Customer browses products                                   │
│       │                                                      │
│       ▼                                                      │
│  Creates quotation / direct rental                           │
│       │                                                      │
│       ▼                                                      │
│  ┌──────────┐     ┌──────────┐     ┌──────────┐            │
│  │ PENDING  │────▶│CONFIRMED │────▶│  ACTIVE  │            │
│  └──────────┘     └──────────┘     └──────────┘            │
│       │                │                 │                   │
│       │                │                 │                   │
│       ▼                ▼                 ▼                   │
│  ┌──────────┐   ┌──────────┐     ┌──────────┐             │
│  │CANCELLED │   │Deposit   │     │OVERDUE   │             │
│  └──────────┘   │Authorized│     │(auto)    │             │
│                  └──────────┘     └──────────┘             │
│                       │                 │                   │
│                       ▼                 ▼                   │
│                  ┌──────────────────────────┐              │
│                  │       RETURNED           │              │
│                  │  + Late fee calculation  │              │
│                  │  + Product status reset  │              │
│                  └──────────────────────────┘              │
└────────────────────────────────────────────────────────────┘
```

## 11.3 Authentication Flow

```
┌─────────────────────────────────────────────────────────┐
│                   AUTH FLOW                               │
│                                                           │
│  OPTION A: Password Login                                │
│  ┌──────────┐  POST /login   ┌──────────┐               │
│  │  Client  │───────────────▶│  Server  │               │
│  └──────────┘                └────┬─────┘               │
│                                   │                       │
│                    ┌──────────────┤                       │
│                    ▼              ▼                       │
│              ┌──────────┐  ┌──────────┐                  │
│              │ Find User│  │ Verify   │                  │
│              │ by email │  │ Password │                  │
│              └────┬─────┘  └────┬─────┘                  │
│                   │              │                        │
│                   ▼              ▼                        │
│              ┌────────────────────────┐                  │
│              │ Generate JWT + Refresh │                  │
│              └────────────────────────┘                  │
│                                                           │
│  OPTION B: OTP Login                                     │
│  ┌──────────┐  POST /otp/request  ┌──────────┐          │
│  │  Client  │────────────────────▶│  Server  │          │
│  └──────────┘                     └────┬─────┘          │
│                                        │                  │
│                    ┌───────────────────┤                  │
│                    ▼                   ▼                  │
│              ┌──────────┐       ┌──────────┐            │
│              │Generate  │       │ Send SMS │            │
│              │OTP (6dig)│       │ /Email   │            │
│              └──────────┘       └──────────┘            │
│                                                           │
│  ┌──────────┐  POST /otp/verify  ┌──────────┐          │
│  │  Client  │───────────────────▶│  Server  │          │
│  └──────────┘                    └────┬─────┘          │
│                                       │                  │
│                    ┌──────────────────┤                  │
│                    ▼                  ▼                  │
│              ┌──────────┐      ┌──────────┐            │
│              │ Verify   │      │ Find/    │            │
│              │ OTP Code │      │ Create   │            │
│              └──────────┘      │ User     │            │
│                                └──────────┘            │
│                                       │                  │
│                                       ▼                  │
│                              ┌──────────────┐           │
│                              │ Return Tokens│           │
│                              └──────────────┘           │
└─────────────────────────────────────────────────────────┘
```

## 11.4 Payment Processing Flow

```
┌──────────────────────────────────────────────────────┐
│                PAYMENT FLOW                            │
│                                                        │
│  1. Invoice Created (status: DRAFT)                   │
│       │                                                │
│       ▼                                                │
│  2. Invoice Sent (status: PENDING)                    │
│       │                                                │
│       ▼                                                │
│  3. Customer Pays via Razorpay                         │
│       │                                                │
│       ▼                                                │
│  4. Payment Record Created (status: COMPLETED)         │
│       │                                                │
│       ▼                                                │
│  5. Invoice Updated:                                   │
│     paid_amount += payment.amount                      │
│     if paid_amount >= total_amount:                    │
│         status = PAID                                  │
│     else:                                              │
│         status = PARTIALLY_PAID                        │
│       │                                                │
│       ▼                                                │
│  6. Security Deposit Captured (if applicable)          │
│       │                                                │
│       ▼                                                │
│  7. WebSocket Notification Sent                        │
└──────────────────────────────────────────────────────┘
```

## 11.5 Background Worker Flow

```
┌──────────────────────────────────────────────────────┐
│                WORKER FLOW                             │
│                                                        │
│  ARQ Worker starts                                     │
│       │                                                │
│       ├─── Cron: 00:00 ──▶ Overdue Detection          │
│       │                    Find ACTIVE + end_date < now│
│       │                    Mark as OVERDUE             │
│       │                    Create LateFee records      │
│       │                    Send notifications          │
│       │                                                │
│       ├─── Cron: 01:00 ──▶ Late Fee Calculation       │
│       │                    Calculate daily fees        │
│       │                    Update rental.late_fees     │
│       │                                                │
│       ├─── Cron: 09:00 ──▶ Reminder Dispatch          │
│       │                    Rentals ending in 3 days    │
│       │                    Overdue invoice reminders   │
│       │                                                │
│       ├─── Every 5 min ──▶ Reservation Expiry          │
│       │                    Expire old reservations     │
│       │                                                │
│       └─── Cron: 02:00 ──▶ Trust Score Recalc         │
│                            Recalculate all scores     │
│                            Update tiers               │
└──────────────────────────────────────────────────────┘
```

---

# 12. API REFERENCE TABLES

## 12.1 All Endpoints (80+)

```
AUTHENTICATION (6 endpoints)
    POST   /api/v1/auth/register       Register new user
    POST   /api/v1/auth/login          Login with password
    POST   /api/v1/auth/otp/request    Request OTP
    POST   /api/v1/auth/otp/verify     Verify OTP and login
    POST   /api/v1/auth/refresh        Refresh access token
    POST   /api/v1/auth/logout         Logout

USERS (4 endpoints)
    GET    /api/v1/users/me            Get current user profile
    PUT    /api/v1/users/me            Update current user profile
    GET    /api/v1/users/              List all users (admin)
    GET    /api/v1/users/{id}          Get user by ID

PRODUCTS (5 endpoints)
    GET    /api/v1/products/           List products
    POST   /api/v1/products/           Create product
    GET    /api/v1/products/{id}       Get product
    PUT    /api/v1/products/{id}       Update product
    DELETE /api/v1/products/{id}       Delete product

CATEGORIES (4 endpoints)
    GET    /api/v1/categories/         List categories
    POST   /api/v1/categories/         Create category
    GET    /api/v1/categories/{id}     Get category
    PUT    /api/v1/categories/{id}     Update category

RENTALS (5 endpoints)
    GET    /api/v1/rentals/            List rentals
    POST   /api/v1/rentals/            Create rental
    GET    /api/v1/rentals/{id}        Get rental
    POST   /api/v1/rentals/{id}/return Process return
    POST   /api/v1/rentals/{id}/extend Extend rental

QUOTATIONS (5 endpoints)
    GET    /api/v1/quotations/         List quotations
    POST   /api/v1/quotations/         Create quotation
    GET    /api/v1/quotations/{id}     Get quotation
    PUT    /api/v1/quotations/{id}     Update quotation
    PUT    /api/v1/quotations/{id}/status Update status

INVOICES (5 endpoints)
    GET    /api/v1/invoices/           List invoices
    POST   /api/v1/invoices/           Create invoice
    GET    /api/v1/invoices/{id}       Get invoice
    PUT    /api/v1/invoices/{id}/status Update status
    POST   /api/v1/invoices/{id}/payments Record payment

DEPOSITS (4 endpoints)
    GET    /api/v1/deposits/           List deposits
    GET    /api/v1/deposits/{rental_id} Get deposit for rental
    POST   /api/v1/deposits/{id}/settle Settle deposit
    POST   /api/v1/deposits/{id}/deductions Add deduction

DISPUTES (5 endpoints)
    GET    /api/v1/disputes/           List disputes
    POST   /api/v1/disputes/           File dispute
    GET    /api/v1/disputes/{id}       Get dispute
    PUT    /api/v1/disputes/{id}       Update dispute
    PUT    /api/v1/disputes/{id}/resolve Resolve dispute

REPAIRS (5 endpoints)
    GET    /api/v1/repairs/            List repair cases
    POST   /api/v1/repairs/            Report repair
    GET    /api/v1/repairs/{id}        Get repair case
    PUT    /api/v1/repairs/{id}        Update repair
    PUT    /api/v1/repairs/{id}/status Update status

RECOVERY (5 endpoints)
    GET    /api/v1/recovery/           List recovery cases
    POST   /api/v1/recovery/           Initiate recovery
    GET    /api/v1/recovery/{id}       Get recovery case
    PUT    /api/v1/recovery/{id}       Update recovery
    PUT    /api/v1/recovery/{id}/status Update status

GROUPS (7 endpoints)
    GET    /api/v1/groups/             List groups
    POST   /api/v1/groups/             Create group
    GET    /api/v1/groups/{id}         Get group
    POST   /api/v1/groups/{id}/members Add member
    DELETE /api/v1/groups/{id}/members/{user_id} Remove member
    POST   /api/v1/groups/{id}/votes   Create vote
    POST   /api/v1/groups/votes/{id}/cast Cast vote

ENTERPRISE (5 endpoints)
    GET    /api/v1/enterprise/         List enterprises
    POST   /api/v1/enterprise/         Create enterprise
    GET    /api/v1/enterprise/{id}     Get enterprise
    POST   /api/v1/enterprise/{id}/members Add member
    GET    /api/v1/enterprise/{id}/members List members

CRM (5 endpoints)
    GET    /api/v1/crm/contacts        List contacts
    POST   /api/v1/crm/contacts        Create contact
    GET    /api/v1/crm/contacts/{id}   Get contact
    PUT    /api/v1/crm/contacts/{id}   Update contact
    POST   /api/v1/crm/interactions    Create interaction

STOCK (6 endpoints)
    GET    /api/v1/stock/              List stock movements
    POST   /api/v1/stock/locations     Create location
    GET    /api/v1/stock/locations     List locations
    GET    /api/v1/stock/locations/{id} Get location
    POST   /api/v1/stock/movements     Create movement
    GET    /api/v1/stock/levels        List stock levels

LOYALTY (5 endpoints)
    GET    /api/v1/loyalty/points      Get points balance
    GET    /api/v1/loyalty/points/ledger Get points history
    POST   /api/v1/loyalty/points/redeem Redeem points
    GET    /api/v1/loyalty/referrals   Get referrals
    GET    /api/v1/loyalty/referrals/{code}/validate Validate code

NOTIFICATIONS (6 endpoints)
    GET    /api/v1/notifications/      List notifications
    GET    /api/v1/notifications/unread-count Get unread count
    PUT    /api/v1/notifications/{id}/read Mark as read
    PUT    /api/v1/notifications/read-all Mark all as read
    GET    /api/v1/notifications/templates List templates
    POST   /api/v1/notifications/templates Create template

ADMIN (6 endpoints)
    GET    /api/v1/admin/dashboard     Get dashboard stats
    GET    /api/v1/admin/audit-logs    List audit logs
    POST   /api/v1/admin/blacklist     Blacklist user
    DELETE /api/v1/admin/blacklist/{user_id} Remove from blacklist
    GET    /api/v1/admin/blacklist     List blacklisted users
    GET    /api/v1/admin/system/health System health check

FILES (2 endpoints)
    POST   /api/v1/files/presigned-url Get upload URL
    DELETE /api/v1/files/{file_key}    Delete file

DASHBOARD (3 endpoints)
    GET    /api/v1/dashboard/stats     Get dashboard statistics
    GET    /api/v1/dashboard/revenue-chart Get revenue chart
    GET    /api/v1/dashboard/rental-chart Get rental chart

WEBSOCKET (1 endpoint)
    WS     /ws/{token}                 Real-time updates

HEALTH (1 endpoint)
    GET    /health                     Health check
```

---

# FILE-BY-FILE SUMMARY

| File | Lines | Purpose |
|------|-------|---------|
| `app/main.py` | 66 | App entry, middleware, routes, lifespan |
| `app/config.py` | 80 | Settings from env vars |
| `app/core/auth.py` | 69 | JWT + bcrypt + OTP |
| `app/core/permissions.py` | 106 | RBAC with 30+ permissions |
| `app/core/cache.py` | 85 | Redis cache with decorator |
| `app/core/websocket.py` | 75 | Connection manager |
| `app/core/events.py` | 36 | WS event types |
| `app/core/exceptions.py` | 73 | Custom HTTP exceptions |
| `app/middleware/request_id.py` | 20 | UUID injection |
| `app/middleware/rate_limiter.py` | 76 | Token bucket rate limiting |
| `app/middleware/audit.py` | 56 | Request logging |
| `app/middleware/compression.py` | 52 | Gzip compression |
| `app/utils/database.py` | 68 | Async DB engine + sessions |
| `app/utils/redis.py` | 23 | Redis connection pool |
| `app/utils/r2.py` | 81 | Cloudflare R2 storage |
| `app/utils/email.py` | 46 | Resend email client |
| `app/utils/sms.py` | 63 | MSG91 SMS client |
| `app/utils/qr.py` | 41 | QR code generation |
| `app/utils/validators.py` | 50 | Indian ID validators |
| `app/api/deps.py` | 68 | Auth + permission deps |
| `app/api/v1/router.py` | 47 | Main API router |
| `app/api/v1/auth.py` | 261 | Auth endpoints |
| `app/api/v1/users.py` | 88 | User endpoints |
| `app/api/v1/products.py` | 117 | Product endpoints |
| `app/api/v1/rentals.py` | 131 | Rental endpoints |
| `app/api/v1/quotations.py` | 86 | Quotation endpoints |
| `app/api/v1/invoices.py` | 88 | Invoice endpoints |
| `app/api/v1/deposits.py` | 57 | Deposit endpoints |
| `app/api/v1/disputes.py` | 82 | Dispute endpoints |
| `app/api/v1/repairs.py` | 53 | Repair endpoints |
| `app/api/v1/recovery.py` | 58 | Recovery endpoints |
| `app/api/v1/groups.py` | 154 | Group endpoints |
| `app/api/v1/enterprise.py` | 72 | Enterprise endpoints |
| `app/api/v1/crm.py` | 120 | CRM endpoints |
| `app/api/v1/stock.py` | ~130 | Stock endpoints |
| `app/api/v1/loyalty.py` | ~110 | Loyalty endpoints |
| `app/api/v1/notifications.py` | ~120 | Notification endpoints |
| `app/api/v1/admin.py` | ~130 | Admin endpoints |
| `app/api/v1/files.py` | ~50 | File upload endpoints |
| `app/api/v1/dashboard.py` | ~100 | Dashboard endpoints |
| `app/api/v1/categories.py` | 45 | Category endpoints |
| `app/services/auth_service.py` | 217 | Auth business logic |
| `app/services/user_service.py` | ~80 | User CRUD |
| `app/services/product_service.py` | ~100 | Product CRUD |
| `app/services/rental_service.py` | 234 | Rental lifecycle |
| `app/services/quotation_service.py` | ~100 | Quotation management |
| `app/services/invoice_service.py` | 178 | Invoice + payments |
| `app/services/deposit_service.py` | 106 | Deposit settlement |
| `app/services/dispute_service.py` | ~80 | Dispute resolution |
| `app/services/repair_service.py` | ~70 | Repair tracking |
| `app/services/recovery_service.py` | ~70 | Recovery management |
| `app/services/group_service.py` | 341 | Group + voting |
| `app/services/enterprise_service.py` | ~80 | Enterprise management |
| `app/services/crm_service.py` | ~100 | CRM operations |
| `app/services/stock_service.py` | ~100 | Stock management |
| `app/services/loyalty_service.py` | 174 | Loyalty + referrals |
| `app/services/notification_service.py` | 162 | Notifications |
| `app/services/pdf_service.py` | ~20 | PDF generation |
| `app/services/payment_service.py` | ~30 | Razorpay integration |
| `app/services/file_service.py` | ~40 | R2 file operations |
| `app/websockets/handlers.py` | 75 | WS endpoint |
| `app/workers/settings.py` | 15 | ARQ config |
| `app/workers/schedules.py` | ~50 | Cron schedules |
| `app/models/*.py` (22) | ~1800 | All ORM models |
| `app/schemas/*.py` (22) | ~1200 | All Pydantic schemas |
| `alembic/versions/001_initial.py` | ~500 | Initial migration |
| `tests/*.py` (7) | ~400 | Test suite |

---

*This document covers every file, algorithm, data flow, and design decision in the Rental Management System backend. It serves as the definitive technical reference for understanding the entire codebase.*
