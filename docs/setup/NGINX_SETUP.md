# Nginx Reverse Proxy Setup

## Overview

Nginx sits in front of the FastAPI backend, handling:
- **SSL termination** (HTTPS)
- **Rate limiting** (API + Auth endpoints)
- **WebSocket proxying** (real-time updates)
- **Gzip compression** (smaller payloads)
- **Security headers** (XSS, clickjacking, etc.)
- **Load balancing** (multiple API workers)

## Architecture

```
                    Internet
                       │
                       ▼
              ┌─────────────────┐
              │     Nginx       │
              │   :80 → :443    │
              │                 │
              │  Rate Limiting  │
              │  SSL Termination│
              │  Gzip           │
              │  Security HDRs  │
              └────────┬────────┘
                       │
          ┌────────────┼────────────┐
          │            │            │
          ▼            ▼            ▼
     ┌─────────┐ ┌─────────┐ ┌─────────┐
     │  API #1  │ │  API #2  │ │  API #3  │
     │  :8000   │ │  :8001   │ │  :8002   │
     └─────────┘ └─────────┘ └─────────┘
```

## Current Configuration

### Rate Limiting Zones

| Zone | Rate | Burst | Purpose |
|------|------|-------|---------|
| `api` | 10 req/s | 20 | General API endpoints |
| `auth` | 5 req/min | 3 | Login/register/OTP (brute-force protection) |

### Endpoint Routing

| Path | Upstream | Rate Limit | Notes |
|------|----------|------------|-------|
| `/api/` | `api:8000` | 10r/s + 20 burst | Main API |
| `/api/v1/auth/` | `api:8000` | 5r/m + 3 burst | Stricter auth |
| `/ws/` | `api:8000` | None | WebSocket (long-lived) |
| `/health` | `api:8000` | None | Health check |

## Step 1: SSL Certificates

### Option A: Self-Signed (Development)

```bash
# Generate self-signed cert
mkdir -p rental-backend/docker/ssl

openssl req -x509 -nodes -days 365 \
  -newkey rsa:2048 \
  -keyout rental-backend/docker/ssl/key.pem \
  -out rental-backend/docker/ssl/cert.pem \
  -subj "/C=IN/ST=Karnataka/L=Bangalore/O=Reprico/CN=localhost"
```

### Option B: Let's Encrypt (Production)

```bash
# Install certbot
sudo apt install certbot

# Get certificate (stop nginx first)
sudo certbot certonly --standalone \
  -d yourdomain.com \
  -d api.yourdomain.com

# Certificates are at:
# /etc/letsencrypt/live/yourdomain.com/fullchain.pem
# /etc/letsencrypt/live/yourdomain.com/privkey.pem

# Copy to nginx ssl directory
cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem docker/ssl/cert.pem
cp /etc/letsencrypt/live/yourdomain.com/privkey.pem docker/ssl/key.pem
```

### Auto-Renewal (Let's Encrypt)

```bash
# Add to crontab
0 0 1 * * certbot renew --quiet && cp /etc/letsencrypt/live/yourdomain.com/*.pem /app/docker/ssl/
```

## Step 2: Configure Nginx

### Development Mode (No SSL)

For local development, use a simplified HTTP-only config:

```nginx
# docker/nginx.dev.conf
worker_processes auto;

events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=auth:10m rate=5r/m;

    # Upstream
    upstream api_servers {
        least_conn;
        server host.docker.internal:8000;
        keepalive 32;
    }

    # Gzip
    gzip on;
    gzip_types text/plain text/css application/json application/javascript;

    server {
        listen 80;
        server_name localhost;

        # API
        location /api/ {
            limit_req zone=api burst=20 nodelay;
            proxy_pass http://api_servers;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Auth (stricter)
        location /api/v1/auth/ {
            limit_req zone=auth burst=3 nodelay;
            proxy_pass http://api_servers;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        }

        # WebSocket
        location /ws/ {
            proxy_pass http://api_servers;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host $host;
            proxy_read_timeout 86400;
        }

        # Health
        location /health {
            proxy_pass http://api_servers;
            access_log off;
        }
    }
}
```

