# DATABASE SCHEMA
## Rental Management System — Complete Multi-DB Design
### Version 3.0 | 2026 | FINAL

---

## Table of Contents

1. [Multi-Database Architecture](#1-multi-database-architecture)
2. [Core Tables — Users & Auth](#2-core-tables--users--auth)
3. [Enterprise & Group Tables](#3-enterprise--group-tables)
4. [Product & Inventory Tables](#4-product--inventory-tables)
5. [Availability Engine Tables](#5-availability-engine-tables)
6. [Rental & Order Tables](#6-rental--order-tables)
7. [Quotes & Invoicing Tables](#7-quotes--invoicing-tables)
8. [Financial & Deposit Tables](#8-financial--deposit-tables)
9. [Chain of Custody Tables](#9-chain-of-custody-tables)
10. [CRM & Customer Management Tables](#10-crm--customer-management-tables)
11. [Stock Management Tables](#11-stock-management-tables)
12. [Loyalty Points & Referral Tables](#12-loyalty-points--referral-tables)
13. [Notification & Audit Tables](#13-notification--audit-tables)
14. [Indexing Strategy](#14-indexing-strategy)
15. [Materialized Views](#15-materialized-views)
16. [Partitioning Strategy](#16-partitioning-strategy)
17. [Connection Pooling & Clustering](#17-connection-pooling--clustering)

---

## 1. Multi-Database Architecture

| Database | Purpose | Technology | Free Tier |
|----------|---------|------------|-----------|
| **Primary DB** | All operational data | PostgreSQL 16 on NeonDB | 0.5 GB, 1 compute unit |
| **Cache DB** | Sessions, rate limits, OTPs, pub/sub | Redis (Upstash) | 10,000 commands/day |
| **Search Index** | Full-text search | PostgreSQL FTS (built-in) | Included |
| **Audit Log DB** | Immutable audit trail | Separate PostgreSQL schema (audit.*) | Included |
| **Analytics DB** | Pre-computed aggregates | PostgreSQL materialized views | Included |
| **File Storage** | KYC docs, photos, invoices | Cloudflare R2 | 10 GB, zero egress |

### Schema Separation

```
NeonDB PostgreSQL Instance
├── public (operational schema)
│   ├── users, enterprises, groups
│   ├── products, categories, accessories
│   ├── rentals, quotations, invoices
│   ├── security_deposits, late_fees
│   ├── availability_blocks, blackout_dates
│   ├── crm_contacts, crm_interactions, crm_tags
│   ├── stock_movements, stock_adjustments
│   ├── loyalty_points, referrals
│   └── ... all operational tables
├── audit (immutable schema)
│   ├── audit_logs
│   └── rate_limit_events
├── analytics (aggregated schema)
│   ├── mv_admin_dashboard
│   ├── mv_revenue_daily
│   ├── mv_customer_lifetime_value
│   ├── mv_product_utilization
│   ├── mv_crm_lead_scores
│   └── ... materialized views
└── archive (historical schema)
    ├── archived_rentals
    └── archived_invoices
```

---

## 2. Core Tables — Users & Auth

### Table: users

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY, DEFAULT gen_random_uuid() | Unique user identifier |
| user_type | ENUM | NOT NULL, DEFAULT 'personal' | personal, enterprise, enterprise_sub |
| role | ENUM | NOT NULL | super_admin, ops_admin, field_agent, portal_user |
| phone | VARCHAR(15) | UNIQUE, NOT NULL | Primary login identifier |
| email | VARCHAR(255) | UNIQUE, NOT NULL | Secondary login identifier |
| password_hash | VARCHAR(255) | NULLABLE | NULL if OTP-only login |
| name | VARCHAR(255) | NOT NULL | Full name |
| dob | DATE | NULLABLE | Date of birth |
| profile_photo_url | TEXT | NULLABLE | Cloudflare R2 URL |
| kyc_status | ENUM | DEFAULT 'pending' | pending, in_progress, verified, rejected |
| kyc_completed_at | TIMESTAMPTZ | NULLABLE | When KYC fully verified |
| trust_score | SMALLINT | DEFAULT 0, CHECK (0 <= trust_score <= 100) | Dynamic trust score |
| trust_tier | ENUM | GENERATED ALWAYS AS | unverified, basic, standard, trusted, vip |
| enterprise_id | UUID | FK -> enterprises.id, NULLABLE | For enterprise sub-users |
| blacklisted | BOOLEAN | DEFAULT false | Blacklist flag |
| blacklisted_at | TIMESTAMPTZ | NULLABLE | When blacklisted |
| blacklisted_by | UUID | FK -> users.id, NULLABLE | Super Admin who blacklisted |
| blacklist_reason | TEXT | NULLABLE | Reason for blacklisting |
| device_fingerprints | TEXT[] | DEFAULT '{}' | Array of known device IDs |
| notification_preferences | JSONB | DEFAULT '{"sms":true,"email":true,"push":true}' | Per-channel opt-in/out |
| points_balance | INTEGER | DEFAULT 0 | Loyalty points |
| lifetime_rentals | INTEGER | DEFAULT 0 | Total rentals completed |
| lifetime_spend | NUMERIC(12,2) | DEFAULT 0 | Total amount spent |
| last_rental_at | TIMESTAMPTZ | NULLABLE | Date of last rental |
| referral_code | VARCHAR(20) | UNIQUE, NULLABLE | Personal referral code |
| referred_by | UUID | FK -> users.id, NULLABLE | Who referred this user |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | Account creation timestamp |
| updated_at | TIMESTAMPTZ | | Auto-updated via trigger |

**Generated Column — trust_tier:**
```sql
CREATE TYPE trust_tier_enum AS ENUM ('unverified','basic','standard','trusted','vip');

ALTER TABLE users ADD COLUMN trust_tier trust_tier_enum
  GENERATED ALWAYS AS (
    CASE
      WHEN trust_score >= 85 THEN 'vip'::trust_tier_enum
      WHEN trust_score >= 70 THEN 'trusted'::trust_tier_enum
      WHEN trust_score >= 50 THEN 'standard'::trust_tier_enum
      WHEN trust_score >= 30 THEN 'basic'::trust_tier_enum
      ELSE 'unverified'::trust_tier_enum
    END
  ) STORED;
```

### Table: refresh_tokens

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | |
| user_id | UUID | FK -> users.id ON DELETE CASCADE | |
| token_hash | VARCHAR(255) | NOT NULL | SHA-256 hash of opaque token |
| device_fingerprint | TEXT | NOT NULL | Browser/device identifier |
| user_agent | TEXT | NULLABLE | Client user agent string |
| ip_address | INET | NULLABLE | IP at token creation |
| expires_at | TIMESTAMPTZ | NOT NULL | 30 days from creation |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | |
| revoked_at | TIMESTAMPTZ | NULLABLE | Set on rotation/logout |

### Table: otp_tokens

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | |
| identifier | VARCHAR(255) | NOT NULL | Phone number or email |
| channel | ENUM | NOT NULL | sms, email |
| code | VARCHAR(6) | NOT NULL | 6-digit OTP |
| purpose | ENUM | NOT NULL | login, register, kyc, transaction, extension |
| attempts | SMALLINT | DEFAULT 0 | Max 3 attempts |
| expires_at | TIMESTAMPTZ | NOT NULL | 5 minutes from creation |
| verified_at | TIMESTAMPTZ | NULLABLE | When verified |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | |

### Table: kyc_records

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | |
| user_id | UUID | FK -> users.id ON DELETE CASCADE | |
| step | ENUM | NOT NULL | phone, email, gov_id, selfie, address, payment, device |
| id_type | ENUM | NULLABLE | aadhaar, pan, passport, driving_licence |
| id_number | VARCHAR(50) | NULLABLE | Encrypted ID number |
| id_doc_url | TEXT | NULLABLE | R2 URL of ID document |
| selfie_url | TEXT | NULLABLE | R2 URL of selfie |
| liveness_video_url | TEXT | NULLABLE | R2 URL of liveness video |
| face_match_score | NUMERIC(5,2) | NULLABLE | AI face match percentage |
| liveness_passed | BOOLEAN | NULLABLE | Liveness check result |
| address_doc_url | TEXT | NULLABLE | R2 URL of address proof |
| address_verified | BOOLEAN | NULLABLE | Address match result |
| payment_method_token | VARCHAR(255) | NULLABLE | Razorpay tokenized card |
| payment_method_last4 | VARCHAR(4) | NULLABLE | Last 4 digits of card |
| payment_method_type | ENUM | NULLABLE | credit, debit |
| device_fingerprint | TEXT | NULLABLE | Device ID at KYC |
| status | ENUM | DEFAULT 'pending' | pending, approved, rejected, manual_review |
| rejection_reason | TEXT | NULLABLE | Reason if rejected |
| reviewed_by | UUID | FK -> users.id, NULLABLE | Admin who reviewed |
| reviewed_at | TIMESTAMPTZ | NULLABLE | When reviewed |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | |

### Table: trust_score_history

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | |
| user_id | UUID | FK -> users.id ON DELETE CASCADE | |
| previous_score | SMALLINT | NOT NULL | Score before change |
| new_score | SMALLINT | NOT NULL | Score after change |
| change_amount | SMALLINT | NOT NULL | +/- points |
| reason | VARCHAR(100) | NOT NULL | rental_complete, late_return, damage, dispute_won, etc. |
| reference_id | UUID | NULLABLE | rental_id, dispute_id, etc. |
| reference_type | VARCHAR(50) | NULLABLE | rental, dispute, kyc, etc. |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | |

---

## 3. Enterprise & Group Tables

### Table: enterprises

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | |
| name | VARCHAR(255) | NOT NULL | Business entity name |
| legal_entity_type | ENUM | NOT NULL | private_ltd, llp, partnership, proprietorship, ngo |
| gst_number | VARCHAR(20) | UNIQUE | GST registration number |
| pan | VARCHAR(12) | NOT NULL | Business PAN |
| cin | VARCHAR(21) | NULLABLE | Corporate Identity Number |
| registered_address | JSONB | NOT NULL | {street, city, state, pincode, country} |
| office_address | JSONB | NULLABLE | {street, city, state, pincode, country} |
| contact_person_name | VARCHAR(255) | NOT NULL | Primary contact |
| contact_person_email | VARCHAR(255) | NOT NULL | |
| contact_person_phone | VARCHAR(15) | NOT NULL | |
| kyc_status | ENUM | DEFAULT 'pending' | pending, in_progress, verified, rejected |
| kyc_verified_at | TIMESTAMPTZ | NULLABLE | |
| trust_score | SMALLINT | DEFAULT 0 | Entity-level trust |
| credit_line_enabled | BOOLEAN | DEFAULT false | Net-30 billing enabled |
| credit_limit_inr | NUMERIC(12,2) | NULL | Max credit amount |
| credit_used_inr | NUMERIC(12,2) | DEFAULT 0 | Current credit usage |
| credit_days | INTEGER | DEFAULT 30 | Payment terms (days) |
| pricelist_id | UUID | FK -> pricelists.id, NULLABLE | Custom enterprise pricing |
| account_manager_id | UUID | FK -> users.id, NULLABLE | Assigned ops_admin |
| total_rentals | INTEGER | DEFAULT 0 | Lifetime rental count |
| total_spend | NUMERIC(14,2) | DEFAULT 0 | Lifetime spend |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | | |

### Table: enterprise_members

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | |
| enterprise_id | UUID | FK -> enterprises.id ON DELETE CASCADE | |
| user_id | UUID | FK -> users.id UNIQUE | One user = one enterprise membership |
| sub_role | ENUM | NOT NULL | admin, procurement, department_user, auditor |
| department | VARCHAR(100) | NULLABLE | e.g., Marketing, IT, Operations |
| designation | VARCHAR(100) | NULLABLE | Job title |
| spending_limit_inr | NUMERIC(12,2) | NULL | Max rental value per order |
| monthly_limit_inr | NUMERIC(12,2) | NULL | Max monthly spend |
| current_month_spend | NUMERIC(12,2) | DEFAULT 0 | Reset monthly |
| can_approve_rentals | BOOLEAN | DEFAULT false | For procurement/admin roles |
| invited_by | UUID | FK -> users.id | Who invited this member |
| invited_at | TIMESTAMPTZ | DEFAULT NOW() | |
| accepted_at | TIMESTAMPTZ | NULLABLE | When invite accepted |

### Table: enterprise_credit_transactions

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | |
| enterprise_id | UUID | FK -> enterprises.id | |
| type | ENUM | NOT NULL | credit_used, credit_paid, credit_adjusted, credit_expired |
| amount | NUMERIC(12,2) | NOT NULL | Transaction amount |
| invoice_id | UUID | FK -> invoices.id, NULLABLE | Related invoice |
| reference | TEXT | NULLABLE | Payment reference |
| created_by | UUID | FK -> users.id | Admin who recorded |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | |

### Table: groups

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | |
| name | VARCHAR(255) | NOT NULL | Group name |
| description | TEXT | NULLABLE | Optional description |
| leader_id | UUID | FK -> users.id NOT NULL | Group Leader |
| trust_score | NUMERIC(5,2) | | Weighted avg of member scores |
| trust_tier | ENUM | GENERATED | unverified, basic, standard, trusted, vip |
| status | ENUM | DEFAULT 'active' | active, dissolved, suspended |
| max_members | SMALLINT | DEFAULT 20, CHECK (max_members <= 20) | |
| current_member_count | SMALLINT | DEFAULT 1 | Cached count |
| joint_liability | BOOLEAN | DEFAULT true | Joint and several liability |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | |
| dissolved_at | TIMESTAMPTZ | NULLABLE | |

### Table: group_members

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | |
| group_id | UUID | FK -> groups.id ON DELETE CASCADE | |
| user_id | UUID | FK -> users.id | |
| role | ENUM | DEFAULT 'member' | leader, member |
| status | ENUM | DEFAULT 'invited' | invited, active, removed |
| deposit_share_pct | NUMERIC(5,2) | DEFAULT 0 | Percentage of group deposit |
| deposit_share_amount | NUMERIC(12,2) | DEFAULT 0 | Calculated amount |
| trust_score_at_join | SMALLINT | NOT NULL | Score when joined |
| joined_at | TIMESTAMPTZ | | |
| removed_at | TIMESTAMPTZ | NULLABLE | |
| removed_by | UUID | FK -> users.id, NULLABLE | |
| UNIQUE(group_id, user_id) | | | |

### Table: group_deposits

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | |
| rental_id | UUID | FK -> rentals.id UNIQUE | One deposit per rental |
| group_id | UUID | FK -> groups.id | |
| total_amount | NUMERIC(12,2) | NOT NULL | Total deposit required |
| total_collected | NUMERIC(12,2) | DEFAULT 0 | Amount collected so far |
| status | ENUM | DEFAULT 'pending' | pending, collecting, held, settled, forfeited |
| settled_at | TIMESTAMPTZ | NULLABLE | |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | |

### Table: group_deposit_members

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | |
| group_deposit_id | UUID | FK -> group_deposits.id ON DELETE CASCADE | |
| user_id | UUID | FK -> users.id | |
| amount | NUMERIC(12,2) | NOT NULL | This member's deposit share |
| payment_status | ENUM | DEFAULT 'pending' | pending, authorized, failed, released, forfeited |
| authorization_code | VARCHAR(255) | NULLABLE | Razorpay auth hold reference |
| refund_amount | NUMERIC(12,2) | NULL | Amount refunded |
| refund_at | TIMESTAMPTZ | NULLABLE | |
| paid_at | TIMESTAMPTZ | NULLABLE | |
| UNIQUE(group_deposit_id, user_id) | | | |

### Table: group_votes

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | |
| group_id | UUID | FK -> groups.id | |
| rental_id | UUID | FK -> rentals.id, NULLABLE | Related rental |
| vote_type | ENUM | NOT NULL | extension, dispute, dissolve |
| requested_by | UUID | FK -> users.id | Who initiated |
| reason | TEXT | NULLABLE | Reason for request |
| status | ENUM | DEFAULT 'pending' | pending, approved, rejected, expired |
| votes_for | SMALLINT | DEFAULT 0 | Cached count |
| votes_against | SMALLINT | DEFAULT 0 | Cached count |
| expires_at | TIMESTAMPTZ | NOT NULL | 24 hours from request |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | |
| resolved_at | TIMESTAMPTZ | NULLABLE | |

### Table: group_vote_records

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | |
| vote_id | UUID | FK -> group_votes.id ON DELETE CASCADE | |
| user_id | UUID | FK -> users.id | |
| vote | ENUM | NOT NULL | approve, reject |
| voted_at | TIMESTAMPTZ | DEFAULT NOW() | |
| UNIQUE(vote_id, user_id) | | | |

---

## 4. Product & Inventory Tables

### Table: categories

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | |
| name | VARCHAR(100) | UNIQUE NOT NULL | e.g., Cameras, Bikes |
| slug | VARCHAR(100) | UNIQUE NOT NULL | URL-friendly name |
| description | TEXT | NULLABLE | |
| parent_id | UUID | FK -> categories.id, NULLABLE | Nested categories |
| icon_url | TEXT | NULLABLE | Category icon |
| deposit_percentage_override | NUMERIC(5,2) | NULL | Overrides product default |
| late_fee_rate_override | NUMERIC(10,2) | NULL | Overrides product default |
| is_active | BOOLEAN | DEFAULT true | |
| sort_order | INTEGER | DEFAULT 0 | Display order |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | |

### Table: products

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | |
| name | VARCHAR(255) | NOT NULL | Product name |
| slug | VARCHAR(255) | UNIQUE NOT NULL | URL-friendly name |
| category_id | UUID | FK -> categories.id NOT NULL | |
| description | TEXT | NULLABLE | |
| short_description | VARCHAR(500) | NULLABLE | For catalog cards |
| serial_number | VARCHAR(100) | UNIQUE | Manufacturer serial |
| qr_code | VARCHAR(255) | UNIQUE | Generated unique QR |
| rfid_tag | VARCHAR(100) | NULLABLE | For IoT-enabled products |
| barcode | VARCHAR(100) | NULLABLE | Secondary identifier |
| sku | VARCHAR(100) | UNIQUE | Stock Keeping Unit |
| status | ENUM | DEFAULT 'available' | available, rented, in_repair, inactive, archived |
| current_holder_id | UUID | FK -> users.id, NULLABLE | Who has it now |
| current_rental_id | UUID | FK -> rentals.id, NULLABLE | Active rental |
| condition_rating | SMALLINT | DEFAULT 5, CHECK (1 <= condition_rating <= 5) | 1=poor, 5=excellent |
| condition_notes | TEXT | NULLABLE | Latest condition description |
| purchase_date | DATE | NULLABLE | When purchased |
| purchase_price | NUMERIC(12,2) | NULL | Original purchase cost |
| current_value | NUMERIC(12,2) | NULL | Depreciated value |
| depreciation_rate | NUMERIC(5,2) | DEFAULT 0 | % per month |
| insurance_expiry | DATE | NULLABLE | Insurance end date |
| warranty_expiry | DATE | NULLABLE | Warranty end date |
| location | VARCHAR(255) | NULLABLE | Current storage location |
| is_insured | BOOLEAN | DEFAULT false | |
| deposit_percentage | NUMERIC(5,2) | DEFAULT 30.00 | Can be overridden by pricelist |
| late_fee_rate | NUMERIC(10,2) | NULL | Per day |
| late_fee_mode | ENUM | DEFAULT 'daily' | hourly, daily, weekly, monthly |
| grace_period_minutes | INTEGER | DEFAULT 30 | |
| max_late_fee_multiplier | NUMERIC(3,1) | DEFAULT 2.0 | Max 2x rental value |
| min_rental_duration | INTEGER | DEFAULT 1 | Minimum rental units |
| max_rental_duration | INTEGER | NULLABLE | Maximum rental units (NULL = unlimited) |
| images | TEXT[] | DEFAULT '{}' | Array of R2 URLs |
| thumbnail_url | TEXT | NULLABLE | Primary image for catalog |
| tags | TEXT[] | DEFAULT '{}' | Searchable tags |
| metadata | JSONB | DEFAULT '{}' | Custom attributes (brand, model, color, size) |
| total_rentals | INTEGER | DEFAULT 0 | Lifetime rental count |
| total_revenue | NUMERIC(14,2) | DEFAULT 0 | Lifetime revenue |
| total_damage_reports | INTEGER | DEFAULT 0 | |
| is_featured | BOOLEAN | DEFAULT false | |
| sort_order | INTEGER | DEFAULT 0 | |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | | |

### Table: product_variants

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | |
| product_id | UUID | FK -> products.id ON DELETE CASCADE | |
| attribute | VARCHAR(50) | NOT NULL | e.g., color, size, brand, model |
| value | VARCHAR(100) | NOT NULL | e.g., Red, Large, Canon |
| sku | VARCHAR(100) | UNIQUE | Stock keeping unit |
| additional_price_inr | NUMERIC(10,2) | DEFAULT 0 | Price adjustment |
| is_default | BOOLEAN | DEFAULT false | Default selection |

### Table: accessories (Bill of Materials)

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | |
| product_id | UUID | FK -> products.id ON DELETE CASCADE | |
| name | VARCHAR(255) | NOT NULL | Accessory name |
| item_code | VARCHAR(100) | NOT NULL | Unique per product |
| description | TEXT | NULLABLE | |
| replacement_cost_inr | NUMERIC(10,2) | NOT NULL | Cost if missing at return |
| is_required | BOOLEAN | DEFAULT true | Must leave and return |
| condition_rating | SMALLINT | DEFAULT 5 | Expected condition |
| image_url | TEXT | NULLABLE | Photo of accessory |
| UNIQUE(product_id, item_code) | | | |

---

## 5. Availability Engine Tables

### Table: availability_blocks

Core table for tracking when products are available, booked, or blocked.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | |
| product_id | UUID | FK -> products.id NOT NULL | |
| block_type | ENUM | NOT NULL | rental, maintenance, reservation, blackout |
| rental_id | UUID | FK -> rentals.id, NULLABLE | For rental blocks |
| start_at | TIMESTAMPTZ | NOT NULL | Block start |
| end_at | TIMESTAMPTZ | NOT NULL | Block end |
| status | ENUM | DEFAULT 'active' | active, cancelled, completed |
| booked_by | UUID | FK -> users.id, NULLABLE | Who booked |
| notes | TEXT | NULLABLE | |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | |

**Composite Index:** `idx_availability_product_start` ON (product_id, start_at, end_at)

### Table: blackout_dates

Admin-configured dates when products cannot be rented.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | |
| product_id | UUID | FK -> products.id, NULLABLE | NULL = applies to all products |
| category_id | UUID | FK -> categories.id, NULLABLE | NULL = not category-wide |
| start_date | DATE | NOT NULL | |
| end_date | DATE | NOT NULL | |
| reason | VARCHAR(255) | NOT NULL | e.g., "Annual maintenance", "Holiday closure" |
| created_by | UUID | FK -> users.id | Admin who set blackout |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | |

### Table: reservations

Temporary holds on products before confirmation.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | |
| product_id | UUID | FK -> products.id NOT NULL | |
| user_id | UUID | FK -> users.id NOT NULL | |
| start_at | TIMESTAMPTZ | NOT NULL | Requested start |
| end_at | TIMESTAMPTZ | NOT NULL | Requested end |
| status | ENUM | DEFAULT 'pending' | pending, confirmed, expired, cancelled |
| expires_at | TIMESTAMPTZ | NOT NULL | Auto-expire (15 min default) |
| quotation_id | UUID | FK -> quotations.id, NULLABLE | Linked quote if applicable |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | |

**Note:** Redis TTL key `reservation:{product_id}:{user_id}` auto-expires after 15 minutes.

### Table: availability_calendar (Materialized View Helper)

Pre-computed daily availability for fast catalog display.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | |
| product_id | UUID | FK -> products.id NOT NULL | |
| date | DATE | NOT NULL | Calendar day |
| available_count | INTEGER | NOT NULL | Units available this day |
| total_count | INTEGER | NOT NULL | Total units in inventory |
| is_available | BOOLEAN | GENERATED ALWAYS AS (available_count > 0) | |
| UNIQUE(product_id, date) | | | |

---

## 6. Rental & Order Tables

### Table: rentals

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | |
| rental_number | VARCHAR(20) | UNIQUE NOT NULL | Sequential: RNT-2026-00001 |
| user_id | UUID | FK -> users.id, NULLABLE | NULL if group rental |
| group_id | UUID | FK -> groups.id, NULLABLE | NULL if personal/enterprise |
| enterprise_id | UUID | FK -> enterprises.id, NULLABLE | NULL if personal |
| rental_context | ENUM | NOT NULL | personal, enterprise, group |
| product_id | UUID | FK -> products.id NOT NULL | |
| status | ENUM | DEFAULT 'draft' | draft, confirmed, active, returned, overdue, cancelled, completed |
| start_at | TIMESTAMPTZ | NOT NULL | |
| end_at | TIMESTAMPTZ | NOT NULL | |
| actual_return_at | TIMESTAMPTZ | NULLABLE | |
| rental_fee | NUMERIC(12,2) | NOT NULL | Total rental cost |
| security_deposit_amount | NUMERIC(12,2) | NOT NULL | Deposit required |
| delivery_method | ENUM | NOT NULL | home_delivery, store_pickup |
| delivery_address | JSONB | NULLABLE | {street, city, state, pincode} |
| delivery_fee | NUMERIC(10,2) | DEFAULT 0 | |
| delivery_scheduled_at | TIMESTAMPTZ | NULLABLE | |
| pickup_scheduled_at | TIMESTAMPTZ | NULLABLE | For store pickup |
| agreement_signed_at | TIMESTAMPTZ | NULLABLE | |
| agreement_pdf_url | TEXT | NULLABLE | R2 URL |
| notes | TEXT | NULLABLE | Customer or admin notes |
| cancellation_reason | TEXT | NULLABLE | If cancelled |
| cancelled_at | TIMESTAMPTZ | NULLABLE | |
| cancelled_by | UUID | FK -> users.id, NULLABLE | |
| created_by | UUID | FK -> users.id NOT NULL | Admin or customer |
| quotation_id | UUID | FK -> quotations.id, NULLABLE | Converted from quote |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | | |

### Table: rental_items

Supports bulk rentals — one rental can have multiple products.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | |
| rental_id | UUID | FK -> rentals.id ON DELETE CASCADE | |
| product_id | UUID | FK -> products.id NOT NULL | |
| quantity | INTEGER | DEFAULT 1 | |
| unit_price | NUMERIC(12,2) | NOT NULL | Price per unit per period |
| rental_duration | INTEGER | NOT NULL | Number of periods |
| duration_unit | ENUM | NOT NULL | hourly, daily, weekly, monthly |
| subtotal | NUMERIC(12,2) | NOT NULL | unit_price * duration * quantity |
| discount_amount | NUMERIC(10,2) | DEFAULT 0 | |
| tax_amount | NUMERIC(10,2) | DEFAULT 0 | |
| total | NUMERIC(12,2) | NOT NULL | |
| condition_at_pickup | TEXT | NULLABLE | |
| condition_at_return | TEXT | NULLABLE | |
| UNIQUE(rental_id, product_id) | | | |

### Table: rental_status_history

Audit trail of every status change.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | |
| rental_id | UUID | FK -> rentals.id ON DELETE CASCADE | |
| from_status | ENUM | NULLABLE | Previous status |
| to_status | ENUM | NOT NULL | New status |
| changed_by | UUID | FK -> users.id | Who changed |
| reason | TEXT | NULLABLE | |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | |

---

## 7. Quotes & Invoicing Tables

### Table: quotation_templates

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | |
| name | VARCHAR(255) | NOT NULL | Template name |
| admin_id | UUID | FK -> users.id NOT NULL | Creator |
| description | TEXT | NULLABLE | |
| header_html | TEXT | NULLABLE | Logo, business name, address |
| footer_html | TEXT | NULLABLE | Terms, signature line |
| default_notes | TEXT | NULLABLE | Pre-filled notes |
| default_rental_period | JSONB | NULLABLE | {duration, unit} |
| default_deposit_pct | NUMERIC(5,2) | NULL | |
| is_active | BOOLEAN | DEFAULT true | |
| usage_count | INTEGER | DEFAULT 0 | How many times used |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | | |

### Table: quotations

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | |
| quote_number | VARCHAR(20) | UNIQUE NOT NULL | QUO-2026-00001 |
| admin_id | UUID | FK -> users.id, NULLABLE | Created by admin (walk-in) |
| customer_id | UUID | FK -> users.id NOT NULL | |
| product_id | UUID | FK -> products.id NOT NULL | |
| rental_period | JSONB | NOT NULL | {duration: 7, unit: "daily"} |
| base_price | NUMERIC(12,2) | NOT NULL | Standard price |
| quoted_price | NUMERIC(12,2) | NOT NULL | Negotiated/discounted price |
| discount_percent | NUMERIC(5,2) | DEFAULT 0 | |
| discount_amount | NUMERIC(10,2) | DEFAULT 0 | |
| deposit_amount | NUMERIC(12,2) | NOT NULL | |
| delivery_fee | NUMERIC(10,2) | DEFAULT 0 | |
| tax_amount | NUMERIC(10,2) | DEFAULT 0 | |
| total_amount | NUMERIC(12,2) | NOT NULL | Grand total |
| currency | VARCHAR(3) | DEFAULT 'INR' | |
| status | ENUM | DEFAULT 'draft' | draft, sent, viewed, accepted, rejected, confirmed, expired, cancelled |
| template_id | UUID | FK -> quotation_templates.id, NULLABLE | |
| custom_notes | TEXT | NULLABLE | |
| terms_and_conditions | TEXT | NULLABLE | |
| valid_until | TIMESTAMPTZ | NOT NULL | Default 24 hours |
| sent_at | TIMESTAMPTZ | NULLABLE | |
| viewed_at | TIMESTAMPTZ | NULLABLE | Customer opened |
| accepted_at | TIMESTAMPTZ | NULLABLE | |
| rejected_at | TIMESTAMPTZ | NULLABLE | |
| rejection_reason | TEXT | NULLABLE | |
| converted_to_rental_id | UUID | FK -> rentals.id, NULLABLE | |
| converted_to_invoice_id | UUID | FK -> invoices.id, NULLABLE | |
| share_token | VARCHAR(64) | UNIQUE | Public link token |
| pdf_url | TEXT | NULLABLE | R2 URL |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | | |

### Table: quotation_items

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | |
| quotation_id | UUID | FK -> quotations.id ON DELETE CASCADE | |
| product_id | UUID | FK -> products.id NOT NULL | |
| quantity | INTEGER | DEFAULT 1 | |
| unit_price | NUMERIC(12,2) | NOT NULL | |
| duration | INTEGER | NOT NULL | |
| duration_unit | ENUM | NOT NULL | hourly, daily, weekly, monthly |
| subtotal | NUMERIC(12,2) | NOT NULL | |
| discount | NUMERIC(10,2) | DEFAULT 0 | |
| total | NUMERIC(12,2) | NOT NULL | |

### Table: invoices

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | |
| invoice_number | VARCHAR(20) | UNIQUE NOT NULL | INV-2026-00001 |
| rental_id | UUID | FK -> rentals.id, NULLABLE | |
| quotation_id | UUID | FK -> quotations.id, NULLABLE | |
| user_id | UUID | FK -> users.id NOT NULL | |
| enterprise_id | UUID | FK -> enterprises.id, NULLABLE | |
| type | ENUM | NOT NULL | booking, return, penalty, late_fee, credit_note, adjustment |
| status | ENUM | DEFAULT 'draft' | draft, issued, paid, partially_paid, overdue, cancelled, void |
| subtotal | NUMERIC(12,2) | NOT NULL | Before tax |
| discount_total | NUMERIC(10,2) | DEFAULT 0 | |
| tax_rate | NUMERIC(5,2) | DEFAULT 18.00 | GST % |
| tax_amount | NUMERIC(12,2) | NOT NULL | |
| total | NUMERIC(12,2) | NOT NULL | Grand total |
| amount_paid | NUMERIC(12,2) | DEFAULT 0 | |
| balance_due | NUMERIC(12,2) | GENERATED ALWAYS AS (total - amount_paid) STORED | |
| currency | VARCHAR(3) | DEFAULT 'INR' | |
| payment_terms | INTEGER | DEFAULT 0 | Days until due (0 = immediate) |
| due_date | DATE | NULLABLE | |
| paid_at | TIMESTAMPTZ | NULLABLE | |
| payment_method | ENUM | NULLABLE | card, cash, upi, bank_transfer, credit |
| payment_reference | VARCHAR(255) | NULLABLE | Transaction ID |
| gstin | VARCHAR(20) | NULLABLE | Customer GSTIN for B2B |
| billing_address | JSONB | NULLABLE | {name, address, city, state, pincode, phone, email} |
| notes | TEXT | NULLABLE | |
| terms_and_conditions | TEXT | NULLABLE | |
| pdf_url | TEXT | NULLABLE | R2 URL |
| sent_at | TIMESTAMPTZ | NULLABLE | |
| emailed_at | TIMESTAMPTZ | NULLABLE | |
| created_by | UUID | FK -> users.id | |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | | |

### Table: invoice_items

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | |
| invoice_id | UUID | FK -> invoices.id ON DELETE CASCADE | |
| description | VARCHAR(500) | NOT NULL | Line item description |
| quantity | NUMERIC(10,2) | DEFAULT 1 | |
| unit_price | NUMERIC(12,2) | NOT NULL | |
| discount | NUMERIC(10,2) | DEFAULT 0 | |
| tax_rate | NUMERIC(5,2) | DEFAULT 18.00 | |
| tax_amount | NUMERIC(12,2) | NOT NULL | |
| total | NUMERIC(12,2) | NOT NULL | |
| item_type | ENUM | NOT NULL | rental_fee, security_deposit, late_fee, damage_fee, missing_item, delivery, discount, other |
| reference_id | UUID | NULLABLE | late_fee.id, deposit_deduction.id, etc. |
| reference_type | VARCHAR(50) | NULLABLE | late_fee, deposit_deduction, etc. |

### Table: payments

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | |
| payment_number | VARCHAR(20) | UNIQUE NOT NULL | PAY-2026-00001 |
| invoice_id | UUID | FK -> invoices.id, NULLABLE | |
| rental_id | UUID | FK -> rentals.id, NULLABLE | |
| user_id | UUID | FK -> users.id NOT NULL | |
| amount | NUMERIC(12,2) | NOT NULL | |
| method | ENUM | NOT NULL | card, cash, upi, bank_transfer, credit_adjustment |
| status | ENUM | DEFAULT 'pending' | pending, processing, completed, failed, refunded, partially_refunded |
| razorpay_order_id | VARCHAR(255) | NULLABLE | |
| razorpay_payment_id | VARCHAR(255) | NULLABLE | |
| razorpay_signature | VARCHAR(255) | NULLABLE | |
| card_last4 | VARCHAR(4) | NULLABLE | |
| card_network | VARCHAR(20) | NULLABLE | visa, mastercard, rupee, etc. |
| upi_id | VARCHAR(50) | NULLABLE | |
| cash_collected_by | UUID | FK -> users.id, NULLABLE | Admin who collected |
| refund_amount | NUMERIC(12,2) | DEFAULT 0 | |
| refund_reason | TEXT | NULLABLE | |
| refunded_at | TIMESTAMPTZ | NULLABLE | |
| metadata | JSONB | DEFAULT '{}' | Extra payment info |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | | |

---

## 8. Financial & Deposit Tables

### Table: security_deposits

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | |
| rental_id | UUID | FK -> rentals.id NOT NULL | |
| user_id | UUID | FK -> users.id NOT NULL | |
| amount | NUMERIC(12,2) | NOT NULL | Total deposit required |
| payment_mode | ENUM | NOT NULL | card_auth, cash, upi, bank_transfer |
| authorization_code | VARCHAR(255) | NULLABLE | Razorpay auth hold reference |
| status | ENUM | DEFAULT 'held' | held, released, partially_deducted, forfeited |
| refund_amount | NUMERIC(12,2) | NULL | Amount refunded |
| refund_method | ENUM | NULLABLE | original, cash, bank_transfer |
| refund_reference | VARCHAR(255) | NULLABLE | |
| refund_at | TIMESTAMPTZ | NULLABLE | |
| settled_by | UUID | FK -> users.id, NULLABLE | Admin who settled |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | | |

### Table: deposit_deductions

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | |
| deposit_id | UUID | FK -> security_deposits.id NOT NULL | |
| reason | ENUM | NOT NULL | late_fee, damage, missing_accessory, other |
| amount | NUMERIC(12,2) | NOT NULL | |
| description | TEXT | NOT NULL | Detailed explanation |
| evidence_urls | TEXT[] | DEFAULT '{}' | Photos, receipts |
| approved_by | UUID | FK -> users.id, NULLABLE | Admin who approved |
| approved_at | TIMESTAMPTZ | NULLABLE | |
| customer_notified | BOOLEAN | DEFAULT false | |
| customer_disputed | BOOLEAN | DEFAULT false | |
| dispute_id | UUID | FK -> disputes.id, NULLABLE | |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | |

### Table: late_fees

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | |
| rental_id | UUID | FK -> rentals.id NOT NULL | |
| grace_period_end | TIMESTAMPTZ | NOT NULL | When late fee starts |
| rate_per_unit | NUMERIC(10,2) | NOT NULL | Per hour/day/week/month |
| charge_mode | ENUM | NOT NULL | hourly, daily, weekly, monthly |
| units_overdue | NUMERIC(10,2) | NOT NULL | Calculated overdue units |
| total_amount | NUMERIC(12,2) | NOT NULL | Running total |
| max_amount | NUMERIC(12,2) | NULL | Cap per config |
| status | ENUM | DEFAULT 'accruing' | accruing, finalized, invoiced, paid |
| invoice_id | UUID | FK -> invoices.id, NULLABLE | |
| finalized_at | TIMESTAMPTZ | NULLABLE | |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | | |

### Table: extension_requests

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | |
| rental_id | UUID | FK -> rentals.id NOT NULL | |
| requested_by | UUID | FK -> users.id NOT NULL | |
| current_end_at | TIMESTAMPTZ | NOT NULL | Original return time |
| requested_end_at | TIMESTAMPTZ | NOT NULL | New return time |
| extension_duration | INTEGER | NOT NULL | Additional time units |
| duration_unit | ENUM | NOT NULL | hourly, daily, weekly, monthly |
| reason | TEXT | NULLABLE | |
| additional_fee | NUMERIC(12,2) | NULL | Calculated on approval |
| status | ENUM | DEFAULT 'pending' | pending, approved, rejected, expired |
| reviewed_by | UUID | FK -> users.id, NULLABLE | |
| review_notes | TEXT | NULLABLE | |
| reviewed_at | TIMESTAMPTZ | NULLABLE | |
| expires_at | TIMESTAMPTZ | NOT NULL | Request expires if not reviewed |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | |

### Table: disputes

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | |
| dispute_number | VARCHAR(20) | UNIQUE NOT NULL | DSP-2026-00001 |
| rental_id | UUID | FK -> rentals.id NOT NULL | |
| user_id | UUID | FK -> users.id NOT NULL | |
| charge_type | ENUM | NOT NULL | late_fee, damage, missing_accessory, deposit_refund, incorrect_charge |
| amount_disputed | NUMERIC(12,2) | NOT NULL | |
| description | TEXT | NOT NULL | Customer's explanation |
| evidence_urls | TEXT[] | DEFAULT '{}' | Customer-provided evidence |
| status | ENUM | DEFAULT 'open' | open, under_review, won, lost, escalated, closed |
| admin_notes | TEXT | NULLABLE | Internal review notes |
| admin_decision | TEXT | NULLABLE | Reason for decision |
| resolution_amount | NUMERIC(12,2) | NULL | Refund amount if won |
| resolved_by | UUID | FK -> users.id, NULLABLE | |
| resolved_at | TIMESTAMPTZ | NULLABLE | |
| escalation_level | SMALLINT | DEFAULT 1 | 1=ops_admin, 2=super_admin |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | | |

### Table: repair_cases

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | |
| case_number | VARCHAR(20) | UNIQUE NOT NULL | REP-2026-00001 |
| product_id | UUID | FK -> products.id NOT NULL | |
| rental_id | UUID | FK -> rentals.id, NULLABLE | |
| damage_description | TEXT | NOT NULL | |
| photos_before | TEXT[] | DEFAULT '{}' | R2 URLs — pre-repair |
| photos_after | TEXT[] | DEFAULT '{}' | R2 URLs — post-repair |
| repair_cost | NUMERIC(12,2) | NULL | Actual vendor/internal cost |
| customer_deduction | NUMERIC(12,2) | DEFAULT 0 | Collected from customer |
| net_loss | NUMERIC(12,2) | GENERATED ALWAYS AS (repair_cost - customer_deduction) STORED | |
| status | ENUM | DEFAULT 'open' | open, in_repair, completed, write_off |
| assigned_to | UUID | FK -> users.id, NULLABLE | Repair technician |
| vendor_name | VARCHAR(255) | NULLABLE | External vendor |
| vendor_cost | NUMERIC(12,2) | NULL | External vendor charge |
| started_at | TIMESTAMPTZ | NULLABLE | |
| completed_at | TIMESTAMPTZ | NULLABLE | |
| days_out_of_service | INTEGER | NULLABLE | Lost rental revenue days |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | |

### Table: recovery_cases

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | |
| case_number | VARCHAR(20) | UNIQUE NOT NULL | RCV-2026-00001 |
| rental_id | UUID | FK -> rentals.id NOT NULL | |
| status | ENUM | DEFAULT 'open' | open, collection_dispatched, legal_action, recovered, write_off |
| assigned_agent_id | UUID | FK -> users.id, NULLABLE | |
| last_contact_at | TIMESTAMPTZ | NULLABLE | |
| contact_log | JSONB | DEFAULT '[]' | [{timestamp, channel, outcome, notes}] |
| fir_generated | BOOLEAN | DEFAULT false | |
| fir_number | VARCHAR(50) | NULLABLE | |
| legal_notice_sent | BOOLEAN | DEFAULT false | |
| legal_notice_url | TEXT | NULLABLE | R2 URL |
| recovery_amount | NUMERIC(12,2) | NULL | Amount recovered |
| product_recovered | BOOLEAN | DEFAULT false | |
| notes | TEXT | NULLABLE | |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | | |

---

## 9. Chain of Custody Tables

### Table: custody_events

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | |
| rental_id | UUID | FK -> rentals.id NOT NULL | |
| product_id | UUID | FK -> products.id NOT NULL | |
| stage | ENUM | NOT NULL | warehouse, pre_pickup, customer_pickup, in_possession, return_initiated, return_inspection, settlement, back_to_warehouse |
| actor_id | UUID | FK -> users.id NOT NULL | Staff or customer |
| customer_id | UUID | FK -> users.id, NULLABLE | |
| timestamp | TIMESTAMPTZ | DEFAULT NOW() | Server-side only |
| gps_lat | DECIMAL(9,6) | NULLABLE | |
| gps_lng | DECIMAL(9,6) | NULLABLE | |
| condition_rating | SMALLINT | CHECK (1 <= condition_rating <= 5) | |
| condition_notes | TEXT | NULLABLE | |
| photos | TEXT[] | DEFAULT '{}' | R2 URLs — front, back, left, right, top |
| video_url | TEXT | NULLABLE | Optional video evidence |
| qr_scan_result | VARCHAR(255) | NULLABLE | QR code scanned value |
| serial_number_verified | BOOLEAN | NULLABLE | |
| device_fingerprint | TEXT | NULLABLE | Device used for scan |
| is_online | BOOLEAN | DEFAULT true | False if synced from offline |
| sync_status | ENUM | DEFAULT 'synced' | synced, pending, conflict |
| notes | TEXT | NULLABLE | |

### Table: accessory_check_items

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | |
| custody_event_id | UUID | FK -> custody_events.id ON DELETE CASCADE | |
| accessory_id | UUID | FK -> accessories.id NOT NULL | |
| present | BOOLEAN | NOT NULL | |
| condition_note | TEXT | NULLABLE | |
| condition_rating | SMALLINT | NULLABLE | |
| photo_url | TEXT | NULLABLE | |

### Table: damage_reports

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | |
| rental_id | UUID | FK -> rentals.id NOT NULL | |
| product_id | UUID | FK -> products.id NOT NULL | |
| custody_event_id | UUID | FK -> custody_events.id, NULLABLE | |
| reported_by | UUID | FK -> users.id NOT NULL | |
| damage_type | ENUM | NOT NULL | scratch, dent, crack, stain, water_damage, electrical, missing_part, other |
| severity | ENUM | NOT NULL | minor, moderate, major, critical |
| description | TEXT | NOT NULL | |
| photos | TEXT[] | DEFAULT '{}' | R2 URLs |
| estimated_repair_cost | NUMERIC(12,2) | NULL | Admin estimate |
| customer_charged | BOOLEAN | DEFAULT false | |
| charge_amount | NUMERIC(12,2) | NULL | |
| repair_case_id | UUID | FK -> repair_cases.id, NULLABLE | |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | |

---

## 10. CRM & Customer Management Tables

### Table: crm_contacts

Extended customer profiles for CRM tracking.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | |
| user_id | UUID | FK -> users.id UNIQUE | Links to main user record |
| contact_type | ENUM | NOT NULL | individual, enterprise, lead |
| company_name | VARCHAR(255) | NULLABLE | For enterprise contacts |
| job_title | VARCHAR(100) | NULLABLE | |
| alternate_phone | VARCHAR(15) | NULLABLE | |
| alternate_email | VARCHAR(255) | NULLABLE | |
| preferred_contact_method | ENUM | DEFAULT 'sms' | sms, email, phone, whatsapp |
| preferred_contact_time | VARCHAR(50) | NULLABLE | e.g., "10am-6pm IST" |
| source | ENUM | NOT NULL | website, walk_in, referral, social_media, advertisement, other |
| referred_by_user_id | UUID | FK -> users.id, NULLABLE | |
| assigned_to | UUID | FK -> users.id, NULLABLE | Sales/ops person assigned |
| lead_status | ENUM | DEFAULT 'new' | new, contacted, qualified, negotiating, converted, lost, dormant |
| lead_score | SMALLINT | DEFAULT 0 | AI-calculated propensity to rent |
| lifetime_value | NUMERIC(14,2) | DEFAULT 0 | Total revenue from this customer |
| average_rental_value | NUMERIC(12,2) | DEFAULT 0 | |
| total_rentals | INTEGER | DEFAULT 0 | |
| favorite_categories | TEXT[] | DEFAULT '{}' | Most rented categories |
| notes | TEXT | NULLABLE | Internal CRM notes |
| tags | TEXT[] | DEFAULT '{}' | VIP, corporate, frequent, at_risk, etc. |
| last_contacted_at | TIMESTAMPTZ | NULLABLE | |
| last_rental_at | TIMESTAMPTZ | NULLABLE | |
| next_follow_up_at | TIMESTAMPTZ | NULLABLE | |
| follow_up_reason | TEXT | NULLABLE | |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | | |

### Table: crm_interactions

Log of all customer touchpoints.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | |
| contact_id | UUID | FK -> crm_contacts.id ON DELETE CASCADE | |
| user_id | UUID | FK -> users.id NOT NULL | Customer |
| interaction_type | ENUM | NOT NULL | call, email, sms, meeting, support_ticket, rental, return, complaint, inquiry |
| direction | ENUM | NOT NULL | inbound, outbound |
| channel | ENUM | NOT NULL | phone, email, sms, whatsapp, in_person, portal, app |
| subject | VARCHAR(255) | NOT NULL | |
| description | TEXT | NOT NULL | Full interaction details |
| outcome | VARCHAR(255) | NULLABLE | Result of interaction |
| duration_seconds | INTEGER | NULLABLE | For calls/meetings |
| attachment_urls | TEXT[] | DEFAULT '{}' | R2 URLs |
| performed_by | UUID | FK -> users.id NOT NULL | Staff member |
| follow_up_required | BOOLEAN | DEFAULT false | |
| follow_up_date | DATE | NULLABLE | |
| related_rental_id | UUID | FK -> rentals.id, NULLABLE | |
| related_dispute_id | UUID | FK -> disputes.id, NULLABLE | |
| sentiment | ENUM | NULLABLE | positive, neutral, negative |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | |

### Table: crm_tags

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | |
| name | VARCHAR(50) | UNIQUE NOT NULL | e.g., VIP, at_risk, corporate |
| color | VARCHAR(7) | DEFAULT '#3B82F6' | Hex color for UI |
| description | TEXT | NULLABLE | |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | |

### Table: crm_contact_tags

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| contact_id | UUID | FK -> crm_contacts.id ON DELETE CASCADE | |
| tag_id | UUID | FK -> crm_tags.id ON DELETE CASCADE | |
| assigned_by | UUID | FK -> users.id | |
| assigned_at | TIMESTAMPTZ | DEFAULT NOW() | |
| PRIMARY KEY(contact_id, tag_id) | | | |

### Table: crm_campaigns

Marketing and re-engagement campaigns.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | |
| name | VARCHAR(255) | NOT NULL | Campaign name |
| type | ENUM | NOT NULL | promotional, re_engagement, seasonal, referral, loyalty |
| channel | ENUM | NOT NULL | email, sms, push, whatsapp |
| status | ENUM | DEFAULT 'draft' | draft, scheduled, active, paused, completed, cancelled |
| target_audience | JSONB | NOT NULL | {trust_tiers: [...], tags: [...], min_rentals: N, categories: [...]} |
| message_template | TEXT | NOT NULL | With {{variables}} |
| subject_line | VARCHAR(255) | NULLABLE | For email campaigns |
| scheduled_at | TIMESTAMPTZ | NULLABLE | |
| started_at | TIMESTAMPTZ | NULLABLE | |
| completed_at | TIMESTAMPTZ | NULLABLE | |
| total_recipients | INTEGER | DEFAULT 0 | |
| total_sent | INTEGER | DEFAULT 0 | |
| total_opened | INTEGER | DEFAULT 0 | |
| total_clicked | INTEGER | DEFAULT 0 | |
| total_converted | INTEGER | DEFAULT 0 | |
| conversion_rate | NUMERIC(5,2) | GENERATED ALWAYS AS (CASE WHEN total_sent > 0 THEN (total_converted::NUMERIC / total_sent) * 100 ELSE 0 END) STORED | |
| created_by | UUID | FK -> users.id | |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | |

### Table: crm_campaign_recipients

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | |
| campaign_id | UUID | FK -> crm_campaigns.id ON DELETE CASCADE | |
| contact_id | UUID | FK -> crm_contacts.id NOT NULL | |
| status | ENUM | DEFAULT 'pending' | pending, sent, delivered, opened, clicked, converted, bounced, unsubscribed |
| sent_at | TIMESTAMPTZ | NULLABLE | |
| opened_at | TIMESTAMPTZ | NULLABLE | |
| clicked_at | TIMESTAMPTZ | NULLABLE | |
| converted_at | TIMESTAMPTZ | NULLABLE | |
| conversion_rental_id | UUID | FK -> rentals.id, NULLABLE | Rental created from campaign |
| UNIQUE(campaign_id, contact_id) | | | |

### Table: crm_lead_scores

AI-calculated scores for lead prioritization.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | |
| contact_id | UUID | FK -> crm_contacts.id UNIQUE | |
| score | SMALLINT | DEFAULT 0, CHECK (0 <= score <= 100) | |
| factors | JSONB | NOT NULL | {recency: N, frequency: N, monetary: N, engagement: N} |
| calculated_at | TIMESTAMPTZ | DEFAULT NOW() | |
| next_calculation_at | TIMESTAMPTZ | | |

---

## 11. Stock Management Tables

### Table: stock_locations

Physical storage locations.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | |
| name | VARCHAR(255) | NOT NULL | e.g., "Main Warehouse", "Store Front" |
| type | ENUM | NOT NULL | warehouse, store, repair_center, field |
| address | JSONB | NULLABLE | {street, city, state, pincode} |
| manager_id | UUID | FK -> users.id, NULLABLE | |
| is_active | BOOLEAN | DEFAULT true | |
| capacity | INTEGER | NULLABLE | Max items |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | |

### Table: stock_movements

Track every product movement between locations.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | |
| product_id | UUID | FK -> products.id NOT NULL | |
| movement_type | ENUM | NOT NULL | transfer, rental_out, rental_return, repair_send, repair_return, adjustment, disposal |
| from_location_id | UUID | FK -> stock_locations.id, NULLABLE | NULL for incoming |
| to_location_id | UUID | FK -> stock_locations.id, NULLABLE | NULL for outgoing |
| quantity | INTEGER | DEFAULT 1 | |
| reference_type | VARCHAR(50) | NULLABLE | rental, repair_case, adjustment |
| reference_id | UUID | NULLABLE | |
| performed_by | UUID | FK -> users.id NOT NULL | |
| notes | TEXT | NULLABLE | |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | |

### Table: stock_adjustments

Manual inventory corrections.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | |
| product_id | UUID | FK -> products.id NOT NULL | |
| location_id | UUID | FK -> stock_locations.id NOT NULL | |
| adjustment_type | ENUM | NOT NULL | damage, lost, found, revaluation, write_off, initial_stock |
| quantity_before | INTEGER | NOT NULL | |
| quantity_after | INTEGER | NOT NULL | |
| reason | TEXT | NOT NULL | |
| evidence_urls | TEXT[] | DEFAULT '{}' | Photos |
| approved_by | UUID | FK -> users.id, NULLABLE | Super Admin approval for write-offs |
| approved_at | TIMESTAMPTZ | NULLABLE | |
| created_by | UUID | FK -> users.id NOT NULL | |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | |

### Table: stock_levels

Current stock at each location (materialized/cached).

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | |
| product_id | UUID | FK -> products.id NOT NULL | |
| location_id | UUID | FK -> stock_locations.id NOT NULL | |
| quantity_available | INTEGER | DEFAULT 0 | |
| quantity_reserved | INTEGER | DEFAULT 0 | Reserved for bookings |
| quantity_in_repair | INTEGER | DEFAULT 0 | |
| quantity_total | INTEGER | GENERATED ALWAYS AS (quantity_available + quantity_reserved + quantity_in_repair) STORED | |
| last_counted_at | TIMESTAMPTZ | NULLABLE | Last physical count |
| UNIQUE(product_id, location_id) | | | |

### Table: maintenance_schedules

Preventive maintenance tracking.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | |
| product_id | UUID | FK -> products.id NOT NULL | |
| maintenance_type | ENUM | NOT NULL | scheduled, preventive, calibration, cleaning |
| description | TEXT | NOT NULL | |
| frequency_days | INTEGER | NULLABLE | Repeat every N days |
| last_performed_at | TIMESTAMPTZ | NULLABLE | |
| next_due_at | TIMESTAMPTZ | NULLABLE | |
| assigned_to | UUID | FK -> users.id, NULLABLE | |
| status | ENUM | DEFAULT 'scheduled' | scheduled, in_progress, completed, overdue |
| completed_at | TIMESTAMPTZ | NULLABLE | |
| cost | NUMERIC(10,2) | NULLABLE | |
| notes | TEXT | NULLABLE | |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | |

---

## 12. Loyalty Points & Referral Tables

### Table: loyalty_points_ledger

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | |
| user_id | UUID | FK -> users.id NOT NULL | |
| type | ENUM | NOT NULL | earned, redeemed, expired, adjusted |
| points | INTEGER | NOT NULL | Positive for earned, negative for redeemed |
| balance_after | INTEGER | NOT NULL | Running balance |
| source | VARCHAR(50) | NOT NULL | rental_complete, referral_bonus, on_time_bonus, campaign, etc. |
| reference_id | UUID | NULLABLE | rental_id, referral_id, etc. |
| reference_type | VARCHAR(50) | NULLABLE | |
| expires_at | DATE | NULLABLE | Points expiry date (12 months from earn) |
| notes | TEXT | NULLABLE | |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | |

### Table: referrals

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | |
| referrer_id | UUID | FK -> users.id NOT NULL | Who referred |
| referred_id | UUID | FK -> users.id NOT NULL | Who was referred |
| referral_code | VARCHAR(20) | NOT NULL | Code used |
| status | ENUM | DEFAULT 'pending' | pending, completed, rewarded |
| referrer_reward_points | INTEGER | DEFAULT 100 | Points awarded to referrer |
| referred_reward_points | INTEGER | DEFAULT 50 | Points awarded to referred |
| first_rental_id | UUID | FK -> rentals.id, NULLABLE | Completed when referred user makes first rental |
| rewarded_at | TIMESTAMPTZ | NULLABLE | |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | |

### Table: loyalty_tiers

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | |
| name | VARCHAR(50) | UNIQUE NOT NULL | Bronze, Silver, Gold, Platinum |
| min_points | INTEGER | NOT NULL | Points required to reach |
| benefits | JSONB | NOT NULL | {discount_pct, free_delivery, priority_support, etc.} |
| icon_url | TEXT | NULLABLE | |
| color | VARCHAR(7) | NULLABLE | Hex color |

---

## 13. Notification & Audit Tables

### Table: notifications

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | |
| user_id | UUID | FK -> users.id NOT NULL | |
| type | VARCHAR(50) | NOT NULL | rental_confirmed, overdue_alert, deposit_refund, etc. |
| title | VARCHAR(255) | NOT NULL | |
| body | TEXT | NOT NULL | |
| data | JSONB | DEFAULT '{}' | Extra payload for deep linking |
| channels | TEXT[] | NOT NULL | ['sms', 'email', 'push', 'in_app'] |
| sent_at | TIMESTAMPTZ | NULLABLE | |
| opened_at | TIMESTAMPTZ | NULLABLE | |
| clicked_at | TIMESTAMPTZ | NULLABLE | |
| status | ENUM | DEFAULT 'pending' | pending, sent, delivered, failed, opened |
| reference_type | VARCHAR(50) | NULLABLE | |
| reference_id | UUID | NULLABLE | |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | |

### Table: notification_templates

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | |
| name | VARCHAR(100) | UNIQUE NOT NULL | e.g., overdue_reminder_24h |
| channel | ENUM | NOT NULL | sms, email, push |
| subject | VARCHAR(255) | NULLABLE | For email |
| body_template | TEXT | NOT NULL | With {{variables}} |
| is_active | BOOLEAN | DEFAULT true | |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | |

### Table: audit_logs (audit schema)

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | |
| actor_id | UUID | NOT NULL | FK -> users.id |
| actor_role | ENUM | NOT NULL | |
| actor_name | VARCHAR(255) | NOT NULL | Denormalized for fast queries |
| action | VARCHAR(100) | NOT NULL | e.g., rental.create, deposit.settle |
| entity_type | VARCHAR(50) | NOT NULL | rental, product, user, invoice, etc. |
| entity_id | UUID | NOT NULL | |
| entity_number | VARCHAR(20) | NULLABLE | RNT-2026-00001, etc. |
| before_state | JSONB | NULLABLE | |
| after_state | JSONB | NULLABLE | |
| ip_address | INET | NULLABLE | |
| device_fingerprint | TEXT | NULLABLE | |
| user_agent | TEXT | NULLABLE | |
| request_id | UUID | NOT NULL | Correlation ID |
| timestamp | TIMESTAMPTZ | DEFAULT NOW() | |

**Partitioning:** `PARTITION BY RANGE (created_at)` — monthly partitions.

### Table: rate_limit_events (audit schema)

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | |
| identifier | VARCHAR(255) | NOT NULL | IP or user_id |
| endpoint | VARCHAR(255) | NOT NULL | |
| method | VARCHAR(10) | NOT NULL | GET, POST, etc. |
| window_start | TIMESTAMPTZ | NOT NULL | |
| request_count | INTEGER | NOT NULL | |
| blocked | BOOLEAN | DEFAULT false | |
| timestamp | TIMESTAMPTZ | DEFAULT NOW() | |

---

## 14. Indexing Strategy

Every index justified by a specific query pattern.

| Table | Index | Type | Query Served |
|-------|-------|------|--------------|
| users | idx_users_phone | BTREE UNIQUE | Login by phone |
| users | idx_users_email | BTREE UNIQUE | Login by email |
| users | idx_users_trust_tier | BTREE | Filter by tier |
| users | idx_users_blacklisted | PARTIAL (WHERE blacklisted=true) | Blacklist check |
| users | idx_users_name_tsvector | GIN | Full-text search |
| users | idx_users_enterprise_id | BTREE | Enterprise members lookup |
| users | idx_users_referral_code | BTREE UNIQUE | Referral lookup |
| refresh_tokens | idx_refresh_tokens_hash | BTREE | Token validation |
| refresh_tokens | idx_refresh_tokens_user | BTREE | Session listing |
| kyc_records | idx_kyc_user_step | COMPOSITE | KYC progress check |
| enterprises | idx_enterprises_gst | BTREE UNIQUE | GST lookup |
| groups | idx_groups_leader | BTREE | Leader's groups |
| group_members | idx_group_members_user | BTREE | User's groups |
| group_members | idx_group_members_group_status | COMPOSITE | Active members |
| products | idx_products_status | BTREE | Catalog filter |
| products | idx_products_category_status | COMPOSITE | Category browse |
| products | idx_products_name_tsvector | GIN | Product search |
| products | idx_products_sku | BTREE UNIQUE | SKU lookup |
| products | idx_products_barcode | BTREE | Barcode scan |
| accessories | idx_accessories_product | BTREE | BoM per product |
| availability_blocks | idx_avail_product_start_end | BTREE | Availability check |
| availability_blocks | idx_avail_status | BTREE | Active blocks |
| reservations | idx_reservations_product_status | COMPOSITE | Active reservations |
| reservations | idx_reservations_expires | BTREE | TTL cleanup |
| rentals | idx_rentals_user_id | BTREE | Customer's orders |
| rentals | idx_rentals_group_id | BTREE | Group rentals |
| rentals | idx_rentals_status | BTREE | Admin dashboard |
| rentals | idx_rentals_end_at | BTREE | Overdue detection |
| rentals | idx_rentals_product_status | COMPOSITE | Product availability |
| rentals | idx_rentals_number | BTREE UNIQUE | Search by number |
| rental_items | idx_rental_items_rental | BTREE | Items per rental |
| quotations | idx_quotations_customer | BTREE | Customer quotes |
| quotations | idx_quotations_status | BTREE | Quote pipeline |
| quotations | idx_quotations_share_token | BTREE UNIQUE | Public share link |
| invoices | idx_invoices_user | BTREE | Customer invoices |
| invoices | idx_invoices_rental | BTREE | Rental invoices |
| invoices | idx_invoices_status | BTREE | Payment tracking |
| invoices | idx_invoices_number | BTREE UNIQUE | Search by number |
| invoices | idx_invoices_due_date | BTREE | Overdue invoices |
| payments | idx_payments_invoice | BTREE | Payments per invoice |
| payments | idx_payments_user | BTREE | Customer payment history |
| payments | idx_payments_razorpay | BTREE | Razorpay lookup |
| security_deposits | idx_deposits_rental | BTREE | Deposit per rental |
| security_deposits | idx_deposits_status | BTREE | Active deposits |
| custody_events | idx_custody_rental | BTREE | Chain of custody |
| custody_events | idx_custody_product | BTREE | Product history |
| late_fees | idx_latefees_rental | BTREE | Fees per rental |
| late_fees | idx_latefees_status | BTREE | Accruing fees |
| disputes | idx_disputes_user | BTREE | Customer disputes |
| disputes | idx_disputes_status | BTREE | Open disputes |
| repair_cases | idx_repair_product | BTREE | Repair history |
| repair_cases | idx_repair_status | BTREE | Active repairs |
| recovery_cases | idx_recovery_status | BTREE | Active recoveries |
| crm_contacts | idx_crm_user | BTREE UNIQUE | User CRM lookup |
| crm_contacts | idx_crm_assigned | BTREE | Assigned contacts |
| crm_contacts | idx_crm_lead_status | BTREE | Lead pipeline |
| crm_contacts | idx_crm_tags | GIN | Tag-based filter |
| crm_interactions | idx_crm_interactions_contact | BTREE | Contact history |
| crm_interactions | idx_crm_interactions_date | BTREE | Recent interactions |
| crm_campaigns | idx_crm_campaigns_status | BTREE | Active campaigns |
| stock_movements | idx_stock_movements_product | BTREE | Product movement history |
| stock_movements | idx_stock_movements_location | BTREE | Location inventory |
| stock_levels | idx_stock_levels_product_location | BTREE UNIQUE | Stock check |
| notifications | idx_notifications_user_status | BTREE | Unread count |
| notifications | idx_notifications_created | BTREE | Recent notifications |
| audit_logs | idx_audit_actor_created | COMPOSITE | User audit trail |
| audit_logs | idx_audit_entity | COMPOSITE | Entity audit trail |
| audit_logs | idx_audit_action | BTREE | Action filtering |
| loyalty_points_ledger | idx_loyalty_user | BTREE | Points history |
| referrals | idx_referrals_referrer | BTREE | Referral stats |

---

## 15. Materialized Views

### mv_admin_dashboard

```sql
CREATE MATERIALIZED VIEW analytics.mv_admin_dashboard AS
SELECT
  (SELECT COUNT(*) FROM public.rentals WHERE status = 'active') AS active_rentals,
  (SELECT COUNT(*) FROM public.rentals WHERE status = 'overdue') AS overdue_rentals,
  (SELECT COUNT(*) FROM public.rentals WHERE end_at::date = CURRENT_DATE) AS due_today,
  (SELECT COUNT(*) FROM public.rentals WHERE status = 'confirmed' AND start_at::date = CURRENT_DATE) AS pickups_today,
  (SELECT COUNT(*) FROM public.rentals WHERE status = 'returned' AND actual_return_at::date = CURRENT_DATE) AS returns_today,
  (SELECT COALESCE(SUM(rental_fee), 0) FROM public.rentals WHERE status IN ('active','returned','completed') AND created_at >= date_trunc('month', CURRENT_DATE)) AS revenue_this_month,
  (SELECT COALESCE(SUM(amount), 0) FROM public.security_deposits WHERE status = 'held') AS deposits_held,
  (SELECT COALESCE(SUM(total_amount), 0) FROM public.late_fees WHERE status = 'accruing') AS late_fees_accruing,
  (SELECT COUNT(*) FROM public.repair_cases WHERE status IN ('open','in_repair')) AS open_repairs,
  (SELECT COUNT(*) FROM public.recovery_cases WHERE status NOT IN ('recovered','write_off')) AS open_recoveries,
  (SELECT COUNT(*) FROM public.disputes WHERE status IN ('open','under_review')) AS open_disputes;
```

**Refresh:** Every 5 minutes via ARQ job.

### mv_revenue_daily

```sql
CREATE MATERIALIZED VIEW analytics.mv_revenue_daily AS
SELECT
  date_trunc('day', created_at)::date AS date,
  rental_context,
  COUNT(*) AS rental_count,
  SUM(rental_fee) AS total_rental_revenue,
  SUM(security_deposit_amount) AS total_deposits_collected,
  AVG(rental_fee) AS avg_rental_value
FROM public.rentals
WHERE status NOT IN ('cancelled', 'draft')
GROUP BY 1, 2;
```

### mv_product_utilization

```sql
CREATE MATERIALIZED VIEW analytics.mv_product_utilization AS
SELECT
  p.id AS product_id,
  p.name AS product_name,
  c.name AS category_name,
  COUNT(r.id) AS total_rentals,
  SUM(CASE WHEN r.status = 'active' THEN 1 ELSE 0 END) AS currently_rented,
  AVG(EXTRACT(EPOCH FROM (r.actual_return_at - r.start_at))/86400) AS avg_rental_days,
  SUM(r.rental_fee) AS total_revenue,
  SUM(CASE WHEN r.status = 'overdue' THEN 1 ELSE 0 END) AS overdue_count
FROM public.products p
LEFT JOIN public.categories c ON p.category_id = c.id
LEFT JOIN public.rentals r ON p.id = r.product_id
GROUP BY 1, 2, 3;
```

### mv_customer_lifetime_value

```sql
CREATE MATERIALIZED VIEW analytics.mv_customer_lifetime_value AS
SELECT
  u.id AS user_id,
  u.name,
  u.email,
  u.trust_tier,
  COUNT(r.id) AS total_rentals,
  SUM(r.rental_fee) AS total_spend,
  AVG(r.rental_fee) AS avg_rental_value,
  MIN(r.created_at) AS first_rental_date,
  MAX(r.created_at) AS last_rental_date,
  AVG(CASE WHEN r.status = 'returned' THEN EXTRACT(EPOCH FROM (r.actual_return_at - r.end_at))/3600 END) AS avg_hours_late
FROM public.users u
LEFT JOIN public.rentals r ON u.id = r.user_id AND r.status NOT IN ('cancelled','draft')
WHERE u.role = 'portal_user'
GROUP BY 1, 2, 3, 4;
```

### mv_crm_lead_scores

```sql
CREATE MATERIALIZED VIEW analytics.mv_crm_lead_scores AS
SELECT
  cc.id AS contact_id,
  cc.user_id,
  -- Recency: days since last rental (lower = better)
  COALESCE(EXTRACT(EPOCH FROM (CURRENT_DATE - cc.last_rental_at::date))/86400, 365) AS days_since_rental,
  -- Frequency: total rentals
  cc.total_rentals,
  -- Monetary: lifetime value
  cc.lifetime_value,
  -- Engagement: total interactions in last 90 days
  (SELECT COUNT(*) FROM public.crm_interactions ci WHERE ci.contact_id = cc.id AND ci.created_at >= CURRENT_DATE - INTERVAL '90 days') AS recent_interactions,
  -- Composite score
  LEAST(100, GREATEST(0,
    (1.0 - LEAST(COALESCE(EXTRACT(EPOCH FROM (CURRENT_DATE - cc.last_rental_at::date))/86400, 365) / 365.0, 1.0)) * 30 +
    LEAST(cc.total_rentals / 20.0, 1.0) * 30 +
    LEAST(cc.lifetime_value / 50000.0, 1.0) * 25 +
    LEAST((SELECT COUNT(*) FROM public.crm_interactions ci WHERE ci.contact_id = cc.id AND ci.created_at >= CURRENT_DATE - INTERVAL '90 days') / 10.0, 1.0) * 15
  ))::SMALLINT AS score
FROM public.crm_contacts cc;
```

---

## 16. Partitioning Strategy

| Table | Partition Key | Strategy | Rationale |
|-------|---------------|----------|-----------|
| audit_logs | created_at | RANGE by month | Immutable; old partitions archived |
| rate_limit_events | timestamp | RANGE by week | High volume; auto-expire old |
| notifications | created_at | RANGE by month | Cleanup old notifications |
| loyalty_points_ledger | created_at | RANGE by quarter | Historical reference |
| crm_interactions | created_at | RANGE by month | Large volume per contact |
| custody_events | timestamp | RANGE by quarter | High volume per rental |

**Example — audit_logs partitioning:**
```sql
CREATE TABLE audit.audit_logs (
  ...
) PARTITION BY RANGE (created_at);

CREATE TABLE audit.audit_logs_2026_01 PARTITION OF audit.audit_logs
  FOR VALUES FROM ('2026-01-01') TO ('2026-02-01');

CREATE TABLE audit.audit_logs_2026_02 PARTITION OF audit.audit_logs
  FOR VALUES FROM ('2026-02-01') TO ('2026-03-01');
-- ... auto-created monthly via pg_partman
```

---

## 17. Connection Pooling & Clustering

### Connection Pooling Strategy

| Component | Setting | Value |
|-----------|---------|-------|
| NeonDB PgBouncer | Mode | transaction |
| NeonDB PgBouncer | Max connections | 10,000 virtual -> 10 physical |
| FastAPI asyncpg | Pool min | 2 |
| FastAPI asyncpg | Pool max | 10 per worker |
| FastAPI asyncpg | Health check | SELECT 1 every 30s |
| FastAPI asyncpg | SSL | require (NeonDB enforces TLS) |

### Database Clustering

| Strategy | Implementation | Benefit |
|----------|----------------|---------|
| Primary-Replica | NeonDB primary (writes) + 1 read replica (reads) | Read throughput doubled |
| Connection Pooling | PgBouncer transaction mode | 10,000 virtual -> 10 physical |
| Schema Separation | public, audit, analytics, crm | Independent query paths |
| Table Partitioning | Monthly/quarterly ranges | Partition pruning |
| Horizontal Sharding (future) | When > 10M rentals: shard by user_id hash | Linear scale |

### Read/Write Routing

```python
# FastAPI dependency example
async def get_db():
    """Write operations go to primary"""
    async with primary_engine.connect() as conn:
        yield conn

async def get_read_db():
    """Read operations go to replica"""
    async with replica_engine.connect() as conn:
        yield conn
```

### Redis Cluster Strategy

| Use Case | Key Pattern | TTL | Notes |
|----------|-------------|-----|-------|
| Session Store | session:{user_id} | 30 days | Rotated on refresh |
| OTP Storage | otp:{identifier}:{purpose} | 5 min | Auto-expire |
| Rate Limiting | ratelimit:{endpoint}:{identifier} | Per rule | Atomic INCR + EXPIRE |
| Reservation Hold | reservation:{product_id}:{user_id} | 15 min | Auto-release |
| Late Fee Cache | latefee:{rental_id} | 60 sec | Real-time display |
| Dashboard Cache | dashboard:{admin_id} | 30 sec | Live metrics |
| WebSocket Pub/Sub | ws:admin:global, ws:rental:{id} | N/A | Real-time events |
| Job Queue | arq:queue | N/A | Background jobs |
| Cache Invalidate | cache:{entity}:{id} | Varies | Query result cache |

---

**— End of DATABASE_SCHEMA.md —**
