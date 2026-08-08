# BACKEND ARCHITECTURE
## Rental Management System — FastAPI Implementation Guide
### Version 3.0 | 2026 | FINAL

---

## Table of Contents

1. [Project Structure](#1-project-structure)
2. [Environment Setup](#2-environment-setup)
3. [Docker Configuration](#3-docker-configuration)
4. [Database Architecture](#4-database-architecture)
5. [Core Modules Implementation](#5-core-modules-implementation)
6. [Authentication & Authorization](#6-authentication--authorization)
7. [API Layer Architecture](#7-api-layer-architecture)
8. [WebSocket Implementation](#8-websocket-implementation)
9. [Background Jobs (ARQ)](#9-background-jobs-arq)
10. [File Storage Integration](#10-file-storage-integration)
11. [Cache Strategy Implementation](#11-cache-strategy-implementation)
12. [Rate Limiting Implementation](#12-rate-limiting-implementation)
13. [Query Optimization](#13-query-optimization)
14. [Data Validation Schemas](#14-data-validation-schemas)
15. [Testing Strategy](#15-testing-strategy)
16. [DevOps & CI/CD](#16-devops--cicd)
17. [Monitoring & Observability](#17-monitoring--observability)
18. [Performance Tuning](#18-performance-tuning)

---

## 1. Project Structure

### 1.1 Directory Layout

```
rental-backend/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI app entry point
│   ├── config.py                  # Settings & env vars
│   ├── dependencies.py            # Shared dependencies
│   │
│   ├── core/                      # Core business logic
│   │   ├── __init__.py
│   │   ├── auth.py                # JWT + refresh token logic
│   │   ├── permissions.py         # RBAC permission checks
│   │   ├── security.py            # Password hashing, OTP generation
│   │   └── exceptions.py          # Custom exception classes
│   │
│   ├── models/                    # SQLAlchemy ORM models
│   │   ├── __init__.py
│   │   ├── base.py                # Base model class
│   │   ├── user.py                # User, RefreshToken, OTP, KYC
│   │   ├── enterprise.py          # Enterprise, EnterpriseMember
│   │   ├── group.py               # Group, GroupMember, GroupDeposit
│   │   ├── product.py             # Product, Category, Accessory
│   │   ├── availability.py        # AvailabilityBlock, Reservation
│   │   ├── rental.py              # Rental, RentalItem, RentalStatus
│   │   ├── quotation.py           # Quotation, QuotationTemplate
│   │   ├── invoice.py             # Invoice, InvoiceItem, Payment
│   │   ├── deposit.py             # SecurityDeposit, DepositDeduction
│   │   ├── custody.py             # CustodyEvent, AccessoryCheck
│   │   ├── fee.py                 # LateFee, ExtensionRequest
│   │   ├── dispute.py             # Dispute
│   │   ├── repair.py              # RepairCase
│   │   ├── recovery.py            # RecoveryCase
│   │   ├── blacklist.py           # Blacklist
│   │   ├── notification.py        # Notification, NotificationTemplate
│   │   ├── pricelist.py           # Pricelist, PricelistItem
│   │   ├── crm.py                 # CRMContact, CRMInteraction, CRMTag
│   │   ├── stock.py               # StockLocation, StockMovement, StockLevel
│   │   ├── loyalty.py             # LoyaltyPointsLedger, Referral
│   │   └── audit.py               # AuditLog (audit schema)
│   │
│   ├── schemas/                   # Pydantic v2 schemas
│   │   ├── __init__.py
│   │   ├── auth.py                # Login, OTP, Token schemas
│   │   ├── user.py                # User create/update/response
│   │   ├── kyc.py                 # KYC upload/verify schemas
│   │   ├── enterprise.py          # Enterprise schemas
│   │   ├── group.py               # Group schemas
│   │   ├── product.py             # Product schemas
│   │   ├── availability.py        # Availability check schemas
│   │   ├── rental.py              # Rental schemas
│   │   ├── quotation.py           # Quotation schemas
│   │   ├── invoice.py             # Invoice schemas
│   │   ├── deposit.py             # Deposit schemas
│   │   ├── custody.py             # Custody schemas
│   │   ├── fee.py                 # Late fee schemas
│   │   ├── dispute.py             # Dispute schemas
│   │   ├── repair.py              # Repair schemas
│   │   ├── recovery.py            # Recovery schemas
│   │   ├── notification.py        # Notification schemas
│   │   ├── pricelist.py           # Pricelist schemas
│   │   ├── crm.py                 # CRM schemas
│   │   ├── stock.py               # Stock schemas
│   │   ├── loyalty.py             # Loyalty schemas
│   │   ├── dashboard.py           # Dashboard aggregate schemas
│   │   ├── common.py              # Shared schemas (pagination, etc.)
│   │   └── websocket.py           # WebSocket message schemas
│   │
│   ├── api/                       # API route handlers
│   │   ├── __init__.py
│   │   ├── deps.py                # Route-level dependencies
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── router.py          # Main v1 router
│   │       ├── auth.py            # Auth endpoints
│   │       ├── users.py           # User endpoints
│   │       ├── kyc.py             # KYC endpoints
│   │       ├── trust_score.py     # Trust score endpoints
│   │       ├── products.py        # Product endpoints
│   │       ├── categories.py      # Category endpoints
│   │       ├── availability.py    # Availability endpoints
│   │       ├── rentals.py         # Rental endpoints
│   │       ├── quotations.py      # Quotation endpoints
│   │       ├── invoices.py        # Invoice endpoints
│   │       ├── deposits.py        # Deposit endpoints
│   │       ├── extensions.py      # Extension endpoints
│   │       ├── disputes.py        # Dispute endpoints
│   │       ├── repairs.py         # Repair endpoints
│   │       ├── recovery.py        # Recovery endpoints
│   │       ├── groups.py          # Group endpoints
│   │       ├── enterprise.py      # Enterprise endpoints
│   │       ├── crm.py             # CRM endpoints
│   │       ├── stock.py           # Stock endpoints
│   │       ├── loyalty.py         # Loyalty endpoints
│   │       ├── notifications.py   # Notification endpoints
│   │       ├── admin.py           # Admin endpoints
│   │       ├── files.py           # File upload endpoints
│   │       └── dashboard.py       # Dashboard endpoints
│   │
│   ├── services/                  # Business logic layer
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   ├── user_service.py
│   │   ├── kyc_service.py
│   │   ├── trust_score_service.py
│   │   ├── product_service.py
│   │   ├── availability_service.py
│   │   ├── rental_service.py
│   │   ├── quotation_service.py
│   │   ├── invoice_service.py
│   │   ├── deposit_service.py
│   │   ├── custody_service.py
│   │   ├── late_fee_service.py
│   │   ├── extension_service.py
│   │   ├── dispute_service.py
│   │   ├── repair_service.py
│   │   ├── recovery_service.py
│   │   ├── group_service.py
│   │   ├── enterprise_service.py
│   │   ├── crm_service.py
│   │   ├── stock_service.py
│   │   ├── loyalty_service.py
│   │   ├── notification_service.py
│   │   ├── pdf_service.py         # PDF generation
│   │   ├── email_service.py       # Email dispatch
│   │   ├── sms_service.py         # SMS dispatch
│   │   ├── payment_service.py     # Razorpay integration
│   │   ├── kyc_provider_service.py # External KYC APIs
│   │   └── file_service.py        # R2 file operations
│   │
│   ├── workers/                   # ARQ background jobs
│   │   ├── __init__.py
│   │   ├── settings.py            # ARQ worker settings
│   │   ├── tasks/
│   │   │   ├── __init__.py
│   │   │   ├── overdue_detection.py
│   │   │   ├── late_fee_calculation.py
│   │   │   ├── reminder_dispatch.py
│   │   │   ├── reservation_expiry.py
│   │   │   ├── trust_score_recalculation.py
│   │   │   ├── pdf_generation.py
│   │   │   ├── email_dispatch.py
│   │   │   ├── sms_dispatch.py
│   │   │   ├── materialized_view_refresh.py
│   │   │   └── audit_archive.py
│   │   └── schedules.py           # Cron job schedules
│   │
│   ├── websockets/                # WebSocket handlers
│   │   ├── __init__.py
│   │   ├── manager.py             # Connection manager
│   │   ├── handlers.py            # WebSocket route handlers
│   │   └── events.py              # Event definitions
│   │
│   ├── middleware/                 # FastAPI middleware
│   │   ├── __init__.py
│   │   ├── request_id.py          # UUID injection
│   │   ├── rate_limiter.py        # Rate limiting
│   │   ├── cors.py                # CORS configuration
│   │   ├── compression.py         # Response compression
│   │   └── audit.py               # Audit logging
│   │
│   └── utils/                     # Shared utilities
│       ├── __init__.py
│       ├── database.py            # DB engine & session
│       ├── redis.py               # Redis connection
│       ├── r2.py                  # Cloudflare R2 client
│       ├── qr.py                  # QR code generation
│       ├── sms.py                 # SMS client
│       ├── email.py               # Email client
│       └── validators.py          # Custom validators
│
├── alembic/                       # Database migrations
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│       ├── 001_initial.py
│       ├── 002_enterprise.py
│       ├── 003_group.py
│       ├── 004_availability.py
│       ├── 005_crm.py
│       └── ...
│
├── tests/                         # Test suite
│   ├── __init__.py
│   ├── conftest.py                # Test fixtures
│   ├── unit/
│   │   ├── test_auth.py
│   │   ├── test_trust_score.py
│   │   ├── test_availability.py
│   │   ├── test_late_fee.py
│   │   └── ...
│   ├── integration/
│   │   ├── test_rental_flow.py
│   │   ├── test_deposit_settlement.py
│   │   ├── test_group_rental.py
│   │   └── ...
│   └── system/
│       ├── test_api_endpoints.py
│       ├── test_websocket.py
│       └── test_full_flow.py
│
├── scripts/                       # Utility scripts
│   ├── seed_data.py               # Seed database
│   ├── create_admin.py            # Create super admin
│   └── refresh_materialized.py    # Refresh analytics views
│
├── docker/                        # Docker configs
│   ├── Dockerfile
│   ├── Dockerfile.worker
│   └── docker-compose.yml
│
├── .env.example                   # Environment variables template
├── .gitignore
├── requirements.txt               # Python dependencies
├── pyproject.toml                 # Project config
├── alembic.ini                    # Alembic config
├── gunicorn.conf.py               # Gunicorn config
└── README.md
```

### 1.2 Module Dependency Flow

```
API Layer (routes)
    │
    ▼
Service Layer (business logic)
    │
    ├──→ Repository Layer (database queries)
    │         │
    │         ▼
    │    Models (SQLAlchemy ORM)
    │
    ├──→ External Services (Razorpay, KYC, Email, SMS)
    │
    ├──→ Cache Layer (Redis)
    │
    └──→ WebSocket Layer (real-time push)
```

---

## 2. Environment Setup

### 2.1 Environment Variables (.env)

```env
# ===========================================
# APPLICATION
# ===========================================
APP_NAME="Rental Management System"
APP_VERSION="3.0.0"
APP_ENV=development  # development | staging | production
DEBUG=true
SECRET_KEY=your-256-bit-secret-key-change-in-production
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001

# ===========================================
# DATABASE (NeonDB PostgreSQL)
# ===========================================
DATABASE_URL=postgresql+asyncpg://user:password@ep-xxx.us-east-2.aws.neon.tech/rental_db?sslmode=require
DATABASE_READ_URL=postgresql+asyncpg://user:password@ep-yyy.us-east-2.aws.neon.tech/rental_db?sslmode=require
DATABASE_POOL_SIZE=10
DATABASE_MAX_OVERFLOW=20
DATABASE_POOL_TIMEOUT=30

# ===========================================
# REDIS (Upstash)
# ===========================================
REDIS_URL=rediss://:password@xxx.upstash.io:6379
REDIS_MAX_CONNECTIONS=20

# ===========================================
# JWT AUTHENTICATION
# ===========================================
JWT_SECRET_KEY=your-jwt-secret-key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=30

# ===========================================
# FILE STORAGE (Cloudflare R2)
# ===========================================
R2_ACCOUNT_ID=your-cloudflare-account-id
R2_ACCESS_KEY_ID=your-r2-access-key
R2_SECRET_ACCESS_KEY=your-r2-secret-key
R2_BUCKET_NAME=rental-files
R2_PUBLIC_URL=https://pub-xxx.r2.dev

# ===========================================
# PAYMENTS (Razorpay)
# ===========================================
RAZORPAY_KEY_ID=rzp_test_xxx
RAZORPAY_KEY_SECRET=your-razorpay-secret
RAZORPAY_WEBHOOK_SECRET=your-webhook-secret

# ===========================================
# E-KYC PROVIDERS
# ===========================================
DIGIO_API_KEY=your-digio-api-key
DIGIO_API_SECRET=your-digio-secret
SUREPASS_API_KEY=your-surepass-key
FACEIO_APP_ID=your-faceio-app-id
FACEIO_SECRET=your-faceio-secret

# ===========================================
# NOTIFICATIONS
# ===========================================
# Email (Resend)
RESEND_API_KEY=re_xxx
EMAIL_FROM=noreply@yourdomain.com

# SMS (MSG91)
MSG91_API_KEY=your-msg91-key
MSG91_TEMPLATE_ID=your-template-id

# Push (Firebase)
FCM_CREDENTIALS_PATH=./firebase-credentials.json

# ===========================================
# MONITORING
# ===========================================
SENTRY_DSN=https://xxx@sentry.io/xxx
LOG_LEVEL=INFO  # DEBUG | INFO | WARNING | ERROR

# ===========================================
# WORKER
# ===========================================
ARQ_REDIS_URL=rediss://:password@xxx.upstash.io:6379
WORKER_CONCURRENCY=4
WORKER_MAX_RETRIES=3
```

### 2.2 Settings Class (Pydantic)

```python
# app/config.py
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Rental Management System"
    APP_VERSION: str = "3.0.0"
    APP_ENV: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str
    ALLOWED_ORIGINS: list[str] = ["http://localhost:3000"]
    
    # Database
    DATABASE_URL: str
    DATABASE_READ_URL: str | None = None
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20
    DATABASE_POOL_TIMEOUT: int = 30
    
    # Redis
    REDIS_URL: str
    REDIS_MAX_CONNECTIONS: int = 20
    
    # JWT
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    
    # File Storage
    R2_ACCOUNT_ID: str
    R2_ACCESS_KEY_ID: str
    R2_SECRET_ACCESS_KEY: str
    R2_BUCKET_NAME: str = "rental-files"
    R2_PUBLIC_URL: str
    
    # Razorpay
    RAZORPAY_KEY_ID: str
    RAZORPAY_KEY_SECRET: str
    RAZORPAY_WEBHOOK_SECRET: str
    
    # KYC
    DIGIO_API_KEY: str
    DIGIO_API_SECRET: str
    SUREPASS_API_KEY: str
    FACEIO_APP_ID: str
    FACEIO_SECRET: str
    
    # Email
    RESEND_API_KEY: str
    EMAIL_FROM: str
    
    # SMS
    MSG91_API_KEY: str
    MSG91_TEMPLATE_ID: str
    
    # Monitoring
    SENTRY_DSN: str | None = None
    LOG_LEVEL: str = "INFO"
    
    # Worker
    ARQ_REDIS_URL: str | None = None
    WORKER_CONCURRENCY: int = 4

    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
```

---

## 3. Docker Configuration

### 3.1 Dockerfile (API Server)

```dockerfile
# docker/Dockerfile
FROM python:3.12-slim AS base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Create app user
RUN groupadd -r appuser && useradd -r -g appuser appuser

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Switch to app user
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

# Run with gunicorn
CMD ["gunicorn", "app.main:app", "-c", "gunicorn.conf.py"]
```

### 3.2 Dockerfile (Worker)

```dockerfile
# docker/Dockerfile.worker
FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd -r worker && useradd -r -g worker worker

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

USER worker

HEALTHCHECK --interval=60s --timeout=10s --retries=3 \
    CMD python -c "import redis; r = redis.from_url('${REDIS_URL}'); r.ping()"

CMD ["arq", "app.workers.settings.WorkerSettings"]
```

### 3.3 Docker Compose

```yaml
# docker/docker-compose.yml
version: '3.8'

services:
  # API Server
  api:
    build:
      context: ..
      dockerfile: docker/Dockerfile
    ports:
      - "8000:8000"
    env_file:
      - ../.env
    depends_on:
      redis:
        condition: service_healthy
    volumes:
      - ../app:/app/app
    restart: unless-stopped
    networks:
      - rental-network

  # Background Worker
  worker:
    build:
      context: ..
      dockerfile: docker/Dockerfile.worker
    env_file:
      - ../.env
    depends_on:
      redis:
        condition: service_healthy
    volumes:
      - ../app:/app/app
    restart: unless-stopped
    networks:
      - rental-network

  # Redis (local for development)
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    volumes:
      - redis-data:/data
    restart: unless-stopped
    networks:
      - rental-network

  # Nginx (reverse proxy)
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - api
    restart: unless-stopped
    networks:
      - rental-network

volumes:
  redis-data:

networks:
  rental-network:
    driver: bridge
```

### 3.4 Nginx Configuration

```nginx
# docker/nginx.conf
events {
    worker_connections 1024;
}

http {
    # Rate limiting zones
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=auth:10m rate=5r/m;

    # Upstream (API servers)
    upstream api_servers {
        least_conn;
        server api:8000;
        keepalive 32;
    }

    # API Server
    server {
        listen 80;
        server_name api.yourdomain.com;

        # Redirect HTTP to HTTPS
        return 301 https://$host$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name api.yourdomain.com;

        # SSL
        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers HIGH:!aNULL:!MD5;

        # Security headers
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-Frame-Options "DENY" always;
        add_header X-XSS-Protection "1; mode=block" always;

        # Gzip compression
        gzip on;
        gzip_types text/plain application/json application/javascript text/css;
        gzip_min_length 1000;

        # API routes
        location /api/ {
            limit_req zone=api burst=20 nodelay;
            
            proxy_pass http://api_servers;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # Connection pooling
            proxy_http_version 1.1;
            proxy_set_header Connection "";
            
            # Timeouts
            proxy_connect_timeout 30s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
        }

        # Auth routes (stricter rate limit)
        location /api/v1/auth/ {
            limit_req zone=auth burst=5 nodelay;
            
            proxy_pass http://api_servers;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }

        # WebSocket routes
        location /ws/ {
            proxy_pass http://api_servers;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host $host;
            proxy_read_timeout 86400;
        }

        # Health check
        location /health {
            proxy_pass http://api_servers;
        }
    }
}
```

### 3.5 Requirements.txt

```
# Web framework
fastapi==0.115.0
uvicorn[standard]==0.30.0
gunicorn==22.0.0
python-multipart==0.0.9

# Database
sqlalchemy[asyncio]==2.0.35
asyncpg==0.30.0
alembic==1.13.0
greenlet==3.0.0

# Redis
redis[hiredis]==5.1.0
aioredis==2.0.1

# Authentication
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
pyjwt==2.9.0

# Validation
pydantic==2.9.0
pydantic-settings==2.5.0
email-validator==2.2.0

# HTTP Client
httpx==0.27.0
aiohttp==3.10.0

# File Storage
boto3==1.35.0

# Payments
razorpay==1.4.0

# PDF Generation
weasyprint==62.0
jinja2==3.1.4

# Background Jobs
arq==0.26.0

# Monitoring
sentry-sdk[fastapi]==2.14.0
structlog==24.4.0

# QR Code
qrcode[pil]==7.4.2

# Testing
pytest==8.3.0
pytest-asyncio==0.24.0
pytest-cov==5.0.0
httpx==0.27.0
factory-boy==3.3.0

# Code quality
ruff==0.6.0
mypy==1.11.0
black==24.8.0

# Utilities
python-dotenv==1.0.1
orjson==3.10.0
python-dateutil==2.9.0
```

---

## 4. Database Architecture

### 4.1 Database Connection Setup

```python
# app/utils/database.py
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase
from app.config import settings

class Base(DeclarativeBase):
    pass

# Primary engine (writes)
primary_engine = create_async_engine(
    settings.DATABASE_URL,
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
    pool_timeout=settings.DATABASE_POOL_TIMEOUT,
    pool_pre_ping=True,
    echo=settings.DEBUG,
)

# Read replica engine (reads)
read_engine = create_async_engine(
    settings.DATABASE_READ_URL or settings.DATABASE_URL,
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
    pool_pre_ping=True,
    echo=False,
)

# Session factories
PrimarySessionLocal = async_sessionmaker(
    bind=primary_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

ReadSessionLocal = async_sessionmaker(
    bind=read_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Dependency injection
async def get_db() -> AsyncSession:
    """Write operations → Primary"""
    async with PrimarySessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

async def get_read_db() -> AsyncSession:
    """Read operations → Replica"""
    async with ReadSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
```

### 4.2 Base Model with Audit Fields

```python
# app/models/base.py
import uuid
from datetime import datetime
from sqlalchemy import Column, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from app.utils.database import Base

class TimestampMixin:
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class BaseModel(Base, TimestampMixin):
    __abstract__ = True
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
```

### 4.3 Alembic Migration Setup

```python
# alembic/env.py
import asyncio
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context
from app.utils.database import Base
from app.models import *  # Import all models

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()

async def run_async_migrations():
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()

def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

### 4.4 Index Creation Example

```python
# app/models/user.py
from sqlalchemy import Index
from app.models.base import BaseModel

class User(BaseModel):
    __tablename__ = "users"
    
    # ... columns ...
    
    __table_args__ = (
        Index("idx_users_phone", "phone", unique=True),
        Index("idx_users_email", "email", unique=True),
        Index("idx_users_trust_tier", "trust_tier"),
        Index("idx_users_blacklisted", "blacklisted", postgresql_where="blacklisted = true"),
        Index("idx_users_enterprise_id", "enterprise_id"),
        Index("idx_users_name_tsvector", "name", postgresql_using="gin"),
    )
```

---

## 5. Core Modules Implementation

### 5.1 FastAPI Application Entry

```python
# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

from app.config import settings
from app.api.v1.router import api_router
from app.middleware import (
    RequestIDMiddleware,
    RateLimiterMiddleware,
    AuditMiddleware,
    CompressionMiddleware,
)
from app.websockets.handlers import ws_router
from app.utils.database import primary_engine
from app.workers.settings import startup, shutdown

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await startup()
    yield
    # Shutdown
    await shutdown()
    await primary_engine.dispose()

# Sentry (if configured)
if settings.SENTRY_DSN:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        integrations=[FastApiIntegration()],
        traces_sample_rate=0.1,
    )

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan,
)

# Middleware stack (order matters - last added = first executed)
app.add_middleware(CompressionMiddleware)
app.add_middleware(AuditMiddleware)
app.add_middleware(RateLimiterMiddleware)
app.add_middleware(RequestIDMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(api_router, prefix="/api/v1")
app.include_router(ws_router, prefix="/ws")

# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": settings.APP_VERSION}
```

### 5.2 API Router Setup

```python
# app/api/v1/router.py
from fastapi import APIRouter
from app.api.v1 import (
    auth, users, kyc, trust_score, products, categories,
    availability, rentals, quotations, invoices, deposits,
    extensions, disputes, repairs, recovery, groups,
    enterprise, crm, stock, loyalty, notifications,
    admin, files, dashboard,
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(kyc.router, prefix="/kyc", tags=["KYC"])
api_router.include_router(trust_score.router, prefix="/trust-score", tags=["Trust Score"])
api_router.include_router(products.router, prefix="/products", tags=["Products"])
api_router.include_router(categories.router, prefix="/categories", tags=["Categories"])
api_router.include_router(availability.router, prefix="/availability", tags=["Availability"])
api_router.include_router(rentals.router, prefix="/rentals", tags=["Rentals"])
api_router.include_router(quotations.router, prefix="/quotations", tags=["Quotations"])
api_router.include_router(invoices.router, prefix="/invoices", tags=["Invoices"])
api_router.include_router(deposits.router, prefix="/deposits", tags=["Deposits"])
api_router.include_router(extensions.router, prefix="/extensions", tags=["Extensions"])
api_router.include_router(disputes.router, prefix="/disputes", tags=["Disputes"])
api_router.include_router(repairs.router, prefix="/repairs", tags=["Repairs"])
api_router.include_router(recovery.router, prefix="/recovery", tags=["Recovery"])
api_router.include_router(groups.router, prefix="/groups", tags=["Groups"])
api_router.include_router(enterprise.router, prefix="/enterprise", tags=["Enterprise"])
api_router.include_router(crm.router, prefix="/crm", tags=["CRM"])
api_router.include_router(stock.router, prefix="/stock", tags=["Stock"])
api_router.include_router(loyalty.router, prefix="/loyalty", tags=["Loyalty"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["Notifications"])
api_router.include_router(admin.router, prefix="/admin", tags=["Admin"])
api_router.include_router(files.router, prefix="/files", tags=["Files"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
```

### 5.3 Dependencies

```python
# app/dependencies.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from app.utils.database import get_db, get_read_db
from app.core.auth import verify_access_token
from app.models.user import User
from app.core.permissions import check_permission

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_read_db),
) -> User:
    """Get current authenticated user from JWT token."""
    token = credentials.credentials
    payload = verify_access_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
    
    user = await db.get(User, payload["user_id"])
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    
    if user.blacklisted:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is blacklisted",
        )
    
    return user

def require_role(*roles):
    """Dependency that checks user has required role."""
    async def role_checker(user: User = Depends(get_current_user)):
        if user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role {user.role} not authorized",
            )
        return user
    return role_checker

def require_permission(permission: str):
    """Dependency that checks user has specific permission."""
    async def perm_checker(user: User = Depends(get_current_user)):
        if not check_permission(user.role, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission '{permission}' required",
            )
        return user
    return perm_checker
```

---

## 6. Authentication & Authorization

### 6.1 JWT Token Implementation

```python
# app/core/auth.py
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.config import settings
import hashlib
import secrets

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(user_id: str, role: str, user_type: str, enterprise_id: str | None = None) -> str:
    """Create JWT access token (15 min TTL)."""
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": user_id,
        "role": role,
        "user_type": user_type,
        "enterprise_id": enterprise_id,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "jti": secrets.token_hex(16),  # Unique token ID
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

def verify_access_token(token: str) -> dict | None:
    """Verify and decode JWT access token."""
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        return payload
    except JWTError:
        return None

def create_refresh_token() -> str:
    """Create opaque refresh token (32 bytes)."""
    return secrets.token_hex(32)

def hash_token(token: str) -> str:
    """Hash token for secure storage."""
    return hashlib.sha256(token.encode()).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash."""
    return pwd_context.verify(plain_password, hashed_password)

def hash_password(password: str) -> str:
    """Hash password."""
    return pwd_context.hash(password)

def generate_otp() -> str:
    """Generate 6-digit OTP."""
    return str(secrets.randbelow(1000000)).zfill(6)
```

### 6.2 RBAC Permission Matrix

```python
# app/core/permissions.py
from enum import Enum

class Role(str, Enum):
    SUPER_ADMIN = "super_admin"
    OPS_ADMIN = "ops_admin"
    FIELD_AGENT = "field_agent"
    PORTAL_USER = "portal_user"

class Permission(str, Enum):
    # Products
    PRODUCT_VIEW = "product:view"
    PRODUCT_CREATE = "product:create"
    PRODUCT_UPDATE = "product:update"
    PRODUCT_DELETE = "product:delete"
    
    # Rentals
    RENTAL_CREATE_OWN = "rental:create_own"
    RENTAL_CREATE_ANY = "rental:create_any"
    RENTAL_VIEW_OWN = "rental:view_own"
    RENTAL_VIEW_ANY = "rental:view_any"
    RENTAL_CONFIRM = "rental:confirm"
    RENTAL_RETURN = "rental:return"
    RENTAL_CANCEL = "rental:cancel"
    
    # Customers
    CUSTOMER_VIEW = "customer:view"
    CUSTOMER_CREATE = "customer:create"
    CUSTOMER_UPDATE = "customer:update"
    CUSTOMER_BLACKLIST = "customer:blacklist"
    
    # Finance
    DEPOSIT_VIEW = "deposit:view"
    DEPOSIT_SETTLE = "deposit:settle"
    DEPOSIT_DEDUCT = "deposit:deduct"
    INVOICE_VIEW = "invoice:view"
    INVOICE_CREATE = "invoice:create"
    
    # Operations
    INSPECTION_PERFORM = "inspection:perform"
    REPAIR_MANAGE = "repair:manage"
    RECOVERY_MANAGE = "recovery:manage"
    
    # Admin
    ADMIN_DASHBOARD = "admin:dashboard"
    ADMIN_SETTINGS = "admin:settings"
    ADMIN_AUDIT = "admin:audit"
    ADMIN_BLACKLIST = "admin:blacklist"
    
    # CRM
    CRM_VIEW = "crm:view"
    CRM_MANAGE = "crm:manage"
    
    # Stock
    STOCK_VIEW = "stock:view"
    STOCK_MANAGE = "stock:manage"

# Permission matrix by role
ROLE_PERMISSIONS = {
    Role.SUPER_ADMIN: [p.value for p in Permission],  # All permissions
    Role.OPS_ADMIN: [
        Permission.PRODUCT_VIEW.value, Permission.PRODUCT_CREATE.value, Permission.PRODUCT_UPDATE.value,
        Permission.RENTAL_CREATE_ANY.value, Permission.RENTAL_VIEW_ANY.value,
        Permission.RENTAL_CONFIRM.value, Permission.RENTAL_RETURN.value,
        Permission.CUSTOMER_VIEW.value, Permission.CUSTOMER_CREATE.value, Permission.CUSTOMER_UPDATE.value,
        Permission.DEPOSIT_VIEW.value, Permission.DEPOSIT_SETTLE.value, Permission.DEPOSIT_DEDUCT.value,
        Permission.INVOICE_VIEW.value, Permission.INVOICE_CREATE.value,
        Permission.INSPECTION_PERFORM.value, Permission.REPAIR_MANAGE.value,
        Permission.ADMIN_DASHBOARD.value, Permission.ADMIN_AUDIT.value,
        Permission.CRM_VIEW.value, Permission.CRM_MANAGE.value,
        Permission.STOCK_VIEW.value, Permission.STOCK_MANAGE.value,
    ],
    Role.FIELD_AGENT: [
        Permission.PRODUCT_VIEW.value,
        Permission.RENTAL_VIEW_ANY.value,
        Permission.INSPECTION_PERFORM.value,
    ],
    Role.PORTAL_USER: [
        Permission.PRODUCT_VIEW.value,
        Permission.RENTAL_CREATE_OWN.value, Permission.RENTAL_VIEW_OWN.value,
        Permission.DEPOSIT_VIEW.value, Permission.INVOICE_VIEW.value,
    ],
}

def check_permission(role: str, permission: str) -> bool:
    """Check if role has specific permission."""
    return permission in ROLE_PERMISSIONS.get(role, [])

# Dependency for checking permissions
def require_permission(permission: str):
    async def dependency(current_user: User = Depends(get_current_user)):
        if not check_permission(current_user.role, permission):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return current_user
    return Depends(dependency)
```

## 7. API Layer Architecture

### 7.1 Router Organization

```
app/api/v1/
├── __init__.py
├── router.py              # Main API router
├── deps.py                # Dependencies (auth, db, permissions)
├── endpoints/
│   ├── auth.py            # Login, register, refresh, logout
│   ├── users.py           # User profile management
│   ├── customers.py       # Customer CRUD
│   ├── products.py        # Product catalog
│   ├── rentals.py         # Rental lifecycle
│   ├── quotes.py          # Quote builder
│   ├── orders.py          # Order processing
│   ├── invoices.py        # Invoice generation
│   ├── payments.py        # Payment processing
│   ├── deposits.py        # Deposit management
│   ├── inspections.py     # Inspection workflows
│   ├── repairs.py         # Repair tracking
│   ├── recoveries.py      # Recovery actions
│   ├── stock.py           # Stock management
│   ├── teams.py           # Enterprise teams
│   ├── groups.py          # Groups
│   ├── analytics.py       # Analytics queries
│   ├── reports.py         # Report generation
│   └── admin.py           # Admin operations
```

### 7.2 Example Route Handler

```python
# app/api/v1/endpoints/rentals.py
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import uuid

from app.api.deps import get_db, get_current_user, require_permission
from app.core.permissions import Permission
from app.schemas.rental import (
    RentalCreate, RentalResponse, RentalListResponse, 
    RentalReturnRequest, RentalExtensionRequest
)
from app.services.rental_service import RentalService
from app.models.user import User

router = APIRouter(prefix="/rentals", tags=["Rentals"])

@router.get("/", response_model=RentalListResponse)
async def list_rentals(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status_filter: Optional[str] = Query(None, alias="status"),
    search: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = require_permission(Permission.RENTAL_VIEW_ANY.value)
):
    """List all rentals with pagination and filtering."""
    service = RentalService(db)
    
    # Build filters
    filters = {}
    if status_filter:
        filters["status"] = status_filter
    if start_date:
        filters["start_date__gte"] = start_date
    if end_date:
        filters["end_date__lte"] = end_date
    
    # For portal users, only show their own rentals
    if current_user.role == "portal_user":
        filters["customer_id"] = current_user.customer_id
    
    result = await service.list_rentals(
        filters=filters,
        search=search,
        page=page,
        limit=limit
    )
    
    return result

@router.post("/", response_model=RentalResponse, status_code=status.HTTP_201_CREATED)
async def create_rental(
    rental_data: RentalCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = require_permission(Permission.RENTAL_CREATE_ANY.value)
):
    """Create a new rental."""
    service = RentalService(db)
    rental = await service.create_rental(
        data=rental_data.dict(),
        created_by=current_user.id
    )
    return rental

@router.get("/{rental_id}", response_model=RentalResponse)
async def get_rental(
    rental_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = require_permission(Permission.RENTAL_VIEW_ANY.value)
):
    """Get rental by ID."""
    service = RentalService(db)
    rental = await service.get_rental(rental_id)
    
    if not rental:
        raise HTTPException(status_code=404, detail="Rental not found")
    
    # Portal users can only view their own rentals
    if (current_user.role == "portal_user" and 
        rental.customer_id != current_user.customer_id):
        raise HTTPException(status_code=403, detail="Access denied")
    
    return rental

@router.post("/{rental_id}/return", response_model=RentalResponse)
async def process_return(
    rental_id: uuid.UUID,
    return_data: RentalReturnRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = require_permission(Permission.RENTAL_RETURN.value)
):
    """Process rental return with inspection."""
    service = RentalService(db)
    rental = await service.process_return(
        rental_id=rental_id,
        condition_notes=return_data.condition_notes,
        photos=return_data.photos,
        processed_by=current_user.id
    )
    return rental

@router.post("/{rental_id}/extend", response_model=RentalResponse)
async def extend_rental(
    rental_id: uuid.UUID,
    extension_data: RentalExtensionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = require_permission(Permission.RENTAL_CREATE_OWN.value)
):
    """Extend rental period."""
    service = RentalService(db)
    rental = await service.extend_rental(
        rental_id=rental_id,
        new_end_date=extension_data.new_end_date,
        extended_by=current_user.id
    )
    return rental
```

## 8. WebSocket Implementation

### 8.1 Connection Manager

```python
# app/core/websocket.py
from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List, Set
import json
import asyncio
from datetime import datetime

class ConnectionManager:
    """Manages WebSocket connections for real-time updates."""
    
    def __init__(self):
        # user_id -> set of WebSocket connections
        self.active_connections: Dict[str, List[WebSocket]] = {}
        # room -> set of user_ids
        self.rooms: Dict[str, Set[str]] = {}
        self._lock = asyncio.Lock()
    
    async def connect(self, websocket: WebSocket, user_id: str, rooms: List[str] = None):
        """Accept WebSocket connection and register user."""
        await websocket.accept()
        
        async with self._lock:
            if user_id not in self.active_connections:
                self.active_connections[user_id] = []
            self.active_connections[user_id].append(websocket)
            
            # Join rooms
            if rooms:
                for room in rooms:
                    if room not in self.rooms:
                        self.rooms[room] = set()
                    self.rooms[room].add(user_id)
    
    async def disconnect(self, websocket: WebSocket, user_id: str, rooms: List[str] = None):
        """Remove WebSocket connection."""
        async with self._lock:
            if user_id in self.active_connections:
                self.active_connections[user_id].remove(websocket)
                if not self.active_connections[user_id]:
                    del self.active_connections[user_id]
            
            # Leave rooms
            if rooms:
                for room in rooms:
                    if room in self.rooms:
                        self.rooms[room].discard(user_id)
                        if not self.rooms[room]:
                            del self.rooms[room]
    
    async def send_personal_message(self, message: dict, user_id: str):
        """Send message to specific user."""
        if user_id in self.active_connections:
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_json(message)
                except:
                    pass
    
    async def broadcast_to_room(self, message: dict, room: str, exclude_user: str = None):
        """Broadcast message to all users in a room."""
        if room in self.rooms:
            for user_id in self.rooms[room]:
                if user_id != exclude_user:
                    await self.send_personal_message(message, user_id)
    
    async def broadcast_to_all(self, message: dict):
        """Broadcast message to all connected users."""
        for user_id in self.active_connections:
            await self.send_personal_message(message, user_id)

manager = ConnectionManager()
```

### 8.2 WebSocket Events

```python
# app/core/events.py
from enum import Enum

class WSEvent(str, Enum):
    # Connection events
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    
    # Rental events
    RENTAL_CREATED = "rental:created"
    RENTAL_UPDATED = "rental:updated"
    RENTAL_RETURNED = "rental:returned"
    RENTAL_EXTENDED = "rental:extended"
    
    # Payment events
    PAYMENT_RECEIVED = "payment:received"
    PAYMENT_FAILED = "payment:failed"
    INVOICE_GENERATED = "invoice:generated"
    
    # Stock events
    STOCK_LOW = "stock:low"
    STOCK_UPDATED = "stock:updated"
    PRODUCT_AVAILABLE = "product:available"
    
    # Notification events
    NOTIFICATION_NEW = "notification:new"
    NOTIFICATION_READ = "notification:read"
    
    # CRM events
    CRM_FOLLOW_UP = "crm:follow_up"
    CRM_INTERACTION = "crm:interaction"
    
    # System events
    SYSTEM_MAINTENANCE = "system:maintenance"
    SYSTEM_ALERT = "system:alert"

# WebSocket endpoint
@app.websocket("/ws/{token}")
async def websocket_endpoint(websocket: WebSocket, token: str):
    """WebSocket endpoint for real-time updates."""
    # Verify token
    user = await verify_ws_token(token)
    if not user:
        await websocket.close(code=4001, reason="Unauthorized")
        return
    
    # Determine rooms based on user role
    rooms = [f"user:{user.id}"]
    if user.role in ["super_admin", "ops_admin"]:
        rooms.append("admin:dashboard")
    if user.customer_id:
        rooms.append(f"customer:{user.customer_id}")
    
    await manager.connect(websocket, user.id, rooms)
    
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle incoming messages
            if message.get("type") == "ping":
                await websocket.send_json({"type": "pong", "timestamp": datetime.utcnow().isoformat()})
            elif message.get("type") == "subscribe":
                # Subscribe to additional rooms
                room = message.get("room")
                if room:
                    async with manager._lock:
                        if room not in manager.rooms:
                            manager.rooms[room] = set()
                        manager.rooms[room].add(user.id)
    
    except WebSocketDisconnect:
        await manager.disconnect(websocket, user.id, rooms)
```

## 9. Background Jobs (ARQ)

### 9.1 Worker Configuration

```python
# app/workers/worker.py
from arq import cron
from arq.connections import RedisSettings
from datetime import timedelta

async def startup(ctx):
    """Initialize worker resources."""
    ctx['db'] = await create_async_engine(settings.DATABASE_URL)
    ctx['redis'] = await aioredis.from_url(settings.REDIS_URL)

async def shutdown(ctx):
    """Cleanup worker resources."""
    await ctx['db'].dispose()
    await ctx['redis'].close()

# Worker settings
class WorkerSettings:
    functions = [
        'app.workers.tasks.rental.send_rental_reminders',
        'app.workers.tasks.rental.process_overdue_rentals',
        'app.workers.tasks.rental.generate_daily_report',
        'app.workers.tasks.customer.process_e_kyc',
        'app.workers.tasks.customer.send_otp_email',
        'app.workers.tasks.customer.send_otp_sms',
        'app.workers.tasks.invoice.generate_recurring_invoices',
        'app.workers.tasks.invoice.send_payment_reminders',
        'app.workers.tasks.stock.check_low_stock',
        'app.workers.tasks.notification.process_notification_queue',
        'app.workers.tasks.recovery.process_recovery_queue',
        'app.workers.tasks.analytics.refresh_analytics_cache',
    ]
    cron_jobs = [
        cron('app.workers.tasks.rental.send_rental_reminders', minute=0, hour=9),
        cron('app.workers.tasks.rental.process_overdue_rentals', minute=0, hour=0),
        cron('app.workers.tasks.rental.generate_daily_report', minute=0, hour=1),
        cron('app.workers.tasks.invoice.generate_recurring_invoices', minute=0, hour=2),
        cron('app.workers.tasks.invoice.send_payment_reminders', minute=30, hour=9),
        cron('app.workers.tasks.stock.check_low_stock', minute=0, hour=8),
        cron('app.workers.tasks.analytics.refresh_analytics_cache', minute=0, hour=3),
    ]
    on_startup = startup
    on_shutdown = shutdown
    redis_settings = RedisSettings.from_dsn(settings.REDIS_URL)
```

### 9.2 Example Task

```python
# app/workers/tasks/rental.py
from datetime import datetime, timedelta
from sqlalchemy import select, and_
from app.models.rental import Rental
from app.models.customer import Customer
from app.core.websocket import manager
from app.core.events import WSEvent

async def send_rental_reminders(ctx):
    """Send reminders for rentals ending in 3 days."""
    async with ctx['db'].session() as session:
        three_days_from_now = datetime.utcnow() + timedelta(days=3)
        
        # Find rentals ending soon
        query = select(Rental).where(
            and_(
                Rental.status == "active",
                Rental.end_date <= three_days_from_now,
                Rental.end_date > datetime.utcnow()
            )
        )
        
        result = await session.execute(query)
        rentals = result.scalars().all()
        
        for rental in rentals:
            # Send WebSocket notification
            await manager.send_personal_message({
                "type": WSEvent.NOTIFICATION_NEW.value,
                "data": {
                    "title": "Rental Ending Soon",
                    "message": f"Your rental for {rental.product.name} ends on {rental.end_date}",
                    "rental_id": str(rental.id)
                }
            }, str(rental.customer.user_id))
            
            # Send email reminder
            await send_email(
                to=rental.customer.email,
                subject="Rental Reminder",
                template="rental_reminder.html",
                context={
                    "customer_name": rental.customer.full_name,
                    "product_name": rental.product.name,
                    "end_date": rental.end_date
                }
            )

async def process_overdue_rentals(ctx):
    """Process overdue rentals and apply late fees."""
    async with ctx['db'].session() as session:
        # Find overdue rentals
        query = select(Rental).where(
            and_(
                Rental.status == "active",
                Rental.end_date < datetime.utcnow()
            )
        )
        
        result = await session.execute(query)
        overdue_rentals = result.scalars().all()
        
        for rental in overdue_rentals:
            # Calculate late fees
            days_overdue = (datetime.utcnow() - rental.end_date).days
            late_fee = days_overdue * rental.daily_rate * 0.1  # 10% daily late fee
            
            # Update rental status
            rental.status = "overdue"
            rental.late_fees = late_fee
            
            # Send notification
            await manager.send_personal_message({
                "type": WSEvent.NOTIFICATION_NEW.value,
                "data": {
                    "title": "Rental Overdue",
                    "message": f"Your rental for {rental.product.name} is {days_overdue} days overdue",
                    "late_fee": late_fee
                }
            }, str(rental.customer.user_id))
        
        await session.commit()
```

## 10. File Storage Integration

### 10.1 Cloudflare R2 Client

```python
# app/core/storage.py
import boto3
from botocore.config import Config
from typing import Optional
import uuid
from datetime import timedelta

class R2Storage:
    """Cloudflare R2 storage client."""
    
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            endpoint_url=settings.R2_ENDPOINT_URL,
            aws_access_key_id=settings.R2_ACCESS_KEY_ID,
            aws_secret_access_key=settings.R2_SECRET_ACCESS_KEY,
            config=Config(
                signature_version='s3v4',
                s3={'addressing_style': 'path'}
            ),
        )
        self.bucket_name = settings.R2_BUCKET_NAME
    
    async def generate_presigned_upload_url(
        self,
        folder: str,
        filename: str,
        content_type: str,
        expires_in: int = 3600
    ) -> dict:
        """Generate pre-signed URL for upload."""
        # Generate unique key
        ext = filename.rsplit('.', 1)[1] if '.' in filename else ''
        key = f"{folder}/{uuid.uuid4().hex}.{ext}"
        
        # Generate pre-signed URL
        presigned_url = self.s3_client.generate_presigned_url(
            'put_object',
            Params={
                'Bucket': self.bucket_name,
                'Key': key,
                'ContentType': content_type,
            },
            ExpiresIn=expires_in
        )
        
        return {
            "upload_url": presigned_url,
            "file_key": key,
            "expires_at": (datetime.utcnow() + timedelta(seconds=expires_in)).isoformat()
        }
    
    async def generate_presigned_download_url(
        self,
        file_key: str,
        expires_in: int = 3600
    ) -> str:
        """Generate pre-signed URL for download."""
        presigned_url = self.s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': self.bucket_name,
                'Key': file_key,
            },
            ExpiresIn=expires_in
        )
        return presigned_url
    
    async def delete_file(self, file_key: str) -> bool:
        """Delete file from storage."""
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=file_key
            )
            return True
        except Exception:
            return False

storage = R2Storage()
```

### 10.2 Upload Endpoints

```python
# app/api/v1/endpoints/uploads.py
from fastapi import APIRouter, Depends, HTTPException
from app.core.storage import storage
from app.schemas.upload import PresignedUrlRequest, PresignedUrlResponse
from app.api.deps import get_current_user

router = APIRouter(prefix="/uploads", tags=["Uploads"])

@router.post("/presigned-url", response_model=PresignedUrlResponse)
async def get_presigned_url(
    request: PresignedUrlRequest,
    current_user: User = Depends(get_current_user)
):
    """Get pre-signed URL for file upload."""
    # Validate file type
    allowed_types = {
        "avatars": ["image/jpeg", "image/png", "image/webp"],
        "documents": ["application/pdf", "image/jpeg", "image/png"],
        "inspections": ["image/jpeg", "image/png", "video/mp4"],
        "contracts": ["application/pdf"],
    }
    
    if request.folder not in allowed_types:
        raise HTTPException(400, "Invalid upload folder")
    
    if request.content_type not in allowed_types[request.folder]:
        raise HTTPException(400, "Invalid file type for this folder")
    
    # Generate pre-signed URL
    result = await storage.generate_presigned_upload_url(
        folder=request.folder,
        filename=request.filename,
        content_type=request.content_type,
        expires_in=3600
    )
    
    return result
```

## 11. Cache Strategy Implementation

### 11.1 Redis Cache Manager

```python
# app/core/cache.py
import json
import hashlib
from typing import Any, Optional, Callable
from functools import wraps
import aioredis

class CacheManager:
    """Redis cache manager with pattern-based invalidation."""
    
    def __init__(self):
        self.redis: Optional[aioredis.Redis] = None
    
    async def connect(self):
        self.redis = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
    
    async def disconnect(self):
        if self.redis:
            await self.redis.close()
    
    def _make_key(self, prefix: str, *args, **kwargs) -> str:
        """Generate cache key from function arguments."""
        key_data = json.dumps({"args": str(args), "kwargs": str(kwargs)}, sort_keys=True)
        key_hash = hashlib.md5(key_data.encode()).hexdigest()[:12]
        return f"{prefix}:{key_hash}"
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        data = await self.redis.get(key)
        if data:
            return json.loads(data)
        return None
    
    async def set(self, key: str, value: Any, ttl: int = 3600):
        """Set value in cache with TTL."""
        await self.redis.set(key, json.dumps(value, default=str), ex=ttl)
    
    async def delete(self, key: str):
        """Delete value from cache."""
        await self.redis.delete(key)
    
    async def invalidate_pattern(self, pattern: str):
        """Delete all keys matching pattern."""
        keys = await self.redis.keys(pattern)
        if keys:
            await self.redis.delete(*keys)
    
    async def get_or_set(
        self, 
        key: str, 
        factory: Callable, 
        ttl: int = 3600
    ) -> Any:
        """Get from cache or compute and cache."""
        cached = await self.get(key)
        if cached is not None:
            return cached
        
        value = await factory()
        await self.set(key, value, ttl)
        return value

cache = CacheManager()

# Cache decorator
def cached(prefix: str, ttl: int = 3600):
    """Decorator for caching function results."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            key = cache._make_key(prefix, *args, **kwargs)
            return await cache.get_or_set(key, lambda: func(*args, **kwargs), ttl)
        return wrapper
    return decorator

# Example usage
@cached(prefix="product", ttl=1800)
async def get_product(product_id: str):
    """Cached product fetch."""
    async with db.session() as session:
        result = await session.execute(
            select(Product).where(Product.id == product_id)
        )
        return result.scalar_one_or_none()

# Invalidation after mutation
async def update_product(product_id: str, data: dict):
    """Update product and invalidate cache."""
    async with db.session() as session:
        # ... update logic ...
        await session.commit()
    
    # Invalidate product cache
    await cache.invalidate_pattern(f"product:*")
    await cache.delete(f"product:{product_id}")
```

## 12. Rate Limiting Implementation

### 12.1 SlowAPI Configuration

```python
# app/core/rate_limit.py
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request
from fastapi.responses import JSONResponse

# Initialize limiter
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200/minute"],
    storage_uri=settings.REDIS_URL,
)

# Custom rate limit responses
async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    """Custom rate limit error handler."""
    return JSONResponse(
        status_code=429,
        content={
            "error": "rate_limit_exceeded",
            "message": f"Rate limit exceeded: {exc.detail}",
            "retry_after": exc.detail.split(" ")[-1]
        }
    )

# Rate limit configurations
RATE_LIMITS = {
    # Authentication
    "login": "5/minute",
    "register": "3/hour",
    "refresh": "10/minute",
    "otp_request": "3/minute",
    
    # API endpoints
    "list": "60/minute",
    "create": "30/minute",
    "update": "30/minute",
    "delete": "10/minute",
    
    # File uploads
    "upload": "20/minute",
    
    # Search
    "search": "30/minute",
    
    # Analytics
    "analytics": "60/minute",
}

# Apply rate limits
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    """Apply rate limiting based on endpoint."""
    path = request.url.path
    method = request.method
    
    # Determine rate limit
    if "/auth/login" in path:
        limit = RATE_LIMITS["login"]
    elif "/auth/register" in path:
        limit = RATE_LIMITS["register"]
    elif "/auth/refresh" in path:
        limit = RATE_LIMITS["refresh"]
    elif method == "GET":
        limit = RATE_LIMITS["list"]
    elif method == "POST":
        limit = RATE_LIMITS["create"]
    elif method in ["PUT", "PATCH"]:
        limit = RATE_LIMITS["update"]
    elif method == "DELETE":
        limit = RATE_LIMITS["delete"]
    else:
        limit = "200/minute"
    
    # Apply limit
    @limiter.limit(limit)
    async def endpoint():
        return await call_next(request)
    
    return await endpoint()
```

## 13. Query Optimization

### 13.1 N+1 Query Prevention

```python
# app/core/query_optimizer.py
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy import select
from typing import List

class QueryOptimizer:
    """Query optimization utilities."""
    
    @staticmethod
    def eager_load_rentals():
        """Optimized rental query with eager loading."""
        return select(Rental).options(
            joinedload(Rental.product),
            selectinload(Rental.customer),
            selectinload(Rental.payments),
            selectinload(Rental.inspections),
            selectinload(Rental.rental_extensions),
        )
    
    @staticmethod
    def eager_load_customers():
        """Optimized customer query with eager loading."""
        return select(Customer).options(
            joinedload(Customer.user),
            selectinload(Customer.rentals),
            selectinload(Customer.payments),
            selectinload(Customer.documents),
        )

# Keyset pagination for large datasets
async def keyset_paginate(
    db: AsyncSession,
    query,
    last_id: str = None,
    limit: int = 20,
    order_by=None
):
    """Implement keyset pagination for better performance."""
    if last_id:
        if order_by is None:
            order_by = desc(Rental.created_at)
        query = query.where(Rental.id > last_id)
    
    query = query.order_by(order_by).limit(limit + 1)
    result = await db.execute(query)
    items = result.scalars().all()
    
    has_next = len(items) > limit
    items = items[:limit]
    
    return {
        "items": items,
        "has_next": has_next,
        "next_cursor": str(items[-1].id) if has_next and items else None
    }

# EXPLAIN ANALYZE for debugging
async def analyze_query(db: AsyncSession, query):
    """Analyze query execution plan."""
    from sqlalchemy import text
    explain_query = text(f"EXPLAIN ANALYZE {query}")
    result = await db.execute(explain_query)
    return result.fetchall()
```

## 14. Data Validation Schemas

### 14.1 Pydantic v2 Models

```python
# app/schemas/rental.py
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime, date
from enum import Enum
import uuid

class RentalStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    ACTIVE = "active"
    RETURNED = "returned"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"

class RentalCreate(BaseModel):
    """Rental creation schema."""
    customer_id: uuid.UUID
    product_id: uuid.UUID
    start_date: date
    end_date: date
    rental_type: str = Field(..., pattern="^(daily|weekly|monthly)$")
    delivery_address: Optional[str] = None
    special_requirements: Optional[str] = None
    insurance_selected: bool = False
    
    @validator('end_date')
    def end_date_after_start(cls, v, values):
        if 'start_date' in values and v <= values['start_date']:
            raise ValueError('end_date must be after start_date')
        return v

class RentalResponse(BaseModel):
    """Rental response schema."""
    id: uuid.UUID
    status: RentalStatus
    customer: "CustomerResponse"
    product: "ProductResponse"
    start_date: date
    end_date: date
    total_amount: float
    deposit_amount: float
    created_at: datetime
    
    class Config:
        from_attributes = True

class RentalListResponse(BaseModel):
    """Paginated rental list response."""
    items: List[RentalResponse]
    total: int
    page: int
    limit: int
    has_next: bool
    next_cursor: Optional[str] = None

class RentalReturnRequest(BaseModel):
    """Rental return request schema."""
    condition_notes: str = Field(..., min_length=10, max_length=1000)
    photos: List[str] = Field(default_factory=list)
    late_fees_waived: bool = False
    waiver_reason: Optional[str] = None
    
    @validator('waiver_reason')
    def waiver_reason_required(cls, v, values):
        if values.get('late_fees_waived') and not v:
            raise ValueError('waiver_reason required when late_fees_waived is True')
        return v

# Similar schemas for other models...
```

## 15. Testing Strategy

### 15.1 Test Structure

```
tests/
├── conftest.py           # Fixtures and setup
├── unit/
│   ├── test_auth.py
│   ├── test_permissions.py
│   ├── test_cache.py
│   └── test_validators.py
├── integration/
│   ├── test_rentals.py
│   ├── test_customers.py
│   ├── test_payments.py
│   └── test_websockets.py
└── system/
    ├── test_api_endpoints.py
    └── test_full_workflows.py
```

### 15.2 Example Tests

```python
# tests/conftest.py
import pytest
import asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def client():
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.fixture
async def db_session():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        async with AsyncSession(bind=conn) as session:
            yield session
            await conn.run_sync(Base.metadata.drop_all)

# tests/unit/test_permissions.py
def test_super_admin_has_all_permissions():
    from app.core.permissions import check_permission, Role
    
    # Super admin should have all permissions
    assert check_permission(Role.SUPER_ADMIN, "product:view")
    assert check_permission(Role.SUPER_ADMIN, "rental:create_any")
    assert check_permission(Role.SUPER_ADMIN, "admin:settings")

def test_portal_user_limited_permissions():
    from app.core.permissions import check_permission, Role
    
    # Portal user should have limited permissions
    assert check_permission(Role.PORTAL_USER, "product:view")
    assert not check_permission(Role.PORTAL_USER, "rental:create_any")
    assert not check_permission(Role.PORTAL_USER, "admin:settings")

# tests/integration/test_rentals.py
@pytest.mark.asyncio
async def test_create_rental(client, db_session, auth_headers):
    response = await client.post(
        "/api/v1/rentals/",
        json={
            "customer_id": "test-customer-id",
            "product_id": "test-product-id",
            "start_date": "2025-01-01",
            "end_date": "2025-01-07",
            "rental_type": "daily"
        },
        headers=auth_headers
    )
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "pending"
```

## 16. DevOps & CI/CD

### 16.1 GitHub Actions Workflow

```yaml
# .github/workflows/ci.yml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_USER: test_user
          POSTGRES_PASSWORD: test_password
          POSTGRES_DB: test_db
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
      
      redis:
        image: redis:7
        ports:
          - 6379:6379
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-dev.txt
      
      - name: Run linting
        run: |
          ruff check app/ tests/
          mypy app/
      
      - name: Run tests
        env:
          DATABASE_URL: postgresql://test_user:test_password@localhost:5432/test_db
          REDIS_URL: redis://localhost:6379
        run: |
          pytest tests/ -v --cov=app --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Build Docker image
        run: docker build -t rental-api:${{ github.sha }} .
      
      - name: Push to registry
        run: |
          docker tag rental-api:${{ github.sha }} registry.example.com/rental-api:latest
          docker push registry.example.com/rental-api:latest
      
      - name: Deploy to production
        run: |
          ssh deploy@server "docker pull registry.example.com/rental-api:latest && docker-compose up -d"
```

### 16.2 Production Deployment

```bash
# deploy.sh
#!/bin/bash

# Build and deploy
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d

# Run migrations
docker-compose exec api alembic upgrade head

# Clear cache
docker-compose exec redis redis-cli FLUSHALL

# Health check
sleep 10
curl -f http://localhost:8000/health || exit 1

echo "Deployment successful!"
```

## 17. Monitoring & Observability

### 17.1 Structured Logging

```python
# app/core/logging.py
import structlog
import logging
from datetime import datetime

# Configure structured logging
structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.dev.ConsoleRenderer() if settings.DEBUG else structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Request logging middleware
@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    """Log all requests with timing."""
    start_time = datetime.utcnow()
    
    # Add request context
    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(
        request_id=request.headers.get("X-Request-ID", str(uuid.uuid4())),
        method=request.method,
        path=request.url.path,
    )
    
    logger.info("request_started")
    
    response = await call_next(request)
    
    duration = (datetime.utcnow() - start_time).total_seconds()
    logger.info(
        "request_completed",
        status_code=response.status_code,
        duration_seconds=duration
    )
    
    return response
```

### 17.2 Sentry Integration

```python
# app/core/monitoring.py
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

def init_sentry():
    """Initialize Sentry for error tracking."""
    if settings.SENTRY_DSN:
        sentry_sdk.init(
            dsn=settings.SENTRY_DSN,
            integrations=[
                FastApiIntegration(),
                SqlalchemyIntegration(),
            ],
            traces_sample_rate=0.1,
            profiles_sample_rate=0.1,
            environment=settings.ENVIRONMENT,
        )

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    checks = {
        "database": await check_database(),
        "redis": await check_redis(),
        "storage": await check_storage(),
    }
    
    all_healthy = all(checks.values())
    
    return {
        "status": "healthy" if all_healthy else "unhealthy",
        "checks": checks,
        "timestamp": datetime.utcnow().isoformat()
    }

async def check_database():
    """Check database connectivity."""
    try:
        async with db.session() as session:
            await session.execute(text("SELECT 1"))
        return True
    except:
        return False

async def check_redis():
    """Check Redis connectivity."""
    try:
        await cache.redis.ping()
        return True
    except:
        return False
```

## 18. Performance Tuning

### 18.1 Connection Pool Configuration

```python
# app/core/database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Optimized connection pool settings
engine = create_async_engine(
    settings.DATABASE_URL,
    pool_size=20,              # Base connections
    max_overflow=10,           # Extra connections when needed
    pool_timeout=30,           # Wait time for connection
    pool_recycle=1800,         # Recycle connections every 30 min
    pool_pre_ping=True,        # Verify connections before use
    echo=settings.DEBUG,       # Log SQL in debug mode
)

async_session = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Redis connection pool
redis_pool = aioredis.ConnectionPool.from_url(
    settings.REDIS_URL,
    max_connections=50,
    retry_on_timeout=True,
    socket_timeout=5,
    socket_connect_timeout=5,
)
```

### 18.2 Query Performance Checklist

```python
# Performance optimization checklist
PERFORMANCE_CHECKLIST = {
    "database": [
        "Use eager loading (selectinload/joinedload) for relationships",
        "Implement keyset pagination for large datasets",
        "Add indexes on frequently queried columns",
        "Use materialized views for complex analytics",
        "Enable connection pooling",
        "Use EXPLAIN ANALYZE to debug slow queries",
    ],
    "caching": [
        "Cache frequently accessed, rarely changing data",
        "Use appropriate TTL values",
        "Implement cache invalidation strategies",
        "Cache database query results",
        "Use Redis for session storage",
    ],
    "api": [
        "Implement pagination for list endpoints",
        "Use field selection to return only needed data",
        "Enable gzip compression",
        "Use async/await for I/O operations",
        "Implement request/response compression",
    ],
    "background_jobs": [
        "Offload heavy operations to background workers",
        "Use connection pooling for worker processes",
        "Implement job retry logic",
        "Monitor job queue length",
    ],
}

# Monitoring queries
async def get_slow_queries():
    """Get slow queries from PostgreSQL."""
    query = """
    SELECT query, mean_exec_time, calls
    FROM pg_stat_statements
    ORDER BY mean_exec_time DESC
    LIMIT 10;
    """
    async with db.session() as session:
        result = await session.execute(text(query))
        return result.fetchall()

async def get_table_stats():
    """Get table statistics."""
    query = """
    SELECT schemaname, relname, n_tup_ins, n_tup_upd, n_tup_del
    FROM pg_stat_user_tables
    ORDER BY n_tup_ins DESC;
    """
    async with db.session() as session:
        result = await session.execute(text(query))
        return result.fetchall()
```

---

## Summary

This backend architecture provides:

1. **Project Structure**: Clean, modular layout with separation of concerns
2. **Docker Configuration**: Multi-container setup with API, worker, Redis, and Nginx
3. **Database Setup**: Async SQLAlchemy with connection pooling and migrations
4. **Authentication**: JWT + refresh token rotation with secure token storage
5. **RBAC**: Role-based access control with 4 roles and 30+ granular permissions
6. **API Layer**: RESTful endpoints with pagination, filtering, and validation
7. **WebSocket**: Real-time updates with room-based pub/sub
8. **Background Jobs**: ARQ worker with scheduled tasks and retry logic
9. **File Storage**: Cloudflare R2 with pre-signed URLs for secure uploads
10. **Caching**: Redis-based caching with pattern invalidation
11. **Rate Limiting**: SlowAPI with endpoint-specific limits
12. **Query Optimization**: Eager loading, keyset pagination, EXPLAIN ANALYZE
13. **Data Validation**: Pydantic v2 schemas with custom validators
14. **Testing**: Unit, integration, and system test structure
15. **CI/CD**: GitHub Actions for testing and deployment
16. **Monitoring**: Structured logging with Sentry integration
17. **Health Checks**: Database, Redis, and storage connectivity checks
18. **Performance**: Connection pooling, caching, and query optimization

**Total Lines**: ~2,700+ lines of implementation guidance