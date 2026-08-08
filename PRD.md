# PRODUCT REQUIREMENTS DOCUMENT (PRD)
## Rental Management System — Frontend Design & Feature Specification
### Version 3.0 | 2026 | FINAL

---

## Table of Contents

1. [Product Overview](#1-product-overview)
2. [Design System](#2-design-system)
3. [Public Portal (Guest)](#3-public-portal-guest)
4. [Customer Portal (Personal User)](#4-customer-portal-personal-user)
5. [Enterprise Portal](#5-enterprise-portal)
6. [Group Portal](#6-group-portal)
7. [Admin Portal](#7-admin-portal)
8. [Field Agent Portal](#8-field-agent-portal)
9. [Shared Components](#9-shared-components)
10. [Responsive Design Rules](#10-responsive-design-rules)
11. [Accessibility (WCAG 2.1)](#11-accessibility-wcag-21)
12. [Performance Requirements](#12-performance-requirements)

---

## 1. Product Overview

### 1.1 Product Vision

A unified rental management platform with role-based portals. Each user type (Guest, Customer, Enterprise, Group, Admin, Field Agent) sees a **tailored UI** showing only features relevant to their role.

### 1.2 Portal Summary

| Portal | Target User | Primary Purpose |
|--------|-------------|-----------------|
| **Public** | Guest (unauthenticated) | Browse catalog, view products, register/login |
| **Customer** | Personal User | Manage rentals, profile, payments, groups |
| **Enterprise** | Enterprise Admin + Sub-users | Team management, bulk orders, billing |
| **Group** | Group Leader + Members | Shared rentals, deposit pool, voting |
| **Admin** | Super Admin + Ops Admin | Full system management, dashboard, operations |
| **Agent** | Field Agent | QR scanning, inspections, route navigation |

---

## 2. Design System

### 2.1 Color Palette

| Token | Hex | Usage |
|-------|-----|-------|
| `primary` | `#1A237E` | Deep indigo — headers, primary buttons |
| `primary-light` | `#3949AB` | Hover states, secondary buttons |
| `primary-dark` | `#0D1642` | Dark mode backgrounds |
| `accent` | `#1565C0` | Electric blue — links, highlights, active states |
| `accent-light` | `#42A5F5` | Hover states for accent elements |
| `success` | `#2E7D32` | Green — available, approved, completed |
| `warning` | `#F57F17` | Yellow — pending, attention needed |
| `danger` | `#C62828` | Red — overdue, rejected, critical alerts |
| `info` | `#0277BD` | Blue — informational messages |
| `background` | `#FAFAFA` | Light mode background |
| `surface` | `#FFFFFF` | Cards, modals, panels |
| `text-primary` | `#212121` | Main text |
| `text-secondary` | `#757575` | Subtitles, descriptions |
| `border` | `#E0E0E0` | Dividers, borders |

### 2.2 Dark Mode

| Token | Hex | Usage |
|-------|-----|-------|
| `bg-dark` | `#0D1117` | Dark background |
| `surface-dark` | `#161B22` | Dark cards |
| `text-dark` | `#E6EDF3` | Dark mode text |
| `border-dark` | `#30363D` | Dark borders |

### 2.3 Typography

| Element | Font | Weight | Size | Line Height |
|---------|------|--------|------|-------------|
| H1 | Inter | 700 | 32px | 1.2 |
| H2 | Inter | 600 | 24px | 1.3 |
| H3 | Inter | 600 | 20px | 1.4 |
| H4 | Inter | 500 | 16px | 1.4 |
| Body | Inter | 400 | 14px | 1.5 |
| Small | Inter | 400 | 12px | 1.5 |
| Code/ID | JetBrains Mono | 400 | 13px | 1.4 |

### 2.4 Spacing Scale

| Token | Value |
|-------|-------|
| `xs` | 4px |
| `sm` | 8px |
| `md` | 16px |
| `lg` | 24px |
| `xl` | 32px |
| `2xl` | 48px |

### 2.5 Border Radius

| Element | Radius |
|---------|--------|
| Button | 8px |
| Card | 12px |
| Input | 8px |
| Modal | 16px |
| Avatar | 50% (circle) |
| Badge | 9999px (pill) |

### 2.6 Component Library

Built on **shadcn/ui** with Tailwind CSS. Key components:

| Component | Variants |
|-----------|----------|
| Button | primary, secondary, outline, ghost, danger, link |
| Input | text, email, phone, password, number, search |
| Select | single, multi, searchable |
| Card | default, interactive, stat |
| Dialog | modal, drawer (mobile), alert |
| Toast | success, error, warning, info |
| Badge | default, success, warning, danger, outline |
| Table | sortable, selectable, paginated |
| Tabs | horizontal, vertical |
| Dropdown | action menu, filter menu |
| Calendar | date picker, date range, date time |
| File Upload | drag-drop, camera capture, preview |
| Skeleton | loading placeholder |

---

## 3. Public Portal (Guest)

### 3.1 Landing Page (`/`)

**Layout:**
- Header: Logo | Navigation (Catalog, About) | Login | Sign Up
- Hero Section: "Rent Anything. Anytime. Anywhere." + Search Bar + CTA
- Featured Categories: 4 category cards with icons (Cameras, Bikes, Electronics, Furniture)
- Featured Products: 4 product cards with image, name, price, rating
- How It Works: 4-step visual (Browse → Select → Pay → Pickup)
- Footer: About | Contact | Terms | Privacy | Social Links

**Features:**
- Product catalog with filter sidebar
- Category browsing
- Product detail with photos, pricing, availability calendar
- Rental period selector
- Deposit amount display (based on default tier)
- "Login to Rent" CTA

### 3.2 Product Catalog (`/catalog`)

**Layout:**
- Breadcrumb: Home > Catalog
- Left Sidebar: Filters (Category, Price Range, Rating, Availability)
- Main Area: Product Grid (3-4 columns)
- Sort: Relevance, Price Low-High, Price High-Low, Rating, Newest
- View Toggle: Grid | List
- Pagination or Load More

**Product Card:**
- Product Image (hover to show second image)
- Product Name
- Category Badge
- Price per period (daily/weekly/monthly)
- Star Rating + Review Count
- "View Details" button
- Availability indicator (Available / Limited / Unavailable)

### 3.3 Product Detail (`/product/[id]`)

**Layout:**
- Breadcrumb: Home > Catalog > Product Name
- Left: Image gallery (main + thumbnails)
- Right: Product info, pricing, availability calendar, accessories list
- Below: Description, Reviews

**Key Elements:**
- Pricing table (hourly/daily/weekly/monthly)
- Security deposit amount with explanation
- Availability calendar (green=available, red=booked)
- Included accessories checklist
- "Login to Rent" CTA (or "Select Dates" if logged in)

### 3.4 Login Page (`/login`)

**Layout:**
- Centered card with logo
- Two login methods:
  1. Phone + OTP (primary)
  2. Email + Password (secondary)
- Social login buttons (Google, Apple)
- "Forgot Password?" link
- "Sign Up" link

### 3.5 Registration Page (`/register`)

**Layout:**
- Multi-step form (stepper UI)
- Step 1: Phone + OTP verification
- Step 2: Email + email verification
- Step 3: Basic profile (name, DOB)
- Step 4: Profile photo (optional)
- Step 5: KYC prompt (can defer)

---

## 4. Customer Portal (Personal User)

### 4.1 Dashboard (`/dashboard`)

**Layout:**
- Header: Logo | Search | Notifications Bell | Profile Avatar
- Sidebar: Dashboard, Orders, Rentals, Profile, KYC, Groups, Disputes, Invoices, Loyalty, Settings
- Main Area: Welcome message + stat cards + active rentals + upcoming pickups + recent activity

**Stat Cards (3-4 across):**
- Active Rentals (count)
- Trust Score (score + tier badge)
- Points Balance (with redeem button)
- Total Spent (lifetime)

**Active Rentals Section:**
- Product name + image
- Countdown timer (days, hours, minutes)
- "View Details" and "Request Extension" buttons

**Upcoming Pickups Section:**
- Product name
- Pickup date/time
- Store address or delivery tracking

**Recent Activity Feed:**
- Invoice downloaded
- Payment received
- Trust score change
- Notification received

### 4.2 My Orders (`/orders`)

**Layout:**
- Filter bar: Status dropdown, Date range, Search by order ID
- Order list with cards

**Order Card:**
- Order number (RNT-2026-00042)
- Status badge (Active=green, Completed=blue, Overdue=red, Cancelled=gray)
- Product name + rental period
- Dates (start to end)
- Deposit status (held/refunded/partially deducted)
- Action buttons: View Details, Download Invoice, Rate (if completed)

### 4.3 Active Rental Detail (`/rentals/[id]`)

**Layout:**
- Breadcrumb: Rentals > RNT-2026-00042
- Rental Countdown Timer (prominent, centered)
- Product Details card
- Accessories Checklist (at pickup)
- Chain of Custody Timeline (vertical timeline with dots)
- Action buttons: Request Extension, Initiate Return, Download Agreement

**Countdown Timer:**
- Large numbers: 2 DAYS 14 HOURS 32 MINS
- Progress bar showing time elapsed
- Return deadline date/time
- Color changes: Green (>24h) → Yellow (<24h) → Red (overdue)

**Chain of Custody Timeline:**
- Vertical line with dots at each stage
- Completed stages: filled dot (green/blue)
- Current stage: pulsing dot
- Future stages: empty dot (gray)
- Each stage shows: timestamp, actor, condition, photos link

### 4.4 KYC Verification (`/kyc`)

**Layout:**
- Progress bar (60% complete)
- Step list with status icons (completed=check, in-progress=spinner, pending=lock)
- Current step form
- Trust score projection after completion

**Steps:**
1. Phone Verification ✅
2. Email Verification ✅
3. Government ID Upload ✅
4. Selfie + Liveness Check (in progress)
5. Address Verification
6. Payment Method
7. Device Fingerprint (auto)

### 4.5 My Profile (`/profile`)

**Layout:**
- Profile photo (editable)
- Personal info form (name, email, phone, DOB)
- KYC status card
- Trust score card with history
- Notification preferences toggle switches
- Active sessions list
- Danger zone (delete account)

### 4.6 My Groups (`/groups`)

**Layout:**
- List of groups user belongs to
- Create Group button
- Group cards showing: name, member count, trust score, status

### 4.7 Loyalty & Referrals (`/loyalty`)

**Layout:**
- Points balance card (large number)
- Tier badge (Bronze/Silver/Gold/Platinum)
- Referral stats card
- Points history table
- Redemption options grid
- Referral code + share buttons

---

## 5. Enterprise Portal

### 5.1 Enterprise Dashboard (`/enterprise/dashboard`)

**Layout:**
- Header: Logo | Enterprise Name | Notifications | Admin Profile
- Sidebar: Dashboard, Team, Orders, Billing, Pricelist, Analytics, Settings
- Main Area: Enterprise stats + team activity + credit usage

**Stat Cards:**
- Active Rentals (team total)
- Credit Used / Credit Limit (progress bar)
- Team Members (active count)
- Monthly Spend

**Team Activity Feed:**
- Recent team rentals
- Pending approvals
- Credit transactions

### 5.2 Team Management (`/enterprise/team`)

**Layout:**
- Invite Member button
- Team member table with columns: Name, Role, Department, Status, Actions
- Role badges (Admin, Procurement, Department User, Auditor)
- Invite dialog with form fields

### 5.3 Billing Dashboard (`/enterprise/billing`)

**Layout:**
- Summary cards: Total Billed, Pending Payment, Overdue, Credit Balance
- Invoice table with filters
- Invoice detail view
- Payment history
- Credit usage chart

### 5.4 Bulk Order Creation (`/enterprise/orders/new`)

**Layout:**
- Product search and add
- Order summary table (multiple products)
- Delivery options
- Combined invoice preview
- Submit for approval button

---

## 6. Group Portal

### 6.1 Group Dashboard (`/group/[id]`)

**Layout:**
- Header: Group Name | Member Count | Trust Score Badge
- Sidebar: Dashboard, Members, Rentals, Deposits, Votes, Settings
- Main Area: Trust score card + members list + active rentals + pending votes

**Trust Score Card:**
- Large score display (67.5 / 100)
- Tier badge (Standard)
- Max rental value
- Score breakdown by member

**Members List:**
- Avatar + name + trust score
- Role badge (Leader/Member)
- Status (Active/Invited/Removed)
- Deposit share percentage

**Pending Votes Section:**
- Vote type (extension, dispute)
- Description
- Votes for/against count
- Approve/Reject buttons
- Expiration countdown

### 6.2 Group Rentals (`/group/[id]/rentals`)

**Layout:**
- List of group rentals
- Rental cards with: product, dates, deposit pool status, settlement status

### 6.3 Deposit Pool (`/group/[id]/deposits`)

**Layout:**
- Total deposit required
- Total collected (progress bar)
- Per-member breakdown table: Member, Share %, Amount, Payment Status, Refund Status
- Action buttons (for leader)

### 6.4 Group Settings (`/group/[id]/settings`)

**Layout:**
- Group name edit
- Max members setting
- Dissolve group button (danger zone)
- Transfer leadership button

---

## 7. Admin Portal

### 7.1 Admin Dashboard (`/admin/dashboard`)

**Layout:**
- Header: Logo | Global Search | Alert Bell | Notifications | Admin Profile
- Priority Feed Bar (top): URGENT (red) | DO TODAY (yellow) | FYI (green)
- Sidebar: Dashboard, Rentals, Customers, Products, Categories, Quotes, Invoices, Deposits, Inspections, Repairs, Recovery, Disputes, Blacklist, Pricelists, CRM, Stock, Notifications, Audit, Settings, Team
- Main Area: Real-time metric cards + charts + actionable feed

**Metric Cards (2 rows of 6):**
- Active Rentals (count, trend arrow)
- Rentals Due Today (count, action button)
- Overdue NOW (count, red alert)
- Revenue This Month (₹ amount)
- Deposits Held (₹ amount)
- Late Fees Collected (₹ amount)
- Recovery Cases Open (count)
- Repair Cases Open (count)
- Open Disputes (count)
- Trust Score Distribution (mini bar chart)
- Overdue Value at Risk (₹ amount)
- CRM Leads (count)

**Charts:**
- Revenue trend (line chart, last 30 days)
- Rentals by category (pie chart)
- Trust tier distribution (bar chart)
- Late return rate (line chart)

**Actionable Priority Feed:**
- URGENT: Items overdue by 2+ hours → [Call Customer] [Send Alert] [Dispatch]
- DO TODAY: Pickups scheduled → [View Route] [Print Checklist]
- DO TODAY: Return inspections pending → [Start Inspection]
- FYI: Revenue trends → [View Report]
- REVIEW: Disputes filed → [Review Dispute]

### 7.2 Customer Management (`/admin/customers`)

**Layout:**
- Search bar (name, phone, email, ID)
- Filter: Trust tier, KYC status, blacklist status, registration date
- Customer table with columns: Name, Phone, Email, Trust Score, Tier, KYC Status, Rentals, Actions
- Customer detail view with tabs: Profile, KYC, Rentals, Deposits, Disputes, Audit

### 7.3 Product Management (`/admin/products`)

**Layout:**
- Add Product button
- Filter: Category, Status, Availability
- Product table with columns: Image, Name, SKU, Category, Status, Condition, Rentals, Actions
- Product detail view with tabs: Info, Variants, Accessories, Calendar, History, Maintenance
- Product availability calendar (monthly view)

### 7.4 Rental Management (`/admin/rentals`)

**Layout:**
- Filter: Status, Date range, Customer, Product
- Rental table with columns: Order #, Customer, Product, Period, Status, Deposit, Actions
- Rental detail view with tabs: Details, Custody, Invoice, Deposit, Extensions, Disputes

### 7.5 Quotation Pipeline (`/admin/quotations`)

**Layout:**
- Kanban board view: Draft → Sent → Viewed → Accepted → Confirmed
- Or list view with status filters
- Create quotation dialog
- Quotation detail with PDF preview

### 7.6 Invoice Management (`/admin/invoices`)

**Layout:**
- Filter: Status, Date range, Type, Customer
- Invoice table with columns: Invoice #, Customer, Amount, Status, Due Date, Actions
- Invoice detail with line items, payment history, PDF download

### 7.7 Inspection Queue (`/admin/inspections`)

**Layout:**
- Pending inspections list
- Inspection form with: QR scan, photo upload, accessory checklist, condition rating
- Inspection history

### 7.8 CRM Dashboard (`/admin/crm`)

**Layout:**
- Lead pipeline funnel chart
- Recent interactions feed
- Campaign performance metrics
- Contact management table
- Campaign creation form

### 7.9 Stock Management (`/admin/stock`)

**Layout:**
- Stock levels by location
- Movement history table
- Transfer form
- Adjustment form with approval workflow
- Maintenance schedule calendar

---

## 8. Field Agent Portal

### 8.1 Agent Dashboard (`/agent/dashboard`)

**Layout:**
- Minimal header with agent name and avatar
- Today's assignments list
- Quick actions: Scan QR, Start Inspection, View Route
- Map view (optional)

**Assignment Card:**
- Type badge (Pickup/Return)
- Customer name
- Product name
- Address
- Time window
- [Start] [Navigate] buttons

### 8.2 QR Scanner (`/agent/scan`)

**Layout:**
- Full-screen camera view
- QR frame overlay
- Scan result overlay
- Action buttons after scan: [Confirm] [Retake] [Report Issue]

**Scan Result Overlay:**
- Product name + image
- Serial number
- Rental ID
- Customer name
- Expected condition
- [Proceed with Inspection] button

### 8.3 Inspection Form (`/agent/inspection`)

**Layout:**
- Product info header
- Photo upload grid (front, back, left, right, top)
- Accessory checklist (toggle each item)
- Condition rating (1-5 stars)
- Notes text area
- Digital signature pad
- [Submit Inspection] button

### 8.4 Route View (`/agent/route`)

**Layout:**
- Map with route markers
- Stop list with addresses
- Estimated time between stops
- Navigation button (opens Google Maps)
- Complete stop button

---

## 9. Shared Components

### 9.1 Notification Bell

- Badge with unread count
- Dropdown with notification list
- Each notification: icon, title, body, timestamp, read/unread status
- "Mark all as read" button
- Link to full notification center

### 9.2 User Profile Dropdown

- Profile photo + name + role badge
- Quick links: Profile, Settings, Logout
- Dark mode toggle
- Notification preferences

### 9.3 Search Bar

- Global search across products, customers, orders
- Autocomplete with recent searches
- Keyboard navigation (arrow keys + enter)

### 9.4 Modal/Dialog

- Centered overlay
- Close button (X) + click outside to close
- Focus trap for accessibility
- Mobile: full-screen drawer from bottom

### 9.5 Toast Notifications

- Slide in from top-right
- Auto-dismiss after 5 seconds
- Types: success (green), error (red), warning (yellow), info (blue)
- Action button (optional)

### 9.6 Data Table

- Sortable columns (click header)
- Pagination (10/25/50/100 per page)
- Row selection (checkboxes)
- Bulk actions dropdown
- Empty state illustration
- Loading skeleton

### 9.7 Empty States

- Illustration (SVG)
- Title ("No orders yet")
- Description ("Your orders will appear here after you make your first rental")
- Action button ("Browse Catalog")

### 9.8 Loading States

- Skeleton screens for content
- Spinner for buttons
- Progress bar for uploads
- Shimmer effect for cards

---

## 10. Responsive Design Rules

### 10.1 Breakpoints

| Breakpoint | Width | Layout |
|------------|-------|--------|
| Mobile | < 640px | Single column, stacked sidebar, bottom nav |
| Tablet | 640-1024px | Two columns, collapsible sidebar |
| Desktop | > 1024px | Full layout with fixed sidebar |
| Large Desktop | > 1440px | Wider content area, more columns |

### 10.2 Mobile Adaptations

| Element | Desktop | Mobile |
|---------|---------|--------|
| Sidebar | Fixed left | Bottom tab bar |
| Tables | Full table | Card list view |
| Modals | Centered overlay | Full-screen drawer |
| Filters | Sidebar | Bottom sheet |
| Calendar | Full calendar | Scrollable date picker |
| Charts | Full size | Stacked vertically |

### 10.3 Touch Interactions

- Swipe to delete (with confirmation)
- Pull to refresh
- Long press for context menu
- Pinch to zoom on images
- Tap to select, double-tap to open

---

## 11. Accessibility (WCAG 2.1)

### 11.1 Requirements

| Requirement | Implementation |
|-------------|----------------|
| **Keyboard Navigation** | All interactive elements focusable with Tab |
| **Focus Indicators** | Visible focus ring on all focusable elements |
| **Screen Reader Labels** | aria-label on icons, buttons, images |
| **Color Contrast** | Minimum 4.5:1 for text, 3:1 for large text |
| **Alt Text** | All images have descriptive alt text |
| **Form Labels** | All inputs have associated labels |
| **Error Messages** | Linked to inputs via aria-describedby |
| **Skip Navigation** | "Skip to main content" link |
| **Semantic HTML** | Proper heading hierarchy, landmarks |
| **Motion** | Respect prefers-reduced-motion |

### 11.2 Component Accessibility

| Component | Accessibility Feature |
|-----------|----------------------|
| Button | role="button", aria-disabled |
| Modal | aria-modal, focus trap, escape to close |
| Dropdown | aria-expanded, aria-haspopup |
| Tabs | aria-selected, arrow key navigation |
| Table | aria-sort, aria-label for sort buttons |
| Toast | aria-live="polite" for announcements |
| Calendar | aria-label for dates, keyboard navigation |

---

## 12. Performance Requirements

### 12.1 Core Web Vitals

| Metric | Target | Measurement |
|--------|--------|-------------|
| **LCP** (Largest Contentful Paint) | < 2.5s | Time to render largest content element |
| **FID** (First Input Delay) | < 100ms | Time from user interaction to response |
| **CLS** (Cumulative Layout Shift) | < 0.1 | Visual stability during page load |
| **TTFB** (Time to First Byte) | < 200ms | Server response time |

### 12.2 Page Load Targets

| Page | Target Load Time |
|------|------------------|
| Landing page | < 1.5s (SSG) |
| Product catalog | < 2s (ISR, 60s revalidation) |
| Product detail | < 2s (SSG + client data) |
| Dashboard | < 2.5s (SSR) |
| Admin dashboard | < 3s (CSR + WebSocket) |

### 12.3 Optimization Strategies

| Strategy | Implementation |
|----------|----------------|
| **Static Generation** | Product catalog, landing page (ISR) |
| **Server Rendering** | Customer dashboard, profile pages |
| **Client Rendering** | Admin dashboard, real-time pages |
| **Code Splitting** | Dynamic imports for heavy components |
| **Image Optimization** | Next.js Image component with lazy loading |
| **Font Optimization** | next/font with preload |
| **Bundle Analysis** | @next/bundle-analyzer |
| **Caching** | React Query with staleTime + cacheTime |
| **Prefetching** | Link prefetch on hover |
| **Compression** | Brotli/gzip via Vercel/Cloudflare |

### 12.4 Real-Time Performance

| Feature | Update Frequency | Method |
|---------|------------------|--------|
| Admin dashboard metrics | Every 60 seconds | WebSocket push |
| Rental countdown timer | Every second | Client-side interval |
| Late fee display | Every 60 seconds | WebSocket push |
| Notification badges | Real-time | WebSocket push |
| Group deposit progress | On event | WebSocket push |

---

**— End of PRD.md —**
