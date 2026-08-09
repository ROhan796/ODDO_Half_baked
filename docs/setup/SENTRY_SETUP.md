# Sentry Error Monitoring Setup

## Overview

Reprico uses **Sentry** for real-time error tracking, performance monitoring, and alerting across backend and frontend.

## Step 1: Create Sentry Account

1. Go to [https://sentry.io](https://sentry.io)
2. Sign up with GitHub
3. Free tier: 5,000 errors/month, 10K performance spans

## Step 2: Create Project

1. Sentry Dashboard → **Create Project**

| Setting | Value |
|---------|-------|
| **Platform** | Python |
| **Framework** | FastAPI |
| **Project Name** | `reprico-backend` |

2. Create another project for frontend:

| Setting | Value |
|---------|-------|
| **Platform** | JavaScript |
| **Framework** | Next.js |
| **Project Name** | `reprico-frontend` |

## Step 3: Get DSN

1. Project Settings → **Client Keys (DSN)**
2. Copy the DSN: `https://xxxx@sentry.io/xxxx`

## Step 4: Configure Backend (Already Integrated)

```bash
# rental-backend/.env

SENTRY_DSN=https://xxxx@sentry.io/xxxx
LOG_LEVEL=INFO
```

### Current Integration (`app/main.py`)

```python
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

if settings.SENTRY_DSN:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        integrations=[FastApiIntegration()],
        traces_sample_rate=0.1,  # 10% of requests
    )
```

### Enhanced Configuration (Recommended)

```python
# app/main.py - enhanced Sentry setup
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

if settings.SENTRY_DSN:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        environment=settings.APP_ENV,
        release=f"reprico-backend@{settings.APP_VERSION}",
        integrations=[
            FastApiIntegration(),
            SqlalchemyIntegration(),
        ],
        traces_sample_rate=0.1,
        profiles_sample_rate=0.1,  # Performance profiling
        send_default_pii=False,  # Don't send PII for compliance
        before_send=filter_sensitive_data,
    )


def filter_sensitive_data(event, hint):
    """Strip sensitive data before sending to Sentry."""
    if "exc_info" in hint:
        exc_type, exc_value, exc_tb = hint["exc_info"]
        # Don't send password or token errors
        if "password" in str(exc_value).lower():
            return None
    return event
```

## Step 5: Configure Frontend

```bash
# rental-frontend/ODOO-FRONT-/.env.local

NEXT_PUBLIC_SENTRY_DSN=https://xxxx@sentry.io/xxxx
```

### Add Sentry to Next.js

```bash
npx @sentry/wizard@latest -i nextjs
```

Or manually add to `next.config.ts`:

```typescript
import { withSentryConfig } from "@sentry/nextjs";

export default withSentryConfig(
  {
    // Next.js config
  },
  {
    org: "your-org",
    project: "reprico-frontend",
    silent: true,
    widenClientFileUpload: true,
    disableLogger: true,
  }
);
```

## Step 6: Alert Rules

### Critical Alerts

1. Sentry Dashboard → **Alerts** → **Create Alert Rule**

| Alert | Condition | Action |
|-------|-----------|--------|
| **New Error** | First seen issue | Email + Slack |
| **High Error Rate** | >5% of sessions | Email + Slack |
| **Performance Degradation** | P95 >2s | Email |
| **Database Errors** | Any DB exception | Email immediately |

### Slack Integration

1. Sentry → **Settings** → **Integrations** → **Slack**
2. Connect workspace
3. Configure alert rules to post to `#alerts` channel

## Step 7: Performance Monitoring

### Backend Spans

```python
# Manual instrumentation for critical paths
from sentry_sdk import start_span

@router.post("/rentals")
async def create_rental(data: RentalCreate, db=Depends(get_db)):
    with start_span(op="db", description="Create rental record"):
        rental = await rental_service.create(db, data)

    with start_span(op="payment", description="Process payment"):
        await payment_service.create_order(rental.total_amount)

    return rental
```

### Database Query Tracking

Already enabled via `SqlalchemyIntegration` - slow queries (>1s) are automatically captured.

## Step 8: Release Tracking

```bash
# During deployment
export SENTRY_RELEASE=$(git rev-parse --short HEAD)

# Set release in Sentry
sentry-cli releases new $SENTRY_RELEASE
sentry-cli releases finalize $SENTRY_RELEASE
```

## Step 9: Source Maps (Frontend)

```bash
# Upload source maps during build
npx @sentry/cli@sentrycli releases files $SENTRY_RELEASE upload-sourcemaps .next/
```

## Environment Variables

```bash
# Backend
SENTRY_DSN=https://xxxx@sentry.io/xxxx
LOG_LEVEL=INFO

# Frontend
NEXT_PUBLIC_SENTRY_DSN=https://xxxx@sentry.io/xxxx
```

## What Gets Captured

| Auto-Captured | Manual Capture |
|---------------|----------------|
| Unhandled exceptions | Custom errors |
| HTTP 5xx responses | Business logic errors |
| Slow database queries | Performance bottlenecks |
|慢 API responses | Custom transactions |

## What Does NOT Get Captured (By Design)

- Health check endpoints (`/health`)
- 4xx client errors (except 429)
- PII (passwords, tokens, Aadhaar numbers)
- Local development errors (unless `APP_ENV=development`)

## Troubleshooting

| Issue | Solution |
|-------|----------|
| No errors showing | Check `SENTRY_DSN` is set correctly |
| Too many events | Lower `traces_sample_rate` or add `before_send` filter |
| Source maps not working | Ensure source maps are uploaded during build |
| PII leaking | Add `before_send` filter, set `send_default_pii=False` |
