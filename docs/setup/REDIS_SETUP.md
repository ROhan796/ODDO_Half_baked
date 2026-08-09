# Upstash Redis Setup Guide

## Overview

Reprico uses **Upstash Redis** for:
- Session/token caching
- Rate limiting
- Real-time pub/sub (WebSocket)
- Background job queue (ARQ workers)
- Query result caching (CacheManager)

## Step 1: Create Upstash Account

1. Go to [https://upstash.com](https://upstash.com)
2. Sign up with GitHub
3. Click **"Create Database"**

## Step 2: Create Redis Database

| Setting | Value |
|---------|-------|
| **Name** | `reprico-redis` |
| **Type** | Regional (choose closest region) |
| **Plan** | Free tier (10K commands/day) or Pay-as-you-go |

### Get Connection Details

After creation, you get:

```
REDIS_URL=rediss://default:xxxx@xxx.upstash.io:6379
```

**Important:** Upstash uses `rediss://` (TLS) protocol.

## Step 3: Configure Environment Variables

```bash
# rental-backend/.env

# Primary Redis (cache, sessions, rate limiting)
REDIS_URL=rediss://default:Axxtokenxxxx@xxx.upstash.io:6379
REDIS_MAX_CONNECTIONS=20

# Worker Redis (same instance, or separate for isolation)
ARQ_REDIS_URL=rediss://default:Axxtokenxxxx@xxx.upstash.io:6379
```

## Step 4: Understanding the Redis Usage

### 1. Cache Manager (`app/core/cache.py`)

```python
# Pattern-based caching with TTL
await cache.set("products:abc123", product_data, ttl=3600)  # 1 hour
await cache.get("products:abc123")
await cache.invalidate_pattern("products:*")  # Clear all product caches

# @cached decorator
@cached(prefix="dashboard_stats", ttl=300)  # 5 minutes
async def get_dashboard_stats(db):
    ...
```

**Cache Key Patterns:**
```
products:{hash}      → Product listings (TTL: 1h)
dashboard:{hash}     → Dashboard stats (TTL: 5m)
rentals:{hash}       → Rental listings (TTL: 5m)
user:{user_id}       → User sessions (TTL: 15m)
rate_limit:{ip}      → Rate limit counters (TTL: 1m)
otp:{phone}          → OTP codes (TTL: 5m)
```

### 2. Rate Limiter (`app/middleware/rate_limiter.py`)

```python
# Limits stored in Redis with sliding window
rate_limit:{identifier}:{window} → counter
```

### 3. ARQ Background Jobs (`app/workers/settings.py`)

```python
# Job queue stored in Redis
arq:queue → pending jobs
arq:result:{job_id} → job results (TTL: 3600s)
```

### 4. WebSocket Pub/Sub

```python
# Real-time notifications
channel: user:{user_id} → notification payloads
channel: rental:{rental_id} → status updates
```

## Step 5: Redis Connection Architecture

```
┌─────────────────────────────────────────────┐
│              UPSTASH REDIS                   │
│  Region: us-east-1 (or your region)         │
│  Protocol: TLS (rediss://)                  │
└──────────────┬──────────────────────────────┘
               │
    ┌──────────┴──────────┐
    │                     │
    ▼                     ▼
┌─────────┐         ┌──────────┐
│  FastAPI │         │   ARQ    │
│  App     │         │  Worker  │
│          │         │          │
│ - Cache  │         │ - Jobs   │
│ - Rate   │         │ - Cron   │
│   Limit  │         │ - Retry  │
│ - Session│         │          │
│ - PubSub │         │          │
└─────────┘         └──────────┘
```

## Step 6: Connection Pool Configuration

```python
# app/utils/redis.py
redis_pool = aioredis.ConnectionPool.from_url(
    settings.REDIS_URL,
    max_connections=20,        # Total connections in pool
    retry_on_timeout=True,    # Auto-retry on timeout
    socket_timeout=5,         # 5s timeout per command
    socket_connect_timeout=5, # 5s connection timeout
    decode_responses=True,    # Auto-decode to strings
)
```

### Upstash-Specific Tuning

| Setting | Dev | Production |
|---------|-----|------------|
| `max_connections` | 10 | 20-50 |
| `socket_timeout` | 5s | 3s |
| `retry_on_timeout` | True | True |
| `pool_timeout` | 5s | 10s |

## Step 7: Monitoring

### Upstash Dashboard

1. Go to your database → **Metrics**
2. Monitor:
   - Commands/sec
   - Memory usage
   - Connection count
   - Hit/miss ratio

### Redis CLI Access

```bash
# From Upstash Console → CLI tab
redis-cli -u rediss://default:xxxx@xxx.upstash.io:6379

# Useful commands
INFO memory          # Memory usage
KEYS products:*      # List cache keys (careful in prod)
DBSIZE               # Total keys
```

## Step 8: Security

### TLS (Required for Upstash)

Already handled by `rediss://` protocol in connection string.

### ACL (Access Control)

Upstash provides token-based auth. Rotate tokens periodically:

1. Upstash Console → **Settings** → **Reset Token**
2. Update `REDIS_URL` in your env
3. Redeploy

### IP Allowlisting

1. Upstash Console → **Settings** → **IP Allowlist**
2. Add your server IPs

## Step 9: Upstash vs Local Redis

| Feature | Upstash | Local Redis |
|---------|---------|-------------|
| Persistence | Optional | Manual |
| TLS | Built-in | Manual setup |
| Scaling | Automatic | Manual |
| Cost | Pay per command | Free (self-hosted) |
| Latency | ~1-5ms | <1ms |

### Development Option: Local Redis

```bash
# Use Docker for local dev
docker run -d --name rental-redis -p 6379:6379 redis:7-alpine

# .env for local
REDIS_URL=redis://localhost:6379
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Connection refused | Check `rediss://` protocol, not `redis://` |
| TLS errors | Ensure Upstash token is valid |
| Rate limit hit | Upgrade plan or optimize command usage |
| Slow queries | Check `KEYS` usage (use `SCAN` instead) |
| Memory limit | Set TTL on all cached data |
| Worker not connecting | Ensure `ARQ_REDIS_URL` matches `REDIS_URL` |
