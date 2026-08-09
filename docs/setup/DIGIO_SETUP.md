# Digio E-KYC Setup Guide

## Overview

Reprico uses **Digio** as the primary e-KYC provider for:
- **Aadhaar Verification** (VID-based e-KYC)
- **PAN Verification** (name, DOB, photo match)
- **E-Sign** (Aadhaar-based document signing)

Additional providers for specific use cases:
- **Surepass** → PAN/GST verification
- **FaceIO** → Biometric face matching + liveness detection

## KYC Flow

```
User uploads document
    │
    ▼
┌─────────────────────┐
│  Step 1: PAN Check   │ ← Surepass API
│  Verify name, DOB    │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Step 2: Aadhaar KYC │ ← Digio API
│  OTP → e-KYC data    │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Step 3: Face Match  │ ← FaceIO
│  Selfie vs Aadhaar   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Step 4: E-Sign      │ ← Digio API
│  Aadhaar OTP sign    │
└──────────┬──────────┘
           │
           ▼
    KYC Verified ✅
```

## Step 1: Create Digio Account

1. Go to [https://app.digio.in](https://app.digio.in)
2. Sign up and complete business verification
3. Choose plan based on volume

### Get API Credentials

1. Digio Dashboard → **Settings** → **API Keys**
2. Note down:
   - **Client ID** (API Key)
   - **Client Secret** (API Secret)
   - **Environment** (sandbox / production)

## Step 2: Configure Environment Variables

```bash
# rental-backend/.env

# Digio (Primary KYC + E-Sign)
DIGIO_API_KEY=your_client_id
DIGIO_API_SECRET=your_client_secret

# Surepass (PAN/GST Verification)
SUREPASS_API_KEY=your_surepass_api_key

# FaceIO (Biometric)
FACEIO_APP_ID=your_faceio_app_id
FACEIO_SECRET=your_faceio_secret
```

## Step 3: Digio API Integration

### Aadhaar e-KYC Flow

```python
# app/services/kyc_service.py
import httpx
from app.config import settings


class DigioKYCService:
    BASE_URL = "https://ext.digio.in/v2"  # Production
    # BASE_URL = "https://extapi.digio.in/v2/client"  # Sandbox

    def __init__(self):
        self.client_id = settings.DIGIO_API_KEY
        self.client_secret = settings.DIGIO_API_SECRET

    async def request_aadhaar_otp(self, aadhaar_number: str) -> dict:
        """Request OTP for Aadhaar e-KYC."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.BASE_URL}/client/kyc/aadhaar/otp/request",
                auth=(self.client_id, self.client_secret),
                json={"aadhaar_number": aadhaar_number},
            )
            return response.json()

    async def verify_aadhaar_otp(self, request_id: str, otp: str) -> dict:
        """Verify OTP and get e-KYC data."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.BASE_URL}/client/kyc/aadhaar/otp/verify",
                auth=(self.client_id, self.client_secret),
                json={
                    "request_id": request_id,
                    "otp": otp,
                },
            )
            return response.json()

    async def verify_pan(self, pan_number: str, name: str = None, dob: str = None) -> dict:
        """Verify PAN card details."""
        async with httpx.AsyncClient() as client:
            payload = {"id_number": pan_number}
            if name:
                payload["name"] = name
            if dob:
                payload["date_of_birth"] = dob

            response = await client.post(
                f"{self.BASE_URL}/client/kyc/pan/verify",
                auth=(self.client_id, self.client_secret),
                json=payload,
            )
            return response.json()

    async def create_e_sign_request(
        self, document_url: str, signer_email: str, signer_name: str
    ) -> dict:
        """Create Aadhaar e-sign request."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.BASE_URL}/client/esign/request",
                auth=(self.client_id, self.client_secret),
                json={
                    "document_url": document_url,
                    "signers": [{
                        "identifier": signer_email,
                        "identifier_type": "email",
                        "name": signer_name,
                        "reason": "Rental Agreement",
                    }],
                },
            )
            return response.json()
```

## Step 4: Surepass Integration (PAN/GST)

```python
# app/services/surepass_service.py
import httpx
from app.config import settings


class SurepassService:
    BASE_URL = "https://api.surepass.io/api/v1"

    def __init__(self):
        self.api_key = settings.SUREPASS_API_KEY

    async def verify_pan(self, pan_number: str) -> dict:
        """Verify PAN card."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/pan/extended",
                headers={"Authorization": f"Bearer {self.api_key}"},
                params={"id_number": pan_number},
            )
            return response.json()

    async def verify_gst(self, gstin: str) -> dict:
        """Verify GST number."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/gst",
                headers={"Authorization": f"Bearer {self.api_key}"},
                params={"gstin": gstin},
            )
            return response.json()
```

## Step 5: FaceIO Integration

```html
<!-- Frontend: FaceIO SDK -->
<script src="https://cdn.faceio.net/fio.js"></script>

<script>
const faceio = new FaceIO("your_faceio_app_id");

async function startFaceAuth() {
  try {
    const response = await faceio.enroll({
      locale: "en-US",
      payload: {
        userId: "user_uuid_here",
        email: "user@example.com",
      },
    });

    // Send faceId to backend for verification
    await api.post("/auth/kyc/face-verify", {
      face_id: response.faceId,
      facial_encryption: response.facialEncryption,
    });
  } catch (error) {
    console.error("Face auth failed:", error);
  }
}
</script>
```

## Step 6: Update KYC Status in Database

```python
# After successful verification, update user KYC
from app.models.user import User, KYCStatus

async def update_kyc_status(db, user_id: str, provider: str, data: dict):
    user = await db.get(User, user_id)
    user.kyc_status = KYCStatus.VERIFIED.value
    user.kyc_verified_at = datetime.utcnow()
    user.kyc_provider = provider
    user.kyc_data = data  # Store encrypted
    await db.commit()
```

## Sandbox vs Production

| Feature | Sandbox | Production |
|---------|---------|------------|
| Aadhaar OTP | Mock OTP (123456) | Real OTP via UIDAI |
| PAN Verification | Mock responses | Real NSDL/UTIITSL |
| E-Sign | Test signing | Legal e-sign |
| URL | `extapi.digio.in` | `ext.digio.in` |

### Test in Sandbox

```python
# Use sandbox URL for testing
DIGIO_SANDBOX_URL = "https://extapi.digio.in/v2/client"
# Set Aadhaar number to any 12-digit for sandbox
```

## Compliance Notes

- **Aadhaar data** must be encrypted at rest (AES-256)
- **KYC data** retention: 5 years after last transaction (RBI mandate)
- **Consent** must be obtained before Aadhaar OTP is sent
- **Data localization:** Store Aadhaar data only in India

## Troubleshooting

| Issue | Solution |
|-------|----------|
| OTP not received | Check Aadhaar number, UIDAI may be down |
| PAN mismatch | Name/DOB must match exactly |
| FaceIO not loading | Check browser compatibility, HTTPS required |
| E-sign fails | Document must be PDF, max 5MB |
| Sandbox working, prod failing | Check API keys, environment URLs |