### Production Mode (With SSL)

The existing `docker/nginx.conf` handles SSL. Ensure:

1. SSL certs exist at `docker/ssl/cert.pem` and `docker/ssl/key.pem`
2. Update `server_name` from `_` to your domain
3. Uncomment/configure HSTS headers

## Step 3: Environment Variables

```bash
# No env vars needed for Nginx itself
# But ensure backend .env has:
ALLOWED_ORIGINS=["https://yourdomain.com","https://www.yourdomain.com"]
```

## Step 4: Running Nginx

### Via Docker Compose (Recommended)

```bash
cd rental-backend/docker
docker-compose up -d nginx

# Check status
docker-compose logs nginx
docker-compose ps
```

### Standalone (Without Docker)

```bash
# Install nginx
# macOS
brew install nginx

# Ubuntu/Debian
sudo apt install nginx

# Copy config
sudo cp docker/nginx.dev.conf /etc/nginx/nginx.conf

# Test config
sudo nginx -t

# Start
sudo nginx

# Reload after changes
sudo nginx -s reload
```

## Rate Limit Tuning

### Current vs Recommended

| Environment | API Rate | Auth Rate | Reason |
|-------------|----------|-----------|--------|
| Development | 100r/s | 10r/m | No limits needed |
| Staging | 10r/s | 5r/m | Moderate protection |
| Production | 10r/s | 5r/m | Brute-force protection |
| High Traffic | 50r/s | 10r/m | Scale up |

### Custom Rate Limits

```nginx
# Add new zone for webhooks
limit_req_zone $binary_remote_addr zone=webhooks:10m rate=20r/s;

# Add to webhook endpoint
location /api/v1/payments/webhook {
    limit_req zone=webhooks burst=50 nodelay;
    proxy_pass http://api_servers;
    # ...
}
```

### IP Whitelisting (Admin Endpoints)

```nginx
# Allow admin API only from office IP
location /api/v1/admin/ {
    allow 103.21.244.0/22;  # Your office IP range
    deny all;

    proxy_pass http://api_servers;
}
```

## WebSocket Configuration

The current config supports WebSocket with these timeouts:

```nginx
location /ws/ {
    proxy_connect_timeout 7d;   # Connection timeout
    proxy_send_timeout 7d;      # Send timeout
    proxy_read_timeout 7d;      # Read timeout (keeps connections alive)
}
```

### Connection Limits

```nginx
# Limit concurrent WebSocket connections per IP
limit_conn_zone $binary_remote_addr zone=ws:10m;

location /ws/ {
    limit_conn ws 10;  # Max 10 WS connections per IP
    # ...
}
```

## Security Headers Explained

| Header | Value | Purpose |
|--------|-------|---------|
| `X-Frame-Options` | `SAMEORIGIN` | Prevent clickjacking |
| `X-Content-Type-Options` | `nosniff` | Prevent MIME sniffing |
| `X-XSS-Protection` | `1; mode=block` | XSS filter |
| `Referrer-Policy` | `strict-origin-when-cross-origin` | Hide referrer |
| `Strict-Transport-Security` | `max-age=31536000` | Force HTTPS for 1 year |

## Monitoring

### Nginx Logs

```bash
# Access logs
docker-compose logs -f nginx

# Error logs
docker-compose exec nginx cat /var/log/nginx/error.log

# Real-time tail
docker-compose logs -f --tail=100 nginx
```

### Status Module (Optional)

```nginx
# Add to http block
server {
    location /nginx_status {
        stub_status on;
        allow 127.0.0.1;
        deny all;
    }
}
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| 502 Bad Gateway | Backend not running; check `docker-compose ps` |
| 504 Gateway Timeout | Increase `proxy_read_timeout` |
| WebSocket disconnects | Check `proxy_read_timeout 86400` (24h) |
| Rate limit too aggressive | Increase zone rate or burst |
| SSL error | Check cert files exist and are valid |
| CORS errors | Ensure `ALLOWED_ORIGINS` in backend matches |
| Nginx won't start | Run `nginx -t` to check config syntax |
