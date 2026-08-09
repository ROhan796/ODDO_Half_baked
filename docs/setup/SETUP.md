# Reprico - Rental Management System Setup Guide

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND (Next.js 15)                    │
│  React 19 · TypeScript · Tailwind CSS · Zustand · TanStack      │
│  6 Portals: Public · Customer · Admin · Enterprise · Group · Agent│
└──────────────────────────┬──────────────────────────────────────┘
                           │ HTTP/WebSocket
┌──────────────────────────▼──────────────────────────────────────┐
│                     API GATEWAY (Nginx)                         │
│  Rate Limiting · SSL · WebSocket Proxy · Security Headers       │
└──────────────────────────┬──────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────────┐
│                   BACKEND (FastAPI + ARQ Workers)                │
│  Python 3.12 · SQLAlchemy Async · JWT Auth · RBAC               │
│  28 API Modules · WebSocket · Background Jobs                   │
└──┬────┬────┬────┬────┬────┬────┬────┬────┬────┬───────────────┘
   │    │    │    │    │    │    │    │    │    │
   ▼    ▼    ▼    ▼    ▼    ▼    ▼    ▼    ▼    ▼
  DB  Redis  R2  Razorpay Digio Resend MSG91 Sentry Gemini
```

## Tech Stack

| Layer | Technology | Version |
|-------|-----------|---------|
| Backend | Python + FastAPI | 3.12+ / 0.115.0 |
| Frontend | Next.js + React | 15.1 / 19.0 |
| Primary DB | PostgreSQL (NeonDB) | 16 |
| Cache | Redis (Upstash) | 7 |
| File Storage | Cloudflare R2 | S3-compatible |
| Payments | Razorpay | 1.4.0 |
| E-KYC | Digio + Surepass + FaceIO | - |
| Email | Resend | API |
| SMS | MSG91 | API |
| Monitoring | Sentry | 2.14.0 |
| AI | Google Gemini | 2.4.0 |

## Prerequisites

- Python 3.12+
- Node.js 20+ / npm 10+
- Git

## Quick Start - Single Command

### macOS / Linux

```bash
./start.sh
```

### Windows

```cmd
start.bat
```

**That's it.** The script handles everything: virtualenv, dependencies, Redis, migrations, and starts both backend + frontend.

---

## Manual Setup (Step by Step)

### 1. Clone & Install

```bash
# Backend
cd rental-backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Frontend
cd ../rental-frontend/ODOO-FRONT-
npm install
```

### 2. Environment Variables

```bash
# Backend - copy and fill
cp rental-backend/.env.example rental-backend/.env

# Frontend - copy and fill
cp rental-frontend/ODOO-FRONT-/.env.example rental-frontend/ODOO-FRONT-/.env.local
```

### 3. Start Services

```bash
# Start Redis (Docker)
docker run -d --name rental-redis -p 6379:6379 redis:7-alpine

# Run migrations
cd rental-backend
alembic upgrade head

# Seed data (optional)
python scripts/seed_data.py

# Start backend
uvicorn app.main:app --reload --port 8000

# Start frontend (new terminal)
cd rental-frontend/ODOO-FRONT-
npm run dev
```

### 4. Verify

- Backend API: http://localhost:8000/docs
- Frontend: http://localhost:3000
- Health Check: http://localhost:8000/health

## Service Setup Guides

Each external service has its own detailed setup guide:

| Service | Guide | Purpose |
|---------|-------|---------|
| **Quick Start** | [start.sh](start.sh) / [start.bat](start.bat) | One-command full stack startup |
| NeonDB PostgreSQL | [NEONDB_SETUP.md](docs/setup/NEONDB_SETUP.md) | Primary database + read replica |
| Upstash Redis | [REDIS_SETUP.md](docs/setup/REDIS_SETUP.md) | Cache, sessions, rate limiting |
| Nginx | [NGINX_SETUP.md](docs/setup/NGINX_SETUP.md) | Reverse proxy, SSL, rate limiting |
| Razorpay | [RAZORPAY_SETUP.md](docs/setup/RAZORPAY_SETUP.md) | Payment processing |
| Digio (KYC) | [DIGIO_SETUP.md](docs/setup/DIGIO_SETUP.md) | Aadhaar/PAN/e-sign |
| Cloudflare R2 | [CLOUDFLARE_R2_SETUP.md](docs/setup/CLOUDFLARE_R2_SETUP.md) | File storage |
| Resend + MSG91 | [NOTIFICATIONS_SETUP.md](docs/setup/NOTIFICATIONS_SETUP.md) | Email + SMS |
| Sentry | [SENTRY_SETUP.md](docs/setup/SENTRY_SETUP.md) | Error monitoring |
| All Variables | [ENVIRONMENT_VARIABLES.md](docs/setup/ENVIRONMENT_VARIABLES.md) | Complete env reference |
| Data Seeder | [DATA_SEEDER.md](docs/setup/DATA_SEEDER.md) | Test data generation |
| Testing | [TESTING.md](docs/setup/TESTING.md) | Test conventions |
| Performance | [PERFORMANCE.md](docs/setup/PERFORMANCE.md) | DB indexing & optimization |

## Project Structure

```
ODDO_Half_baked/
├── SETUP.md                  # This file
├── start.sh                  # One-click startup (macOS/Linux)
├── start.bat                 # One-click startup (Windows)
│
├── rental-backend/          # Python/FastAPI
│   ├── app/
│   │   ├── api/v1/          # 28 API route modules
│   │   ├── core/            # Auth, cache, permissions, security
│   │   ├── models/          # 30 SQLAlchemy models (60+ tables)
│   │   ├── schemas/         # Pydantic v2 validation
│   │   ├── services/        # Business logic layer
│   │   ├── workers/         # ARQ background jobs
│   │   ├── middleware/       # Request ID, rate limit, audit, compression
│   │   └── utils/           # DB, Redis, R2, email, SMS, QR
│   ├── alembic/             # Database migrations
│   ├── docker/              # Dockerfile, docker-compose, nginx.conf
│   ├── tests/               # Unit, integration, system tests
│   └── scripts/             # Seed data, admin creation
│
├── rental-frontend/ODOO-FRONT-/  # Next.js 15
│   ├── app/                 # App Router (6 portals)
│   ├── components/          # Shared UI components
│   ├── lib/                 # API client, stores, hooks
│   └── types/               # TypeScript definitions
│
└── docs/setup/              # Service setup documentation (12 guides)
```

## Docker Deployment

```bash
cd rental-backend/docker
docker-compose up -d

# Services: api:8000, worker, redis:6379, nginx:80/443
```

For Nginx-specific configuration (SSL, rate limiting, WebSocket proxy), see [NGINX_SETUP.md](docs/setup/NGINX_SETUP.md).

## Production Checklist

- [ ] All env vars set (no defaults in production)
- [ ] `APP_ENV=production`, `DEBUG=false`
- [ ] `SECRET_KEY` and `JWT_SECRET_KEY` are 256-bit random values
- [ ] NeonDB connection pooling configured
- [ ] Redis TLS enabled (`rediss://` protocol)
- [ ] Razorpay webhook secret configured
- [ ] R2 bucket with proper CORS policy
- [ ] Sentry DSN configured
- [ ] Domain verified in Resend
- [ ] SSL certificates via Nginx
- [ ] Rate limiting tuned for traffic
- [ ] `alembic upgrade head` run
