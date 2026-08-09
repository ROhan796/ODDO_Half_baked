# COMPATIBLE.md
## Frontend-Backend Integration & Compatibility Report
### Reprico Rental Management System | Version 1.0 | August 2026

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [System Architecture Overview](#2-system-architecture-overview)
3. [Backend Index (Complete)](#3-backend-index-complete)
4. [Frontend Index (Complete)](#4-frontend-index-complete)
5. [Endpoint-to-Page Mapping](#5-endpoint-to-page-mapping)
6. [Data Model Compatibility Matrix](#6-data-model-compatibility-matrix)
7. [Gap Analysis: Frontend Features Without Backend](#7-gap-analysis-frontend-features-without-backend)
8. [Gap Analysis: Backend Features Without Frontend](#8-gap-analysis-backend-features-without-frontend)
9. [Service Coverage Matrix](#9-service-coverage-matrix)
10. [Software Services for Rentals](#10-software-services-for-rentals)
11. [Integration Plan](#11-integration-plan)
12. [Priority Action Items](#12-priority-action-items)

---

## 1. Executive Summary

| Metric | Backend | Frontend |
|--------|---------|----------|
| **Framework** | FastAPI 0.115 (Python 3.12) | Next.js 15 (React 19, TypeScript) |
| **API Endpoints** | 68 (67 HTTP + 1 WebSocket) | 0 real API calls |
| **Database Models** | 44 models | 22 TypeScript interfaces |
| **Pages/Views** | N/A | 33 pages across 5 portals |
| **Service Classes** | 16 (~75 functions) | 0 (Zustand mock store) |
| **Auth** | JWT + RBAC (4 roles, 26 permissions) | Mock sessionStorage tokens |
| **Real-time** | WebSocket + Redis pub/sub | None |
| **Integration Status** | **COMPLETE** | **ZERO INTEGRATION** |

**Critical Finding:** The frontend is 100% mock data. Zero HTTP requests, zero API calls. All data flows through a Zustand in-memory store populated from `data/mockData.ts`. React Query is configured but unused. The entire backend is production-ready with 68 endpoints, but no wiring exists.

---

## 2. System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    FRONTEND (Next.js 15)                        │
│  Port 3000 | App Router | TypeScript | Tailwind CSS             │
│                                                                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │ Customer │  │  Admin   │  │Enterprise│  │  Agent   │ ...   │
│  │ Portal   │  │  Portal  │  │  Portal  │  │  Portal  │       │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘       │
│       │              │              │              │             │
│       └──────────────┴──────┬───────┴──────────────┘             │
│                             │                                    │
│                    ┌────────▼────────┐                           │
│                    │  Zustand Store  │  ← MOCK DATA ONLY        │
│                    │  (lib/store.ts) │                           │
│                    └────────┬────────┘                           │
│                             │                                    │
│                    ┌────────▼────────┐                           │
│                    │  React Query    │  ← CONFIGURED, UNUSED    │
│                    │  (providers.tsx)│                           │
│                    └─────────────────┘                           │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                    ╳ NO INTEGRATION ╳
                          │
┌─────────────────────────▼───────────────────────────────────────┐
│                    BACKEND (FastAPI)                             │
│  Port 8000 | Async | PostgreSQL | Redis | R2                    │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ 68 API Endpoints across 19 modules                       │  │
│  │ auth | users | products | categories | rentals |          │  │
│  │ quotations | invoices | deposits | disputes | repairs |   │  │
│  │ recovery | groups | enterprise | crm | stock | loyalty |  │  │
│  │ notifications | admin | files | dashboard                 │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │PostgreSQL│  │  Redis   │  │ Cloudflare│  │  ARQ     │       │
│  │ (NeonDB) │  │(Upstash) │  │    R2     │  │ Workers  │       │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘       │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. Backend Index (Complete)

### 3.1 All API Endpoints (68 Total)

#### Authentication (`/api/v1/auth`)
| Method | Path | Frontend Page | Status |
|--------|------|---------------|--------|
| POST | `/auth/register` | `/register` | ⚠️ Not wired |
| POST | `/auth/login` | `/login` | ⚠️ Not wired |
| POST | `/auth/otp/request` | `/login` (OTP mode) | ⚠️ Not wired |
| POST | `/auth/otp/verify` | `/login` (OTP mode) | ⚠️ Not wired |
| POST | `/auth/refresh` | All (token refresh) | ⚠️ Not wired |
| POST | `/auth/logout` | AppShell sign-out | ⚠️ Not wired |

#### Users (`/api/v1/users`)
| Method | Path | Frontend Page | Status |
|--------|------|---------------|--------|
| GET | `/users/me` | `/customer/profile` | ⚠️ Not wired |
| PUT | `/users/me` | `/customer/profile` | ⚠️ Not wired |
| GET | `/users/` | `/admin/*` (user lists) | ⚠️ Not wired |
| GET | `/users/{id}` | Profile views | ⚠️ Not wired |

#### Products (`/api/v1/products`)
| Method | Path | Frontend Page | Status |
|--------|------|---------------|--------|
| GET | `/products/` | `/catalog`, `/admin/inventory` | ⚠️ Not wired |
| POST | `/products/` | `/admin/inventory` (add form) | ⚠️ Not wired |
| GET | `/products/{id}` | `/product/[id]` | ⚠️ Not wired |
| PUT | `/products/{id}` | `/admin/inventory` (edit) | ⚠️ Not wired |
| DELETE | `/products/{id}` | `/admin/inventory` (archive) | ⚠️ Not wired |

#### Categories (`/api/v1/categories`)
| Method | Path | Frontend Page | Status |
|--------|------|---------------|--------|
| GET | `/categories/` | `/catalog` (filters) | ⚠️ Not wired |
| POST | `/categories/` | Admin (category mgmt) | ⚠️ Not wired |
| GET | `/categories/{id}` | Category detail | ⚠️ Not wired |

#### Rentals (`/api/v1/rentals`)
| Method | Path | Frontend Page | Status |
|--------|------|---------------|--------|
| GET | `/rentals/` | `/customer/rentals`, `/admin/rentals` | ⚠️ Not wired |
| POST | `/rentals/` | `/product/[id]` (checkout wizard) | ⚠️ Not wired |
| GET | `/rentals/{id}` | Rental detail views | ⚠️ Not wired |
| POST | `/rentals/{id}/return` | `/agent/inspection` | ⚠️ Not wired |
| POST | `/rentals/{id}/extend` | `/customer/rentals` (extend) | ⚠️ Not wired |

#### Quotations (`/api/v1/quotations`)
| Method | Path | Frontend Page | Status |
|--------|------|---------------|--------|
| GET | `/quotations/` | Enterprise quotes list | ⚠️ Not wired |
| POST | `/quotations/` | Enterprise quote creation | ⚠️ Not wired |
| GET | `/quotations/{id}` | QuoteViewer component | ⚠️ Not wired |

#### Invoices (`/api/v1/invoices`)
| Method | Path | Frontend Page | Status |
|--------|------|---------------|--------|
| GET | `/invoices/` | `/customer/invoices` | ⚠️ Not wired |
| POST | `/invoices/` | Admin invoice creation | ⚠️ Not wired |
| GET | `/invoices/{id}` | InvoiceViewer component | ⚠️ Not wired |
| POST | `/invoices/payments` | Payment processing | ⚠️ Not wired |

#### Deposits (`/api/v1/deposits`)
| Method | Path | Frontend Page | Status |
|--------|------|---------------|--------|
| GET | `/deposits/` | `/admin/deposits`, `/customer/payments` | ⚠️ Not wired |
| GET | `/deposits/{id}` | Deposit detail | ⚠️ Not wired |
| POST | `/deposits/{id}/settle` | `/admin/deposits` (settle action) | ⚠️ Not wired |

#### Disputes (`/api/v1/disputes`)
| Method | Path | Frontend Page | Status |
|--------|------|---------------|--------|
| GET | `/disputes/` | `/customer/disputes`, `/admin/disputes` | ⚠️ Not wired |
| POST | `/disputes/` | `/customer/disputes` (file form) | ⚠️ Not wired |
| GET | `/disputes/{id}` | Dispute detail | ⚠️ Not wired |

#### Repairs (`/api/v1/repairs`)
| Method | Path | Frontend Page | Status |
|--------|------|---------------|--------|
| GET | `/repairs/` | Admin repair tracking | ⚠️ Not wired |
| POST | `/repairs/` | Admin repair creation | ⚠️ Not wired |
| GET | `/repairs/{id}` | Repair detail | ⚠️ Not wired |

#### Recovery (`/api/v1/recovery`)
| Method | Path | Frontend Page | Status |
|--------|------|---------------|--------|
| GET | `/recovery/` | Admin recovery tracking | ⚠️ Not wired |
| POST | `/recovery/` | Admin recovery creation | ⚠️ Not wired |
| GET | `/recovery/{id}` | Recovery detail | ⚠️ Not wired |

#### Groups (`/api/v1/groups`)
| Method | Path | Frontend Page | Status |
|--------|------|---------------|--------|
| GET | `/groups/` | `/group/dashboard` | ⚠️ Not wired |
| POST | `/groups/` | `/group/create` | ⚠️ Not wired |
| GET | `/groups/{id}` | `/group/[id]` | ⚠️ Not wired |
| POST | `/groups/{id}/members` | `/group/[id]` (invite) | ⚠️ Not wired |
| POST | `/groups/{id}/votes` | `/group/[id]` (create vote) | ⚠️ Not wired |
| POST | `/groups/{id}/votes/{vid}/cast` | `/group/[id]` (cast vote) | ⚠️ Not wired |

#### Enterprise (`/api/v1/enterprise`)
| Method | Path | Frontend Page | Status |
|--------|------|---------------|--------|
| GET | `/enterprise/` | `/enterprise/dashboard` | ⚠️ Not wired |
| POST | `/enterprise/` | Enterprise registration | ⚠️ Not wired |
| GET | `/enterprise/{id}` | Enterprise detail | ⚠️ Not wired |
| POST | `/enterprise/{id}/members` | Enterprise team mgmt | ⚠️ Not wired |

#### CRM (`/api/v1/crm`)
| Method | Path | Frontend Page | Status |
|--------|------|---------------|--------|
| GET | `/crm/contacts` | Admin CRM views | ⚠️ Not wired |
| POST | `/crm/contacts` | Admin CRM creation | ⚠️ Not wired |
| GET | `/crm/contacts/{id}` | Contact detail | ⚠️ Not wired |
| PUT | `/crm/contacts/{id}` | Contact edit | ⚠️ Not wired |
| POST | `/crm/interactions` | Admin interaction logging | ⚠️ Not wired |

#### Stock (`/api/v1/stock`)
| Method | Path | Frontend Page | Status |
|--------|------|---------------|--------|
| GET | `/stock/` | Admin stock movements | ⚠️ Not wired |
| POST | `/stock/locations` | Admin location creation | ⚠️ Not wired |
| GET | `/stock/locations` | Admin location list | ⚠️ Not wired |
| GET | `/stock/locations/{id}` | Location detail | ⚠️ Not wired |
| POST | `/stock/movements` | Admin stock movement | ⚠️ Not wired |
| GET | `/stock/movements` | Admin movement log | ⚠️ Not wired |
| GET | `/stock/levels` | Admin stock levels | ⚠️ Not wired |

#### Loyalty (`/api/v1/loyalty`)
| Method | Path | Frontend Page | Status |
|--------|------|---------------|--------|
| GET | `/loyalty/points` | `/customer/loyalty` (redirect) | ⚠️ Not wired |
| GET | `/loyalty/points/ledger` | Loyalty history | ⚠️ Not wired |
| POST | `/loyalty/points/redeem` | Loyalty redemption | ⚠️ Not wired |
| GET | `/loyalty/referrals` | Referral program | ⚠️ Not wired |
| GET | `/loyalty/referrals/{code}/validate` | Referral validation | ⚠️ Not wired |

#### Notifications (`/api/v1/notifications`)
| Method | Path | Frontend Page | Status |
|--------|------|---------------|--------|
| GET | `/notifications/` | `/customer/notifications` | ⚠️ Not wired |
| GET | `/notifications/unread-count` | Bell icon badge | ⚠️ Not wired |
| PUT | `/notifications/{id}/read` | Mark as read | ⚠️ Not wired |
| PUT | `/notifications/read-all` | Mark all read | ⚠️ Not wired |
| GET | `/notifications/templates` | Admin templates | ⚠️ Not wired |
| POST | `/notifications/templates` | Admin template creation | ⚠️ Not wired |

#### Admin (`/api/v1/admin`)
| Method | Path | Frontend Page | Status |
|--------|------|---------------|--------|
| GET | `/admin/dashboard` | `/admin/dashboard` | ⚠️ Not wired |
| GET | `/admin/audit-logs` | `/enterprise/audit-logs` | ⚠️ Not wired |
| POST | `/admin/blacklist` | Admin blacklist user | ⚠️ Not wired |
| DELETE | `/admin/blacklist/{id}` | Admin unblacklist | ⚠️ Not wired |
| GET | `/admin/blacklist` | Admin blacklist list | ⚠️ Not wired |
| GET | `/admin/system/health` | Admin system health | ⚠️ Not wired |

#### Files (`/api/v1/files`)
| Method | Path | Frontend Page | Status |
|--------|------|---------------|--------|
| POST | `/files/presigned-url` | Photo uploads (KYC, inspection) | ⚠️ Not wired |
| DELETE | `/files/{key}` | File deletion | ⚠️ Not wired |

#### Dashboard (`/api/v1/dashboard`)
| Method | Path | Frontend Page | Status |
|--------|------|---------------|--------|
| GET | `/dashboard/stats` | `/admin/dashboard`, `/customer/dashboard` | ⚠️ Not wired |
| GET | `/dashboard/revenue-chart` | `/admin/financials` | ⚠️ Not wired |
| GET | `/dashboard/rental-chart` | `/admin/financials` | ⚠️ Not wired |

#### WebSocket
| Protocol | Path | Frontend | Status |
|----------|------|----------|--------|
| WS | `/ws/{token}` | None | ⚠️ Not wired |

---

## 4. Frontend Index (Complete)

### 4.1 All Pages (33 Total)

| Portal | Route | File | Backend Endpoint Required |
|--------|-------|------|--------------------------|
| **Public** | `/` | `app/page.tsx` | None (landing) |
| **Public** | `/login` | `app/login/page.tsx` | `POST /auth/login`, `POST /auth/otp/request`, `POST /auth/otp/verify` |
| **Public** | `/register` | `app/register/page.tsx` | `POST /auth/register` |
| **Public** | `/forgot-password` | `app/forgot-password/page.tsx` | `POST /auth/otp/request` |
| **Public** | `/catalog` | `app/catalog/page.tsx` | `GET /products/`, `GET /categories/` |
| **Public** | `/product/[id]` | `app/product/[id]/page.tsx` | `GET /products/{id}`, `POST /rentals/` |
| **Customer** | `/customer/dashboard` | `app/customer/dashboard/page.tsx` | `GET /dashboard/stats`, `GET /rentals/` |
| **Customer** | `/customer/rentals` | `app/customer/rentals/page.tsx` | `GET /rentals/`, `GET /rentals/{id}`, `POST /rentals/{id}/extend`, `POST /rentals/{id}/return` |
| **Customer** | `/customer/orders` | `app/customer/orders/page.tsx` | `GET /rentals/` (orders view) |
| **Customer** | `/customer/invoices` | `app/customer/invoices/page.tsx` | `GET /invoices/`, `GET /invoices/{id}` |
| **Customer** | `/customer/payments` | `app/customer/payments/page.tsx` | `GET /deposits/` |
| **Customer** | `/customer/kyc` | `app/customer/kyc/page.tsx` | `POST /auth/otp/request`, KYC submission |
| **Customer** | `/customer/profile` | `app/customer/profile/page.tsx` | `GET /users/me`, `PUT /users/me` |
| **Customer** | `/customer/addresses` | `app/customer/addresses/page.tsx` | `PUT /users/me` (address field) |
| **Customer** | `/customer/disputes` | `app/customer/disputes/page.tsx` | `GET /disputes/`, `POST /disputes/` |
| **Customer** | `/customer/notifications` | `app/customer/notifications/page.tsx` | `GET /notifications/`, `PUT /notifications/{id}/read` |
| **Customer** | `/customer/loyalty` | `app/customer/loyalty/page.tsx` | `GET /loyalty/points`, `GET /loyalty/points/ledger` |
| **Customer** | `/customer/groups` | `app/customer/groups/page.tsx` | `GET /groups/` |
| **Admin** | `/admin/dashboard` | `app/admin/dashboard/page.tsx` | `GET /admin/dashboard`, `GET /dashboard/stats` |
| **Admin** | `/admin/rentals` | `app/admin/rentals/page.tsx` | `GET /rentals/`, `POST /rentals/{id}/return` |
| **Admin** | `/admin/inventory` | `app/admin/inventory/page.tsx` | `GET /products/`, `POST /products/`, `PUT /products/{id}` |
| **Admin** | `/admin/kyc` | `app/admin/kyc/page.tsx` | `GET /users/` (KYC status) |
| **Admin** | `/admin/dispatch` | `app/admin/dispatch/page.tsx` | Agent task management |
| **Admin** | `/admin/deposits` | `app/admin/deposits/page.tsx` | `GET /deposits/`, `POST /deposits/{id}/settle` |
| **Admin** | `/admin/disputes` | `app/admin/disputes/page.tsx` | `GET /disputes/` |
| **Admin** | `/admin/financials` | `app/admin/financials/page.tsx` | `GET /dashboard/revenue-chart`, `GET /dashboard/rental-chart` |
| **Enterprise** | `/enterprise/dashboard` | `app/enterprise/dashboard/page.tsx` | `GET /enterprise/{id}` |
| **Enterprise** | `/enterprise/po-approvals` | `app/enterprise/po-approvals/page.tsx` | Enterprise PO endpoints |
| **Enterprise** | `/enterprise/credit-limit` | `app/enterprise/credit-limit/page.tsx` | Enterprise credit endpoints |
| **Enterprise** | `/enterprise/departments` | `app/enterprise/departments/page.tsx` | Enterprise member endpoints |
| **Enterprise** | `/enterprise/master-agreement` | `app/enterprise/master-agreement/page.tsx` | Enterprise detail |
| **Enterprise** | `/enterprise/audit-logs` | `app/enterprise/audit-logs/page.tsx` | `GET /admin/audit-logs` |
| **Group** | `/group/dashboard` | `app/group/dashboard/page.tsx` | `GET /groups/` |
| **Group** | `/group/create` | `app/group/create/page.tsx` | `POST /groups/` |
| **Group** | `/group/[id]` | `app/group/[id]/page.tsx` | `GET /groups/{id}`, `POST /groups/{id}/members`, `POST /groups/{id}/votes` |
| **Agent** | `/agent/tasks` | `app/agent/tasks/page.tsx` | Agent task endpoints |
| **Agent** | `/agent/tasks/[id]` | `app/agent/tasks/[id]/page.tsx` | Agent task detail |
| **Agent** | `/agent/qr-scanner` | `app/agent/qr-scanner/page.tsx` | `GET /products/` (by QR) |
| **Agent** | `/agent/inspection` | `app/agent/inspection/page.tsx` | `POST /rentals/{id}/return` |
| **Agent** | `/agent/profile` | `app/agent/profile/page.tsx` | `GET /users/me` |

---

## 5. Endpoint-to-Page Mapping

### 5.1 Mapping Summary

| Backend Module | Endpoints | Frontend Pages Using It | Coverage |
|----------------|-----------|------------------------|----------|
| Auth | 6 | login, register, forgot-password | 0% |
| Users | 4 | profile, admin pages | 0% |
| Products | 5 | catalog, product detail, inventory | 0% |
| Categories | 3 | catalog filters | 0% |
| Rentals | 5 | rentals, orders, admin rentals, checkout | 0% |
| Quotations | 3 | enterprise quotes | 0% |
| Invoices | 4 | customer invoices, admin | 0% |
| Deposits | 3 | payments, admin deposits | 0% |
| Disputes | 3 | customer disputes, admin disputes | 0% |
| Repairs | 3 | admin inventory/repairs | 0% |
| Recovery | 3 | admin (implicit) | 0% |
| Groups | 6 | group dashboard, create, detail | 0% |
| Enterprise | 4 | enterprise portal pages | 0% |
| CRM | 5 | admin CRM (implicit) | 0% |
| Stock | 7 | admin inventory, dispatch | 0% |
| Loyalty | 5 | customer loyalty (redirect stub) | 0% |
| Notifications | 6 | customer notifications, bell icon | 0% |
| Admin | 6 | admin dashboard, audit logs | 0% |
| Files | 2 | photo uploads (KYC, inspection) | 0% |
| Dashboard | 3 | admin/customer dashboards, financials | 0% |
| WebSocket | 1 | None | 0% |

**Overall Integration: 0% — No endpoints are wired.**

---

## 6. Data Model Compatibility Matrix

### 6.1 User Model

| Field | Backend (`users` table) | Frontend (`User` interface) | Compatible? |
|-------|------------------------|----------------------------|-------------|
| id | UUID | string (`usr-1`) | ⚠️ ID format differs |
| name | VARCHAR(255) | string | ✅ |
| email | VARCHAR(255) | string | ✅ |
| phone | VARCHAR(15) | string | ✅ |
| role | ENUM (super_admin, ops_admin, field_agent, portal_user) | UserRole ('customer','enterprise_admin','group_leader','admin','field_agent') | ⚠️ Role names differ |
| user_type | ENUM (personal, enterprise, enterprise_sub) | accountType ('personal','group','enterprise') | ⚠️ Field name differs |
| kyc_status | ENUM (pending, in_progress, verified, rejected) | kycStatus ('unverified','pending','verified','rejected') | ⚠️ Extra value 'unverified' |
| trust_score | SMALLINT (0-100) | trustScore (number) | ✅ |
| enterprise_id | UUID FK | enterpriseId (string) | ⚠️ ID format differs |
| group_id | Not in backend model | groupId (string) | ❌ Backend missing |
| profile_photo_url | TEXT | avatar (string) | ⚠️ Field name differs |
| password_hash | VARCHAR(255) | Not exposed | ✅ (correct — never expose) |
| points_balance | INTEGER | Not in User type | ❌ Backend has, frontend missing |
| lifetime_rentals | INTEGER | Not in User type | ❌ Backend has, frontend missing |
| lifetime_spend | NUMERIC | Not in User type | ❌ Backend has, frontend missing |
| referral_code | VARCHAR(20) | Not in User type | ❌ Backend has, frontend missing |
| device_fingerprints | TEXT[] | Not in User type | ✅ (correct — never expose) |

### 6.2 Product Model

| Field | Backend (`products` table) | Frontend (`Product` interface) | Compatible? |
|-------|---------------------------|-------------------------------|-------------|
| id | UUID | string (`prod-1`) | ⚠️ ID format differs |
| name | VARCHAR(255) | string | ✅ |
| slug | VARCHAR(255) | string | ✅ |
| category_id | UUID FK | category (string name) | ⚠️ FK vs name |
| brand | Not a column (in metadata JSONB) | string | ⚠️ Backend uses JSONB |
| model | Not a column (in metadata JSONB) | string | ⚠️ Backend uses JSONB |
| serial_number | VARCHAR(100) | serialNumber (string) | ✅ |
| daily_rate | Not a column (in pricelist) | dailyRate (number) | ⚠️ Backend uses pricelist |
| weekly_rate | Not a column (in pricelist) | weeklyRate (number) | ⚠️ Backend uses pricelist |
| monthly_rate | Not a column (in pricelist) | monthlyRate (number) | ⚠️ Backend uses pricelist |
| deposit_percentage | NUMERIC(5,2) | securityDeposit (number) | ⚠️ % vs absolute value |
| condition_rating | SMALLINT (1-5) | conditionGrade (string enum) | ⚠️ Number vs string |
| status | ENUM (available, rented, in_repair, inactive, archived) | status (AVAILABLE, RENTED, MAINTENANCE, RESERVED, DAMAGED) | ⚠️ Different enum values |
| images | TEXT[] | string[] | ✅ |
| metadata | JSONB | specs: Record<string, string> | ⚠️ Generic vs structured |
| accessories | Separate `accessories` table | accessories: string[] | ⚠️ Table vs inline array |
| stock_quantity | Not a column (in stock_levels) | stockQuantity (number) | ⚠️ Separate table vs inline |
| available_quantity | Not a column (computed) | availableQuantity (number) | ⚠️ Computed vs inline |
| description | TEXT | string | ✅ |
| terms | Not a column | terms (string) | ❌ Frontend only |
| damagePolicy | Not a column | damagePolicy (string) | ❌ Frontend only |
| cancellationPolicy | Not a column | cancellationPolicy (string) | ❌ Frontend only |
| is_featured | BOOLEAN | Not in type | ❌ Backend has, frontend missing |
| total_rentals | INTEGER | Not in type | ❌ Backend has, frontend missing |
| total_revenue | NUMERIC | Not in type | ❌ Backend has, frontend missing |

### 6.3 Rental Model

| Field | Backend (`rentals` table) | Frontend (`Rental` interface) | Compatible? |
|-------|--------------------------|------------------------------|-------------|
| id | UUID | string (`RN-1048`) | ⚠️ ID format differs |
| rental_number | Not in model (DB schema has it) | id serves as rental number | ⚠️ Different approach |
| customer_id | UUID FK | customerId (string) | ⚠️ ID format differs |
| product_id | UUID FK | productId (string) | ⚠️ ID format differs |
| status | ENUM (pending, confirmed, active, returned, overdue, cancelled) | status (PENDING, CONFIRMED, ACTIVE, OVERDUE, INSPECTION, COMPLETED, DISPUTED, CANCELLED) | ⚠️ Extra statuses in frontend |
| start_date | DATE | startDate (string) | ✅ (format) |
| end_date | DATE | endDate (string) | ✅ (format) |
| actual_return_date | DATE | actualReturnDate (string) | ✅ |
| daily_rate | NUMERIC | dailyRate (number) | ✅ |
| total_amount | NUMERIC | totalRentalFee (number) | ⚠️ Field name differs |
| deposit_amount | NUMERIC | securityDepositHeld (number) | ⚠️ Field name differs |
| late_fees | NUMERIC | accumulatedLateFee (number) | ⚠️ Field name differs |
| damage_charges | NUMERIC | Not directly (in deductions) | ⚠️ Different structure |
| insurance_selected | BOOLEAN | Not in type | ❌ Backend has, frontend missing |
| delivery_address | TEXT | deliveryAddress (string) | ✅ |
| pickup_type | Not a column (in delivery_method) | pickupType ('DELIVERY'/'SELF_PICKUP') | ⚠️ Different field |
| assigned_agent | Not a column | assignedAgent (string) | ❌ Frontend only |
| checkout_condition | Not a column (separate custody) | checkoutCondition (string) | ⚠️ Different approach |
| return_condition | Not a column (separate custody) | returnCondition (string) | ⚠️ Different approach |
| accessories_checked | Not a column (separate table) | accessoriesChecked (Record) | ⚠️ Different approach |
| checkout_photos | TEXT | checkoutPhotos (string[]) | ⚠️ Single text vs array |
| return_photos | TEXT | returnPhotos (string[]) | ⚠️ Single text vs array |
| customer_name | Not a column (joined) | customerName (string) | ⚠️ Computed vs stored |
| customer_phone | Not a column (joined) | customerPhone (string) | ⚠️ Computed vs stored |
| product_name | Not a column (joined) | productName (string) | ⚠️ Computed vs stored |
| product_image | Not a column (joined) | productImage (string) | ⚠️ Computed vs stored |
| order_id | UUID | orderId (string) | ✅ |

### 6.4 Invoice Model

| Field | Backend (`invoices` table) | Frontend (`Invoice` interface) | Compatible? |
|-------|---------------------------|-------------------------------|-------------|
| id | UUID | string (`INV-2026-001`) | ⚠️ ID format differs |
| invoice_number | VARCHAR(20) | id serves as invoice number | ⚠️ Different approach |
| rental_id | UUID FK | rentalId (string) | ✅ |
| user_id | UUID FK | customerId (string) | ⚠️ Field name differs |
| status | ENUM (draft, issued, paid, partially_paid, overdue, cancelled, void) | status (PAID, UNPAID, OVERDUE, PARTIALLY_PAID) | ⚠️ Different enum values |
| subtotal | NUMERIC | subtotal (number) | ✅ |
| tax_amount | NUMERIC | cgst + sgst + igst (3 fields) | ⚠️ Single vs split tax |
| total | NUMERIC | total (number) | ✅ |
| amount_paid | NUMERIC | paidAmount (number) | ⚠️ Field name differs |
| billing_type | Not a column (in invoice_items) | billingType (RENTAL, LATE_FEE, etc.) | ⚠️ Different structure |
| customer_name | Not a column (joined) | customerName (string) | ⚠️ Computed vs stored |
| customer_email | Not a column (joined) | customerEmail (string) | ⚠️ Computed vs stored |
| customer_gst | Not a column | customerGst (string) | ❌ Frontend only |
| customer_address | Not a column (billing_address JSONB) | customerAddress (string) | ⚠️ Different structure |
| pdf_url | TEXT | pdfUrl (string) | ✅ |

### 6.5 Dispute Model

| Field | Backend (`disputes` table) | Frontend (`Dispute` interface) | Compatible? |
|-------|---------------------------|-------------------------------|-------------|
| id | UUID | string (`DISP-102`) | ⚠️ ID format differs |
| dispute_number | VARCHAR(20) | id serves as dispute number | ⚠️ Different approach |
| rental_id | UUID FK | rentalId (string) | ✅ |
| filed_by / customer_id | UUID FK | raisedBy, customerName (strings) | ⚠️ Different fields |
| dispute_type | ENUM | reason (string enum) | ⚠️ Different enum values |
| amount_disputed | NUMERIC | disputedAmount (number) | ✅ |
| description | TEXT | description (string) | ✅ |
| evidence_urls | TEXT[] | evidenceUrls (string[]) | ✅ |
| status | ENUM (open, under_review, won, lost, escalated, closed) | status (OPEN, IN_REVIEW, RESOLVED_REFUND, RESOLVED_REJECTED, ESCALATED) | ⚠️ Different enum values |
| resolution_amount | NUMERIC | Not directly | ❌ Backend has, frontend missing |
| admin_notes | TEXT | adminNotes (string) | ✅ |

---

## 7. Gap Analysis: Frontend Features Without Backend

### 7.1 Frontend-Only Features (Need Backend Support)

| # | Frontend Feature | Frontend Location | Backend Status | Action Required |
|---|-----------------|-------------------|----------------|-----------------|
| 1 | **Agent task management** (task feed, task detail, GPS status) | `/agent/tasks`, `/agent/tasks/[id]` | ❌ No agent/task model | Create AgentTask model + endpoints |
| 2 | **Agent QR scanner** (camera-based QR scanning) | `/agent/qr-scanner` | ⚠️ Products have qr_code field | Wire to `GET /products/?qr_code=X` |
| 3 | **Agent 5-point inspection** (functional check, cosmetic grade, accessories) | `/agent/inspection` | ⚠️ CustodyEvent model exists but no inspection endpoint | Create inspection endpoint |
| 4 | **Photo comparison** (checkout vs return side-by-side) | `components/inspection/PhotoComparison.tsx` | ⚠️ CustodyEvent has photos field | Wire custody events to frontend |
| 5 | **PO Requisition approval** | `/enterprise/po-approvals` | ❌ No PO model | Create PO model + endpoints |
| 6 | **Credit limit expansion request** | `/enterprise/credit-limit` | ⚠️ Enterprise has credit fields but no request endpoint | Create credit request endpoint |
| 7 | **Department management** | `/enterprise/departments` | ⚠️ EnterpriseMember has department field | Wire enterprise member endpoints |
| 8 | **Master SLA agreement** | `/enterprise/master-agreement` | ❌ No SLA model | Create or wire to enterprise detail |
| 9 | **Address management** (saved delivery addresses) | `/customer/addresses` | ⚠️ User has delivery_address in rental | Create user address sub-resource |
| 10 | **Financial charts** (bar chart, pie chart) | `/admin/financials` | ⚠️ Dashboard has chart endpoints | Wire `GET /dashboard/revenue-chart` |
| 11 | **Dispatch map view** (SVG GPS visualization) | `/admin/dispatch` | ❌ No dispatch/agent model | Create dispatch endpoints |
| 12 | **Global search modal** (Cmd+K) | `components/common/GlobalSearchModal.tsx` | ❌ No search endpoint | Create search endpoint |
| 13 | **Rental timeline** (5-step vertical timeline) | `components/viewers/RentalTimeline.tsx` | ⚠️ Rental status history exists in DB schema | Wire rental status history |
| 14 | **ConditionGrade matrix** (5-point inspection) | `components/inspection/ConditionGrade.tsx` | ⚠️ CustodyEvent has condition fields | Wire custody inspection data |
| 15 | **Software services rental** (SaaS, licenses, subscriptions) | Not yet in frontend | ❌ No software service model | **NEW: Create software service models** |

### 7.2 Critical Missing Backend Endpoints

| Priority | Endpoint Needed | Frontend Page | Description |
|----------|----------------|---------------|-------------|
| **P0** | `POST /api/v1/auth/login` | `/login` | Real auth with JWT |
| **P0** | `POST /api/v1/auth/register` | `/register` | Real registration |
| **P0** | `GET /api/v1/products/?category=X&search=Y` | `/catalog` | Product listing with filters |
| **P0** | `POST /api/v1/rentals/` | `/product/[id]` checkout | Real rental creation |
| **P1** | `GET /api/v1/dashboard/stats` | Dashboards | Aggregated stats |
| **P1** | `GET /api/v1/notifications/` | Bell icon | Notification feed |
| **P1** | `GET /api/v1/loyalty/points` | `/customer/loyalty` | Points balance |
| **P2** | `GET /api/v1/stock/levels` | Admin inventory | Stock levels |
| **P2** | `GET /api/v1/crm/contacts` | Admin CRM | CRM contacts |
| **P2** | `POST /api/v1/groups/{id}/votes` | Group voting | Vote creation |

---

## 8. Gap Analysis: Backend Features Without Frontend

### 8.1 Backend-Only Features (No Frontend UI)

| # | Backend Feature | Endpoint(s) | Frontend Status |
|---|----------------|-------------|-----------------|
| 1 | **Pricelist management** | Pricelist model exists, no endpoints | No UI |
| 2 | **Availability blocks** | AvailabilityBlock model, no endpoints | No UI |
| 3 | **Blackout dates** | BlackoutDate model, no endpoints | No UI |
| 4 | **Reservations** | Reservation model, no endpoints | No UI |
| 5 | **Custody events** | CustodyEvent model, no dedicated endpoints | Partial (inspection page) |
| 6 | **Accessory checks** | AccessoryCheck model, no endpoints | No UI |
| 7 | **Late fee calculation** | LateFee model, background worker exists | No UI |
| 8 | **Extension requests** | RentalExtension model, endpoint exists | Partial (extend button) |
| 9 | **Trust score history** | TrustScoreHistory model, no endpoints | No UI |
| 10 | **KYC records** | KYCRecord model, no dedicated endpoints | Partial (Digio modal) |
| 11 | **Audit logs** | AuditLog model, admin endpoint exists | Partial (enterprise audit) |
| 12 | **Notification templates** | NotificationTemplate model, admin endpoints | No UI |
| 13 | **Quotation templates** | QuotationTemplate model, no endpoints | No UI |
| 14 | **Campaign management** | CRMCampaign model, no endpoints | No UI |
| 15 | **Lead scoring** | CRMLeadScore model, no endpoints | No UI |
| 16 | **Stock adjustments** | StockAdjustment model, no endpoints | No UI |
| 17 | **Damage reports** | DamageReport model, no endpoints | No UI |
| 18 | **Referral system** | Referral model, loyalty endpoints exist | No UI |
| 19 | **Materialized views** | Analytics schema, no endpoints | No UI |
| 20 | **PDF generation** | PDFService (placeholder), no endpoints | No UI |

---

## 9. Service Coverage Matrix

### 9.1 Backend Service → Frontend Feature Mapping

| Backend Service | Functions | Frontend Feature | Connected? |
|----------------|-----------|-----------------|------------|
| `AuthService` | register, login, refresh, logout, OTP | Login/Register pages | ❌ No |
| `UserService` | get, list, update, profile | Profile page | ❌ No |
| `ProductService` | create, get, list, update, delete | Catalog, Inventory | ❌ No |
| `RentalService` | create, get, list, confirm, return, extend | Rentals, Checkout | ❌ No |
| `QuotationService` | create, get, list, update_status | Enterprise quotes | ❌ No |
| `InvoiceService` | create, get, list, record_payment | Invoices page | ❌ No |
| `DepositService` | create, get, settle, add_deduction | Payments, Admin deposits | ❌ No |
| `DisputeService` | create, get, list, resolve | Disputes pages | ❌ No |
| `RepairService` | create, get, list, update | Admin repairs | ❌ No |
| `RecoveryService` | create, get, list, update | Admin recovery | ❌ No |
| `GroupService` | create, get, list, add_member, vote | Group pages | ❌ No |
| `EnterpriseService` | create, get, list, add_member | Enterprise pages | ❌ No |
| `CRMService` | create, get, list, update, interactions | Admin CRM | ❌ No |
| `StockService` | create_location, create_movement, levels | Admin inventory | ❌ No |
| `LoyaltyService` | balance, ledger, redeem, referrals | Customer loyalty | ❌ No |
| `NotificationService` | list, unread_count, mark_read, templates | Notifications page | ❌ No |
| `PaymentService` | create_order, verify_payment | Checkout payment | ❌ No |
| `PDFService` | generate_invoice_pdf, generate_quotation_pdf | InvoiceViewer, QuoteViewer | ❌ No |
| `FileService` | presigned_url, delete | Photo uploads | ❌ No |

---

## 10. Software Services for Rentals

### 10.1 Overview

The Reprico platform supports **both Hardware AND Software service rentals**. This is a critical differentiator. Software services include:

| Category | Examples | Rental Model |
|----------|----------|--------------|
| **SaaS Subscriptions** | Adobe Creative Cloud, Microsoft 365, Figma Team | Monthly/Annual license rental |
| **Software Licenses** | Windows Server, VMware, AutoCAD | Per-seat or node-locked license rental |
| **Cloud Compute** | GPU instances, CPU clusters, storage buckets | Hourly/Daily usage-based rental |
| **API Access** | Third-party API credits, data feeds | Usage-based or monthly quota |
| **Digital Content** | Stock footage, music libraries, font licenses | Per-project or subscription rental |
| **Development Tools** | CI/CD pipelines, testing frameworks, monitoring | Monthly subscription rental |
| **Plugin/Extension Licenses** | WordPress plugins, Shopify apps, VS Code extensions | Annual license rental |
| **Data & Analytics** | Market data feeds, analytics platforms, BI tools | Monthly subscription rental |

### 10.2 Software Service Data Model (Backend Addition)

```sql
-- New table: software_services
CREATE TABLE software_services (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(255) UNIQUE NOT NULL,
    category_id UUID REFERENCES categories(id),
    description TEXT,
    short_description VARCHAR(500),
    
    -- Software-specific fields
    vendor VARCHAR(255),                    -- e.g., "Adobe", "Microsoft"
    version VARCHAR(50),                     -- e.g., "v2026.1"
    license_type ENUM NOT NULL,              -- saas_subscription, node_locked, floating, cloud_credit, api_quota
    delivery_method ENUM NOT NULL,           -- email_license_key, cloud_access, api_key, download_link
    
    -- Pricing
    hourly_rate NUMERIC(10,2),
    daily_rate NUMERIC(10,2),
    weekly_rate NUMERIC(10,2),
    monthly_rate NUMERIC(10,2),
    annual_rate NUMERIC(12,2),
    currency VARCHAR(3) DEFAULT 'INR',
    
    -- Access control
    max_concurrent_users INTEGER DEFAULT 1,
    max_seats INTEGER,
    requires_vpn BOOLEAN DEFAULT false,
    ip_whitelist TEXT[],                     -- Allowed IPs
    
    -- Technical details
    system_requirements TEXT,
    api_endpoint TEXT,                       -- For API-based services
    documentation_url TEXT,
    support_email VARCHAR(255),
    
    -- Metadata
    metadata JSONB DEFAULT '{}',            -- Flexible key-value pairs
    tags TEXT[] DEFAULT '{}',
    images TEXT[] DEFAULT '{}',
    thumbnail_url TEXT,
    
    -- Status
    status ENUM DEFAULT 'available',        -- available, rented, deprecated, inactive
    is_featured BOOLEAN DEFAULT false,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ
);

-- New table: software_rentals
CREATE TABLE software_rentals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    rental_number VARCHAR(20) UNIQUE NOT NULL,
    customer_id UUID REFERENCES users.id NOT NULL,
    software_service_id UUID REFERENCES software_services(id) NOT NULL,
    
    -- Rental period
    start_at TIMESTAMPTZ NOT NULL,
    end_at TIMESTAMPTZ NOT NULL,
    actual_access_revoked_at TIMESTAMPTZ,
    
    -- License details
    license_key TEXT,                        -- Encrypted license key
    license_server_url TEXT,                 -- For floating licenses
    api_key_hash VARCHAR(255),              -- For API access
    access_credentials JSONB,               -- Encrypted credentials
    
    -- Pricing
    rental_fee NUMERIC(12,2) NOT NULL,
    security_deposit_amount NUMERIC(12,2) DEFAULT 0,
    currency VARCHAR(3) DEFAULT 'INR',
    
    -- Usage tracking
    usage_metric VARCHAR(50),               -- e.g., "api_calls", "storage_gb", "compute_hours"
    usage_limit NUMERIC(12,2),              -- Max allowed usage
    usage_current NUMERIC(12,2) DEFAULT 0,  -- Current usage
    
    -- Status
    status ENUM DEFAULT 'pending',          -- pending, active, suspended, expired, cancelled
    
    -- Access management
    provisioned_at TIMESTAMPTZ,
    access_granted_at TIMESTAMPTZ,
    access_revoked_at TIMESTAMPTZ,
    
    -- Relations
    quotation_id UUID REFERENCES quotations(id),
    invoice_id UUID REFERENCES invoices(id),
    
    created_by UUID REFERENCES users.id NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ
);

-- New table: software_usage_logs
CREATE TABLE software_usage_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    software_rental_id UUID REFERENCES software_rentals(id) NOT NULL,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    metric_type VARCHAR(50) NOT NULL,       -- api_call, storage_read, compute_second
    quantity NUMERIC(12,2) NOT NULL,
    metadata JSONB DEFAULT '{}'
);
```

### 10.3 Software Service API Endpoints (Backend Addition)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/software-services/` | List all software services |
| POST | `/api/v1/software-services/` | Create software service (admin) |
| GET | `/api/v1/software-services/{id}` | Get software service detail |
| PUT | `/api/v1/software-services/{id}` | Update software service (admin) |
| DELETE | `/api/v1/software-services/{id}` | Archive software service (admin) |
| GET | `/api/v1/software-services/{id}/availability` | Check license availability |
| POST | `/api/v1/software-rentals/` | Rent a software service |
| GET | `/api/v1/software-rentals/` | List software rentals |
| GET | `/api/v1/software-rentals/{id}` | Get software rental detail |
| POST | `/api/v1/software-rentals/{id}/activate` | Activate license |
| POST | `/api/v1/software-rentals/{id}/deactivate` | Revoke access |
| GET | `/api/v1/software-rentals/{id}/usage` | Get usage metrics |
| POST | `/api/v1/software-rentals/{id}/usage` | Log usage (for API services) |

---

## 11. Integration Plan

### 11.1 Phase 1: API Client Layer (Frontend)

Create `lib/api.ts` — a typed API client that replaces Zustand mock calls:

```typescript
// lib/api.ts
const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

class ApiClient {
  private token: string | null = null;

  setToken(token: string) { this.token = token; }

  private async request<T>(method: string, path: string, body?: any): Promise<T> {
    const headers: Record<string, string> = { 'Content-Type': 'application/json' };
    if (this.token) headers['Authorization'] = `Bearer ${this.token}`;
    
    const res = await fetch(`${API_BASE}${path}`, {
      method, headers, body: body ? JSON.stringify(body) : undefined,
    });
    
    if (!res.ok) throw new ApiError(res.status, await res.json());
    return res.json();
  }

  // Auth
  login(data: LoginRequest) { return this.request<TokenResponse>('POST', '/auth/login', data); }
  register(data: RegisterRequest) { return this.request<TokenResponse>('POST', '/auth/register', data); }
  
  // Products
  getProducts(params?: ProductListParams) { return this.request<PaginatedResponse<Product>>('GET', `/products/?${new URLSearchParams(params)}`); }
  getProduct(id: string) { return this.request<Product>('GET', `/products/${id}`); }
  
  // Rentals
  getRentals(params?: RentalListParams) { return this.request<PaginatedResponse<Rental>>('GET', `/rentals/?${new URLSearchParams(params)}`); }
  createRental(data: RentalCreate) { return this.request<Rental>('POST', '/rentals/', data); }
  
  // ... all other endpoints
}

export const api = new ApiClient();
```

### 11.2 Phase 2: React Query Hooks

Replace Zustand store with React Query hooks:

```typescript
// hooks/useProducts.ts
import { useQuery } from '@tanstack/react-query';
import { api } from '@/lib/api';

export function useProducts(params?: ProductListParams) {
  return useQuery({
    queryKey: ['products', params],
    queryFn: () => api.getProducts(params),
  });
}

export function useProduct(id: string) {
  return useQuery({
    queryKey: ['product', id],
    queryFn: () => api.getProduct(id),
    enabled: !!id,
  });
}
```

### 11.3 Phase 3: Auth Integration

Replace mock auth with real JWT flow:

1. Login page → `POST /auth/login` → store tokens in httpOnly cookies
2. AppShell auth gate → validate token, fetch `/users/me`
3. Token refresh → intercept 401, call `POST /auth/refresh`
4. Logout → `POST /auth/logout`, clear cookies

### 11.4 Phase 4: Page-by-Page Integration

| Priority | Pages | Backend Endpoints | Effort |
|----------|-------|-------------------|--------|
| **P0** | Login, Register, Catalog, Product Detail | Auth, Products, Categories | 2 days |
| **P0** | Checkout wizard, Customer Rentals | Rentals, Deposits | 2 days |
| **P1** | Customer Dashboard, Invoices, Payments | Dashboard, Invoices, Deposits | 1 day |
| **P1** | Admin Dashboard, Admin Rentals, Inventory | Admin, Products, Rentals | 2 days |
| **P1** | Notifications, Profile | Notifications, Users | 1 day |
| **P2** | Groups, Enterprise, Disputes | Groups, Enterprise, Disputes | 2 days |
| **P2** | Agent tasks, Inspection, QR Scanner | Rentals, Custody | 2 days |
| **P3** | Financials, CRM, Stock, Loyalty | Dashboard, CRM, Stock, Loyalty | 2 days |

### 11.5 Phase 5: Software Services

1. Add software service models to backend (see Section 10.2)
2. Add software service API endpoints (see Section 10.3)
3. Create `/catalog?type=software` frontend filter
4. Create `/product/[id]?type=software` software detail view
5. Add license key display and access management UI

---

## 12. Priority Action Items

### Immediate (This Sprint)

| # | Task | Owner | Files Affected | Est. |
|---|------|-------|----------------|------|
| 1 | Create `lib/api.ts` API client | Frontend | New file | 4h |
| 2 | Add `NEXT_PUBLIC_API_URL` env var | Frontend | `.env.local` | 5min |
| 3 | Wire Login page to `POST /auth/login` | Frontend | `app/login/page.tsx` | 2h |
| 4 | Wire Register page to `POST /auth/register` | Frontend | `app/register/page.tsx` | 2h |
| 5 | Wire Catalog to `GET /products/` | Frontend | `app/catalog/page.tsx` | 2h |
| 6 | Wire Product Detail to `GET /products/{id}` | Frontend | `app/product/[id]/page.tsx` | 2h |
| 7 | Wire Checkout to `POST /rentals/` | Frontend | `app/product/[id]/page.tsx` | 3h |
| 8 | Add CORS `http://localhost:3000` to backend | Backend | `app/config.py` | 5min |
| 9 | Create software service models | Backend | New model files | 4h |
| 10 | Create software service endpoints | Backend | New API files | 4h |

### Next Sprint

| # | Task | Owner | Files Affected | Est. |
|---|------|-------|----------------|------|
| 11 | Wire all Customer portal pages | Frontend | 10 page files | 8h |
| 12 | Wire all Admin portal pages | Frontend | 8 page files | 8h |
| 13 | Wire Enterprise portal pages | Frontend | 6 page files | 4h |
| 14 | Wire Group portal pages | Frontend | 3 page files | 3h |
| 15 | Wire Agent portal pages | Frontend | 5 page files | 4h |
| 16 | Add search endpoint | Backend | New endpoint | 2h |
| 17 | Add agent task endpoints | Backend | New model + endpoints | 4h |
| 18 | Add inspection endpoint | Backend | New endpoint | 2h |
| 19 | WebSocket integration | Both | Frontend + Backend | 4h |
| 20 | Software service catalog UI | Frontend | New pages | 4h |

---

## Appendix A: Backend Config — CORS

Backend must allow frontend origin. Current config:

```python
# app/config.py
ALLOWED_ORIGINS: list[str] = ["http://localhost:3000"]
```

Already configured correctly for local development.

## Appendix B: Frontend Environment Variables Needed

```env
# .env.local (frontend)
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws
NEXT_PUBLIC_APP_NAME=Reprico
```

## Appendix C: Role Name Mapping

| Frontend Role | Backend Role | Mapping |
|---------------|-------------|---------|
| `customer` | `portal_user` | Map on login |
| `admin` | `super_admin` or `ops_admin` | Map on login |
| `field_agent` | `field_agent` | Direct match |
| `enterprise_admin` | `portal_user` (with enterprise_id) | Check enterprise_id |
| `group_leader` | `portal_user` (with group context) | Check group membership |

## Appendix D: Status Enum Mapping

| Entity | Frontend Status | Backend Status | Mapping |
|--------|----------------|----------------|---------|
| Rental | `PENDING` | `pending` | Lowercase |
| Rental | `CONFIRMED` | `confirmed` | Lowercase |
| Rental | `ACTIVE` | `active` | Lowercase |
| Rental | `OVERDUE` | `overdue` | Lowercase |
| Rental | `INSPECTION` | — | Map to `returned` |
| Rental | `COMPLETED` | — | Map to `returned` |
| Rental | `DISPUTED` | — | Map to `active` + dispute flag |
| Rental | `CANCELLED` | `cancelled` | Lowercase |
| Product | `AVAILABLE` | `available` | Lowercase |
| Product | `RENTED` | `rented` | Lowercase |
| Product | `MAINTENANCE` | `in_repair` | Different name |
| Product | `RESERVED` | — | Map to `available` |
| Product | `DAMAGED` | — | Map to `in_repair` |
| KYC | `verified` | `verified` | Direct match |
| KYC | `pending` | `pending` | Direct match |
| KYC | `rejected` | `rejected` | Direct match |
| KYC | `unverified` | `pending` | Map to pending |

---

*Document generated: August 9, 2026*
*Backend: 68 endpoints | 44 models | 16 services*
*Frontend: 33 pages | 14 components | 22 TypeScript interfaces*
*Integration Status: 0% → Target 100%*
