# RENTAL MANAGEMENT SYSTEM
## Complete Project Plan · System Architecture · Full Stack Design
### Version 3.0 | 2026 | FINAL
### CONFIDENTIAL — INTERNAL USE ONLY

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [User Types & Roles](#2-user-types--roles)
3. [Application Entry & Onboarding](#3-application-entry--onboarding)
4. [E-KYC & Trust Score System](#4-e-kyc--trust-score-system)
5. [Core Rental Workflows](#5-core-rental-workflows)
6. [Chain of Custody](#6-chain-of-custody)
7. [Security Deposit Engine](#7-security-deposit-engine)
8. [Late Return & Escalation](#8-late-return--escalation)
9. [Group Rental System](#9-group-rental-system)
10. [Enterprise Features](#10-enterprise-features)
11. [System Architecture & Tech Stack](#11-system-architecture--tech-stack)
12. [Database Design](#12-database-design)
13. [Authentication & Security](#13-authentication--security)
14. [Performance & Scaling](#14-performance--scaling)
15. [Free Tier Stack](#15-free-tier-stack)
16. [Development Phases](#16-development-phases)
17. [Customer Extension Request Workflow](#17-customer-extension-request-workflow)
18. [Dispute Filing & Resolution Workflow](#18-dispute-filing--resolution-workflow)
19. [Repair Workflow](#19-repair-workflow)
20. [Customer Blacklisting Workflow](#20-customer-blacklisting-workflow)
21. [Rental Operations Dashboard](#21-rental-operations-dashboard)
22. [Notification & Alert System](#22-notification--alert-system)
23. [Pricing, Pricelists & Product Management](#23-pricing-pricelists--product-management)
24. [Customer Portal Features](#24-customer-portal-features)
25. [Admin Configuration Panel](#25-admin-configuration-panel)
26. [Availability Engine](#26-availability-engine)
27. [Quotes & Orders Workflow](#27-quotes--orders-workflow)
28. [Invoicing System](#28-invoicing-system)
29. [CRM — Customer Relationship Management](#29-crm--customer-relationship-management)
30. [Stock Management](#30-stock-management)
31. [Loyalty Points & Referral System](#31-loyalty-points--referral-system)
32. [Critical Edge Cases (Extended)](#32-critical-edge-cases-extended)

---

## 1. Executive Summary

### 1.1 The Problem

Rental businesses lose money, assets, and customer trust because they have zero control the moment a product leaves their hands. There is no real-time visibility, no automated enforcement, no tamper-proof evidence chain, and no intelligent escalation system.

**The Three Root Problems:**
- **TRUST PROBLEM** — "Can I trust this person / company / group with my ₹50,000 asset?"
- **VISIBILITY PROBLEM** — "Where is my inventory right now? Who has what?"
- **ENFORCEMENT PROBLEM** — "They returned it late. Now what? They are arguing."

### 1.2 Our Solution

Airbnb + Uber + a tamper-proof Legal Contract — all in one intelligent rental platform. Every feature is designed around one principle: **no one goes out of line — neither the customer nor the admin.**

### 1.3 What We Solve

| Problem | Solution |
|---------|----------|
| No centralized dashboard | Real-time WebSocket dashboard with live metrics |
| Difficulty tracking pickups/returns | Automated scheduling + QR scanning at every handoff |
| Manual late fee calculation | Auto-calculated with configurable rules per product |
| No visibility into overdue rentals | Priority feed + automated escalation timeline |
| Security deposits outside workflow | Smart deposit engine with dynamic calculation |
| Limited operational insights | KPI analytics + business intelligence reports |

---

## 2. User Types & Roles

### 2.1 Three-Tier Customer Model

Every account is classified at registration, and the tier determines feature access, deposit rates, pricelist priority, and trust-score computation methodology.

---

### 2.2 TIER 1 — PERSONAL USER

A Personal User is a single individual renting for personal use. This is the baseline tier.

#### Account Characteristics
- Single individual — one primary identity mapped to one account
- One active KYC record (Aadhaar / PAN / Passport / Driving Licence)
- One tokenized payment method minimum (Razorpay)
- Individual Trust Score: 0–100 computed from KYC signals + rental history
- Rental access gated by Trust Tier: Unverified → Basic → Standard → Trusted → VIP

#### Feature Access

| Feature | Access Level | Notes |
|---------|--------------|-------|
| Browse catalog | Full | All categories visible |
| Rent products | Yes — gated by trust tier | Max rental value by tier |
| Group Rental (join) | Yes | Can join a group as a member |
| Group Rental (create) | No | Must upgrade to Group account |
| Enterprise billing | No | Must upgrade to Enterprise |
| Team management | No | Not available for Personal tier |
| GST invoice | No | Consumer invoices only |

#### Trust Score Thresholds

| Tier | Score | Max Rental Value | Deposit Rate |
|------|-------|------------------|--------------|
| Unverified | 0–29 | NOT ALLOWED | N/A |
| Basic | 30–49 | Up to ₹5,000 | 50% of item value |
| Standard | 50–69 | Up to ₹25,000 | 30% of item value |
| Trusted | 70–84 | Up to ₹1,00,000 | 20% of item value |
| VIP | 85–100 | Unlimited | 10% of item value |

---

### 2.3 TIER 2 — ENTERPRISE USER

An Enterprise User is a registered business entity (Private Ltd, LLP, Partnership, Proprietorship, NGO) that rents products for commercial use.

#### Enterprise Account Characteristics
- Entity-level account — not tied to a single individual
- Primary Contact: one designated human administrator manages the account
- Sub-users: Enterprise can invite internal team members with role-based permissions
- Entity KYC: GST number, PAN (business), Certificate of Incorporation
- Enterprise Trust Score: calculated from business KYC + payment history + rental history
- Credit Line available: 30-day credit billing instead of upfront payment (subject to approval)
- Custom pricelist: Enterprise accounts can negotiate corporate pricing

#### Enterprise KYC Pipeline

| Step | Verification | Method | Free Tool |
|------|--------------|--------|-----------|
| 1 | GST Registration Check | GST API (govt) | Surepass free tier |
| 2 | PAN Verification (Entity) | PAN API | Surepass sandbox |
| 3 | Director / Owner Aadhaar | Aadhaar OTP | Digio sandbox |
| 4 | Business Bank Account Verify | Penny drop | Razorpay sandbox |
| 5 | Office Address Proof | Document upload + OCR | Tesseract OCR |
| 6 | Entity Face Liveness | Selfie + ID match | FaceIO free tier |
| 7 | Digital Agreement Signing | Aadhaar OTP e-sign | Digio sandbox |

#### Enterprise Teams Feature

Enterprise accounts include a Teams sub-system. The Enterprise Admin can invite internal users and assign them roles.

| Sub-Role | Who | Key Powers | Restrictions |
|----------|-----|------------|--------------|
| Enterprise Admin | CXO / Finance Head | Full enterprise control, invite/remove team, approve rentals, view all financials | Cannot override system-level blacklist |
| Procurement Manager | Ops / Procurement | Create and approve rental orders up to ₹50,000 | Cannot change pricing |
| Department User | Employee | Create rental requests, view own rentals | Cannot approve own requests |
| Auditor (Read-only) | Finance Auditor | View all enterprise rentals, invoices | No create/edit access |

#### Enterprise Feature Access

| Feature | Access |
|---------|--------|
| GST Tax Invoice (B2B) | Yes — full B2B invoice with enterprise GSTIN |
| Net 30 / Credit Billing | Yes — after creditworthiness check |
| Custom Pricelist | Yes — negotiated and assigned by admin |
| Dedicated Account Manager | Yes — assigned human support contact |
| Multi-user / Team Sub-accounts | Yes — unlimited sub-users, role-based |
| Bulk Rental Orders | Yes — rent multiple products in a single PO |
| Centralized Billing Dashboard | Yes — all team rentals in one view |
| API Access (Headless Rental) | Yes — REST API for ERP integration |

---

### 2.4 TIER 3 — GROUP USER

A Group is a collection of two or more Personal Users who wish to rent a product together, sharing financial responsibility. Designed for friends, roommates, college groups, sports teams, or informal communities.

#### Group Account Characteristics
- 2 to 20 individual Personal Users can form a Group
- One user is designated **Group Leader** — manages the group, invites members, primary signatory on agreements
- Every group member must have an active KYC-verified Personal account (minimum Basic tier, score ≥ 30)
- **Group Trust Score** = Weighted Average of all member trust scores
- **Group Safety Deposit** = Sum of proportional contributions from each member
- Each member's contribution is tracked independently in the deposit ledger
- All members receive notifications and can view shared rental status
- All members are legally bound by the group rental agreement

#### Group Trust Score Formula

**Simple Average:**
```
Group Trust Score = (Σ Individual Member Trust Scores) ÷ Total Members
```

**Weighted Variant (for high-value items > ₹15,000):**
```
Group Trust Score = (2 × Leader Score + Σ Other Member Scores) ÷ (Members + 1)
```

**Example:** Group of 4 with scores 75, 60, 55, 80 (leader = 75)
- Simple Average: (75+60+55+80) ÷ 4 = **67.5** → Standard Tier
- Weighted (leader 2×): (150+60+55+80) ÷ 5 = **69** → Standard Tier

#### Group Safety Deposit — Shared Pool Model

| Rule | Details |
|------|---------|
| Default split | Equal split: Total Deposit ÷ Number of Members |
| Custom split | Group Leader can assign custom % per member (must sum to 100%) |
| Member payment | Each member pays their share via their own Razorpay-linked card |
| Shortfall handling | If any member's payment fails, rental is blocked until resolved. 48-hour window. |
| Refund routing | Each member's deposit share is refunded independently to their original payment method |
| Deduction routing | Deductions are applied proportionally from all member shares unless Group Leader absorbs |
| Dispute on deduction | Any member can dispute a deduction; resolution applies to that member's share only |

#### Group Rental Agreement
- One single agreement signed by ALL members — via Aadhaar OTP e-sign (Digio sandbox)
- Agreement explicitly lists: all member names, KYC IDs, contribution amounts, liability clause
- **Joint and several liability clause**: if any member fails to pay their deduction, the Group Leader is responsible for the remaining amount
- Agreement PDF generated with each member's digital signature and timestamp

#### Group Trust Score — Impact on Rental Access

| Group Score | Max Rental Value | Deposit Rate | Additional Action |
|-------------|------------------|--------------|-------------------|
| 0–29 | NOT ALLOWED | N/A | All members must be KYC verified |
| 30–49 | Up to ₹10,000 | 50% | Admin notified; manual review |
| 50–69 | Up to ₹50,000 | 30% | Standard group checkout |
| 70–84 | Up to ₹2,00,000 | 20% | Expedited checkout |
| 85–100 | Unlimited | 10% | VIP group treatment |

#### Member Trust Score Impact After Rental

| Outcome | Group Leader Impact | Other Members Impact |
|---------|---------------------|----------------------|
| On-time return, no damage | +5 points (group bonus) | +5 points each |
| Late return | -15 penalty | -15 penalty each |
| Damage | -20 (if responsible) | -5 (group negligence) |
| Non-return | -50 + LOCKED | -25 each |

#### Group Management Features

| Feature | Who Can Perform | Notes |
|---------|-----------------|-------|
| Create Group | Any KYC-verified Personal user | Becomes Group Leader automatically |
| Invite Members | Group Leader only | Members receive in-app + email invite |
| Remove Member | Group Leader (before rental only) | Cannot remove during active rental |
| Transfer Leadership | Group Leader | New leader must have equal or higher trust score |
| Dissolve Group | Group Leader | Only if no active rentals pending settlement |
| View Group Dashboard | All members | See all group rentals, deposit pool, shared timeline |
| Initiate Group Rental | Group Leader only | Leader selects product; members approve deposit split |
| Request Extension | Group Leader only | Requires majority member approval (>50%) via in-app vote |
| File Dispute | Any member independently | Only for their own deposit deduction share |

---

### 2.5 Admin Roles & Permissions

| Role | Who | Key Powers | Restrictions |
|------|-----|------------|--------------|
| Super Admin / Owner | Business owner | Full access. Override any decision. View all financials. Configure all rules. | None |
| Operations Admin | Store manager | Create/confirm rentals, manage pickups/returns, process deposits, run inspections | Cannot change global pricing rules |
| Field Agent | Pickup/delivery personnel | Scan QR codes, upload condition photos, confirm pickup/return, GPS location | Read-only on financials. No deposit access. |
| Portal User (Personal) | End customer | Browse, rent, pay, view own orders, download invoices | Cannot see other customers' data |
| Portal User (Enterprise Admin) | Business administrator | All Personal powers + manage team sub-users, GST invoices | Cannot override system blacklist |
| Portal User (Enterprise Sub-user) | Employee / team member | Role-based — as assigned by Enterprise Admin | Varies by assigned sub-role |
| Group Leader | Personal user who created group | Initiate group rentals, invite/remove members, manage deposits | Cannot act without all members completing KYC |
| Group Member | Personal user invited to group | View group dashboard, pay own deposit share, file disputes | Cannot initiate rentals independently |
| Walk-in Customer | Offline customer | Admin creates record and rental on their behalf | Same as Personal User once account created |
| Guest | Unauthenticated visitor | Browse product catalog, view rental periods | Cannot rent anything |

---

## 3. Application Entry & Onboarding

### 3.1 Screen Flow

```
Splash Screen → App logo + brand name (2 seconds while session checked)
    ↓
Session exists? → YES → Dashboard (customer) or Admin Panel (admin)
    ↓ NO
Login Screen
```

### 3.2 Login Screen
- Login with phone number + OTP (primary, India-first)
- Login with email + password (secondary)
- Login with Google / Apple SSO (optional)
- Forgot password flow: email-based reset link
- Failed login lockout: 5 failed attempts → 15-minute cooldown → Admin alert after 10 attempts

### 3.3 New User Registration

| Step | Action | Required |
|------|--------|----------|
| 1 | Phone number + OTP verification | Yes |
| 2 | Email address + email verification link | Yes |
| 3 | Basic profile (name, date of birth) | Yes |
| 4 | Profile photo upload | Optional at registration, required before first rental |
| 5 | KYC prompt | Required before any rental |

### 3.4 Post-Registration
- Trust Score initialized at 0
- User redirected to KYC flow or dashboard with KYC banner
- Dashboard shows KYC completion percentage + what they unlock at each step

---

## 4. E-KYC & Trust Score System

### 4.1 E-KYC Pipeline — All 7 Steps

| Step | Type | Method | Pass Condition | Failure Action |
|------|------|--------|----------------|----------------|
| 1 | Phone Verification | OTP to mobile number | OTP matched within 5 minutes | 3 retries → 15-min cooldown |
| 2 | Email Verification | Magic link to email | Link clicked within 24 hours | Resend option × 3 |
| 3 | Government ID Upload | Aadhaar / PAN / Passport / Driving Licence | OCR extracts data; API confirms ID is valid | Upload rejected → retry |
| 4 | Selfie + Liveness Check | Selfie photo captured vs. ID photo | AI face match score > 85% | Manual review queue |
| 5 | Address Verification | Utility bill / Aadhaar address page | Address on document matches registered address | Additional document requested |
| 6 | Payment Method | Credit or debit card added | Card tokenized via Razorpay | Card declined → add another |
| 7 | Device Fingerprint | Browser / app device ID generated | Device ID stored against account | 3+ devices → Security flag |

### 4.2 KYC Verification Partners

| Service | Purpose | Free Tier |
|---------|---------|-----------|
| Hyperverge | Aadhaar + PAN verification, face match, liveness | Sandbox available |
| Digio | E-sign, Aadhaar OTP-based signing | Sandbox available |
| Surepass | PAN + GST verification for corporate customers | Sandbox available |
| Razorpay | Payment method tokenization and authorization holds | Sandbox available |

### 4.3 Customer Trust Score (0–100)

| Signal | Points | Notes |
|--------|--------|-------|
| Identity verified (E-KYC passed) | +30 | One-time permanent score |
| Verified address on file | +15 | Must match government ID |
| Valid tokenized payment method | +15 | Credit/debit card authorized |
| Each successful past rental returned on time | +10 | Capped at +20 total |
| No damage history | +10 | Resets to 0 if damage reported |
| No late return history | +10 | Partial deduction per late event |
| Late return (per occurrence) | -15 | Cumulative |
| Reported damage (per occurrence) | -20 | Cumulative |
| Disputed charge filed (lost) | -10 | Reversed if dispute won |
| Missing accessories (per event) | -10 | Reduced further if repeat |
| Failed to return product | -50 + LOCKED | Account permanently flagged |

### 4.4 Trust Tier — Rental Access Permissions

| Tier | Score | Max Rental Value | Deposit Rate | Additional Action |
|------|-------|------------------|--------------|-------------------|
| Unverified | 0–29 | NOT ALLOWED | N/A | Must complete KYC |
| Basic | 30–49 | Up to ₹5,000 | 50% | Admin notified for rentals > ₹2,000 |
| Standard | 50–69 | Up to ₹25,000 | 30% | Normal checkout flow |
| Trusted | 70–84 | Up to ₹1,00,000 | 20% | Expedited checkout |
| VIP | 85–100 | Unlimited | 10% | Priority support |

---

## 5. Core Rental Workflows

### 5.1 Online Rental Flow (Portal / App)

| Step | Action |
|------|--------|
| 1 | Customer logs in → Trust Score and KYC status checked |
| 2 | Browse product catalog → Filter by category, availability, rental period |
| 3 | Select product → View full details: photos, accessories, rates, deposit, late fee |
| 4 | Select rental period (hourly / daily / weekly / monthly) |
| 5 | Choose delivery method — Home delivery OR Store pickup |
| 6 | Add to cart → Review order summary |
| 7 | Review and sign Digital Rental Agreement → OTP confirmation |
| 8 | Payment → Rental fee charged. Deposit pre-authorized (hold on card). |
| 9 | Confirmation screen → Order ID generated. Invoice downloadable. |
| 10 | Pickup reminder scheduled automatically |

### 5.2 Cart & Checkout Rules
- Only one rental of the same product allowed per customer at a time
- If product becomes unavailable between cart and checkout → customer notified
- Coupon / promotional code field (admin-configurable discounts)
- GST calculation applied automatically based on product category

### 5.3 Offline / In-Store Rental Flow (Walk-in)

#### Walk-in Flow Steps

| Step | Action |
|------|--------|
| 1 | Admin searches for existing customer by phone number or ID |
| 2a | If existing customer → Verify identity → Proceed to Step 4 |
| 2b | If new customer → Admin creates account → KYC manually expedited |
| 3 | Admin sets Trust Score manually for walk-in new customer |
| 4 | Admin selects product and rental period → System checks availability |
| 5 | Admin creates Quotation → Reviews with customer |
| 6 | Customer agrees → Admin confirms → Rental created → Invoice generated |
| 7 | Admin collects payment: cash, card swipe (POS), UPI QR, or card-on-file |
| 8 | Admin collects Security Deposit: cash or card hold |
| 9 | Pre-pickup inspection → QR scanned → Accessories checked → Photos uploaded |
| 10 | Product handed over → Chain of Custody: Warehouse → Customer Pickup |

#### Return (Walk-in)
- Customer arrives at store by the agreed return deadline
- Admin scans the product QR → System checks: correct product? serial number? on time?
- Admin performs return inspection → Condition, accessories check, photos uploaded
- System calculates deposit settlement: full refund OR deductions applied
- Cash/card refund issued → Customer signs acknowledgment → Rental closed

---

## 6. Chain of Custody

Every rental asset has a complete, tamper-proof digital custody trail. Every handoff is recorded with multi-point evidence.

### 6.1 Custody Stages

| Stage | Custodian | Evidence Captured | Trigger to Next Stage |
|-------|-----------|-------------------|----------------------|
| 1. Warehouse / Storage | Business | Inventory record, serial number, last inspection date | Rental confirmed → Pre-Pickup Inspection scheduled |
| 2. Pre-Pickup Inspection | Business (Staff) | Staff scans QR. Photos of all sides. Accessory-by-accessory checklist. Condition rating (1–5). | Inspection approved → Ready for Pickup |
| 3. Customer Pickup / Handoff | Both parties | Customer scans QR. Staff scans QR. BOTH must confirm. Customer digital signature. GPS location logged. | Both confirmations → In Customer Possession |
| 4. In Customer Possession | Customer | Rental timer running. Automated reminders scheduled. Return deadline visible. | Customer initiates return OR overdue timer triggers |
| 5. Return Initiated | Transition | Customer marks return in app OR collection team dispatched | Staff begins Return Inspection |
| 6. Return Inspection | Business (Staff) | Staff scans QR → system checks. Photos. Accessory checklist. Damage report if needed. | Inspection complete → Deposit Settlement |
| 7. Deposit Settlement | Finance (System) | System auto-calculates: deposit minus deductions. Itemized breakdown shown. Refund issued. | Settlement confirmed → Rental closed |
| 8. Back to Warehouse | Business | If clean: marked Available. If damaged: Repair Workflow initiated. | Rental cycle complete OR Repair begins |

### 6.2 Evidence Captured at Every Handoff

- **Timestamp** — server-side only. Client timestamps cannot be used.
- **GPS coordinates** of the scan location
- **Employee ID** of the staff member who performed the action
- **Customer ID** and digital acknowledgment / signature
- **Product ID + Serial Number + QR/Barcode scan result**
- **Condition rating (1–5)** with mandatory photos minimum: front, back, left side, right side, top
- **Accessories checklist** — every item confirmed present/absent individually
- **Digital signature** OR biometric confirmation (fingerprint on mobile)
- **Device fingerprint** of every device used at handoff
- **Internet connection status** at time of scan (if offline, sync queued)

### 6.3 Missing Accessories Management

Every product has a defined **Bill of Materials (BoM)** — a complete list of every component that must leave and return with the product. Accessories are tracked individually, not as a group.

#### Example BoM — Camera Rental

| # | Item Name | Item Code | Replacement Cost | Required at Pickup | Required at Return |
|---|-----------|-----------|------------------|--------------------|--------------------|
| 1 | Camera Body | CAM-BODY-001 | ₹45,000 | Yes | Yes |
| 2 | Battery (LP-E6) | CAM-BAT-001 | ₹2,500 | Yes | Yes |
| 3 | Battery Charger | CAM-CHG-001 | ₹1,800 | Yes | Yes |
| 4 | Memory Card 64GB | CAM-MEM-001 | ₹900 | Yes | Yes |
| 5 | Lens 18-55mm | CAM-LENS-001 | ₹12,000 | Yes | Yes |
| 6 | Lens Cap 58mm | CAM-CAP-001 | ₹200 | Yes | Yes |
| 7 | Carrying Case | CAM-CASE-001 | ₹1,500 | Yes | Yes |

**At Pickup:** 7/7 items confirmed ✅ — stamped in chain of custody with staff ID and timestamp.
**At Return:** 6/7 items confirmed — Missing: Battery Charger ❌ — Replacement cost ₹1,800 auto-deducted from deposit.

#### Missing Item Resolution Flow

| Step | Action | Actor |
|------|--------|-------|
| 1 | Return inspection detects missing accessory | System (auto-detect) |
| 2 | Missing Item Case created automatically | System |
| 3 | Replacement cost pre-configured per accessory | Admin (pre-set) |
| 4 | Amount deducted from security deposit | System |
| 5 | If deposit insufficient → Invoice generated for balance | System |
| 6 | Card on file charged automatically | Razorpay |
| 7 | Customer receives itemized breakdown notification instantly | System |
| 8 | Admin can override deduction amount within 24 hours | Admin |
| 9 | Customer has 48 hours to return the missing item and avoid the charge | Customer |

#### Missing Item Case Data

| Field | Description |
|-------|-------------|
| Case ID | Auto-generated: MIS-2026-00001 |
| Rental ID | Linked rental |
| Product ID | Product with missing accessory |
| Accessory Name | "Battery Charger" |
| Accessory Code | "CAM-CHG-001" |
| Replacement Cost | ₹1,800 (pre-configured) |
| Detected At | Return inspection timestamp |
| Detected By | Staff member ID |
| Deduction Amount | ₹1,800 |
| Customer Notified | Yes/No + timestamp |
| Resolution | Pending / Item Returned / Charge Applied |

---

### 6.4 Anti-Swap & Product Identity Protection

A customer renting Sony Camera Unit A (Serial: CAM-A-19282) **cannot** return Sony Camera Unit B (Serial: CAM-B-88372). Even if the models look identical, the system catches the swap immediately.

#### Identity Verification at Return

| Check | Method | Pass | Fail Action |
|-------|--------|------|-------------|
| **QR Code Scan** | Staff scans QR on returned product | QR matches product ID in rental record | Return BLOCKED. Exception Case created. Admin alerted. |
| **Serial Number Match** | Staff manually reads or OCR-scans serial number | Serial matches product ID in database | Mismatch blocks return completion |
| **RFID / IoT Check** | RFID reader confirms tag ID (if hardware present) | Tag ID matches asset record | Tag mismatch → Exception Case created |
| **Barcode Scan** | Secondary barcode scan if QR fails | Barcode matches | All three fail → mandatory manual Admin review |

#### Damaged QR Code Protocol

| Scenario | Protocol |
|----------|----------|
| QR sticker torn/removed | Field agent CANNOT complete return independently |
| Agent submits Exception Report | Product description, visible serial number, condition photos |
| Admin manually verifies | Serial number + cross-checks condition photos vs pre-pickup |
| Admin approves or rejects | Every manual override logged in Audit Trail |
| Serial cannot be confirmed | Product held in warehouse, customer notified, investigation opened |

#### Legal Binding

The Digital Rental Agreement explicitly states:

> *"This agreement legally binds you to the specific asset with Product ID [CAM-A-19282] and Serial Number [SN-19282-CAM]. Returning a different unit constitutes fraud and will result in immediate legal action."*

This clause is shown prominently and requires a **separate checkbox confirmation** during agreement signing.

---

### 6.5 Product Condition Tracking

Every product has a condition history tracked across all rentals.

| Condition Event | Data Captured | Trigger |
|-----------------|---------------|---------|
| **Purchase** | Purchase date, price, initial condition (5/5) | Product creation |
| **Pre-Pickup Inspection** | Photos, condition rating, accessory check | Before every rental |
| **Return Inspection** | Photos, condition rating, damage reports | After every rental |
| **Repair** | Repair case photos, cost, before/after | Damage identified |
| **Maintenance** | Maintenance type, cost, technician notes | Scheduled maintenance |

#### Condition Rating Scale

| Rating | Label | Description | Action |
|--------|-------|-------------|--------|
| 5 | Excellent | Like new, no wear | Available for rental |
| 4 | Good | Minor cosmetic wear, fully functional | Available for rental |
| 3 | Fair | Visible wear, fully functional | Available with disclosure |
| 2 | Poor | Significant wear, may have minor issues | Discounted rental or repair |
| 1 | Damaged | Non-functional or major damage | Repair required before rental |

---

## 7. Security Deposit Engine

### 7.1 Dynamic Deposit Calculation

Deposit is calculated dynamically per rental based on risk signals from the Trust Score system.

| Factor | Adjustment | Reason |
|--------|------------|--------|
| Base deposit | Configurable % (default: 30%) | Admin sets per product category |
| New customer — no rental history | +20% | No behavioral data available |
| Low trust score (30–49) | +15% | Higher risk profile |
| High-value item (above ₹25,000) | +10% | Higher replacement cost |
| Long rental period (above 7 days) | +5% | More time = more exposure |
| VIP customer (score 85+) | -10% | Proven, reliable renter |
| 5+ rentals — all returned on time | -5% | Loyalty reward |

### 7.2 Deposit Payment & Hold Methods

| Method | How It Works | Refund Method |
|--------|--------------|---------------|
| Credit Card Pre-Authorization | Card held via Razorpay auth hold. Customer NOT charged. | Hold released → within 3-5 business days |
| Debit Card Authorization Hold | Same as credit card — hold on account balance. | Hold released → balance restored within 3-5 days |
| Cash Deposit | Admin collects cash, records in system. Receipt printed. | Cash refunded in person at store |
| UPI / Bank Transfer | Customer transfers to business account. | Bank transfer back within 24 hours of return |

### 7.3 Deposit Settlement at Return

| Scenario | Action |
|----------|--------|
| ON TIME + NO DAMAGE + ALL ACCESSORIES | Full deposit refunded within 24 hours |
| LATE RETURN | Refund = Deposit minus Late Fee. Remaining refunded. |
| DAMAGE FOUND | Refund = Deposit minus Damage Assessment. Remaining refunded. |
| MISSING ACCESSORIES | Refund = Deposit minus Replacement Cost(s). Remaining refunded. |
| MULTIPLE DEDUCTIONS | All stacked. Itemized breakdown shown to customer. |
| DEDUCTIONS EXCEED DEPOSIT | Full deposit forfeited. Invoice generated for balance. Card on file charged. |

### 7.4 Deposit History & Audit Trail
- Every deposit event is recorded: creation, authorization, deduction, refund, cancellation
- Customer can view their own deposit history in the portal
- Admin can view deposit status across all active rentals in one screen
- Deposit ledger exportable as CSV or PDF for accounting purposes

---

## 8. Late Return & Escalation

### 8.1 Automated Reminder & Escalation Timeline

| Time | Event | System Action | Channel |
|------|-------|---------------|---------|
| T - 48 hours | Early reminder | Return reminder with item details and deadline | Email |
| T - 24 hours | Pre-return reminder | Your rental is due tomorrow at [time] | SMS + Email + Push |
| T - 2 hours | Final reminder | Your rental is due in 2 hours | SMS + Push |
| T + 0 (due) | Deadline reached | Admin dashboard alert triggered. Customer final notice. | All channels + Admin |
| T + 30 minutes | Within grace period | Grace period warning | SMS + Push |
| T + 1 hour | Late fee begins | Late fee calculation starts. Current fee shown in app. | SMS + Email |
| T + 6 hours | Running fee update | Your current late fee is ₹[X] | SMS + Email |
| T + 24 hours | Overdue status | Account status → OVERDUE. High-priority on dashboard. | All channels + Admin |
| T + 48 hours | High-priority alert | Admin gets priority alert. Collection team checked. | Internal admin alert |
| T + 72 hours | Collection dispatch | Field team dispatched to customer address | Internal ops notification |
| T + 7 days | Legal escalation | Legal notice template auto-generated. Legal team notified. | Customer formal notice |

### 8.2 Late Fee Calculation Rules
- Configurable per product category: cameras, bikes, furniture, electronics
- Charging modes: Hourly / Daily / Weekly / Monthly — admin picks per product
- Grace period: configurable per product (default: 30 minutes)
- Maximum late fee cap: prevents unlimited accumulation (e.g., max 2× rental value)
- Late fee auto-deducted from deposit. Remaining deposit refunded.
- If late fee exceeds deposit: Invoice auto-generated. Card on file charged.

### 8.3 Asset Recovery Workflow

| Stage | Status | Who Acts | System Action |
|-------|--------|----------|---------------|
| 1 | Overdue | System | Automated reminders + late fee accruing |
| 2 | No Response (24h) | Operations Admin | Admin manually calls customer |
| 3 | Confirmed Not Returning | Operations Admin | Recovery Case created |
| 4 | Collection Dispatch | Field Agent | Agent assigned. Dispatched to address. GPS tracked. |
| 5 | Product Not at Address | Super Admin + Legal | FIR template generated. Legal team notified. |
| 6 | Legal Action | Legal Team | Rental agreement submitted as evidence. |
| 7 | Product Recovered | Operations Admin | Full inspection. Final late fees. Account blacklisted. |

### 8.4 Recovery Case — Complete Data Package

- **Customer**: full name, KYC-verified government ID, verified phone, verified address, profile photo
- **Product**: name, Product ID, Serial Number, QR code, estimated current value
- **Financials**: rental value, deposit amount collected, days overdue, total accrued late fee
- **Location**: GPS coordinates from last confirmed pickup scan, registered home address
- **Communication log**: every reminder sent, every channel, every delivery receipt, every call attempt
- **Rental history**: all past rentals, return behavior, trust score history
- **Legal documents**: signed rental agreement, pre-pickup inspection report with photos
- **FIR Template**: pre-filled with all the above — admin just reviews and files

---

## 9. Group Rental System

### 9.1 Group Creation Flow

| Step | Action | Actor |
|------|--------|-------|
| 1 | User clicks "Create Group" | KYC-verified Personal user |
| 2 | Enters group name, selects max members (2-20) | Group Leader |
| 3 | System creates group, assigns leader | System |
| 4 | Leader invites members via phone/email | Group Leader |
| 5 | Members receive invite, accept via link | Invited Members |
| 6 | All members must complete KYC (min. Basic tier) | Each Member |
| 7 | Group Trust Score calculated when all members verified | System |

### 9.2 Group Rental Flow

| Step | Action | Actor |
|------|--------|-------|
| 1 | Leader browses catalog, selects product | Group Leader |
| 2 | System checks Group Trust Score vs. product requirements | System |
| 3 | Leader selects rental period | Group Leader |
| 4 | System calculates total deposit based on Group Trust Score | System |
| 5 | Leader configures deposit split (equal or custom %) | Group Leader |
| 6 | Each member receives deposit split notification | System |
| 7 | Each member pays their share via their own card | Each Member |
| 8 | When all shares collected → Rental confirmed | System |
| 9 | Multi-signatory agreement generated, sent to all members | System |
| 10 | All members sign via OTP e-sign | All Members |
| 11 | Product handed over → Chain of Custody begins | Field Agent |

### 9.3 Group Return & Settlement Flow

| Step | Action | Actor |
|------|--------|-------|
| 1 | Product returned (by leader or designated member) | Group Member |
| 2 | Return inspection performed | Operations Admin |
| 3 | System calculates total deductions (late fee, damage, missing items) | System |
| 4 | Deductions distributed proportionally across all members | System |
| 5 | Each member's deposit share independently settled | Razorpay |
| 6 | All members notified of settlement outcome | System |
| 7 | All members' individual trust scores updated | System |
| 8 | Group Trust Score recalculated | System |

### 9.4 Group Voting System

For group decisions (extension requests), the system implements a voting mechanism:

| Rule | Details |
|------|---------|
| Voting trigger | Extension request requires majority approval |
| Approval threshold | >50% of members must approve |
| Voting window | 24 hours from request |
| Default action | If no votes cast, request is denied |
| Vote visibility | All votes are visible to all members |
| Leader override | No — leader cannot override member votes |

---

## 10. Enterprise Features

### 10.1 Enterprise Account Management

| Feature | Description |
|---------|-------------|
| Entity KYC | GST + PAN + Director Aadhaar verification |
| Team Management | Invite/remove sub-users with role-based access |
| Custom Pricelist | Negotiated corporate pricing applied to all team members |
| Credit Billing | Net 30 payment terms after creditworthiness approval |
| GST Invoices | Full B2B invoices with enterprise GSTIN |
| Bulk Rentals | Rent multiple products in a single purchase order |
| Dedicated Account Manager | Assigned human support contact |
| API Access | REST API for ERP integration |

### 10.2 Enterprise Billing Dashboard

| Metric | Description |
|--------|-------------|
| Total Rentals (Month) | All team rentals in current month |
| Pending Invoices | Unpaid invoices with due dates |
| Credit Utilization | Current credit usage vs. credit limit |
| Team Activity | Which team members are renting most |
| Cost Center Breakdown | Rentals by department/category |

---

## 11. System Architecture & Tech Stack

### 11.1 High-Level Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              FRONTEND                                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │  Customer     │  │  Admin       │  │  Enterprise  │  │  Field Agent │   │
│  │  Portal       │  │  Dashboard   │  │  Portal      │  │  App         │   │
│  │  (Next.js)    │  │  (Next.js)   │  │  (Next.js)   │  │  (React)     │   │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              LOAD BALANCER                                  │
│                         Cloudflare Free / Nginx                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           API GATEWAY / REVERSE PROXY                       │
│                              Nginx / Caddy                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │  Rate         │  │  SSL/TLS     │  │  Request     │  │  CORS        │   │
│  │  Limiting     │  │  Termination │  │  Routing     │  │  Headers     │   │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           BACKEND API SERVERS                                │
│                         FastAPI (Python 3.12)                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │  Auth         │  │  Business    │  │  WebSocket   │  │  Background  │   │
│  │  Service      │  │  Logic       │  │  Handler     │  │  Jobs (ARQ)  │   │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    ▼               ▼               ▼
┌───────────────────────┐ ┌───────────────────────┐ ┌───────────────────────┐
│     PRIMARY DB        │ │       CACHE           │ │    FILE STORAGE       │
│  PostgreSQL (NeonDB)  │ │    Redis (Upstash)    │ │  Cloudflare R2        │
│  ┌──────────────┐     │ │  ┌──────────────┐     │ │  ┌──────────────┐     │
│  │  Write         │     │ │  │  Session       │     │ │  │  KYC Docs     │     │
│  │  Operations    │     │ │  │  Store         │     │ │  │  Photos        │     │
│  └──────────────┘     │ │  └──────────────┘     │ │  └──────────────┘     │
│  ┌──────────────┐     │ │  ┌──────────────┐     │ │  ┌──────────────┐     │
│  │  Read          │     │ │  │  Rate Limit    │     │ │  │  Invoices      │     │
│  │  Replica       │     │ │  │  Counters      │     │ │  │  Agreements    │     │
│  └──────────────┘     │ │  └──────────────┘     │ │  └──────────────┘     │
└───────────────────────┘ └───────────────────────┘ └───────────────────────┘
                    │               │               │
                    └───────────────┼───────────────┘
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          EXTERNAL SERVICES                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │  Razorpay     │  │  Digio        │  │  Twilio/     │  │  Firebase    │   │
│  │  (Payments)   │  │  (e-KYC)      │  │  MSG91 (SMS) │  │  (Push)      │   │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │  Resend       │  │  FaceIO       │  │  Tesseract   │  │  Surepass    │   │
│  │  (Email)      │  │  (Face)       │  │  (OCR)       │  │  (PAN/GST)   │   │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 11.2 Technology Stack Summary

| Layer | Technology | Why This Choice |
|-------|------------|-----------------|
| Frontend (Web) | Next.js 14 + React 18 + Tailwind CSS | SSR + SSG + ISR; SEO for catalog; streaming |
| UI Components | shadcn/ui | Accessible, composable, no runtime cost |
| State Management | Zustand + TanStack Query | Lightweight global state; server-state sync |
| Forms | React Hook Form + Zod | Type-safe validation; minimal re-renders |
| Real-time | Native WebSocket API + custom hook | Dashboard live updates |
| Charts | Recharts (open source) | KPI dashboard widgets |
| QR Scanning | ZXing-js (open source) | Browser-based QR scan for field agents |
| Backend API | FastAPI (Python 3.12) | Async-first; auto OpenAPI docs; Pydantic v2 |
| ORM | SQLAlchemy (async) + asyncpg | Non-blocking PostgreSQL queries |
| Primary Database | PostgreSQL 16 on NeonDB | Relational model; ACID transactions |
| Cache | Redis (Upstash) | Session management; rate limiting; pub/sub |
| File Storage | Cloudflare R2 | 10GB free; zero egress fees; S3-compatible |
| WebSocket | FastAPI WebSocket + Redis Pub/Sub | Real-time dashboard updates |
| Background Jobs | ARQ + Redis | Async Python job queue |
| Authentication | JWT + Refresh Tokens | Secure stateless auth with rotation |
| e-KYC | Digio sandbox + FaceIO + Tesseract | Free tier stack |
| Payments | Razorpay | Card tokenization; authorization holds |
| SMS | Twilio / MSG91 | OTP delivery with receipts |
| Email | Resend | 3,000 emails/month free |
| Push | Firebase Cloud Messaging | iOS + Android push |
| Rate Limiting | slowapi + Nginx | Multi-layer defense |
| Load Balancing | Cloudflare Free / Nginx | DNS-level + reverse proxy |
| CDN | Cloudflare Free | Global asset delivery |
| TLS Certificate | Let's Encrypt / Cloudflare | Free auto-renewal |

---

## 12. Database Design

### 12.1 Multi-Database Architecture

| Database | Purpose | Technology |
|----------|---------|------------|
| Primary DB | All operational data (users, rentals, products, payments) | PostgreSQL 16 on NeonDB |
| Cache DB | Sessions, rate limits, OTPs, real-time pub/sub | Redis (Upstash) |
| Search Index | Full-text search on products, users | PostgreSQL Full-Text Search (built-in) |
| Audit Log DB | Immutable audit trail | Separate PostgreSQL schema (audit.*) |
| Analytics DB | Pre-computed aggregates for dashboards | PostgreSQL materialized views |

### 12.2 Connection Pooling Strategy

- **NeonDB built-in PgBouncer** in transaction mode
- **FastAPI uses asyncpg** — non-blocking queries
- **Connection pool size**: min=2, max=10 per API instance
- **Health check**: SELECT 1 every 30s; dead connections replaced automatically
- **Read replicas**: NeonDB supports read replicas — route GET-heavy endpoints to replica

### 12.3 Database Clustering Strategy

| Strategy | Implementation | Benefit |
|----------|----------------|---------|
| Primary-Replica | NeonDB primary (writes) + 1 read replica (reads) | Read throughput doubled |
| Connection Pooling | PgBouncer transaction mode | 10,000 virtual → 10 physical connections |
| Schema Separation | public (operational), audit (immutable), analytics (aggregated) | Independent query paths |
| Table Partitioning | audit_logs by month; rentals by quarter | Partition pruning; old data archived |
| Horizontal Sharding (future) | When > 10M rentals: shard by user_id hash | Linear scale |

### 12.4 Complete Database Schema

#### Table: users

| Column | Type | Constraints / Notes |
|--------|------|---------------------|
| id | UUID | PRIMARY KEY, DEFAULT gen_random_uuid() |
| user_type | ENUM(personal, enterprise, enterprise_sub) | NOT NULL, DEFAULT personal |
| role | ENUM(super_admin, ops_admin, field_agent, portal_user) | NOT NULL |
| phone | VARCHAR(15) | UNIQUE, NOT NULL |
| email | VARCHAR(255) | UNIQUE, NOT NULL |
| password_hash | VARCHAR(255) | NULLABLE (NULL if OTP-only login) |
| name | VARCHAR(255) | NOT NULL |
| dob | DATE | NULLABLE |
| kyc_status | ENUM(pending, in_progress, verified, rejected) | DEFAULT pending |
| trust_score | SMALLINT | DEFAULT 0, CHECK (0 <= trust_score <= 100) |
| trust_tier | ENUM(unverified, basic, standard, trusted, vip) | GENERATED from trust_score via trigger |
| enterprise_id | UUID | FK → enterprises.id, NULLABLE |
| blacklisted | BOOLEAN | DEFAULT false |
| device_fingerprints | TEXT[] | Array of known device fingerprints |
| created_at | TIMESTAMPTZ | DEFAULT NOW() |
| updated_at | TIMESTAMPTZ | AUTO-UPDATE via trigger |

#### Table: enterprises

| Column | Type | Notes |
|--------|------|-------|
| id | UUID | PRIMARY KEY |
| name | VARCHAR(255) | Business name |
| gst_number | VARCHAR(20) | UNIQUE; verified via GST API |
| pan | VARCHAR(12) | Business PAN; verified |
| registered_address | JSONB | {street, city, state, pincode} |
| kyc_status | ENUM(pending, verified, rejected) | |
| trust_score | SMALLINT | Entity-level trust (0–100) |
| credit_line_enabled | BOOLEAN | DEFAULT false |
| credit_limit_inr | NUMERIC(12,2) | NULL if no credit line |
| pricelist_id | UUID | FK → pricelists.id; custom enterprise pricing |
| account_manager_id | UUID | FK → users.id (ops_admin role) |
| created_at | TIMESTAMPTZ | |

#### Table: enterprise_members

| Column | Type | Notes |
|--------|------|-------|
| id | UUID | PRIMARY KEY |
| enterprise_id | UUID | FK → enterprises.id ON DELETE CASCADE |
| user_id | UUID | FK → users.id |
| sub_role | ENUM(admin, procurement, department_user, auditor) | NOT NULL |
| department | VARCHAR(100) | NULLABLE |
| spending_limit_inr | NUMERIC(12,2) | NULLABLE; max rental value per order |
| created_at | TIMESTAMPTZ | |
| UNIQUE(enterprise_id, user_id) | | |

#### Table: groups

| Column | Type | Notes |
|--------|------|-------|
| id | UUID | PRIMARY KEY |
| name | VARCHAR(255) | Group name (e.g., "College Trip Crew") |
| leader_id | UUID | FK → users.id; Group Leader |
| trust_score | NUMERIC(5,2) | GENERATED: weighted avg of member scores |
| trust_tier | ENUM(unverified, basic, standard, trusted, vip) | GENERATED from trust_score |
| status | ENUM(active, dissolved, suspended) | DEFAULT active |
| max_members | SMALLINT | DEFAULT 20, CHECK (max_members <= 20) |
| created_at | TIMESTAMPTZ | |

#### Table: group_members

| Column | Type | Notes |
|--------|------|-------|
| id | UUID | PRIMARY KEY |
| group_id | UUID | FK → groups.id ON DELETE CASCADE |
| user_id | UUID | FK → users.id |
| joined_at | TIMESTAMPTZ | |
| status | ENUM(invited, active, removed) | DEFAULT invited |
| deposit_share_pct | NUMERIC(5,2) | Percentage of group deposit this member pays |
| UNIQUE(group_id, user_id) | | |

#### Table: group_deposits

| Column | Type | Notes |
|--------|------|-------|
| id | UUID | PRIMARY KEY |
| rental_id | UUID | FK → rentals.id |
| group_id | UUID | FK → groups.id |
| total_amount | NUMERIC(12,2) | Total deposit for the group rental |
| status | ENUM(pending, collecting, held, settled, forfeited) | |
| settled_at | TIMESTAMPTZ | |

#### Table: group_deposit_members

| Column | Type | Notes |
|--------|------|-------|
| id | UUID | PRIMARY KEY |
| group_deposit_id | UUID | FK → group_deposits.id |
| user_id | UUID | FK → users.id |
| amount | NUMERIC(12,2) | This member's deposit share |
| payment_status | ENUM(pending, authorized, failed, released, forfeited) | |
| authorization_code | VARCHAR(255) | Razorpay auth hold reference |
| refund_amount | NUMERIC(12,2) | Amount refunded to this member |
| refund_at | TIMESTAMPTZ | |

#### Table: group_votes

| Column | Type | Notes |
|--------|------|-------|
| id | UUID | PRIMARY KEY |
| group_id | UUID | FK → groups.id |
| rental_id | UUID | FK → rentals.id |
| vote_type | ENUM(extension, dispute, other) | |
| requested_by | UUID | FK → users.id |
| status | ENUM(pending, approved, rejected, expired) | |
| expires_at | TIMESTAMPTZ | 24 hours from request |
| created_at | TIMESTAMPTZ | |

#### Table: group_vote_records

| Column | Type | Notes |
|--------|------|-------|
| id | UUID | PRIMARY KEY |
| vote_id | UUID | FK → group_votes.id |
| user_id | UUID | FK → users.id |
| vote | ENUM(approve, reject) | |
| voted_at | TIMESTAMPTZ | |
| UNIQUE(vote_id, user_id) | | |

#### Table: products

| Column | Type | Notes |
|--------|------|-------|
| id | UUID | PRIMARY KEY |
| name | VARCHAR(255) | NOT NULL |
| category_id | UUID | FK → categories.id |
| description | TEXT | |
| serial_number | VARCHAR(100) | UNIQUE |
| qr_code | VARCHAR(255) | UNIQUE; generated on creation |
| rfid_tag | VARCHAR(100) | NULLABLE; for IoT-enabled products |
| status | ENUM(available, rented, in_repair, inactive) | DEFAULT available |
| current_holder_id | UUID | FK → users.id; NULL if in warehouse |
| deposit_percentage | NUMERIC(5,2) | DEFAULT 30.00; can be overridden by pricelist |
| late_fee_rate | NUMERIC(10,2) | Per day; configurable |
| late_fee_mode | ENUM(hourly, daily, weekly, monthly) | DEFAULT daily |
| grace_period_minutes | INTEGER | DEFAULT 30 |
| max_late_fee_multiplier | NUMERIC(3,1) | DEFAULT 2.0; max 2x rental value |
| created_at | TIMESTAMPTZ | |
| updated_at | TIMESTAMPTZ | |

#### Table: product_variants

| Column | Type | Notes |
|--------|------|-------|
| id | UUID | PRIMARY KEY |
| product_id | UUID | FK → products.id ON DELETE CASCADE |
| attribute | VARCHAR(50) | e.g., color, size, brand, model |
| value | VARCHAR(100) | e.g., Red, Large, Canon |
| sku | VARCHAR(100) | UNIQUE; stock keeping unit |
| additional_price_inr | NUMERIC(10,2) | DEFAULT 0; price adjustment |

#### Table: categories

| Column | Type | Notes |
|--------|------|-------|
| id | UUID | PRIMARY KEY |
| name | VARCHAR(100) | UNIQUE |
| description | TEXT | |
| parent_id | UUID | FK → categories.id; for nested categories |
| deposit_percentage_override | NUMERIC(5,2) | NULLABLE; overrides product default |
| late_fee_rate_override | NUMERIC(10,2) | NULLABLE; overrides product default |

#### Table: accessories (Bill of Materials)

| Column | Type | Notes |
|--------|------|-------|
| id | UUID | PRIMARY KEY |
| product_id | UUID | FK → products.id ON DELETE CASCADE |
| name | VARCHAR(255) | |
| item_code | VARCHAR(100) | UNIQUE per product |
| replacement_cost_inr | NUMERIC(10,2) | Cost if missing at return |
| is_required | BOOLEAN | DEFAULT true; must leave and return |

#### Table: rentals

| Column | Type | Notes |
|--------|------|-------|
| id | UUID | PRIMARY KEY |
| user_id | UUID | FK → users.id (NULL if group rental) |
| group_id | UUID | FK → groups.id (NULL if personal/enterprise) |
| enterprise_id | UUID | FK → enterprises.id (NULL if personal) |
| rental_context | ENUM(personal, enterprise, group) | Determines billing + deposit logic |
| product_id | UUID | FK → products.id |
| status | ENUM(draft, confirmed, active, returned, overdue, cancelled) | |
| start_at | TIMESTAMPTZ | |
| end_at | TIMESTAMPTZ | |
| actual_return_at | TIMESTAMPTZ | NULL until returned |
| rental_fee | NUMERIC(12,2) | |
| agreement_signed_at | TIMESTAMPTZ | |
| agreement_pdf_url | TEXT | Cloudflare R2 URL |
| created_by | UUID | FK → users.id (admin or customer) |
| created_at | TIMESTAMPTZ | |

#### Table: security_deposits

| Column | Type | Notes |
|--------|------|-------|
| id | UUID | PRIMARY KEY |
| rental_id | UUID | FK → rentals.id |
| amount | NUMERIC(12,2) | |
| payment_mode | ENUM(card_auth, cash, upi, bank_transfer) | |
| authorization_code | VARCHAR(255) | Razorpay auth hold reference |
| status | ENUM(held, released, partially_deducted, forfeited) | |
| refund_amount | NUMERIC(12,2) | |
| refund_at | TIMESTAMPTZ | |

#### Table: deposit_deductions

| Column | Type | Notes |
|--------|------|-------|
| id | UUID | PRIMARY KEY |
| deposit_id | UUID | FK → security_deposits.id |
| reason | ENUM(late_fee, damage, missing_accessory, other) | |
| amount | NUMERIC(12,2) | |
| description | TEXT | |
| approved_by | UUID | FK → users.id; admin who approved |

#### Table: custody_events

| Column | Type | Notes |
|--------|------|-------|
| id | UUID | PRIMARY KEY |
| rental_id | UUID | FK → rentals.id |
| product_id | UUID | FK → products.id |
| stage | ENUM(warehouse, pre_pickup, customer_pickup, in_possession, return_initiated, return_inspection, settlement, back_to_warehouse) | |
| actor_id | UUID | FK → users.id (staff or customer) |
| customer_id | UUID | FK → users.id |
| timestamp | TIMESTAMPTZ | Server-side only |
| gps_lat | DECIMAL(9,6) | |
| gps_lng | DECIMAL(9,6) | |
| condition_rating | SMALLINT | CHECK (1 <= rating <= 5) |
| photos | TEXT[] | Array of R2 URLs |
| notes | TEXT | |

#### Table: accessory_check_items

| Column | Type | Notes |
|--------|------|-------|
| id | UUID | PRIMARY KEY |
| custody_event_id | UUID | FK → custody_events.id |
| accessory_id | UUID | FK → accessories.id |
| present | BOOLEAN | |
| condition_note | TEXT | NULLABLE |
| photo_url | TEXT | NULLABLE |

#### Table: late_fees

| Column | Type | Notes |
|--------|------|-------|
| id | UUID | PRIMARY KEY |
| rental_id | UUID | FK → rentals.id |
| grace_period_end | TIMESTAMPTZ | |
| rate_per_unit | NUMERIC(10,2) | Per hour/day/week/month |
| charge_mode | ENUM(hourly, daily, weekly, monthly) | |
| units_overdue | NUMERIC(10,2) | |
| total_amount | NUMERIC(12,2) | |
| status | ENUM(accruing, finalized, invoiced, paid) | |
| invoice_id | UUID | FK → invoices.id; NULL until invoiced |

#### Table: invoices

| Column | Type | Notes |
|--------|------|-------|
| id | UUID | PRIMARY KEY |
| rental_id | UUID | FK → rentals.id |
| type | ENUM(booking, return, penalty, late_fee) | |
| line_items | JSONB | [{name, quantity, unit_price, total}] |
| subtotal | NUMERIC(12,2) | |
| gst | NUMERIC(12,2) | |
| total | NUMERIC(12,2) | |
| pdf_url | TEXT | Cloudflare R2 URL |
| sent_at | TIMESTAMPTZ | |

#### Table: pricelists

| Column | Type | Notes |
|--------|------|-------|
| id | UUID | PRIMARY KEY |
| name | VARCHAR(255) | |
| type | ENUM(default, seasonal, corporate, loyalty, promotional) | |
| start_date | DATE | NULLABLE; for time-bounded pricelists |
| end_date | DATE | NULLABLE |
| applicable_tier | ENUM(unverified, basic, standard, trusted, vip, all) | |
| applicable_user_id | UUID | FK → users.id; NULLABLE; for customer-specific |
| applicable_enterprise_id | UUID | FK → enterprises.id; NULLABLE |
| is_default | BOOLEAN | DEFAULT false; only one default allowed |

#### Table: pricelist_items

| Column | Type | Notes |
|--------|------|-------|
| id | UUID | PRIMARY KEY |
| pricelist_id | UUID | FK → pricelists.id ON DELETE CASCADE |
| product_id | UUID | FK → products.id |
| rate_hourly | NUMERIC(10,2) | |
| rate_daily | NUMERIC(10,2) | |
| rate_weekly | NUMERIC(10,2) | |
| rate_monthly | NUMERIC(10,2) | |

#### Table: quotations

| Column | Type | Notes |
|--------|------|-------|
| id | UUID | PRIMARY KEY |
| admin_id | UUID | FK → users.id |
| customer_id | UUID | FK → users.id |
| product_id | UUID | FK → products.id |
| rental_period | JSONB | {duration, unit} |
| total_fee | NUMERIC(12,2) | |
| deposit_amount | NUMERIC(12,2) | |
| status | ENUM(draft, sent, accepted, confirmed, expired, cancelled) | |
| expires_at | TIMESTAMPTZ | Default 24 hours |
| template_id | UUID | FK → quotation_templates.id; NULLABLE |

#### Table: quotation_templates

| Column | Type | Notes |
|--------|------|-------|
| id | UUID | PRIMARY KEY |
| name | VARCHAR(255) | |
| admin_id | UUID | FK → users.id |
| header_html | TEXT | |
| footer_html | TEXT | |
| default_notes | TEXT | |
| created_at | TIMESTAMPTZ | |

#### Table: disputes

| Column | Type | Notes |
|--------|------|-------|
| id | UUID | PRIMARY KEY |
| rental_id | UUID | FK → rentals.id |
| user_id | UUID | FK → users.id |
| charge_type | ENUM(late_fee, damage, missing_accessory, deposit_refund) | |
| description | TEXT | |
| evidence_urls | TEXT[] | Array of R2 URLs |
| status | ENUM(open, under_review, won, lost, escalated) | |
| admin_decision | TEXT | NULLABLE; reason for decision |
| resolved_by | UUID | FK → users.id |
| resolved_at | TIMESTAMPTZ | |

#### Table: extension_requests

| Column | Type | Notes |
|--------|------|-------|
| id | UUID | PRIMARY KEY |
| rental_id | UUID | FK → rentals.id |
| requested_by | UUID | FK → users.id |
| new_return_at | TIMESTAMPTZ | |
| reason | TEXT | |
| status | ENUM(pending, approved, rejected) | |
| reviewed_by | UUID | FK → users.id; NULLABLE |
| additional_fee | NUMERIC(12,2) | Calculated on approval |

#### Table: repair_cases

| Column | Type | Notes |
|--------|------|-------|
| id | UUID | PRIMARY KEY |
| product_id | UUID | FK → products.id |
| rental_id | UUID | FK → rentals.id; NULLABLE |
| damage_description | TEXT | |
| photos | TEXT[] | Array of R2 URLs |
| repair_cost | NUMERIC(12,2) | NULLABLE until repair complete |
| customer_deduction | NUMERIC(12,2) | Collected from customer |
| status | ENUM(open, in_repair, completed, write_off) | |
| assigned_to | UUID | FK → users.id; NULLABLE |
| completed_at | TIMESTAMPTZ | |

#### Table: recovery_cases

| Column | Type | Notes |
|--------|------|-------|
| id | UUID | PRIMARY KEY |
| rental_id | UUID | FK → rentals.id |
| status | ENUM(open, collection_dispatched, legal_action, recovered, write_off) | |
| assigned_agent_id | UUID | FK → users.id; NULLABLE |
| last_contact_at | TIMESTAMPTZ | |
| contact_log | JSONB | [{timestamp, channel, outcome}] |
| fir_generated | BOOLEAN | DEFAULT false |
| notes | TEXT | |

#### Table: blacklist

| Column | Type | Notes |
|--------|------|-------|
| id | UUID | PRIMARY KEY |
| user_id | UUID | FK → users.id |
| reason | TEXT | |
| evidence_ref | TEXT | |
| blacklisted_by | UUID | FK → users.id (Super Admin) |
| blacklisted_at | TIMESTAMPTZ | |
| reinstated_by | UUID | FK → users.id; NULLABLE |
| reinstated_at | TIMESTAMPTZ | NULLABLE |

#### Table: audit_logs

| Column | Type | Notes |
|--------|------|-------|
| id | UUID | PRIMARY KEY |
| actor_id | UUID | FK → users.id |
| actor_role | ENUM | |
| action | VARCHAR(100) | e.g., rental.create, deposit.settle |
| entity_type | VARCHAR(50) | e.g., rental, product, user |
| entity_id | UUID | |
| before_state | JSONB | NULLABLE |
| after_state | JSONB | |
| ip_address | INET | |
| device_fingerprint | TEXT | |
| timestamp | TIMESTAMPTZ | DEFAULT NOW() |

#### Table: notifications

| Column | Type | Notes |
|--------|------|-------|
| id | UUID | PRIMARY KEY |
| user_id | UUID | FK → users.id |
| type | VARCHAR(50) | e.g., rental_confirmed, overdue_alert |
| channel | ENUM(sms, email, push, in_app) | |
| content | TEXT | |
| delivered_at | TIMESTAMPTZ | |
| opened_at | TIMESTAMPTZ | |
| status | ENUM(pending, delivered, failed, opened) | |

#### Table: refresh_tokens

| Column | Type | Notes |
|--------|------|-------|
| id | UUID | PRIMARY KEY |
| user_id | UUID | FK → users.id |
| token_hash | VARCHAR(255) | SHA-256 hash of opaque token |
| device_fingerprint | TEXT | |
| ip_address | INET | |
| expires_at | TIMESTAMPTZ | 30 days from creation |
| created_at | TIMESTAMPTZ | |
| revoked_at | TIMESTAMPTZ | NULLABLE; set on rotation/logout |

#### Table: rate_limit_events

| Column | Type | Notes |
|--------|------|-------|
| id | UUID | PRIMARY KEY |
| identifier | VARCHAR(255) | IP or user_id |
| endpoint | VARCHAR(255) | |
| window_start | TIMESTAMPTZ | |
| request_count | INTEGER | |
| blocked | BOOLEAN | DEFAULT false |

### 12.5 Indexing Strategy

Every index is justified by a specific query pattern. No index is added speculatively.

| Table | Index | Type | Query it Serves |
|-------|-------|------|-----------------|
| users | idx_users_phone | BTREE UNIQUE | Login by phone; OTP lookup |
| users | idx_users_email | BTREE UNIQUE | Login by email; KYC email lookup |
| users | idx_users_trust_tier | BTREE | Admin: filter customers by tier |
| users | idx_users_blacklisted | PARTIAL (WHERE blacklisted=true) | Blacklist check at registration |
| users | idx_users_name_tsvector | GIN | Full-text search on customer name |
| rentals | idx_rentals_user_id | BTREE | Customer: my orders |
| rentals | idx_rentals_group_id | BTREE | Group: all group rentals |
| rentals | idx_rentals_status | BTREE | Admin dashboard: filter by status |
| rentals | idx_rentals_end_at | BTREE | Background job: find overdue rentals |
| rentals | idx_rentals_product_id_status | COMPOSITE | Check product availability |
| products | idx_products_status | BTREE | Catalog: filter available products |
| products | idx_products_name_tsvector | GIN | Full-text product search |
| products | idx_products_category_id_status | COMPOSITE | Browse by category + available |
| audit_logs | idx_audit_actor_id_created | COMPOSITE | Admin: audit trail per user |
| custody_events | idx_custody_rental_id | BTREE | Chain of custody per rental |
| group_members | idx_group_members_user_id | BTREE | User: find all groups they belong to |
| notifications | idx_notifications_user_status | COMPOSITE | Unread notification count |

### 12.6 Query Optimization Patterns

- Use `EXPLAIN ANALYZE` on every query in staging before production deploy
- Avoid N+1: all list endpoints use JOIN or prefetch (SQLAlchemy selectinload)
- Pagination: KEYSET pagination (`WHERE id > :last_id`) not OFFSET for large tables
- Read-heavy endpoints (catalog, dashboard aggregates) served from Redis cache; TTL 30s
- Heavy aggregates run as materialized views refreshed every 5 minutes
- Materialized view example: `mv_admin_dashboard` — pre-computes active rental count, overdue count, today's revenue

---

## 13. Authentication & Security

### 13.1 Token Architecture

#### Access Token
- Type: JWT (HS256)
- Payload: user_id, role, user_type, enterprise_id (if applicable), iat, exp
- TTL: 15 minutes
- Storage: httpOnly, Secure, SameSite=Strict cookie

#### Refresh Token
- Type: Opaque random string (32 bytes, hex)
- Stored: Hashed in PostgreSQL (refresh_tokens table) + Redis cache
- TTL: 30 days (rolling)
- Rotation: Every refresh call invalidates old token and issues new one
- Storage: httpOnly cookie (separate from access token)

### 13.2 Auth Flows

| Flow | Steps | Security Notes |
|------|-------|----------------|
| Login (phone+OTP) | 1. POST /auth/otp/send → OTP in Redis (TTL 5min) 2. POST /auth/otp/verify → issue tokens | OTP rate-limited: 3 sends per 15min |
| Login (email+password) | 1. POST /auth/login → bcrypt verify 2. Issue tokens | Failed login lockout: 5 attempts → 15min ban |
| Token Refresh | 1. POST /auth/refresh → validate refresh hash 2. Rotate: delete old, issue new pair | Old token immediately invalidated |
| Logout | 1. POST /auth/logout → delete refresh token 2. Clear cookies | All devices or specific device |
| Multi-device Sessions | Each device gets own refresh token | Max 5 active sessions |
| Google/Apple SSO | OAuth2 code flow → backend exchanges → issue our JWT | We own the session |

### 13.3 RBAC Permission Matrix (Key Endpoints)

| Endpoint | Personal | Ent. Admin | Ent. Sub-user | Group Leader | Ops Admin | Super Admin |
|----------|----------|------------|---------------|--------------|-----------|-------------|
| POST /rentals/ | Own only | Yes (team) | Request only | Group context | Yes | Yes |
| GET /admin/dashboard | No | No | No | No | Yes | Yes |
| PATCH /users/{id}/blacklist | No | No | No | No | Propose only | Yes |
| POST /deposits/{id}/settle | No | No | No | No | Up to threshold | Yes |
| GET /enterprise/{id}/team | No | Own org | Own org (read) | No | Yes | Yes |
| POST /groups/{id}/rental | No | No | No | Own group | Yes | Yes |

### 13.4 FastAPI Middleware Stack

Every request flows through the following middleware in order:

1. **HTTPS Enforcement** — HSTS header injected; HTTP → HTTPS redirect at Nginx level
2. **CORS Middleware** — Allowed origins: Next.js domain only
3. **Rate Limiter (slowapi)** — Multi-layer rate limiting
4. **Request ID Middleware** — UUID injected into every request for tracing
5. **JWT Auth Middleware** — Validates access token; sets request.state.user
6. **RBAC Middleware** — Checks user role against endpoint permission matrix
7. **Audit Logger** — Logs all write operations async
8. **Response Compression** — gzip/brotli for responses > 1KB

---

## 14. Performance & Scaling

### 14.1 WebSocket — Real-Time Dashboard

#### WebSocket Architecture
- Technology: FastAPI native WebSocket + Redis Pub/Sub
- Pattern: Client connects → FastAPI validates JWT → subscribes to Redis channel → receives events

#### WebSocket Channels & Events

| Channel | Who Subscribes | Events Published |
|---------|----------------|------------------|
| ws:admin:global | All admin dashboard connections | new_overdue, new_rental, new_dispute, system_alert |
| ws:admin:{admin_id} | Specific admin | Personal alerts, assigned recovery cases |
| ws:rental:{rental_id} | Customer + admin viewing rental | status_change, late_fee_update, inspection_complete |
| ws:group:{group_id} | All group members | member_joined, deposit_paid, vote_required, rental_status |
| ws:agent:{agent_id} | Field agent app | new_pickup_assignment, route_update, inspection_reminder |

### 14.2 Rate Limiting — Multi-Layer Defense

#### Rate Limit Rules

| Endpoint / Action | Limit | Window | Burst | On Exceed |
|-------------------|-------|--------|-------|-----------|
| POST /auth/otp/send | 3 requests | 15 min per phone | No burst | 429 + 15min lockout |
| POST /auth/login | 5 requests | 15 min per IP | No burst | 429 + 15min lockout |
| POST /auth/refresh | 20 requests | 1 hour per user | 5 burst | 429; log security event |
| GET /catalog (public) | 200 requests | 1 min per IP | 20 burst | 429 with Retry-After |
| POST /rentals/ | 10 requests | 1 hour per user | No burst | 429; flag suspicious |
| POST /kyc/upload | 10 uploads | 24 hours per user | No burst | 429 |
| GET /* (authenticated) | 1000 requests | 1 hour per user | 50 burst | 429 with Retry-After |
| WebSocket connect | 5 connections | Per user simultaneously | | Reject; close oldest |

#### Implementation
- Library: slowapi (FastAPI-native, Redis-backed)
- Nginx rate limiting at the edge — first line of defense
- Redis INCR + EXPIRE for atomic counter operations
- Rate limit headers returned: X-RateLimit-Limit, X-RateLimit-Remaining, X-RateLimit-Reset
- IP-based for public endpoints; user_id-based for authenticated endpoints

### 14.3 Load Balancing & Scaling

#### Free Tier Solution
- Cloudflare Free Plan (DNS-level load balancing)
- Multiple A records (Round Robin) for the API domain
- Cloudflare health checks every 60s; unhealthy origin removed
- DDoS protection: Cloudflare Magic Transit free tier

#### Horizontal Scaling Plan

| Scale Level | Setup | Handles | Cost |
|-------------|-------|---------|------|
| MVP (0–1K users) | 1 FastAPI instance (uvicorn, 4 workers) | ~100 concurrent requests | Free |
| Growth (1K–10K) | 2 FastAPI instances behind Nginx LB + NeonDB read replica | ~500 concurrent requests | Minimal paid |
| Scale (10K–100K) | 4–8 API instances; Redis Cluster; NeonDB Pro; CDN | ~5000 concurrent | Moderate |
| Enterprise (100K+) | Kubernetes (k3s or GKE); horizontal pod autoscaling; DB sharding | Unlimited | Cloud costs |

#### Uvicorn Worker Configuration
- Workers: 4 × (CPU cores) uvicorn workers per instance
- Worker class: uvicorn.workers.UvicornWorker via gunicorn
- Graceful shutdown: 30s timeout
- Health endpoint: GET /health → 200 if DB + Redis reachable

### 14.4 HTTPS & Transport Security

- TLS 1.3 enforced at Nginx level; TLS 1.0 and 1.1 disabled
- HSTS header: `Strict-Transport-Security: max-age=31536000; includeSubDomains; preload`
- Certificate: Let's Encrypt (free, auto-renew via Certbot) OR Cloudflare Origin Certificate
- HTTP/2 enabled on Nginx for connection multiplexing
- OCSP Stapling enabled — reduces TLS handshake latency
- Security headers: X-Content-Type-Options, X-Frame-Options, Content-Security-Policy, Referrer-Policy
- All cookies: Secure; HttpOnly; SameSite=Strict
- Connection pooling: asyncpg to PostgreSQL uses TLS

### 14.5 Background Job Queue — ARQ + Redis

#### Background Jobs

| Job | Trigger | Schedule | Priority |
|-----|---------|----------|----------|
| Overdue detection scan | Time-based | Every 5 minutes | High |
| Late fee calculation | On overdue detection | Immediate | High |
| Reminder dispatch | Time-based + rental end_at | Calculated per rental | Medium |
| Trust score recalculation | After rental close / dispute resolve | Immediate async | Medium |
| Group trust score update | After any member score changes | Immediate async | Medium |
| PDF generation | After rental confirmation / return | Immediate async | Medium |
| Email dispatch | Queued by any service | Immediate async | Medium |
| KYC OCR processing | After document upload confirmed | Immediate async | High |
| Materialized view refresh | Time-based | Every 5 minutes | Low |
| Audit log archive | Time-based | Daily at 2 AM | Low |
| Deposit settlement calculation | After return inspection complete | Immediate async | High |

#### ARQ Worker Configuration
- Worker pool: 4 concurrent job workers per instance
- Job retry: max 3 retries with exponential backoff (5s, 25s, 125s)
- Dead letter queue: failed jobs after max retries → Redis sorted set
- Job deduplication: unique job IDs prevent double-scheduling

### 14.6 File Storage — Cloudflare R2

#### Storage Structure

| Bucket / Prefix | Contents | Access | TTL / Lifecycle |
|-----------------|----------|--------|-----------------|
| rental-files/kyc/{user_id}/ | ID documents, selfies, liveness videos | Private (signed URLs, 15min TTL) | Retain 7 years |
| rental-files/products/{product_id}/ | Product photos, condition photos | Public (via CDN) | Permanent |
| rental-files/custody/{rental_id}/{stage}/ | Inspection photos at each custody stage | Private (signed URL) | Retain 5 years |
| rental-files/agreements/{rental_id}/ | Signed rental agreement PDFs | Private (signed URL) | Retain 7 years |
| rental-files/invoices/{rental_id}/ | Invoice PDFs | Private (signed URL, 24h TTL) | Retain 7 years |
| rental-files/audit/{year}/{month}/ | Audit log exports (encrypted) | Admin only | Retain 10 years |

#### File Upload Flow
1. Client requests a pre-signed upload URL: `POST /api/v1/files/presign`
2. FastAPI generates a pre-signed R2 URL (TTL: 5 minutes)
3. Client uploads file directly to R2 via the pre-signed URL (no backend traffic)
4. Client notifies FastAPI of upload completion: `POST /api/v1/files/confirm`
5. FastAPI runs async validation (file type, size, virus scan)
6. If valid: stores R2 path in DB; triggers downstream workflow
7. If invalid: deletes file from R2, returns error

---

## 15. Free Tier Stack

Every component listed below is available on a free tier or is fully open-source. None require a credit card for development.

| Category | Tool / Service | Free Tier Limit | Signup |
|----------|----------------|-----------------|--------|
| Database | NeonDB (PostgreSQL) | 0.5 GB, 1 compute unit, branching | Email; no CC |
| Cache | Upstash Redis | 10,000 commands/day, 256 MB | Email; no CC |
| File Storage | Cloudflare R2 | 10 GB, 1M Class A ops/month, zero egress | Email; no CC |
| API Hosting | Railway.app | $5 free credit/month; 512MB RAM | GitHub; no CC |
| Frontend Hosting | Vercel | Unlimited (hobby); Next.js native | GitHub; no CC |
| Email | Resend | 3,000 emails/month; 1 domain | Email; no CC |
| SMS/OTP | MSG91 | 100 OTP/month free | Phone; no CC |
| Push Notifications | Firebase Cloud Messaging | Unlimited (free) | Google account |
| Face Liveness / Match | FaceIO | 3,000 auths/month | Email; no CC |
| Face Match (self-hosted) | DeepFace (Python) | Unlimited (self-hosted) | Open source |
| OCR | Tesseract (self-hosted) | Unlimited (self-hosted) | Open source |
| e-Sign / Aadhaar OTP | Digio Sandbox | Dev sandbox; unlimited test calls | Email; no CC |
| GST Verification | GST Search API (govt) | Truly free public API | None |
| PAN Verification | Surepass Sandbox | Dev sandbox | Email; no CC |
| Payments | Razorpay Sandbox | Unlimited test transactions | Phone+PAN; no CC for sandbox |
| CDN | Cloudflare Free | Unlimited bandwidth | Email; no CC |
| DDoS Protection | Cloudflare Free | Layer 3/4/7 basic DDoS | Included with Cloudflare |
| TLS Certificate | Let's Encrypt / Cloudflare | Free forever | Domain required |
| PDF Generation | WeasyPrint / ReportLab (Python) | Unlimited (open source) | Open source |
| QR Generation | qrcode (Python) + ZXing-js | Unlimited (open source) | Open source |
| Background Jobs | ARQ (Python Redis Queue) | Unlimited (open source) | Open source |
| API Framework | FastAPI + uvicorn | Unlimited (open source) | Open source |
| ORM | SQLAlchemy (async) + asyncpg | Unlimited (open source) | Open source |
| Monitoring | Sentry (free tier) | 5,000 errors/month | Email; no CC |
| Logging | Loguru + Railway logs | Included | Included |

---

## 16. Development Phases

| Phase | What to Build | Est. Duration | Key Deliverable |
|-------|---------------|---------------|-----------------|
| Phase 1 — Foundation | Auth (JWT + refresh rotation + RBAC), Registration with user_type selection, E-KYC pipeline, Trust Score engine, Device fingerprinting | 3 weeks | Working KYC → Trust Score. Personal, Enterprise, Group account creation. |
| Phase 2 — Enterprise | Enterprise KYC (GST+PAN), Team sub-user system, Enterprise pricelist, B2B invoice, Credit billing framework | 2 weeks | Enterprise accounts fully operational. Team invite and role management working. |
| Phase 3 — Group System | Group creation + invite flow, Group trust score engine, Shared deposit pool, Multi-signatory agreement, Group rental flow, Member voting system | 3 weeks | End-to-end group rental with shared deposits and group trust scoring. |
| Phase 4 — Rental Core | Product catalog (SSG), Online rental flow, Offline walk-in flow, Razorpay integration, Invoice generation | 3 weeks | End-to-end rental — all three user types — with payment and invoice. |
| Phase 5 — Chain of Custody | QR scanning, Photo upload to R2, Accessory checklist, Anti-swap verification, GPS capture, Damaged QR exception flow | 3 weeks | Full tamper-proof custody trail with photo evidence. |
| Phase 6 — Automation | ARQ background jobs, Overdue detection, Late fee engine, Automated reminder timeline, Recovery case creation, FIR template | 2 weeks | Fully automated escalation. Zero manual intervention. |
| Phase 7 — Financials | Dynamic deposit settlement, Missing item deduction, Damage deduction, Penalty invoice, Auto-charge on card decline, Deposit ledger | 2 weeks | Complete financial settlement at return. |
| Phase 8 — Real-Time | WebSocket dashboard, Admin live metrics, Group deposit progress bar, Rental countdown timer | 1 week | Live admin command center. Real-time updates. |
| Phase 9 — Portal | Customer dashboard, My Orders, Group dashboard, Profile + KYC management, Dispute filing UI | 2 weeks | Complete self-service portal for all user types. |
| Phase 10 — Hardening | Rate limiting, Load balancing, Security headers, HTTPS/TLS configuration, penetration testing | 1 week | Production-ready security posture. |
| Phase 11 — Analytics | KPI dashboard (materialized views), Trust tier distribution, Revenue analytics, Export (CSV/PDF) | 2 weeks | Business intelligence layer. |

---

## 17. Customer Extension Request Workflow

Sometimes customers genuinely need more time. The system handles this gracefully — while protecting the business from abuse.

### 17.1 Extension Request Flow

| Step | Action | Actor |
|------|--------|-------|
| 1 | Customer raises extension request in portal/app **BEFORE** return deadline | Customer |
| 2 | Customer specifies: new return date/time + reason (optional) | Customer |
| 3 | System checks: is product already booked by another customer after current return date? | System |
| 4 | If **YES** → extension blocked automatically, customer notified | System |
| 5 | If product is available → Request sent to Operations Admin for approval | System |
| 6 | Admin reviews: customer trust score, rental history, reason | Admin |
| 7a | **APPROVED** → New rental period confirmed. Additional rental fee calculated and charged. | Admin |
| 7b | **DENIED** → Customer notified with reason. Original return deadline stands. | Admin |

### 17.2 Extension Rules

| Rule | Details |
|------|---------|
| **Maximum extensions** | 2 extensions per rental (admin-configurable) |
| **Notice period** | Extension request must be made at least 2 hours before original deadline |
| **VIP auto-approve** | Customers with score 85+ may get auto-approved extensions for up to 24 hours |
| **Overdue history** | Customers with overdue history cannot self-request — requires Admin to initiate |
| **Agreement Addendum** | New rental period documented as addendum to original agreement |
| **Deposit adjustment** | If extension significantly extends period, additional deposit hold may be required |

### 17.3 Extension Fee Calculation

```
Additional Fee = (Remaining days × Daily Rate) × (1 + GST%)
```

| Scenario | Calculation |
|----------|-------------|
| 3-day extension on ₹200/day camera | ₹600 + ₹108 GST = ₹708 |
| 1-week extension on ₹500/week bike | ₹500 + ₹90 GST = ₹590 |
| VIP customer (score 85+) | May receive 10-20% discount on extension fee |

### 17.4 Extension Status Tracking

| Status | Description |
|--------|-------------|
| **Pending** | Awaiting admin review |
| **Approved** | Extension granted, new return date set |
| **Rejected** | Denied by admin, original deadline stands |
| **Expired** | Request not reviewed within 24 hours (auto-denied) |

---

## 18. Dispute Filing & Resolution Workflow

Customers can formally disputes charges. The system is designed so disputes from bad-faith actors are resolved quickly with evidence. Genuine disputes from good-faith customers are handled fairly.

### 18.1 What Customers Can Dispute

| Dispute Type | Description |
|--------------|-------------|
| **Late Fee Charge** | "I returned it on time" |
| **Damage Deduction** | "The item was already damaged when I got it" |
| **Missing Accessory Deduction** | "I returned all accessories" |
| **Deposit Not Refunded** | "Refund not received within expected timeframe" |
| **Incorrect Charge** | "Charged more than agreed amount" |

### 18.2 Dispute Flow

| Step | Action | Actor |
|------|--------|-------|
| 1 | Customer files dispute in portal → selects charge type, enters description | Customer |
| 2 | Customer uploads supporting evidence (photos, screenshots) | Customer |
| 3 | Dispute ticket created → Operations Admin notified | System |
| 4 | Admin reviews evidence package | Admin |
| 5 | Admin makes decision within **48 hours** (SLA) | Admin |
| 6a | **Dispute WON** → Charge reversed. Refund issued. Trust score impact reversed. | Admin |
| 6b | **Dispute LOST** → Admin provides evidence package to customer. Charge stands. | Admin |
| 7 | Customer can escalate to **Super Admin** (final level) | Customer |
| 8 | Super Admin decision is binding | Super Admin |

### 18.3 Non-Repudiation Evidence Package

For every dispute, the system automatically assembles:

| Evidence | Source | Purpose |
|----------|--------|---------|
| Digital rental agreement | Agreement PDF with customer signature | Proves terms accepted |
| OTP confirmation receipt | SMS/email delivery log | Proves customer agreed to all terms |
| Reminder delivery receipts | SMS delivered, email opened | Proves customer was notified |
| Pre-pickup inspection photos | Custody event with timestamps | Proves item condition at handoff |
| Return inspection photos | Custody event with timestamps | Proves item condition at return |
| QR scan logs | Scan time + device fingerprint | Proves exact scan time and location |
| Accessory checklist | Per-item confirmation at pickup and return | Proves missing/returned items |
| GPS location data | Lat/lng at pickup and return | Proves location of handoff |

### 18.4 Dispute Resolution Timeline

| Stage | Timeframe | Action |
|-------|-----------|--------|
| Filed | T+0 | Customer submits dispute |
| Acknowledged | T+1 hour | Auto-email confirmation with ticket number |
| Under Review | T+2-24 hours | Admin investigates |
| Decision | T+24-48 hours | Admin makes decision |
| Escalation Window | T+48h to T+7 days | Customer can escalate to Super Admin |
| Final Decision | T+7 days | Super Admin ruling is binding |

---

## 19. Repair Workflow

When a product is returned damaged or fails inspection, it enters the Repair Workflow and is immediately removed from rentable inventory until the workflow is closed.

### 19.1 Repair Workflow Steps

| Step | Action | Actor |
|------|--------|-------|
| 1 | Return inspection staff marks product as DAMAGED | Staff |
| 2 | Staff describes damage and uploads photos | Staff |
| 3 | Repair Case automatically created | System |
| 4 | Product status set to **IN REPAIR** — not visible in catalog | System |
| 5 | Admin assigns repair to internal team or external vendor | Admin |
| 6 | Repair cost logged in system | Repair team |
| 7 | On repair completion → staff performs inspection | Staff |
| 8 | Photos uploaded → product condition updated | Staff |
| 9 | Admin approves repair completion | Admin |
| 10 | Product status reset to **AVAILABLE** → appears in catalog again | System |
| 11 | Repair case closed with full cost log and timeline | System |

### 19.2 Repair Case Data

| Field | Description |
|-------|-------------|
| Case ID | Auto-generated: REP-2026-00001 |
| Product ID | Product requiring repair |
| Serial Number | Product serial |
| Category | Product category |
| Rental ID | Rental that caused the damage (if applicable) |
| Damage Description | Staff description of damage |
| Photos (Before) | Pre-repair photos |
| Photos (After) | Post-repair photos |
| Damage Deduction | Amount collected from customer |
| Actual Repair Cost | Cost from vendor/internal |
| Net Loss/Profit | Damage collected vs repair cost |
| Days Out of Service | Lost rental revenue tracked |
| Assigned To | Internal team or external vendor |
| Status | Open → In Repair → Completed → Write-off |

### 19.3 Repair Status Tracking

| Status | Description | Inventory Impact |
|--------|-------------|------------------|
| **Open** | Damage identified, awaiting assignment | Product hidden from catalog |
| **In Repair** | Repair in progress | Product hidden from catalog |
| **Completed** | Repair done, awaiting inspection | Product hidden until approved |
| **Write-off** | Product beyond repair, disposed | Product marked as archived |

### 19.4 Repair Cost Tracking

| Cost Category | Description |
|---------------|-------------|
| **Parts** | Replacement parts needed |
| **Labor** | Technician labor cost |
| **Vendor Fee** | External repair vendor charges |
| **Shipping** | Cost to ship to/from vendor |
| **Total Repair Cost** | Sum of all above |
| **Customer Deduction** | Amount collected from customer |
| **Net Loss** | Total Repair Cost - Customer Deduction |

---

## 20. Customer Blacklisting Workflow

### 20.1 Triggers for Blacklisting

| Trigger | Evidence Required |
|---------|-------------------|
| Failed to return a product | Recovery Case reaches legal stage |
| Product swap confirmed (fraud) | QR + serial mismatch evidence |
| Multiple fake disputes filed | Dispute resolution records |
| Fraudulent KYC documents detected | KYC verification failure records |
| Chargebacks filed on legitimate charges | Payment dispute records |
| Verbal or physical abuse of staff | Operations Admin report |

### 20.2 Blacklisting Process

| Step | Action | Actor |
|------|--------|-------|
| 1 | Operations Admin proposes blacklist | Admin |
| 2 | Admin provides reason and evidence references | Admin |
| 3 | **Super Admin must approve** | Super Admin |
| 4 | Customer account status set to **BLACKLISTED** | System |
| 5 | Customer cannot log in or place new rentals | System |
| 6 | If same phone/email/ID used → System detects and blocks | System |
| 7 | Device fingerprint blacklisted — blocks registration from same device | System |
| 8 | Admin sees **BLACKLISTED** badge on any search | System |

### 20.3 Blacklist Appeal

| Step | Action |
|------|--------|
| 1 | Blacklisted customer submits appeal via email only (not in-app) |
| 2 | Super Admin reviews appeal |
| 3 | Super Admin can reinstate with conditions (higher deposit, lower tier) |
| 4 | All reinstatements logged with reason in Audit Trail |

### 20.4 Blacklist Data

| Field | Description |
|-------|-------------|
| Blacklist ID | Auto-generated |
| User ID | Blacklisted customer |
| Reason | Detailed reason for blacklisting |
| Evidence References | Rental IDs, dispute IDs, photos |
| Blacklisted By | Admin who proposed |
| Approved By | Super Admin who approved |
| Blacklisted At | Timestamp |
| Reinstated By | Super Admin (if reinstated) |
| Reinstated At | Timestamp (if reinstated) |
| Reinstatement Conditions | Higher deposit, lower tier, etc. |

---

## 21. Rental Operations Dashboard

### 21.1 Real-Time Metrics Panel

| Metric | What It Shows | Actions Available |
|--------|---------------|-------------------|
| **Active Rentals** | Count + list of all currently rented products | View details, send custom reminder |
| **Rentals Due Today** | Products whose return deadline is today | Contact customer, view custody record |
| **Overdue NOW** | Products past return deadline — red alert | Escalate, view accrued fee, dispatch |
| **Upcoming Pickups (Today)** | Confirmed rentals pending pickup | View route, print checklist, assign agent |
| **Upcoming Returns (Today)** | Returns expected today | Prepare inspection station |
| **Revenue This Month** | Total rental fees collected | Breakdown by category, by day |
| **Deposits Currently Held** | Total deposit value across all active rentals | Drill down by customer, by product |
| **Late Fees Collected (Month)** | Total penalties collected | Breakdown by product, by tier |
| **Recovery Cases Open** | Active asset recovery cases | View details, assign agent |
| **Repair Cases Open** | Products currently in repair | View which products unavailable |
| **Trust Score Distribution** | Customer count per tier | Identify high-risk concentration |
| **Overdue Value at Risk** | Total value held by overdue customers | Prioritize recovery efforts |

### 21.2 Actionable Priority Feed

| Priority | Color | Example Actions |
|----------|-------|-----------------|
| **URGENT NOW** | 🔴 Red | 3 items overdue by 2+ hours → [Call Customer] [Send Alert] [Dispatch Collection] |
| **DO TODAY** | 🟡 Yellow | 5 pickups scheduled before noon → [View Route] [Print Checklist] |
| **DO TODAY** | 🟡 Yellow | 2 return inspections pending → [Start Inspection] |
| **FYI THIS WEEK** | 🟢 Green | Revenue 12% above last week → [View Report] |
| **REVIEW NEEDED** | 🔵 Blue | 1 dispute filed today → [Review Dispute] |

### 21.3 Customizable Dashboard Widgets

| Feature | Description |
|---------|-------------|
| **Drag-and-Drop** | Admin can rearrange dashboard layout |
| **Role-Based Views** | Field agent sees different widgets than owner |
| **Date Range Selector** | Today / This Week / This Month / Custom Range |
| **Export** | Any widget data as CSV or PDF |
| **Widget Types** | Metrics card, Line chart, Bar chart, Pie chart, Table, Map |

---

## 22. Notification & Alert System

### 22.1 Customer Notifications

| Notification Type | Default Channels | Customer Can Opt Out? |
|-------------------|------------------|----------------------|
| Rental confirmation | Email + SMS | No — mandatory |
| Invoice generated | Email | No — mandatory |
| Pickup reminder (T-24h, T-2h) | SMS + Email + Push | Partial — can disable push, not SMS |
| Return reminder (T-24h, T-2h) | SMS + Email + Push | Partial — can disable push, not SMS |
| Overdue alert | SMS + Email + Push | No — mandatory |
| Late fee update | SMS + Email | No — mandatory |
| Extension approved/denied | Email + Push | No — mandatory |
| Dispute status update | Email + Push | No — mandatory |
| Deposit refund initiated | Email + SMS | No — mandatory |
| Marketing / promotions | Email + Push | Yes — fully opt-out |

### 22.2 Admin / Internal Alerts

| Alert | Recipients | Trigger |
|-------|------------|---------|
| New overdue rental | Operations Admin | Overdue detection job |
| New dispute filed | Operations Admin | Customer files dispute |
| High-value rental by New/Basic tier | Super Admin | Rental > threshold by low-tier customer |
| 3+ device fingerprints on one account | Super Admin | Security flag |
| Recovery case escalation | Super Admin + Legal | Recovery reaches legal stage |
| Failed card charge on penalty | Finance + Admin | Razorpay charge fails |
| KYC face match below threshold | Operations Admin | Manual review queue |

### 22.3 Notification Channels

| Channel | Use Case | Delivery Receipt |
|---------|----------|------------------|
| **SMS** | OTP, critical alerts, reminders | Delivery status logged |
| **Email** | Invoices, agreements, detailed info | Open tracking for non-repudiation |
| **Push** | Real-time alerts, reminders | Delivery confirmation |
| **In-App** | Dashboard notifications, badges | Read status tracked |
| **WhatsApp** | High-engagement markets (future) | Delivery status |

---

## 23. Pricing, Pricelists & Product Management

### 23.1 Pricelist System

| Feature | Description |
|---------|-------------|
| **Default Pricelist** | Applies to all products and all customers unless overridden |
| **Custom Pricelists** | Admin can create unlimited custom pricelists |
| **Pricelist Types** | General / Seasonal / Corporate / Loyalty / Promotional |
| **Time-Bounded** | Active only between specific start and end dates (seasonal promos) |
| **Tier-Specific** | VIP pricelist auto-applies to Trust Score 85+ customers |
| **Customer-Specific** | Bespoke price assigned to a corporate client account |
| **Priority Order** | Customer-specific > Tier-based > Seasonal > Default |

### 23.2 Rental Period Configuration

| Configuration | Description |
|---------------|-------------|
| **Available Periods** | Hourly / Daily / Weekly / Monthly per product |
| **Pricing Tiers** | Weekly rate cheaper per day than 7× daily rate |
| **Blackout Dates** | Configurable per product (maintenance windows) |
| **Minimum Rental** | Configurable per product (e.g., cameras: minimum 1 day) |
| **Maximum Rental** | Optional cap (e.g., max 90 days for certain items) |

### 23.3 Product Catalog Management

| Feature | Description |
|---------|-------------|
| **Categories** | Cameras, Bikes, Electronics, Furniture, Vehicles, etc. |
| **Product Details** | Name, description, photos (multiple), rental rates, deposit %, late fee rate |
| **Variants** | Brand / Model / Color / Size / Condition — each variant is a separate SKU |
| **Serial Numbers** | Each SKU has its own serial number, QR code, RFID tag |
| **Availability Calendar** | Shows booked dates, available dates, maintenance dates |
| **Inactive Products** | Admin can mark as INACTIVE to hide from catalog |
| **Featured Products** | Admin can feature products for promotional display |

### 23.4 Dynamic Pricing Rules

| Rule | Description |
|------|-------------|
| **Peak Season** | Higher rates during holidays/events |
| **Off-Season Discounts** | Lower rates during slow periods |
| **Bulk Discount** | Discount for renting multiple items |
| **Loyalty Discount** | Auto-applied based on trust tier |
| **Coupon Codes** | Admin-configurable promotional codes |
| **Enterprise Pricing** | Negotiated rates for enterprise accounts |

---

## 24. Customer Portal Features

### 24.1 Dashboard

| Feature | Description |
|---------|-------------|
| **Active Rentals** | Countdown timer to return deadline |
| **Quick Actions** | Request Extension, Initiate Return, Download Invoice |
| **KYC Status** | Trust Score with improvement guidance |
| **Upcoming Pickups** | Store address / delivery tracking |
| **Points Balance** | Current loyalty points |
| **Recent Activity** | Last 5 transactions |

### 24.2 My Orders

| Feature | Description |
|---------|-------------|
| **Full History** | All rentals with status: Active / Completed / Cancelled / Overdue |
| **Order Details** | Product details, rental period, total paid, deposit status |
| **Invoice Download** | PDF download for each order |
| **Filters** | By date range, status, product category |

### 24.3 My Profile

| Feature | Description |
|---------|-------------|
| **Personal Info** | Update name, email (re-verification), phone (OTP) |
| **Profile Photo** | Upload and change |
| **KYC Documents** | View submitted docs, re-submit if expired |
| **Notification Preferences** | Manage per-channel opt-in/out |

### 24.4 My Addresses

| Feature | Description |
|---------|-------------|
| **Address Management** | Add / edit / delete delivery addresses |
| **Default Address** | Set primary delivery address |
| **KYC Verification** | Addresses verified against KYC — mismatch flagged |

### 24.5 Payment Methods

| Feature | Description |
|---------|-------------|
| **Card Management** | View tokenized cards (last 4 digits, expiry) |
| **Add Card** | Razorpay tokenization |
| **Remove Card** | Cannot remove if only card and active rental exists |
| **Payment History** | All charges and refunds with dates and references |

### 24.6 My Groups

| Feature | Description |
|---------|-------------|
| **Group Dashboard** | View all groups user belongs to |
| **Group Rentals** | Shared rental status and timeline |
| **Deposit Pool** | View individual contribution and group total |
| **Voting** | Approve/reject group decisions (extension requests) |

---

## 25. Admin Configuration Panel

### 25.1 Organisation Settings

| Setting | Description |
|---------|-------------|
| **Business Name** | Used on invoices and quotations |
| **Logo** | Displayed on all documents |
| **Address** | Business address |
| **GST Number** | For GST-compliant invoices |
| **Currency** | Default currency (INR) |
| **GST Rates** | Per product category |

### 25.2 Rental Rule Configuration

| Rule | Description |
|------|-------------|
| **Grace Period** | Per product category (default: 30 minutes) |
| **Late Fee Rates** | Per category, charging mode (hourly/daily/weekly/monthly) |
| **Maximum Late Fee Cap** | Prevents unlimited accumulation |
| **Default Deposit Percentage** | Per category (default: 30%) |
| **Minimum Rental Period** | Per category |
| **Maximum Rental Period** | Per category |
| **Extension Rules** | Max extensions, minimum notice, auto-approve threshold |

### 25.3 Trust Score Thresholds

| Configuration | Description |
|---------------|-------------|
| **Point Values** | Configurable for each trust signal |
| **Tier Boundaries** | What score = what tier |
| **Deposit Adjustments** | Per tier percentage adjustments |
| **High-Value Threshold** | Rental value requiring admin approval |

### 25.4 User Management

| Feature | Description |
|---------|-------------|
| **Staff Accounts** | Create and manage Operations Admin, Field Agent accounts |
| **Role Assignment** | Assign roles and permissions |
| **Customer Search** | Search by name, phone, ID number |
| **Trust Score View** | View all customers with trust scores and KYC status |
| **Blacklist/Reinstate** | Customer blacklist management |
| **Audit Trail** | View full audit trail for any user or action |

### 25.5 Quotation Templates

| Feature | Description |
|---------|-------------|
| **Template Management** | Create, edit, delete quotation templates |
| **Header/Footer** | Configure business logo, address, T&C |
| **Signature Line** | Digital signature placement |
| **Default Values** | Pre-filled rental period, deposit %, notes |

---

## 26. Availability Engine

### 26.1 Core Concept

The Availability Engine is the heart of the rental system. It determines in real-time whether a product can be booked for a given date range, preventing double-bookings and managing inventory across all rental contexts (Personal, Enterprise, Group).

### 26.2 Availability Check Flow

```
Customer selects product + dates
        ↓
API: GET /api/v1/products/{id}/availability?start=2026-09-01&end=2026-09-07
        ↓
┌─────────────────────────────────────────────────┐
│  1. Check blackout_dates table                   │
│     → If blackout exists for range: BLOCKED      │
│  2. Check availability_blocks table              │
│     → If rental/maintenance block exists: BLOCKED │
│  3. Check reservations table (pending)           │
│     → If pending reservation exists: HELD         │
│  4. Check stock_levels table                     │
│     → If quantity_available == 0: OUT OF STOCK    │
│  5. Check product.status                         │
│     → If inactive/archived: UNAVAILABLE           │
└─────────────────────────────────────────────────┘
        ↓
Return: { available: true/false, alternate_dates: [...], waitlist_available: true/false }
```

### 26.3 Availability Block Types

| Block Type | Created When | Duration | Can Override? |
|------------|--------------|----------|---------------|
| **Rental** | Rental confirmed (status=confirmed/active) | start_at to end_at | No |
| **Reservation** | Customer adds to cart / quotation created | 15 min TTL (auto-expires) | No |
| **Maintenance** | Admin marks product for repair | Admin-defined dates | Super Admin only |
| **Blackout** | Admin configures holiday/closure dates | Admin-defined dates | Super Admin only |

### 26.4 Real-Time Availability API

```
GET /api/v1/products/{id}/availability
Query Params:
  - start_at: ISO 8601 timestamp (required)
  - end_at: ISO 8601 timestamp (required)
  - quantity: integer (default 1, for bulk)

Response:
{
  "product_id": "uuid",
  "available": true,
  "total_units": 5,
  "available_units": 3,
  "blocked_dates": [
    {"start": "2026-09-10", "end": "2026-09-15", "reason": "maintenance"}
  ],
  "alternate_suggestions": [
    {"product_id": "uuid", "name": "Similar Camera Model B", "price": 800}
  ],
  "waitlist_enabled": false
}
```

### 26.5 Calendar View API (Admin Dashboard)

```
GET /api/v1/admin/products/{id}/calendar
Query Params:
  - month: YYYY-MM (required)

Response:
{
  "product_id": "uuid",
  "month": "2026-09",
  "days": [
    {"date": "2026-09-01", "status": "available", "units_available": 5},
    {"date": "2026-09-02", "status": "partially_booked", "units_available": 2},
    {"date": "2026-09-03", "status": "fully_booked", "units_available": 0},
    ...
  ]
}
```

### 26.6 Reservation System

| Feature | Description |
|---------|-------------|
| **Hold Duration** | 15 minutes from add-to-cart (configurable) |
| **Auto-Release** | ARQ job checks every minute for expired reservations |
| **Conflict Prevention** | Redis lock `reservation_lock:{product_id}` prevents concurrent bookings |
| **Waitlist** | Optional: customers can join waitlist if product unavailable |
| **Notification** | When reserved product becomes available, waitlisted users notified |

### 26.7 Multi-Unit Inventory

Products can have multiple identical units. Availability is tracked per-unit.

| Field | Description |
|-------|-------------|
| `total_units` | Total identical units in inventory |
| `available_units` | Currently available for rent |
| `rented_units` | Currently rented out |
| `repair_units` | In repair workshop |
| `reserved_units` | Reserved (pending confirmation) |

**Example:** Store has 5 Canon EOS R5 cameras.
- 3 currently rented → available_units = 2
- Customer rents 1 more → available_units = 1
- Last one rented → available_units = 0 (show "Out of Stock")

### 26.8 Availability Cache Strategy

| Cache Key | TTL | Invalidation |
|-----------|-----|--------------|
| `avail:{product_id}:{date}` | 30 sec | On rental create/cancel/return |
| `calendar:{product_id}:{month}` | 5 min | On any block change |
| `stock_level:{product_id}:{location}` | 60 sec | On stock movement |

---

## 27. Quotes & Orders Workflow

### 18.1 Quotation Lifecycle

```
┌─────────┐     ┌─────────┐     ┌──────────┐     ┌───────────┐     ┌───────────┐
│  DRAFT   │────>│  SENT   │────>│  VIEWED  │────>│ ACCEPTED  │────>│ CONFIRMED │
└─────────┘     └─────────┘     └──────────┘     └───────────┘     └───────────┘
     │               │               │                │                   │
     │               │               │                │                   │
     v               v               v                v                   v
 CANCELLED      EXPIRED        REJECTED          EXPIRED             CONVERTED
                  (24h)        (by customer)     (if not paid)       TO RENTAL
```

### 18.2 Quotation Creation Flow

#### Online Portal (Customer-Initiated)
| Step | Action | Actor |
|------|--------|-------|
| 1 | Customer browses product, selects rental period | Customer |
| 2 | System calculates price from pricelist + deposit from trust tier | System |
| 3 | Customer sees "Request Quote" option (for negotiation) | Customer |
| 4 | Customer submits quote request with notes | Customer |
| 5 | Quote created in DRAFT status | System |
| 6 | Customer can accept or request modifications | Customer |
| 7 | On acceptance → Quote confirmed → Rental created | System |

#### In-Store (Admin-Initiated)
| Step | Action | Actor |
|------|--------|-------|
| 1 | Walk-in customer discusses requirements | Admin + Customer |
| 2 | Admin searches/creates customer record | Admin |
| 3 | Admin selects products and rental periods | Admin |
| 4 | Admin applies custom pricing / discount | Admin |
| 5 | System generates quote with PDF | System |
| 6 | Admin shares quote via email/WhatsApp/print | Admin |
| 7 | Customer agrees → Admin confirms → Rental created | Admin |

### 18.3 Quotation Templates

Admins can save frequently-used configurations as templates.

| Template Feature | Description |
|------------------|-------------|
| **Saved Configurations** | Product + period + deposit + terms saved as template |
| **Header/Footer** | Business logo, address, T&C appears on all quotes |
| **Quick Apply** | One-click apply template to new quote |
| **Usage Tracking** | System tracks which templates are used most |
| **Template Categories** | Organize by: corporate, seasonal, bulk, VIP |

### 18.4 Order Management

Once a quotation is accepted and payment is received, it becomes an **Order** (Rental).

| Order Status | Description | Next Possible States |
|--------------|-------------|---------------------|
| **Draft** | Quote created, not yet sent | Sent, Cancelled |
| **Confirmed** | Payment received, rental agreed | Active (on pickup date) |
| **Active** | Product in customer possession | Returned, Overdue |
| **Overdue** | Past return deadline | Returned, Recovery |
| **Returned** | Product returned, pending settlement | Completed |
| **Completed** | Fully settled, deposit refunded | — |
| **Cancelled** | Cancelled before pickup | — |

### 18.5 Order Actions

| Action | Trigger | System Response |
|--------|---------|-----------------|
| **Confirm Order** | Payment received | Create availability block, schedule pickup, send confirmation |
| **Cancel Order** | Customer/Admin cancels | Release availability block, refund rental fee (minus cancellation fee if applicable) |
| **Modify Order** | Admin adjusts before pickup | Recalculate fees, update agreement, notify customer |
| **Convert Quote** | Quote accepted | Auto-generate rental + invoice, collect deposit |
| **Clone Order** | Repeat customer | Copy previous order details for quick re-rental |

### 18.6 Bulk Order Support (Enterprise)

Enterprise users can create bulk orders with multiple products in a single PO.

| Feature | Description |
|---------|-------------|
| **Multiple Products** | Add 10+ products to single order |
| **Bulk Discount** | Automatic discount based on quantity |
| **Combined Invoice** | Single invoice for entire order |
| **Staggered Delivery** | Different products delivered on different dates |
| **Centralized Tracking** | Single dashboard view for all items |

---

## 28. Invoicing System

### 19.1 Invoice Types

| Invoice Type | When Generated | Contents |
|--------------|----------------|----------|
| **Booking Invoice** | Rental confirmed | Rental fee + deposit + delivery + GST |
| **Return Invoice** | Product returned | Deposit refund amount + deductions breakdown |
| **Penalty Invoice** | Deductions exceed deposit | Balance owed after deposit forfeited |
| **Late Fee Invoice** | Late fee exceeds deposit | Accrued late fees as separate charge |
| **Credit Note** | Refund / dispute won | Negative invoice offsetting previous charge |
| **Adjustment Invoice** | Admin manual correction | Manual financial adjustment |

### 19.2 Invoice Generation Flow

```
Rental Confirmed
      ↓
Booking Invoice Generated
  ├── Line Items: Rental Fee, Security Deposit, Delivery Fee
  ├── GST Calculated (18% or per category config)
  ├── Total = Subtotal + GST
  ├── Invoice Number: INV-2026-00001 (sequential)
  └── PDF Generated → Stored in R2 → Email to Customer

Product Returned
      ↓
Return Invoice Generated
  ├── Line Items: Deposit Refund, Late Fee Deduction, Damage Deduction
  ├── Net Refund = Deposit - All Deductions
  ├── If Net > 0: Refund issued
  ├── If Net < 0: Penalty Invoice generated for balance
  └── PDF Generated → Stored in R2 → Email to Customer
```

### 19.3 Invoice Line Items

Each invoice contains detailed line items for transparency.

| Line Item Type | Description | Example |
|----------------|-------------|---------|
| `rental_fee` | Base rental cost | ₹2,000 for 7-day camera rental |
| `security_deposit` | Deposit collected (shown as info) | ₹3,000 (30% of item value) |
| `delivery_fee` | Home delivery charge | ₹200 |
| `late_fee` | Penalty for late return | ₹500 |
| `damage_fee` | Damage assessment charge | ₹1,500 |
| `missing_item` | Missing accessory replacement | ₹900 (memory card) |
| `discount` | Coupon/promotional discount | -₹500 |
| `gst` | Tax calculated on subtotal | ₹468 (18% of ₹2,600) |
| `credit_adjustment` | Enterprise credit applied | -₹1,000 |
| `loyalty_points_redeem` | Points redeemed | -₹200 (200 points) |

### 19.4 Invoice Numbering

```
Format: {PREFIX}-{YEAR}-{SEQUENTIAL}
Examples:
  - RNT-2026-00001 (standard rental)
  - ENT-2026-00001 (enterprise order)
  - GRP-2026-00001 (group rental)
  - CRN-2026-00001 (credit note)
```

### 19.5 GST Compliance

| Rule | Implementation |
|------|----------------|
| GST Rate | 18% default, configurable per product category |
| GSTIN Display | Customer GSTIN on B2B invoices (enterprise) |
| HSN Code | Configurable per product category |
| CGST + SGST | Split for intra-state (9% + 9%) |
| IGST | For inter-state (18%) |
| Invoice Format | Compliant with GST e-invoicing standards |

### 19.6 Invoice PDF Generation

| Component | Content |
|-----------|---------|
| **Header** | Business logo, name, address, GSTIN, state code |
| **Invoice Details** | Invoice number, date, due date, payment terms |
| **Bill To** | Customer name, address, phone, email, GSTIN (if B2B) |
| **Line Items Table** | Description, HSN, quantity, rate, amount, GST, total |
| **Summary** | Subtotal, GST breakdown, discount, total, amount paid, balance due |
| **Payment Info** | Bank details, UPI QR code, payment link |
| **Footer** | Terms and conditions, signature line |

### 19.7 Payment Tracking

| Invoice Status | Meaning | System Action |
|----------------|---------|---------------|
| **Draft** | Not yet issued | Can be edited |
| **Issued** | Sent to customer | Payment reminder scheduled |
| **Partially Paid** | Some amount received | Track remaining balance |
| **Paid** | Full amount received | Mark complete, send receipt |
| **Overdue** | Past due date | Escalation emails, admin alert |
| **Cancelled** | Voided | Reversed in accounting |
| **Refunded** | Amount returned | Credit note generated |

---

## 29. CRM — Customer Relationship Management

### 20.1 CRM Overview

The CRM module tracks every customer interaction, manages leads, automates follow-ups, and provides insights into customer behavior for the rental business.

### 20.2 Customer Profile (CRM View)

Beyond the basic user record, CRM maintains extended profiles.

| CRM Field | Description |
|-----------|-------------|
| **Contact Type** | individual, enterprise, lead |
| **Lead Source** | website, walk_in, referral, social_media, advertisement |
| **Lead Status** | new, contacted, qualified, negotiating, converted, lost, dormant |
| **Lead Score** | AI-calculated 0-100 based on engagement |
| **Assigned To** | Sales/ops person responsible |
| **Preferred Contact** | sms, email, phone, whatsapp |
| **Lifetime Value** | Total revenue from this customer |
| **Favorite Categories** | Most frequently rented product categories |
| **Tags** | VIP, corporate, frequent, at_risk, new, etc. |
| **Next Follow-Up** | Scheduled follow-up date + reason |

### 20.3 Interaction Logging

Every touchpoint with a customer is logged automatically or manually.

| Interaction Type | Auto-Logged? | Example |
|------------------|--------------|---------|
| **Rental Created** | Yes | Customer rented Camera X for 7 days |
| **Rental Returned** | Yes | Product returned, deposit settled |
| **Payment Received** | Yes | ₹2,500 received via UPI |
| **Dispute Filed** | Yes | Customer disputed late fee charge |
| **Email Sent** | Yes (by system) | Reminder email sent for return |
| **SMS Sent** | Yes (by system) | OTP verification |
| **Phone Call** | Manual | Admin called customer about overdue |
| **Meeting** | Manual | In-store consultation about bulk order |
| **Support Ticket** | Manual | Customer complained about damaged item |
| **Complaint** | Manual | Customer dissatisfied with service |

### 20.4 Lead Scoring Algorithm

```
Lead Score = (Recency Score × 0.30) + (Frequency Score × 0.30) + (Monetary Score × 0.25) + (Engagement Score × 0.15)

Recency Score = (1 - min(days_since_last_rental / 365, 1)) × 100
Frequency Score = min(total_rentals / 20, 1) × 100
Monetary Score = min(lifetime_value / 50000, 1) × 100
Engagement Score = min(interactions_last_90_days / 10, 1) × 100
```

### 20.5 CRM Tags & Segmentation

| Tag Category | Examples | Use Case |
|--------------|----------|----------|
| **Value** | VIP, Premium, Budget | Pricelist targeting |
| **Behavior** | Frequent, One-time, At-risk | Re-engagement campaigns |
| **Source** | Walk-in, Online, Referral | Marketing attribution |
| **Status** | Active, Dormant, Blacklisted | Operational actions |
| **Custom** | Wedding, Corporate Event, Film Production | Personalized offers |

### 20.6 Campaign Management

| Campaign Type | Description | Trigger |
|---------------|-------------|---------|
| **Promotional** | Discount offers for specific products/categories | Admin-created |
| **Re-engagement** | Win back dormant customers (no rental in 90+ days) | Automated |
| **Seasonal** | Holiday/season-specific promotions | Scheduled |
| **Referral** | Incentivize referrals | On registration |
| **Loyalty** | Points bonus / tier upgrade offers | On milestone |

### 20.7 Automated Follow-Up Rules

| Trigger | Follow-Up Action | Channel |
|---------|------------------|---------|
| New lead (no rental in 7 days) | "Still interested?" message | Email + Push |
| Rental completed | "Rate your experience" survey | Email + Push |
| 30 days since last rental | "We miss you" + discount offer | SMS + Email |
| 90 days since last rental | "Come back" + special offer | Email |
| Dispute resolved (won) | "Thank you" + loyalty bonus | Email + Push |
| Birthday | Happy birthday + special discount | SMS + Email |
| KYC expiry reminder | "Update your documents" | SMS + Push |

### 20.8 CRM Dashboard Metrics

| Metric | Description | Visualization |
|--------|-------------|---------------|
| **Lead Pipeline** | Count by lead status (new → converted) | Funnel chart |
| **Conversion Rate** | % of leads that become customers | KPI card |
| **Customer Retention** | % returning within 90 days | Trend line |
| **Avg. Response Time** | Time to first contact after inquiry | KPI card |
| **Campaign ROI** | Revenue generated per campaign | Bar chart |
| **Churn Risk** | Customers with declining engagement | Alert list |
| **Top Performers** | Staff by customer satisfaction / conversion | Leaderboard |

---

## 30. Stock Management

### 21.1 Stock Overview

Complete inventory management across physical locations with real-time tracking, movement history, and maintenance scheduling.

### 21.2 Stock Locations

| Location Type | Description | Example |
|---------------|-------------|---------|
| **Warehouse** | Central storage facility | Main warehouse, City B hub |
| **Store** | Retail outlet / pickup point | Store Front, Mall Kiosk |
| **Repair Center** | Maintenance workshop | In-house repair, Vendor workshop |
| **Field** | With customer / in transit | Customer location, Delivery truck |

### 21.3 Stock Movement Tracking

Every product movement is recorded with full audit trail.

| Movement Type | From | To | Trigger |
|---------------|------|----|---------|
| **Transfer** | Warehouse A | Warehouse B | Admin-initiated stock redistribution |
| **Rental Out** | Warehouse/Store | Customer | Rental confirmed + pickup |
| **Rental Return** | Customer | Warehouse/Store | Product returned + inspection |
| **Repair Send** | Warehouse | Repair Center | Damage identified |
| **Repair Return** | Repair Center | Warehouse | Repair completed |
| **Adjustment** | Any | Any | Manual correction (damage, loss, found) |
| **Disposal** | Warehouse | — | Product written off |

### 21.4 Stock Level Management

| Concept | Description |
|---------|-------------|
| **Available** | Ready for rental, physically in location |
| **Reserved** | Booked but not yet picked up (pending confirmation) |
| **In Repair** | Being serviced, not rentable |
| **In Transit** | Being moved between locations |
| **Total** | Available + Reserved + In Repair |

### 21.5 Stock Adjustment Workflow

| Step | Action | Actor |
|------|--------|-------|
| 1 | Staff notices discrepancy (damage, loss, found) | Field Agent / Ops Admin |
| 2 | Creates stock adjustment record | Staff |
| 3 | Uploads evidence photos | Staff |
| 4 | For write-offs: Super Admin approval required | Super Admin |
| 5 | Stock levels updated | System |
| 6 | Audit log recorded | System |
| 7 | If damage: repair_case initiated | System |

### 21.6 Maintenance Scheduling

| Feature | Description |
|---------|-------------|
| **Preventive Maintenance** | Scheduled servicing (e.g., camera sensor cleaning every 90 days) |
| **Calibration** | Equipment accuracy checks |
| **Cleaning** | Regular cleaning schedules |
| **Overdue Alerts** | Notifications when maintenance is overdue |
| **Cost Tracking** | Track maintenance costs per product |

### 21.7 Stock Reports

| Report | Description | Frequency |
|--------|-------------|-----------|
| **Current Stock Levels** | All products at all locations | Real-time |
| **Stock Movement History** | All transfers, rentals, returns | On-demand |
| **Utilization Report** | % of time each product is rented | Weekly |
| **Maintenance Due** | Products needing scheduled maintenance | Weekly |
| **Damage Report** | Products with damage history | Monthly |
| **Write-Off Report** | Products disposed / written off | Monthly |
| **Location-wise Inventory** | Stock distribution across locations | On-demand |

---

## 31. Loyalty Points & Referral System

### 22.1 Points Earning Rules

| Action | Points Earned | Cap |
|--------|---------------|-----|
| Successful rental (on-time return) | 10 points per ₹100 spent | No cap |
| On-time return bonus | 50 points | 1x per rental |
| No damage bonus | 25 points | 1x per rental |
| First rental | 200 points | Once |
| Profile completion (KYC verified) | 100 points | Once |
| Referral (referrer) | 100 points | No cap |
| Referral (referred) | 50 points | Once |
| Review/Rating submitted | 25 points | 1x per rental |
| Birthday bonus | 50 points | Annual |

### 22.2 Points Redemption

| Redemption Option | Points Required | Value |
|-------------------|-----------------|-------|
| ₹10 discount on rental | 100 points | ₹10 |
| Free delivery | 150 points | ₹200 value |
| Deposit reduction (5%) | 500 points | Varies |
| Free day extension | 300 points | 1 day added |
| Priority support | 200 points | 1 month |

### 22.3 Points Expiry

- Points expire 12 months from date earned
- ARQ job runs monthly to expire old points
- Expiry notification sent 30 days before expiry
- Points are deducted in FIFO order (oldest first)

### 22.4 Referral Program

```
Referrer shares unique code → Referred uses code at registration
        ↓
Referred completes first rental → Both get points
        ↓
Referrer: 100 points credited
Referred: 50 points credited
Status updated to 'completed'
```

| Rule | Details |
|------|---------|
| **Referral Code** | Unique 8-character alphanumeric, auto-generated |
| **Validity** | No expiry on codes |
| **Limit** | No limit on referrals per user |
| **Fraud Prevention** | Same device/IP cannot be used for referrer + referred |
| **Reward Timing** | Credited after referred user's first successful rental |

---

## 32. Critical Edge Cases (Extended)

| Edge Case | Scenario | System Response |
|-----------|----------|-----------------|
| **Simultaneous Booking** | Two customers book same product same time | Redis lock prevents race condition. First to complete payment wins. Second notified with alternatives. |
| **Availability Mid-Checkout** | Product becomes unavailable during checkout | Cart invalidated. Customer notified. Suggested alternatives shown. |
| **Quote Expiry During Payment** | Payment processing when quote expires | Payment held in escrow. If quote expired, auto-refund initiated. |
| **Partial Group Payment** | Some group members pay, others don't | 48-hour window. If not all paid, rental blocked. Members notified. |
| **Enterprise Credit Limit Exceeded** | Order exceeds available credit | Block order. Notify Enterprise Admin. Require payment or credit limit increase. |
| **Stock Discrepancy at Return** | Physical count doesn't match system | Admin creates stock adjustment. Audit log records discrepancy. Investigation triggered. |
| **Points Redemption During Active Rental** | Customer tries to redeem points for active rental | Points redeemed. Discount applied to current rental invoice. |
| **Campaign Overlapping Discounts** | Customer has multiple active promotions | System applies best single discount (no stacking unless configured). |
| **CRM Auto-Scoring Accuracy** | Lead score doesn't reflect actual behavior | Admin can manually override lead score. Override logged in audit trail. |
| **Maintenance During Active Rental** | Scheduled maintenance overlaps with rental period | Maintenance rescheduled. Product flagged for post-return maintenance. |

---

## Final Guarantee Summary

| Guarantee | How We Deliver It |
|-----------|-------------------|
| Customer CANNOT cheat the system | E-KYC identity lock + device fingerprint + anti-swap QR/serial/RFID triple-check + tamper-proof custody trail + legal rental agreement with per-clause OTP + non-repudiation evidence |
| Groups CANNOT abuse shared deposits | Individual deposit auth holds per member + proportional deduction + joint & several liability in agreement + all member trust scores affected |
| Enterprise users get B2B-grade service | Entity KYC + team management + GST invoices + credit billing + custom pricing + dedicated account manager + API access |
| Admin has FULL visibility at all times | Real-time WebSocket dashboard + chain of custody at every stage + GPS at handoffs + complete audit log + recovery case data package |
| Zero manual work required | Auto late fee + auto reminders + auto invoice + auto deposit settlement + auto escalation to legal + auto group trust score recalculation |
| System is production-ready at zero cost | Every component free-tier or open-source. No credit card for any tool. |
| System scales with the business | Stateless FastAPI workers + connection pooling + Redis cache + CDN + read replica + materialized views |
| Security is enterprise-grade | JWT with 15-min access tokens + refresh rotation + httpOnly cookies + RBAC + rate limiting + TLS 1.3 + HSTS + CSP + Cloudflare DDoS |
| Data is safe and compliant | Audit logs immutable + documents retained 7 years + signed URLs + bcrypt passwords + OTP tokens hashed |

---

**— End of Rental Management System Project Plan v3.0 —**

**CONFIDENTIAL — INTERNAL USE ONLY**
