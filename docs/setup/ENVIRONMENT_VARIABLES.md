# Complete Environment Variables Reference

## Backend Variables (`rental-backend/.env`)

### Application

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `APP_NAME` | No | `"Rental Management System"` | Application display name |
| `APP_VERSION` | No | `"3.0.0"` | Current version |
| `APP_ENV` | **Yes** | `"development"` | `development` / `staging` / `production` |
| `DEBUG` | **Yes** | `true` | Enable debug mode, SQL logging, docs |
| `SECRET_KEY` | **Yes** | - | 256-bit random key for app security |
| `ALLOWED_ORIGINS` | **Yes** | `["http://localhost:3000"]` | CORS allowed origins (JSON array) |

### Database (NeonDB PostgreSQL)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | **Yes** | - | Primary DB connection (asyncpg) |
| `DATABASE_READ_URL` | No | Same as primary | Read replica connection |
| `DATABASE_POOL_SIZE` | No | `10` | Connection pool size |
| `DATABASE_MAX_OVERFLOW` | No | `20` | Max burst connections |
| `DATABASE_POOL_TIMEOUT` | No | `30` | Seconds before pool timeout |

**Format:** `postgresql+asyncpg://user:password@host/dbname?sslmode=require`

### Redis (Upstash)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `REDIS_URL` | **Yes** | - | Redis connection (TLS for Upstash) |
| `REDIS_MAX_CONNECTIONS` | No | `20` | Max connections in pool |
| `ARQ_REDIS_URL` | No | Same as `REDIS_URL` | Worker Redis (can separate) |

**Format:** `rediss://:password@host:6379` (Upstash) or `redis://localhost:6379` (local)

### JWT Authentication

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `JWT_SECRET_KEY` | **Yes** | - | JWT signing key (256-bit) |
| `JWT_ALGORITHM` | No | `HS256` | JWT algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | No | `15` | Access token TTL |
| `REFRESH_TOKEN_EXPIRE_DAYS` | No | `30` | Refresh token TTL |

### File Storage (Backblaze B2)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `STORAGE_ACCOUNT_ID` | No | - | Account ID (optional for B2) |
| `STORAGE_ACCESS_KEY_ID` | **Yes** | - | B2 Application Key ID |
| `STORAGE_SECRET_ACCESS_KEY` | **Yes** | - | B2 Application Key |
| `STORAGE_BUCKET_NAME` | No | `rental-files` | Bucket name |
| `STORAGE_PUBLIC_URL` | **Yes** | - | Public URL for file access |
| `STORAGE_ENDPOINT_URL` | **Yes** | - | S3-compatible endpoint |

**Endpoint format:** `https://s3.us-west-004.backblazeb2.com`
**Public URL format:** `https://f004.backblazeb2.com/file/rental-files`

### Payments (Razorpay)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `RAZORPAY_KEY_ID` | **Yes** | - | Razorpay API key (`rzp_test_xxx` / `rzp_live_xxx`) |
| `RAZORPAY_KEY_SECRET` | **Yes** | - | Razorpay secret key |
| `RAZORPAY_WEBHOOK_SECRET` | **Yes** | - | Webhook signature secret |

### E-KYC Providers

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DIGIO_API_KEY` | **Yes** | - | Digio client ID (Aadhaar/e-sign) |
| `DIGIO_API_SECRET` | **Yes** | - | Digio client secret |
| `SUREPASS_API_KEY` | No | - | Surepass API key (PAN/GST) |
| `FACEIO_APP_ID` | No | - | FaceIO app ID (biometric) |
| `FACEIO_SECRET` | No | - | FaceIO secret key |

### Notifications

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `RESEND_API_KEY` | **Yes** | - | Resend API key (`re_xxxx`) |
| `EMAIL_FROM` | **Yes** | - | Sender email (`noreply@yourdomain.com`) |
| `MSG91_API_KEY` | **Yes** | - | MSG91 auth key (SMS) |
| `MSG91_TEMPLATE_ID` | **Yes** | - | MSG91 OTP template ID |

### Monitoring

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SENTRY_DSN` | No | - | Sentry DSN for error tracking |
| `LOG_LEVEL` | No | `INFO` | Logging level |

### Worker (ARQ)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `WORKER_CONCURRENCY` | No | `4` | Max concurrent jobs |
| `WORKER_MAX_RETRIES` | No | `3` | Max retry attempts |

---

