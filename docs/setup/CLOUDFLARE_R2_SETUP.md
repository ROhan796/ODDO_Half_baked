# Cloudflare R2 File Storage Setup

## Overview

Reprico uses **Cloudflare R2** (S3-compatible object storage) for:
- KYC document storage (Aadhaar, PAN, selfie photos)
- Product images
- Invoice PDFs
- Inspection photos
- User profile pictures

R2 is chosen over S3 for: **zero egress fees**, global CDN integration, lower storage costs.

## Architecture

```
┌─────────────────────────────────────────────────┐
│                  CLOUDFLARE R2                   │
│                                                  │
│  Bucket: rental-files                            │
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
│  Public URL: https://pub-xxx.r2.dev              │
│  API Endpoint: https://xxx.r2.cloudflarestorage  │
└─────────────────────────────────────────────────┘
         ▲                    ▲
         │                    │
    Pre-signed URLs      Direct Access
    (uploads/downloads)  (via public URL)
```

## Step 1: Create Cloudflare Account

1. Go to [https://dash.cloudflare.com](https://dash.cloudflare.com)
2. Sign up or log in
3. Note your **Account ID** (visible in URL or dashboard)

## Step 2: Create R2 Bucket

1. Cloudflare Dashboard → **R2** → **Overview**
2. Click **"Create Bucket"**

| Setting | Value |
|---------|-------|
| **Bucket name** | `rental-files` |
| **Location** | Auto (or choose closest region) |
| **Storage class** | Standard |

## Step 3: Configure Public Access

1. R2 → Your bucket → **Settings**
2. Enable **"Public Access"**
3. Note the public URL: `https://pub-xxx.r2.dev`

### Custom Domain (Optional)

1. R2 → **Settings** → **Custom Domains**
2. Add: `files.yourdomain.com`
3. Update `R2_PUBLIC_URL` accordingly

## Step 4: Generate API Tokens

1. R2 → **Manage R2 API Tokens**
2. Click **"Create API Token"**

| Setting | Value |
|---------|-------|
| **Token name** | `reprico-backend` |
| **Permission** | Object Read & Write |
| **Specify bucket** | `rental-files` |
| **TTL** | No expiry (or set for security) |

After creation, note:
- **Access Key ID**
- **Secret Access Key**

## Step 5: Configure Environment Variables

```bash
# rental-backend/.env

# Cloudflare R2
R2_ACCOUNT_ID=your_cloudflare_account_id
R2_ACCESS_KEY_ID=your_r2_access_key
R2_SECRET_ACCESS_KEY=your_r2_secret_key
R2_BUCKET_NAME=rental-files
R2_PUBLIC_URL=https://pub-xxx.r2.dev
R2_ENDPOINT_URL=https://xxx.r2.cloudflarestorage.com
```

**Endpoint URL format:** `https://{account_id}.r2.cloudflarestorage.com`

## Step 6: CORS Configuration

Set CORS policy in R2 bucket settings:

```json
[
  {
    "AllowedOrigins": [
      "http://localhost:3000",
      "https://yourdomain.com"
    ],
    "AllowedMethods": ["GET", "PUT", "POST", "DELETE"],
    "AllowedHeaders": ["*"],
    "MaxAgeSeconds": 3600
  }
]
```

## Step 7: Current Implementation

### R2 Client (`app/utils/r2.py`)

```python
import boto3
from botocore.config import Config
import uuid
from datetime import datetime, timedelta
from app.config import settings


class R2Storage:
    def __init__(self):
        self._s3_client = None
        self.bucket_name = settings.R2_BUCKET_NAME

    @property
    def s3_client(self):
        if self._s3_client is None:
            self._s3_client = boto3.client(
                "s3",
                endpoint_url=settings.R2_ENDPOINT_URL,
                aws_access_key_id=settings.R2_ACCESS_KEY_ID,
                aws_secret_access_key=settings.R2_SECRET_ACCESS_KEY,
                config=Config(
                    signature_version="s3v4",
                    s3={"addressing_style": "path"},
                ),
            )
        return self._s3_client

    async def generate_presigned_upload_url(
        self, folder: str, filename: str, content_type: str, expires_in: int = 3600
    ) -> dict:
        ext = filename.rsplit(".", 1)[1] if "." in filename else ""
        key = f"{folder}/{uuid.uuid4().hex}.{ext}"

        presigned_url = self.s3_client.generate_presigned_url(
            "put_object",
            Params={
                "Bucket": self.bucket_name,
                "Key": key,
                "ContentType": content_type,
            },
            ExpiresIn=expires_in,
        )

        return {
            "upload_url": presigned_url,
            "file_key": key,
            "expires_at": (datetime.utcnow() + timedelta(seconds=expires_in)).isoformat(),
        }

    async def generate_presigned_download_url(
        self, file_key: str, expires_in: int = 3600
    ) -> str:
        return self.s3_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": self.bucket_name, "Key": file_key},
            ExpiresIn=expires_in,
        )

    async def delete_file(self, file_key: str) -> bool:
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name, Key=file_key
            )
            return True
        except Exception:
            return False


storage = R2Storage()
```

## Step 8: Usage in API Endpoints

### Upload Flow

```python
# app/api/v1/files.py
from fastapi import APIRouter, Depends
from app.utils.r2 import storage

router = APIRouter()

@router.post("/presigned-url")
async def get_upload_url(
    folder: str,
    filename: str,
    content_type: str,
    current_user = Depends(get_current_user),
):
    """Get pre-signed URL for client-side upload."""
    result = await storage.generate_presigned_upload_url(
        folder=folder,
        filename=filename,
        content_type=content_type,
    )
    return result

# Frontend uses the presigned URL to upload directly:
# PUT {upload_url} with file body
```

### Download Flow

```python
@router.get("/download/{file_key:path}")
async def get_download_url(
    file_key: str,
    current_user = Depends(get_current_user),
):
    """Get pre-signed download URL."""
    url = await storage.generate_presigned_download_url(file_key)
    return {"download_url": url}
```

## File Size Limits

| Folder | Max Size | Retention |
|--------|----------|-----------|
| `kyc/` | 10 MB | 5 years |
| `products/` | 5 MB | Indefinite |
| `invoices/` | 2 MB | 7 years |
| `inspections/` | 10 MB | 2 years |
| `profiles/` | 2 MB | Until replaced |
| `temp/` | 10 MB | 24 hours (auto-delete) |

## Storage Cost Estimate

| Volume | Monthly Cost |
|--------|-------------|
| 1 GB stored | ~$0.015 |
| 10 GB stored | ~$0.15 |
| 100 GB stored | ~$1.50 |
| 1M Class A ops | ~$4.50 |
| 1M Class B ops | ~$0.36 |

**No egress fees** (major advantage over AWS S3).

## Troubleshooting

| Issue | Solution |
|-------|----------|
| 403 Forbidden | Check R2 access keys and bucket permissions |
| CORS error | Update CORS policy in bucket settings |
| Presigned URL expired | Default 1 hour; regenerate |
| File not accessible | Check if public access is enabled |
| Large file upload fails | Check pre-signed URL TTL; use multipart for >5GB |
