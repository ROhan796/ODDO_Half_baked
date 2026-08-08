# SYSTEM ARCHITECTURE
## Rental Management System — Full Stack Design
### Version 3.0 | 2026 | FINAL

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Tech Stack](#2-tech-stack)
3. [RBAC Portal System](#3-rbac-portal-system)
4. [Authentication Architecture](#4-authentication-architecture)
5. [API Gateway & Routes](#5-api-gateway--routes)
6. [Database Architecture](#6-database-architecture)
7. [WebSocket Architecture](#7-websocket-architecture)
8. [File Storage Architecture](#8-file-storage-architecture)
9. [Cache Strategy](#9-cache-strategy)
10. [Background Jobs](#10-background-jobs)
11. [Rate Limiting & Security](#11-rate-limiting--security)
12. [Load Balancing & Scaling](#12-load-balancing--scaling)
13. [Deployment Architecture](#13-deployment-architecture)

---

## 1. Architecture Overview

### 1.1 High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                                    CLIENTS                                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │   Customer    │  │   Admin      │  │  Enterprise  │  │  Field Agent │       │
│  │   Portal      │  │   Dashboard  │  │  Portal      │  │  Mobile App  │       │
│  │   (Next.js)   │  │   (Next.js)  │  │  (Next.js)   │  │  (React)     │       │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘       │
│         │                  │                  │                  │               │
│         └──────────────────┴──────────────────┴──────────────────┘               │
│                                    │                                            │
│                              HTTPS/WSS                                          │
└────────────────────────────────────┼────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           CLOUDFLARE (Free Tier)                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │  CDN          │  │  DDoS        │  │  DNS         │  │  SSL/TLS     │       │
│  │  Protection   │  │  Protection  │  │  Load Bal.   │  │  Termination │       │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘       │
└────────────────────────────────────┼────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           NGINX (Reverse Proxy)                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │  Rate         │  │  Request     │  │  CORS        │  │  Static      │       │
│  │  Limiting     │  │  Routing     │  │  Headers     │  │  Files       │       │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘       │
└────────────────────────────────────┼────────────────────────────────────────────┘
                                     │
              ┌──────────────────────┼──────────────────────┐
              ▼                      ▼                      ▼
┌─────────────────────┐ ┌─────────────────────┐ ┌─────────────────────┐
│  FastAPI Instance 1  │ │  FastAPI Instance 2  │ │  FastAPI Instance N  │
│  (uvicorn, 4 workers)│ │  (uvicorn, 4 workers)│ │  (uvicorn, 4 workers)│
└──────────┬──────────┘ └──────────┬──────────┘ └──────────┬──────────┘
           │                       │                       │
           └───────────────────────┼───────────────────────┘
                                   │
           ┌───────────────────────┼───────────────────────┐
           ▼                       ▼                       ▼
┌─────────────────────┐ ┌─────────────────────┐ ┌─────────────────────┐
│    PostgreSQL        │ │      Redis           │ │    Cloudflare R2    │
│    (NeonDB)          │ │    (Upstash)         │ │    (File Storage)   │
│  ┌──────────────┐   │ │  ┌──────────────┐    │ │  ┌──────────────┐  │
│  │ Primary (W)   │   │ │  │ Sessions      │    │ │  │ KYC Docs      │  │
│  │ Replica (R)   │   │ │  │ Rate Limits   │    │ │  │ Photos        │  │
│  │ PgBouncer     │   │ │  │ OTP Store     │    │ │  │ Invoices      │  │
│  └──────────────┘   │ │  │ Pub/Sub       │    │ │  │ Agreements    │  │
└─────────────────────┘ │  └──────────────┘    │ │  └──────────────┘  │
                        └─────────────────────┘ └─────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                          EXTERNAL SERVICES                                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│  │ Razorpay  │  │  Digio   │  │  FaceIO  │  │  Resend  │  │  MSG91   │        │
│  │ (Payments)│  │ (e-KYC)  │  │ (Face)   │  │ (Email)  │  │  (SMS)   │        │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘  └──────────┘        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐                      │
│  │ Tesseract │  │ Surepass  │  │ Firebase │  │  Sentry  │                      │
│  │  (OCR)    │  │ (PAN/GST) │  │  (Push)  │  │ (Monitor)│                      │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘                      │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Request Flow

```
Client Request
    │
    ▼
Cloudflare (CDN + DDoS + SSL)
    │
    ▼
Nginx (Rate Limit + Reverse Proxy)
    │
    ▼
FastAPI Middleware Pipeline:
    1. HTTPS Enforcement (HSTS)
    2. CORS Validation
    3. Rate Limit Check (slowapi)
    4. Request ID Injection (UUID)
    5. JWT Auth Validation
    6. RBAC Permission Check
    7. Audit Logger (async)
    8. Response Compression
    │
    ▼
Route Handler → Database Query → Response
    │
    ▼
WebSocket Push (if real-time event)
    │
    ▼
Background Job Queue (ARQ) → Redis → Async Processing
```

---

## 2. Tech Stack

### 2.1 Frontend Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| Framework | Next.js 14 (App Router) | SSR + SSG + ISR |
| UI Library | React 18 | Component rendering |
| Styling | Tailwind CSS | Utility-first CSS |
| Components | shadcn/ui | Accessible components |
| State (Global) | Zustand | Client-side state |
| State (Server) | TanStack Query | API data sync |
| Forms | React Hook Form + Zod | Validation |
| Charts | Recharts | Dashboard widgets |
| Real-time | Native WebSocket | Live updates |
| QR Scanning | ZXing-js | Camera barcode scan |
| PDF Viewer | react-pdf | Agreement preview |
| Animations | Framer Motion | Page transitions |
| Icons | Lucide React | Icon library |
| Auth Tokens | httpOnly cookies | XSS prevention |

### 2.2 Backend Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| Framework | FastAPI (Python 3.12) | Async REST API |
| ASGI Server | uvicorn | HTTP/WebSocket server |
| Process Manager | gunicorn | Worker management |
| ORM | SQLAlchemy (async) | Database queries |
| DB Driver | asyncpg | Non-blocking PostgreSQL |
| Validation | Pydantic v2 | Request/response models |
| Background Jobs | ARQ | Async task queue |
| PDF Generation | WeasyPrint | Invoice/agreement PDFs |
| OCR | Tesseract | ID document extraction |
| Face Match | DeepFace / FaceIO | Liveness + face match |

### 2.3 Infrastructure Stack

| Layer | Technology | Free Tier |
|-------|------------|-----------|
| Database | PostgreSQL 16 (NeonDB) | 0.5 GB |
| Cache | Redis (Upstash) | 10K cmds/day |
| File Storage | Cloudflare R2 | 10 GB |
| CDN | Cloudflare | Unlimited |
| Email | Resend | 3K/month |
| SMS | MSG91 | 100 OTP/month |
| Push | Firebase FCM | Unlimited |
| Hosting (API) | Railway | $5 credit/month |
| Hosting (Frontend) | Vercel | Hobby free |
| Monitoring | Sentry | 5K errors/month |

---

## 3. RBAC Portal System

### 3.1 Portal Architecture

Each user role gets a **separate portal** with role-specific pages, widgets, and permissions. The frontend uses Next.js middleware + route groups to render different layouts per role.

```
app/
├── (public)/                    # Guest + Login
│   ├── layout.tsx              # Public layout (no sidebar)
│   ├── page.tsx                # Landing page
│   ├── catalog/                # Product browsing
│   ├── product/[id]/           # Product detail
│   ├── login/                  # Login page
│   ├── register/               # Registration
│   └── quote/[token]/          # Public quote view
│
├── (customer)/                  # Personal User Portal
│   ├── layout.tsx              # Customer sidebar layout
│   ├── dashboard/              # Customer dashboard
│   ├── orders/                 # My orders list
│   ├── orders/[id]/            # Order detail
│   ├── rentals/                # Active rentals
│   ├── rentals/[id]/           # Rental detail + countdown
│   ├── profile/                # Profile management
│   ├── kyc/                    # KYC verification
│   ├── addresses/              # Address book
│   ├── payments/               # Payment methods
│   ├── groups/                 # My groups
│   ├── groups/[id]/            # Group dashboard
│   ├── disputes/               # My disputes
│   ├── disputes/new/           # File dispute
│   ├── invoices/               # My invoices
│   ├── loyalty/                # Points + referrals
│   └── notifications/          # Notification center
│
├── (enterprise)/                # Enterprise Portal
│   ├── layout.tsx              # Enterprise sidebar layout
│   ├── dashboard/              # Enterprise dashboard
│   ├── team/                   # Team management
│   ├── team/[id]/              # Team member detail
│   ├── orders/                 # All team orders
│   ├── orders/new/             # Create bulk order
│   ├── billing/                # Invoices + credit
│   ├── billing/[id]/           # Invoice detail
│   ├── pricelist/              # Custom pricing
│   ├── analytics/              # Usage reports
│   ├── profile/                # Company profile
│   └── kyc/                    # Enterprise KYC
│
├── (group)/                     # Group Portal
│   ├── layout.tsx              # Group sidebar layout
│   ├── dashboard/              # Group dashboard
│   ├── create/                 # Create group
│   ├── [id]/                   # Group detail
│   ├── [id]/members/           # Member management
│   ├── [id]/rentals/           # Group rentals
│   ├── [id]/deposits/          # Deposit pool
│   ├── [id]/votes/             # Active votes
│   └── [id]/settings/          # Group settings
│
├── (admin)/                     # Admin Portal
│   ├── layout.tsx              # Admin sidebar layout
│   ├── dashboard/              # Real-time dashboard
│   ├── rentals/                # All rentals
│   ├── rentals/[id]/           # Rental detail
│   ├── customers/              # Customer management
│   ├── customers/[id]/         # Customer detail
│   ├── products/               # Product management
│   ├── products/[id]/          # Product detail + calendar
│   ├── products/new/           # Add product
│   ├── categories/             # Category management
│   ├── quotations/             # Quote pipeline
│   ├── quotations/[id]/        # Quote detail
│   ├── invoices/               # All invoices
│   ├── invoices/[id]/          # Invoice detail
│   ├── deposits/               # Deposit management
│   ├── inspections/            # Inspection queue
│   ├── repairs/                # Repair cases
│   ├── recovery/               # Recovery cases
│   ├── disputes/               # Dispute management
│   ├── blacklist/              # Blacklist management
│   ├── pricelists/             # Pricelist management
│   ├── crm/                    # CRM dashboard
│   ├── crm/contacts/           # Contact management
│   ├── crm/campaigns/          # Campaign management
│   ├── stock/                  # Stock management
│   ├── stock/movements/        # Movement history
│   ├── notifications/          # Notification management
│   ├── audit/                  # Audit logs
│   ├── settings/               # System settings
│   └── team/                   # Staff management
│
├── (agent)/                     # Field Agent Portal
│   ├── layout.tsx              # Minimal agent layout
│   ├── dashboard/              # Agent dashboard
│   ├── scan/                   # QR scanner
│   ├── inspection/             # Inspection form
│   ├── pickup/                 # Pickup queue
│   ├── return/                 # Return queue
│   ├── route/                  # Route map
│   └── profile/                # Agent profile
│
└── api/                         # API Routes
    └── v1/
        ├── auth/
        ├── users/
        ├── products/
        ├── rentals/
        ├── ...
        └── ws/                  # WebSocket endpoints
```

### 3.2 RBAC Permission Matrix

#### Portal Access by Role

| Portal | Guest | Personal | Enterprise Admin | Enterprise Sub | Group Leader | Group Member | Ops Admin | Super Admin | Field Agent |
|--------|-------|----------|------------------|----------------|--------------|--------------|-----------|-------------|-------------|
| Public Catalog | R | R | R | R | R | R | R | R | R |
| Customer Dashboard | - | R/W | - | - | R | R | - | - | - |
| Enterprise Dashboard | - | - | R/W | R | - | - | R | R | - |
| Group Dashboard | - | - | - | - | R/W | R | R | R | - |
| Admin Dashboard | - | - | - | - | - | - | R/W | R/W | - |
| Agent Dashboard | - | - | - | - | - | - | - | - | R/W |

#### Feature Access by Role

| Feature | Personal | Ent. Admin | Ent. Sub | Group Leader | Group Member | Ops Admin | Super Admin | Field Agent |
|---------|----------|------------|----------|--------------|--------------|-----------|-------------|-------------|
| Browse Catalog | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes |
| Create Rental | Own only | Team | Request | Group | - | Yes | Yes | - |
| View All Rentals | Own only | Team | Own org | Group | Group | Yes | Yes | - |
| Manage Products | - | - | - | - | - | Yes | Yes | - |
| Manage Pricelists | - | - | - | - | - | Yes | Yes | - |
| View Dashboard | Own | Enterprise | Enterprise | Group | Group | Admin | Full | Agent |
| Process Payment | Own | Team | - | Group | - | Yes | Yes | - |
| Settle Deposit | - | - | - | - | - | Yes | Yes | - |
| Approve Extension | - | - | - | Group vote | Vote | Yes | Yes | - |
| File Dispute | Own | Own | Own | Group | Own share | - | - | - |
| Resolve Dispute | - | - | - | - | - | Yes | Yes | - |
| Blacklist User | - | - | - | - | - | Propose | Yes | - |
| View Audit Logs | - | - | - | - | - | Yes | Yes | - |
| Manage Staff | - | - | - | - | - | - | Yes | - |
| System Settings | - | - | - | - | - | - | Yes | - |
| Scan QR Code | - | - | - | - | - | - | - | Yes |
| Upload Photos | - | - | - | - | - | Yes | Yes | Yes |
| Create Quotation | - | - | - | - | - | Yes | Yes | - |
| Send Notifications | - | - | - | - | - | Yes | Yes | - |
| Manage CRM | - | - | - | - | - | Yes | Yes | - |
| Manage Stock | - | - | - | - | - | Yes | Yes | - |

### 3.3 Route Protection (Next.js Middleware)

```typescript
// middleware.ts
const ROLE_ROUTES = {
  guest: ['/catalog', '/product/*', '/login', '/register'],
  customer: ['/dashboard', '/orders/*', '/rentals/*', '/profile', '/kyc', '/groups/*'],
  enterprise: ['/enterprise/*'],
  group: ['/group/*'],
  admin: ['/admin/*'],
  agent: ['/agent/*'],
};

export function middleware(request: NextRequest) {
  const token = request.cookies.get('access_token');
  const role = decodeJWT(token)?.role;
  const path = request.nextUrl.pathname;
  
  // Check if route is protected
  for (const [portal, routes] of Object.entries(ROLE_ROUTES)) {
    if (routes.some(r => path.startsWith(r))) {
      if (!token) return redirect('/login');
      if (!hasAccess(role, portal)) return redirect('/unauthorized');
    }
  }
}
```

### 3.4 Portal Layout Components

#### Customer Layout
```
┌─────────────────────────────────────────────────┐
│  Header: Logo | Search | Notifications | Profile │
├──────────┬──────────────────────────────────────┤
│          │                                      │
│ Sidebar  │         Main Content Area            │
│          │                                      │
│ Dashboard│  ┌─────────────────────────────────┐ │
│ Orders   │  │                                 │ │
│ Rentals  │  │     Page Content Renders Here    │ │
│ Profile  │  │                                 │ │
│ KYC      │  │                                 │ │
│ Groups   │  └─────────────────────────────────┘ │
│ Disputes │                                      │
│ Invoices │                                      │
│ Loyalty  │                                      │
│          │                                      │
├──────────┴──────────────────────────────────────┤
│  Footer: Support | Terms | Privacy              │
└─────────────────────────────────────────────────┘
```

#### Admin Layout
```
┌─────────────────────────────────────────────────────────────────┐
│  Header: Logo | Global Search | Alerts | Notifications | User   │
├─────────────────────────────────────────────────────────────────┤
│  Priority Feed Bar: [URGENT: 3 overdue] [TODAY: 5 pickups]     │
├──────────┬──────────────────────────────────────────────────────┤
│          │                                                      │
│ Sidebar  │              Main Content Area                        │
│          │                                                      │
│ Dashboard│  ┌────────────────────────────────────────────────┐  │
│ Rentals  │  │                                                │  │
│ Customers│  │           Page Content Renders Here            │  │
│ Products │  │                                                │  │
│ Quotes   │  │                                                │  │
│ Invoices │  └────────────────────────────────────────────────┘  │
│ Deposits │                                                      │
│ Inspect  │                                                      │
│ Repairs  │                                                      │
│ Recovery │                                                      │
│ Disputes │                                                      │
│ CRM      │                                                      │
│ Stock    │                                                      │
│ Settings │                                                      │
│ Audit    │                                                      │
│          │                                                      │
├──────────┴──────────────────────────────────────────────────────┤
│  Status Bar: DB Status | Redis Status | Queue Status | Version  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 4. Authentication Architecture

### 4.1 Token System

```
┌─────────────────────────────────────────────────────────────┐
│                    AUTH TOKEN PAIR                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ACCESS TOKEN (JWT)              REFRESH TOKEN (Opaque)     │
│  ┌─────────────────────┐        ┌─────────────────────┐    │
│  │ Header: {           │        │ 32-byte random hex  │    │
│  │   alg: "HS256",     │        │                     │    │
│  │   typ: "JWT"        │        │ Stored:             │    │
│  │ }                   │        │ - Hashed in DB      │    │
│  │                     │        │ - Redis cache       │    │
│  │ Payload: {          │        │                     │    │
│  │   user_id: "uuid",  │        │ TTL: 30 days        │    │
│  │   role: "portal_    │        │ (rolling)           │    │
│  │     user",          │        │                     │    │
│  │   user_type:        │        │ Rotation:           │    │
│  │     "personal",     │        │ Every refresh       │    │
│  │   enterprise_id:    │        │ issues new pair     │    │
│  │     null,           │        │ and invalidates     │    │
│  │   iat: 1722000000,  │        │ old one             │    │
│  │   exp: 1722000900   │        │                     │    │
│  │ }                   │        │ Storage:            │    │
│  │                     │        │ httpOnly cookie     │    │
│  │ TTL: 15 minutes     │        │                     │    │
│  │ Storage:            │        │                     │    │
│  │ httpOnly cookie     │        │                     │    │
│  └─────────────────────┘        └─────────────────────┘    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 4.2 Auth Flows

#### Login Flow (Phone + OTP)
```
1. POST /api/v1/auth/otp/send
   Request: { "phone": "+919876543210" }
   Response: { "message": "OTP sent", "expires_in": 300 }
   
   Server: Generate 6-digit OTP → Store in Redis (key: otp:+919876543210, TTL: 5min)
          → Send via MSG91/Twilio

2. POST /api/v1/auth/otp/verify
   Request: { "phone": "+919876543210", "code": "123456" }
   
   Server: Verify OTP from Redis → If valid:
          → Find or create user
          → Generate access + refresh tokens
          → Store refresh token hash in DB + Redis
          → Set httpOnly cookies
          
   Response: { "access_token": "...", "user": { "id", "role", "name", "trust_score" } }
```

#### Token Refresh Flow
```
POST /api/v1/auth/refresh
Cookie: refresh_token=abc123...

Server:
  1. Hash the refresh token
  2. Look up in DB: SELECT * FROM refresh_tokens WHERE token_hash = hash AND revoked_at IS NULL
  3. If found and not expired:
     → Revoke old token: UPDATE refresh_tokens SET revoked_at = NOW() WHERE id = ...
     → Issue new pair (access + refresh)
     → Store new refresh token
  4. If not found or expired:
     → Return 401 Unauthorized

Response: { "access_token": "...", "refresh_token": "..." }
```

#### Logout Flow
```
POST /api/v1/auth/logout
Cookie: refresh_token=abc123...

Server:
  1. Hash refresh token
  2. DELETE FROM refresh_tokens WHERE token_hash = hash
  3. Clear cookies
  4. Add access token JID to Redis denylist (TTL = 15min)

Response: { "message": "Logged out" }
```

### 4.3 Multi-Device Session Management

| Rule | Value |
|------|-------|
| Max active sessions | 5 per user |
| Session tracking | device_fingerprint + IP stored with refresh token |
| Oldest session | Revoked when 6th login occurs |
| Session list | User can view all active sessions in profile |
| Remote logout | User can revoke specific session |

---

## 5. API Gateway & Routes

### 5.1 API Structure

All endpoints prefixed with `/api/v1/`.

#### Auth Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/auth/otp/send` | None | Send OTP to phone |
| POST | `/auth/otp/verify` | None | Verify OTP, issue tokens |
| POST | `/auth/login` | None | Email + password login |
| POST | `/auth/refresh` | Refresh Token | Rotate token pair |
| POST | `/auth/logout` | Access Token | Invalidate session |
| POST | `/auth/forgot-password` | None | Send reset link |
| POST | `/auth/reset-password` | None | Reset with token |

#### User Endpoints

| Method | Endpoint | Auth | Role | Description |
|--------|----------|------|------|-------------|
| GET | `/users/me` | Access | Any | Get current user profile |
| PATCH | `/users/me` | Access | Any | Update own profile |
| POST | `/users/me/photo` | Access | Any | Upload profile photo |
| GET | `/users/{id}` | Access | Admin | Get user by ID |
| GET | `/users` | Access | Admin | List users (filterable) |
| GET | `/users/search` | Access | Admin | Search users |

#### KYC Endpoints

| Method | Endpoint | Auth | Role | Description |
|--------|----------|------|------|-------------|
| POST | `/kyc/initiate` | Access | Customer | Start KYC process |
| POST | `/kyc/upload-doc` | Access | Customer | Upload ID document |
| POST | `/kyc/verify-face` | Access | Customer | Selfie + liveness check |
| GET | `/kyc/status` | Access | Customer | Get KYC progress |
| GET | `/kyc/admin/review` | Access | Admin | Manual review queue |
| PATCH | `/kyc/admin/{id}/approve` | Access | Admin | Approve KYC |
| PATCH | `/kyc/admin/{id}/reject` | Access | Admin | Reject KYC |

#### Trust Score Endpoints

| Method | Endpoint | Auth | Role | Description |
|--------|----------|------|------|-------------|
| GET | `/trust-score/me` | Access | Customer | Get own trust score |
| GET | `/trust-score/history` | Access | Customer | Score change history |
| GET | `/trust-score/admin/{user_id}` | Access | Admin | View user trust details |
| POST | `/trust-score/admin/recalculate` | Access | Admin | Force recalculation |

#### Product Endpoints

| Method | Endpoint | Auth | Role | Description |
|--------|----------|------|------|-------------|
| GET | `/products` | None | Guest | List products (catalog) |
| GET | `/products/{id}` | None | Guest | Product detail |
| GET | `/products/{id}/availability` | None | Guest | Check availability |
| GET | `/products/{id}/calendar` | None | Guest | Monthly calendar |
| POST | `/products` | Access | Admin | Create product |
| PATCH | `/products/{id}` | Access | Admin | Update product |
| DELETE | `/products/{id}` | Access | Super Admin | Archive product |
| POST | `/products/{id}/images` | Access | Admin | Upload product images |

#### Category Endpoints

| Method | Endpoint | Auth | Role | Description |
|--------|----------|------|------|-------------|
| GET | `/categories` | None | Guest | List categories |
| POST | `/categories` | Access | Admin | Create category |
| PATCH | `/categories/{id}` | Access | Admin | Update category |

#### Rental Endpoints

| Method | Endpoint | Auth | Role | Description |
|--------|----------|------|------|-------------|
| POST | `/rentals` | Access | Customer | Create rental |
| GET | `/rentals` | Access | Any | List rentals (filtered by role) |
| GET | `/rentals/{id}` | Access | Any | Rental detail |
| PATCH | `/rentals/{id}/confirm` | Access | Admin | Confirm rental |
| PATCH | `/rentals/{id}/cancel` | Access | Any | Cancel rental |
| POST | `/rentals/{id}/return` | Access | Admin | Process return |
| GET | `/rentals/{id}/custody` | Access | Any | Chain of custody |
| GET | `/rentals/{id}/timeline` | Access | Any | Rental timeline |

#### Quotation Endpoints

| Method | Endpoint | Auth | Role | Description |
|--------|----------|------|------|-------------|
| POST | `/quotations` | Access | Admin | Create quotation |
| GET | `/quotations` | Access | Admin | List quotations |
| GET | `/quotations/{id}` | Access | Any | Quotation detail |
| PATCH | `/quotations/{id}/send` | Access | Admin | Send to customer |
| PATCH | `/quotations/{id}/accept` | Access | Customer | Accept quote |
| PATCH | `/quotations/{id}/reject` | Access | Customer | Reject quote |
| GET | `/quotations/public/{token}` | None | Guest | Public quote view |

#### Invoice Endpoints

| Method | Endpoint | Auth | Role | Description |
|--------|----------|------|------|-------------|
| GET | `/invoices` | Access | Any | List invoices |
| GET | `/invoices/{id}` | Access | Any | Invoice detail |
| GET | `/invoices/{id}/pdf` | Access | Any | Download PDF |
| POST | `/invoices/{id}/send` | Access | Admin | Email invoice |
| POST | `/invoices/{id}/payment` | Access | Admin | Record payment |

#### Deposit Endpoints

| Method | Endpoint | Auth | Role | Description |
|--------|----------|------|------|-------------|
| GET | `/deposits/{rental_id}` | Access | Any | Deposit details |
| POST | `/deposits/{id}/settle` | Access | Admin | Settle deposit |
| POST | `/deposits/{id}/deduct` | Access | Admin | Apply deduction |
| GET | `/deposits/history` | Access | Customer | Deposit history |

#### Extension Endpoints

| Method | Endpoint | Auth | Role | Description |
|--------|----------|------|------|-------------|
| POST | `/extensions` | Access | Customer | Request extension |
| GET | `/extensions/{rental_id}` | Access | Any | Extension status |
| PATCH | `/extensions/{id}/approve` | Access | Admin | Approve extension |
| PATCH | `/extensions/{id}/reject` | Access | Admin | Reject extension |

#### Dispute Endpoints

| Method | Endpoint | Auth | Role | Description |
|--------|----------|------|------|-------------|
| POST | `/disputes` | Access | Customer | File dispute |
| GET | `/disputes` | Access | Any | List disputes |
| GET | `/disputes/{id}` | Access | Any | Dispute detail |
| PATCH | `/disputes/{id}/resolve` | Access | Admin | Resolve dispute |
| PATCH | `/disputes/{id}/escalate` | Access | Customer | Escalate to Super Admin |

#### Group Endpoints

| Method | Endpoint | Auth | Role | Description |
|--------|----------|------|------|-------------|
| POST | `/groups` | Access | Customer | Create group |
| GET | `/groups` | Access | Customer | List my groups |
| GET | `/groups/{id}` | Access | Group Member | Group detail |
| POST | `/groups/{id}/invite` | Access | Group Leader | Invite member |
| POST | `/groups/{id}/rental` | Access | Group Leader | Create group rental |
| POST | `/groups/{id}/vote` | Access | Group Leader | Create vote |
| PATCH | `/groups/{id}/vote/{vote_id}` | Access | Group Member | Cast vote |

#### Enterprise Endpoints

| Method | Endpoint | Auth | Role | Description |
|--------|----------|------|------|-------------|
| POST | `/enterprise` | Access | Customer | Create enterprise |
| GET | `/enterprise/{id}` | Access | Ent. Admin | Enterprise detail |
| POST | `/enterprise/{id}/invite` | Access | Ent. Admin | Invite team member |
| PATCH | `/enterprise/{id}/member/{uid}/role` | Access | Ent. Admin | Change member role |
| GET | `/enterprise/{id}/team` | Access | Ent. Admin | List team |
| GET | `/enterprise/{id}/billing` | Access | Ent. Admin | Billing dashboard |

#### CRM Endpoints

| Method | Endpoint | Auth | Role | Description |
|--------|----------|------|------|-------------|
| GET | `/crm/contacts` | Access | Admin | List CRM contacts |
| GET | `/crm/contacts/{id}` | Access | Admin | Contact detail |
| PATCH | `/crm/contacts/{id}` | Access | Admin | Update contact |
| POST | `/crm/interactions` | Access | Admin | Log interaction |
| GET | `/crm/interactions/{contact_id}` | Access | Admin | Interaction history |
| POST | `/crm/campaigns` | Access | Admin | Create campaign |
| GET | `/crm/campaigns` | Access | Admin | List campaigns |
| GET | `/crm/leads` | Access | Admin | Lead pipeline |

#### Stock Endpoints

| Method | Endpoint | Auth | Role | Description |
|--------|----------|------|------|-------------|
| GET | `/stock/levels` | Access | Admin | Current stock levels |
| GET | `/stock/movements` | Access | Admin | Movement history |
| POST | `/stock/transfer` | Access | Admin | Transfer stock |
| POST | `/stock/adjustment` | Access | Admin | Adjust stock |
| GET | `/stock/locations` | Access | Admin | List locations |

#### Admin Endpoints

| Method | Endpoint | Auth | Role | Description |
|--------|----------|------|------|-------------|
| GET | `/admin/dashboard` | Access | Admin | Dashboard aggregates |
| GET | `/admin/priority-feed` | Access | Admin | Actionable priority list |
| GET | `/admin/audit-logs` | Access | Admin | Audit trail |
| GET | `/admin/settings` | Access | Super Admin | System settings |
| PATCH | `/admin/settings` | Access | Super Admin | Update settings |
| POST | `/admin/blacklist` | Access | Admin | Propose blacklist |
| PATCH | `/admin/blacklist/{id}/approve` | Access | Super Admin | Approve blacklist |

#### File Endpoints

| Method | Endpoint | Auth | Role | Description |
|--------|----------|------|------|-------------|
| POST | `/files/presign` | Access | Any | Get pre-signed upload URL |
| POST | `/files/confirm` | Access | Any | Confirm upload completion |
| GET | `/files/{id}/download` | Access | Any | Get pre-signed download URL |

#### WebSocket Endpoints

| Endpoint | Auth | Role | Events |
|----------|------|------|--------|
| `/ws/dashboard/{admin_id}` | JWT | Admin | new_overdue, new_rental, new_dispute, system_alert |
| `/ws/rental/{rental_id}` | JWT | Any | status_change, late_fee_update, inspection_complete |
| `/ws/group/{group_id}` | JWT | Group Member | member_joined, deposit_paid, vote_required |
| `/ws/agent/{agent_id}` | JWT | Field Agent | new_assignment, route_update |
| `/ws/notifications/{user_id}` | JWT | Any | notification_received |

---

## 6. Database Architecture

### 6.1 Connection Architecture

```
FastAPI Application
    │
    ├── Primary Engine (asyncpg)
    │   ├── Pool: min=2, max=10
    │   ├── SSL: require
    │   ├── Target: NeonDB Primary
    │   └── Usage: All WRITE operations
    │
    ├── Replica Engine (asyncpg)
    │   ├── Pool: min=2, max=10
    │   ├── SSL: require
    │   ├── Target: NeonDB Read Replica
    │   └── Usage: All READ operations
    │
    └── Redis Connection
        ├── Host: Upstash Redis
        ├── TLS: enabled
        └── Usage: Cache, sessions, rate limits, pub/sub
```

### 6.2 Query Routing

```python
# Dependency injection for read/write splitting
async def get_db():
    """Write operations → Primary"""
    async with primary_engine.connect() as conn:
        yield conn

async def get_read_db():
    """Read operations → Replica"""
    async with replica_engine.connect() as conn:
        yield conn

# Example usage in routes
@router.get("/products")
async def list_products(db: AsyncSession = Depends(get_read_db)):
    # This query goes to the read replica
    result = await db.execute(select(Product).where(Product.status == 'available'))
    return result.scalars().all()

@router.post("/products")
async def create_product(data: ProductCreate, db: AsyncSession = Depends(get_db)):
    # This query goes to the primary
    product = Product(**data.dict())
    db.add(product)
    await db.commit()
    return product
```

### 6.3 Schema Separation

```
PostgreSQL Database (NeonDB)
│
├── public (Operational Schema)
│   ├── users
│   ├── refresh_tokens
│   ├── kyc_records
│   ├── trust_score_history
│   ├── enterprises
│   ├── enterprise_members
│   ├── groups
│   ├── group_members
│   ├── products
│   ├── categories
│   ├── accessories
│   ├── availability_blocks
│   ├── reservations
│   ├── rentals
│   ├── rental_items
│   ├── quotations
│   ├── invoices
│   ├── payments
│   ├── security_deposits
│   ├── deposit_deductions
│   ├── late_fees
│   ├── custody_events
│   ├── accessory_check_items
│   ├── damage_reports
│   ├── extension_requests
│   ├── disputes
│   ├── repair_cases
│   ├── recovery_cases
│   ├── blacklist
│   ├── notifications
│   ├── pricelists
│   ├── pricelist_items
│   ├── crm_contacts
│   ├── crm_interactions
│   ├── crm_campaigns
│   ├── crm_tags
│   ├── stock_locations
│   ├── stock_movements
│   ├── stock_levels
│   ├── loyalty_points_ledger
│   └── referrals
│
├── audit (Immutable Schema)
│   ├── audit_logs (partitioned by month)
│   └── rate_limit_events (partitioned by week)
│
├── analytics (Materialized Views)
│   ├── mv_admin_dashboard
│   ├── mv_revenue_daily
│   ├── mv_product_utilization
│   ├── mv_customer_lifetime_value
│   └── mv_crm_lead_scores
│
└── archive (Historical Data)
    ├── archived_rentals
    └── archived_invoices
```

### 6.4 Redis Key Patterns

| Key Pattern | TTL | Purpose |
|-------------|-----|---------|
| `otp:{phone}:{purpose}` | 5 min | OTP storage |
| `session:{user_id}:{device}` | 30 days | Session cache |
| `ratelimit:{endpoint}:{identifier}` | Per rule | Rate limiting |
| `reservation:{product_id}:{user_id}` | 15 min | Cart hold |
| `latefee:{rental_id}` | 60 sec | Real-time fee cache |
| `dashboard:{admin_id}` | 30 sec | Dashboard cache |
| `ws:admin:global` | N/A | WebSocket pub/sub |
| `ws:rental:{rental_id}` | N/A | WebSocket pub/sub |
| `ws:group:{group_id}` | N/A | WebSocket pub/sub |
| `ws:agent:{agent_id}` | N/A | WebSocket pub/sub |
| `denylist:{token_jti}` | 15 min | JWT denylist |
| `lock:reservation:{product_id}` | 30 sec | Concurrency lock |
| `arq:queue` | N/A | Background job queue |

---

## 7. WebSocket Architecture

### 7.1 Connection Flow

```
1. Client connects to /ws/{channel}/{id}
2. FastAPI WebSocket handler receives connection
3. Client sends auth message: { "token": "jwt_access_token" }
4. FastAPI validates JWT
5. If valid → subscribe to Redis channel
6. If invalid → close connection with 4001

7. Events published to Redis channels by:
   - API handlers (on rental create, return, etc.)
   - ARQ background jobs (overdue detection, reminders)
   - System events (payment received, dispute filed)

8. FastAPI WebSocket handler receives Redis events
9. Pushes to connected clients in real-time
```

### 7.2 WebSocket Events by Channel

#### Admin Dashboard Channel (`ws:admin:global`)

| Event | Payload | Trigger |
|-------|---------|---------|
| `new_overdue` | `{rental_id, customer_name, product_name, hours_overdue, late_fee}` | Overdue detection job |
| `new_rental` | `{rental_id, customer_name, product_name, amount}` | Rental confirmed |
| `new_dispute` | `{dispute_id, customer_name, charge_type, amount}` | Dispute filed |
| `deposit_settled` | `{rental_id, customer_name, refund_amount}` | Return processed |
| `system_alert` | `{type, message, severity}` | System events |
| `metrics_update` | `{active_rentals, overdue, revenue_today}` | Periodic (60s) |

#### Rental Channel (`ws:rental:{rental_id}`)

| Event | Payload | Trigger |
|-------|---------|---------|
| `status_change` | `{from, to, timestamp}` | Status update |
| `late_fee_update` | `{current_fee, units_overdue}` | Late fee calculation (60s) |
| `inspection_complete` | `{stage, condition_rating, photos}` | Inspection submitted |
| `extension_approved` | `{new_end_at, additional_fee}` | Extension approved |

#### Group Channel (`ws:group:{group_id}`)

| Event | Payload | Trigger |
|-------|---------|---------|
| `member_joined` | `{user_id, name, trust_score}` | Member accepted invite |
| `deposit_paid` | `{user_id, amount, total_collected, total_required}` | Member paid share |
| `vote_required` | `{vote_id, vote_type, requested_by, expires_at}` | New vote created |
| `vote_cast` | `{vote_id, user_id, vote, votes_for, votes_against}` | Member voted |
| `rental_status` | `{rental_id, status}` | Rental status change |

#### Agent Channel (`ws:agent:{agent_id}`)

| Event | Payload | Trigger |
|-------|---------|---------|
| `new_assignment` | `{type, rental_id, customer, address, products}` | New pickup/return |
| `route_update` | `{stops: [...]}` | Route optimized |
| `inspection_reminder` | `{rental_id, stage}` | Pending inspection |

---

## 8. File Storage Architecture

### 8.1 Cloudflare R2 Bucket Structure

```
rental-files/
├── kyc/
│   └── {user_id}/
│       ├── aadhaar_front.jpg
│       ├── aadhaar_back.jpg
│       ├── selfie.jpg
│       ├── liveness_video.mp4
│       └── address_proof.pdf
│
├── products/
│   └── {product_id}/
│       ├── thumbnail.jpg
│       ├── photo_1.jpg
│       ├── photo_2.jpg
│       └── photo_3.jpg
│
├── custody/
│   └── {rental_id}/
│       ├── pre_pickup/
│       │   ├── front.jpg
│       │   ├── back.jpg
│       │   ├── left.jpg
│       │   ├── right.jpg
│       │   └── top.jpg
│       ├── pickup/
│       │   └── ...
│       └── return/
│           └── ...
│
├── agreements/
│   └── {rental_id}/
│       └── agreement_signed.pdf
│
├── invoices/
│   └── {rental_id}/
│       ├── booking_invoice.pdf
│       └── return_invoice.pdf
│
├── damage/
│   └── {damage_report_id}/
│       ├── damage_1.jpg
│       └── damage_2.jpg
│
└── audit/
    └── {year}/{month}/
        └── audit_export.csv.enc
```

### 8.2 File Upload Flow

```
1. Client → POST /api/v1/files/presign
   Request: { "purpose": "kyc", "file_type": "image/jpeg", "file_size": 1024000 }
   
2. Server → Generate pre-signed R2 URL (TTL: 5 minutes)
   Response: { "upload_url": "https://...", "file_id": "uuid" }

3. Client → PUT {upload_url} (direct to R2, no backend traffic)
   Body: Binary file data

4. Client → POST /api/v1/files/confirm
   Request: { "file_id": "uuid", "purpose": "kyc" }

5. Server → Validate file (type, size, virus scan)
   → Store R2 path in DB
   → Trigger downstream (e.g., KYC OCR processing)
   
6. Response: { "url": "https://...", "status": "uploaded" }
```

### 8.3 Pre-Signed URL Generation (Python)

```python
import boto3
from botocore.config import Config

r2_client = boto3.client(
    's3',
    endpoint_url=f'https://{R2_ACCOUNT_ID}.r2.cloudflarestorage.com',
    aws_access_key_id=R2_ACCESS_KEY,
    aws_secret_access_key=R2_SECRET_KEY,
    config=Config(signature_version='s3v4'),
    region_name='auto'
)

def generate_upload_url(bucket: str, key: str, expiresIn: int = 300):
    return r2_client.generate_presigned_url(
        'put_object',
        Params={'Bucket': bucket, 'Key': key},
        ExpiresIn=expiresIn
    )

def generate_download_url(bucket: str, key: str, expiresIn: int = 900):
    return r2_client.generate_presigned_url(
        'get_object',
        Params={'Bucket': bucket, 'Key': key},
        ExpiresIn=expiresIn
    )
```

---

## 9. Cache Strategy

### 9.1 Cache Layers

| Layer | Technology | TTL | Invalidation |
|-------|------------|-----|--------------|
| **CDN Cache** | Cloudflare | 1 hour | Manual purge |
| **API Response Cache** | Redis | 30 sec | On data change |
| **Session Cache** | Redis | 30 days | On logout/rotate |
| **Rate Limit Counter** | Redis | Per rule | Auto-expire |
| **Reservation Hold** | Redis | 15 min | Auto-expire |
| **Materialized View** | PostgreSQL | 5 min | ARQ refresh job |

### 9.2 Cache Invalidation Strategy

```python
# Cache-aside pattern with invalidation
async def get_product(product_id: str):
    # 1. Check cache
    cached = await redis.get(f"product:{product_id}")
    if cached:
        return json.loads(cached)
    
    # 2. Cache miss → query DB
    product = await db.get(Product, product_id)
    
    # 3. Store in cache
    await redis.setex(
        f"product:{product_id}",
        30,  # TTL: 30 seconds
        json.dumps(product.to_dict())
    )
    
    return product

# Invalidate on write
async def update_product(product_id: str, data: dict):
    product = await db.update(Product, product_id, data)
    
    # Invalidate cache
    await redis.delete(f"product:{product_id}")
    
    # Invalidate related caches
    await redis.delete(f"product:{product_id}:availability")
    
    return product
```

---

## 10. Background Jobs

### 10.1 ARQ Worker Architecture

```
FastAPI Application
    │
    ├── API Request → Creates Job → Redis Queue
    │
    └── ARQ Worker (separate process)
        │
        ├── Polls Redis Queue
        ├── Executes job function
        ├── Retries on failure (max 3, exponential backoff)
        ├── Dead letter queue after max retries
        └── Publishes results to Redis
```

### 10.2 Job Definitions

| Job | Schedule | Priority | Description |
|-----|----------|----------|-------------|
| `scan_overdue_rentals` | Every 5 min | High | Detect overdue, create late fees |
| `calculate_late_fees` | Every 60 sec | High | Update running late fees |
| `send_reminders` | Every hour | Medium | T-48h, T-24h, T-2h reminders |
| `expire_reservations` | Every minute | High | Release expired cart holds |
| `refresh_dashboard` | Every 5 min | Low | Update materialized views |
| `process_kyc_ocr` | On upload | High | Extract text from ID docs |
| `generate_invoice_pdf` | On rental confirm | Medium | Create invoice PDF |
| `generate_agreement_pdf` | On rental confirm | Medium | Create agreement PDF |
| `recalculate_trust_score` | On event | Medium | Update trust scores |
| `send_email` | On queue | Medium | Dispatch via Resend |
| `send_sms` | On queue | Medium | Dispatch via MSG91 |
| `archive_old_records` | Daily 2AM | Low | Move old data to archive |

---

## 11. Rate Limiting & Security

### 11.1 Multi-Layer Rate Limiting

```
Request → Cloudflare (DDoS) → Nginx (edge) → FastAPI (slowapi)
              │                    │                  │
              ▼                    ▼                  ▼
         Layer 1              Layer 2            Layer 3
      IP-based           IP + endpoint        User + endpoint
    (100 req/min)       (200 req/min)        (1000 req/hr)
```

### 11.2 Rate Limit Rules

| Endpoint | Limit | Window | On Exceed |
|----------|-------|--------|-----------|
| `POST /auth/otp/send` | 3 | 15 min/phone | 429 + lockout |
| `POST /auth/login` | 5 | 15 min/IP | 429 + lockout |
| `POST /auth/refresh` | 20 | 1 hr/user | 429 + log |
| `GET /products` (public) | 200 | 1 min/IP | 429 + Retry-After |
| `POST /rentals` | 10 | 1 hr/user | 429 + flag |
| `POST /kyc/upload` | 10 | 24 hr/user | 429 |
| `GET /*` (authenticated) | 1000 | 1 hr/user | 429 + Retry-After |
| `WS /ws/*` | 5 | Per user | Reject oldest |

### 11.3 Security Headers

```
Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
Content-Security-Policy: default-src 'self'; script-src 'self'
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: camera=(), microphone=(), geolocation=(self)
X-XSS-Protection: 1; mode=block
```

---

## 12. Load Balancing & Scaling

### 12.1 Scaling Tiers

| Tier | Users | Setup | Cost |
|------|-------|-------|------|
| **MVP** | 0-1K | 1 FastAPI (4 workers) + NeonDB free + Upstash free | Free |
| **Growth** | 1K-10K | 2 FastAPI + Nginx LB + NeonDB replica | Minimal |
| **Scale** | 10K-100K | 4-8 FastAPI + Redis Cluster + NeonDB Pro | Moderate |
| **Enterprise** | 100K+ | Kubernetes + autoscaling + DB sharding | Cloud |

### 12.2 Uvicorn Configuration

```python
# gunicorn.conf.py
workers = 4  # 4 × CPU cores
worker_class = "uvicorn.workers.UvicornWorker"
bind = "0.0.0.0:8000"
timeout = 120
keepalive = 5
max_requests = 1000  # Restart worker after 1000 requests (memory leak prevention)
max_requests_jitter = 50  # Random jitter to prevent all workers restarting at once
```

---

## 13. Deployment Architecture

### 13.1 Deployment Pipeline

```
Git Push → GitHub Actions → Build → Test → Deploy
                                        │
                                        ▼
                              ┌─────────────────────┐
                              │   Staging (auto)     │
                              │   - Railway free     │
                              │   - NeonDB branch    │
                              └──────────┬──────────┘
                                         │ Manual approval
                                         ▼
                              ┌─────────────────────┐
                              │   Production         │
                              │   - Railway          │
                              │   - NeonDB main      │
                              │   - Cloudflare       │
                              └─────────────────────┘
```

### 13.2 Environment Variables

```env
# Database
DATABASE_URL=postgresql://user:pass@ep-xxx.us-east-2.aws.neon.tech/dbname?sslmode=require
DATABASE_READ_URL=postgresql://user:pass@ep-yyy.us-east-2.aws.neon.tech/dbname?sslmode=require

# Redis
REDIS_URL=rediss://:password@xxx.upstash.io:6379

# JWT
JWT_SECRET=your-256-bit-secret
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=30

# File Storage
R2_ACCOUNT_ID=xxx
R2_ACCESS_KEY=xxx
R2_SECRET_KEY=xxx
R2_BUCKET=rental-files

# Payment
RAZORPAY_KEY_ID=rzp_test_xxx
RAZORPAY_KEY_SECRET=xxx

# KYC
DIGIO_API_KEY=xxx
FACEIO_APP_ID=xxx
SUREPASS_API_KEY=xxx

# Notification
RESEND_API_KEY=re_xxx
MSG91_API_KEY=xxx
FCM_SERVER_KEY=xxx

# Monitoring
SENTRY_DSN=https://xxx@sentry.io/xxx
```

---

**— End of SYSTEM_ARCHITECTURE.md —**