## Frontend Variables (`rental-frontend/ODOO-FRONT-/.env.local`)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `NEXT_PUBLIC_API_URL` | **Yes** | - | Backend API base URL |
| `NEXT_PUBLIC_WS_URL` | **Yes** | - | WebSocket URL |
| `NEXT_PUBLIC_APP_NAME` | No | `"Reprico"` | Display name |
| `NEXT_PUBLIC_APP_VERSION` | No | `"1.0.0"` | Frontend version |
| `GEMINI_API_KEY` | No | - | Google Gemini AI key |
| `NEXT_PUBLIC_RAZORPAY_KEY_ID` | **Yes** | - | Razorpay key for checkout |
| `NEXT_PUBLIC_SENTRY_DSN` | No | - | Sentry DSN for frontend |

**Important:** Frontend env vars must be prefixed with `NEXT_PUBLIC_` to be accessible in browser.

---

## Quick Copy Template

```bash
# ===========================================
# APPLICATION
# ===========================================
APP_NAME="Rental Management System"
APP_VERSION="3.0.0"
APP_ENV=development
DEBUG=true
SECRET_KEY=generate-a-random-256-bit-key
ALLOWED_ORIGINS=["http://localhost:3000","http://localhost:3001"]

# ===========================================
# DATABASE (NeonDB PostgreSQL)
# ===========================================
DATABASE_URL=postgresql+asyncpg://user:password@ep-xxx.neon.tech/rental_db?sslmode=require
DATABASE_READ_URL=postgresql+asyncpg://user:password@ep-yyy.neon.tech/rental_db?sslmode=require
DATABASE_POOL_SIZE=10
DATABASE_MAX_OVERFLOW=20
DATABASE_POOL_TIMEOUT=30

# ===========================================
# REDIS (Upstash)
# ===========================================
REDIS_URL=rediss://:password@xxx.upstash.io:6379
REDIS_MAX_CONNECTIONS=20
ARQ_REDIS_URL=rediss://:password@xxx.upstash.io:6379

# ===========================================
# JWT AUTHENTICATION
# ===========================================
JWT_SECRET_KEY=generate-a-random-secret-key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=30

# ===========================================
# FILE STORAGE (Backblaze B2 - Free 10GB)
# ===========================================
STORAGE_ACCESS_KEY_ID=your_b2_key_id
STORAGE_SECRET_ACCESS_KEY=your_b2_app_key
STORAGE_BUCKET_NAME=rental-files
STORAGE_PUBLIC_URL=https://f004.backblazeb2.com/file/rental-files
STORAGE_ENDPOINT_URL=https://s3.us-west-004.backblazeb2.com

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
RESEND_API_KEY=re_xxx
EMAIL_FROM=noreply@yourdomain.com
MSG91_API_KEY=your-msg91-key
MSG91_TEMPLATE_ID=your-template-id

# ===========================================
# MONITORING
# ===========================================
SENTRY_DSN=https://xxx@sentry.io/xxx
LOG_LEVEL=INFO

# ===========================================
# WORKER
# ===========================================
WORKER_CONCURRENCY=4
WORKER_MAX_RETRIES=3
```

---

## Environment Profiles

### Development

```bash
APP_ENV=development
DEBUG=true
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/rental_db
REDIS_URL=redis://localhost:6379
# External services can use sandbox/test keys
```

### Staging

```bash
APP_ENV=staging
DEBUG=false
DATABASE_URL=postgresql+asyncpg://...neon.tech/rental_db?sslmode=require
REDIS_URL=rediss://...upstash.io:6379
# Use Razorpay test keys, Digio sandbox
```

### Production

```bash
APP_ENV=production
DEBUG=false
SECRET_KEY=<random 256-bit>
JWT_SECRET_KEY=<random 256-bit>
DATABASE_URL=postgresql+asyncpg://...neon.tech/rental_db?sslmode=require
DATABASE_READ_URL=postgresql+asyncpg://...neon.tech/rental_db?sslmode=require
REDIS_URL=rediss://...upstash.io:6379
# All service keys must be production/live
```

---

## Generating Secret Keys

```bash
# Generate 256-bit random key
python -c "import secrets; print(secrets.token_hex(32))"

# Or for JWT
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

---

## Security Notes

1. **Never commit `.env` files** - they're in `.gitignore`
2. **Rotate keys** if any leak is suspected
3. **Use different keys** for dev/staging/production
4. **Restrict CORS** in production (no `*`)
5. **Disable debug** in production (`DEBUG=false`)
6. **Use TLS** for Redis (`rediss://`) in production
7. **Validate env vars** on startup (Pydantic does this automatically)
