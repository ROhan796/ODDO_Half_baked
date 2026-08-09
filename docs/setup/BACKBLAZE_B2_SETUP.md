# Backblaze B2 File Storage Setup (Free 10GB)

## Why Backblaze B2

| Feature | Backblaze B2 | Cloudflare R2 | AWS S3 |
|---------|-------------|---------------|--------|
| **Free storage** | 10GB permanent | 10GB | 5GB (12mo) |
| **Free egress** | 1GB/day | Unlimited | Paid |
| **Credit card** | **Not required** | Required | Required |
| **S3-compatible** | Yes | Yes | Native |
| **Durability** | 99.999999999% | 99.999999999% | 99.999999999% |
| **API requests** | Free | Free | Paid |

## Architecture

```
┌─────────────────────────────────────────────────┐
│            BACKBLAZE B2 BUCKET                  │
│            rental-files                          │
│                                                  │
│  ┌──────────────────────────────────────────┐    │
│  │           FOLDER STRUCTURE               │    │
│  │                                          │    │
│  │  kyc/          → KYC documents           │    │
│  │  products/     → Product images           │    │
│  │  invoices/     → Generated PDFs           │    │
│  │  inspections/  → Inspection photos        │    │
│  │  profiles/     → Profile pictures         │    │
│  │  temp/         → Temporary uploads        │    │
│  └──────────────────────────────────────────┘    │
│                                                  │
│  Public URL: https://f004.backblazeb2.com/file/  │
│  S3 Endpoint: https://s3.us-west-004.backblazeb2 │
└─────────────────────────────────────────────────┘
```

## Step 1: Create Account

1. Go to [https://www.backblaze.com/sign-up/b2](https://www.backblaze.com/sign-up/b2)
2. Sign up with email
3. **No credit card required**
4. Verify email

## Step 2: Create Bucket

1. Backblaze Dashboard → **B2 Cloud Storage** → **Buckets**
2. Click **"Create a Bucket"**

| Setting | Value |
|---------|-------|
| **Bucket Name** | `rental-files` |
| **Files in Bucket** | Public (or Private + CDN) |
| **Default Encryption** | Enabled |
| **Object Lock** | Disable (unless needed) |

### Bucket Visibility

- **Public**: Files accessible via URL directly (good for product images)
- **Private**: Files only accessible via pre-signed URLs (good for KYC docs)

**Recommended:** Create two buckets:
- `rental-files-public` (Public) - product images, profile photos
- `rental-files-private` (Private) - KYC docs, invoices, sensitive data

## Step 3: Generate Application Key

1. Backblaze Dashboard → **B2 Cloud Storage** → **Application Keys**
2. Click **"Add a New Application Key"**

| Setting | Value |
|---------|-------|
| **Name** | `reprico-backend` |
| **Bucket** | `rental-files` (or specific bucket) |
| **Type of Access** | Read and Write |
| **File name prefix** | (leave blank for full access) |

3. Click **"Create New Key"**
4. **Copy immediately** - you won't see the key again:
   - **Key ID**: `004xxxxx` (this is your `STORAGE_ACCESS_KEY_ID`)
   - **Application Key**: `K004xxxxx` (this is your `STORAGE_SECRET_ACCESS_KEY`)

## Step 4: Get Endpoint URL

Backblaze B2 uses S3-compatible endpoints by region:

| Region | Endpoint |
|--------|----------|
| **US West** | `https://s3.us-west-004.backblazeb2.com` |
| US East | `https://s3.us-east-005.backblazeb2.com` |
| EU Central | `https://s3.eu-central-005.backblazeb2.com` |

Check your bucket's region in the Buckets page.

## Step 5: Get Public URL

If your bucket is public:

```
https://f004.backblazeb2.com/file/{bucket-name}/{file-key}
```

Example: `https://f004.backblazeb2.com/file/rental-files/products/abc123.jpg`

If using a custom domain or CDN, use that URL instead.

## Step 6: Configure Environment Variables

```bash
# rental-backend/.env

STORAGE_ACCOUNT_ID=
STORAGE_ACCESS_KEY_ID=004xxxxx
STORAGE_SECRET_ACCESS_KEY=K004xxxxx
STORAGE_BUCKET_NAME=rental-files
STORAGE_PUBLIC_URL=https://f004.backblazeb2.com/file/rental-files
STORAGE_ENDPOINT_URL=https://s3.us-west-004.backblazeb2.com
```

## Step 7: CORS Configuration

If uploading from browser, set CORS on the bucket:

1. Backblaze Dashboard → **Buckets** → Your bucket → **CORS Rules**
2. Add rule:

```json
[
  {
    "cors_rule_name": "allow-uploads",
    "allowed_origins": ["http://localhost:3000", "https://yourdomain.com"],
    "allowed_headers": ["*"],
    "allowed_operations": ["b2_download_file_by_name", "b2_upload_file"],
    "max_age_seconds": 3600
  }
]
```

## Step 8: Code (No Changes Needed)

The existing `app/utils/r2.py` works with Backblaze B2 out of the box because it uses boto3 (S3-compatible):

```python
# This code works with Backblaze B2, Cloudflare R2, or AWS S3
# Just update the .env values

self._s3_client = boto3.client(
    "s3",
    endpoint_url=settings.STORAGE_ENDPOINT_URL,  # Backblaze endpoint
    aws_access_key_id=settings.STORAGE_ACCESS_KEY_ID,      # B2 Key ID
    aws_secret_access_key=settings.STORAGE_SECRET_ACCESS_KEY,  # B2 App Key
)
```

## File Size Limits

| Folder | Max Size | Notes |
|--------|----------|-------|
| `kyc/` | 10 MB | Encrypted at rest |
| `products/` | 5 MB | Compress if larger |
| `invoices/` | 2 MB | PDFs only |
| `inspections/` | 10 MB | Photos |
| `profiles/` | 2 MB | Avatar-sized |

## Free Tier Limits

| Resource | Free Allowance |
|----------|----------------|
| Storage | 10 GB |
| Egress | 1 GB/day (~30 GB/month) |
| Class B (downloads) | 2,500/day |
| Class A (uploads) | 2,500/day |

**For a rental platform:** 10GB storage handles ~5,000 product images + ~2,000 KYC documents. The 1GB/day egress is sufficient for moderate traffic.

## Cost After Free Tier

| Resource | Price |
|----------|-------|
| Storage | $6/TB/month |
| Egress | $0.01/GB |
| API calls | Free |

## Troubleshooting

| Issue | Solution |
|-------|----------|
| 403 Forbidden | Check Application Key permissions, bucket name |
| CORS error | Add CORS rule in bucket settings |
| Presigned URL expired | Default 1 hour; regenerate |
| File not accessible publicly | Set bucket to Public or use pre-signed URLs |
| Connection timeout | Check endpoint URL matches bucket region |
| "No such bucket" | Verify bucket name and region |
