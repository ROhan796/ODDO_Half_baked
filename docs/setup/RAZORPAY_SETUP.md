# Razorpay Payment Integration Setup

## Overview

Reprico integrates **Razorpay** for payment processing:

- **Order Creation** → Create payment orders for invoices
- **Payment Verification** → HMAC SHA256 signature verification
- **Webhook Handling** → Async payment status updates
- **Refunds** → Process deposit refunds, cancellation refunds

## Current Status

| Component | Status |
|-----------|--------|
| `PaymentService` | Placeholder (dev mode) |
| Order creation | Mock implementation |
| Payment verification | Mock implementation |
| Webhook handler | Not implemented |
| Refund handler | Not implemented |

## Step 1: Create Razorpay Account

1. Go to [https://dashboard.razorpay.com](https://dashboard.razorpay.com)
2. Sign up and complete KYC (Indian business required)
3. Verify your email and phone

## Step 2: Get API Keys

### Test Mode (Development)

1. Razorpay Dashboard → **Settings** → **API Keys**
2. Click **"Generate Test Mode Key"**
3. You get:
   - `rzp_test_xxxxxxxxxxxxx` (Key ID)
   - `xxxxxxxxxxxxxxxxxxxxx` (Key Secret)

### Live Mode (Production)

1. Complete business verification
2. Generate live mode keys
3. Update webhook URL

## Step 3: Configure Environment Variables

```bash
# rental-backend/.env

# Razorpay API Keys
RAZORPAY_KEY_ID=rzp_test_xxxxxxxxxxxxx
RAZORPAY_KEY_SECRET=your_razorpay_key_secret

# Webhook Secret (for verifying webhook signatures)
RAZORPAY_WEBHOOK_SECRET=your_webhook_secret
```

## Step 4: Implement Payment Service

Replace the placeholder in `app/services/payment_service.py`:

```python
# app/services/payment_service.py
import razorpay
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from app.config import settings


class PaymentService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.client = razorpay.Client(
            auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
        )

    async def create_order(
        self, amount: Decimal, currency: str, receipt: str
    ) -> dict:
        """Create a Razorpay order."""
        order = self.client.order.create({
            "amount": int(amount * 100),  # Razorpay uses paise
            "currency": currency,
            "receipt": receipt,
            "payment_capture": 1,  # Auto-capture
        })
        return order

    async def verify_payment(
        self, order_id: str, payment_id: str, signature: str
    ) -> dict:
        """Verify payment signature using HMAC SHA256."""
        try:
            self.client.utility.verify_payment_signature({
                "razorpay_order_id": order_id,
                "razorpay_payment_id": payment_id,
                "razorpay_signature": signature,
            })
            return {"verified": True, "order_id": order_id, "payment_id": payment_id}
        except razorpay.errors.SignatureVerificationError:
            return {"verified": False, "error": "Invalid signature"}

    async def fetch_payment(self, payment_id: str) -> dict:
        """Fetch payment details."""
        return self.client.payment.fetch(payment_id)

    async def create_refund(
        self, payment_id: str, amount: Decimal, notes: dict = None
    ) -> dict:
        """Create a partial or full refund."""
        refund_data = {"amount": int(amount * 100)}
        if notes:
            refund_data["notes"] = notes
        return self.client.payment.refund(payment_id, refund_data)

    async def verify_webhook(self, payload: str, signature: str) -> bool:
        """Verify Razorpay webhook signature."""
        return self.client.utility.verify_webhook_signature(
            payload, signature, settings.RAZORPAY_WEBHOOK_SECRET
        )
```

## Step 5: Webhook Endpoint

Create webhook handler in `app/api/v1/payments.py`:

```python
# Webhook handler (add to router)
from fastapi import Request, HTTPException
from app.services.payment_service import PaymentService

@router.post("/webhook")
async def razorpay_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    payload = await request.body()
    signature = request.headers.get("X-Razorpay-Signature", "")

    service = PaymentService(db)
    is_valid = await service.verify_webhook(payload.decode(), signature)

    if not is_valid:
        raise HTTPException(status_code=400, detail="Invalid webhook signature")

    import json
    event = json.loads(payload)

    if event["event"] == "payment.captured":
        # Handle successful payment
        payment = event["payload"]["payment"]["entity"]
        await handle_payment_captured(db, payment)
    elif event["event"] == "payment.failed":
        # Handle failed payment
        payment = event["payload"]["payment"]["entity"]
        await handle_payment_failed(db, payment)
    elif event["event"] == "refund.created":
        # Handle refund
        refund = event["payload"]["refund"]["entity"]
        await handle_refund_created(db, refund)

    return {"status": "ok"}
```

## Step 6: Configure Webhook in Razorpay

1. Razorpay Dashboard → **Settings** → **Webhooks**
2. Click **"Add New Webhook"**
3. Configure:

| Setting | Value |
|---------|-------|
| **URL** | `https://your-domain.com/api/v1/payments/webhook` |
| **Secret** | Same as `RAZORPAY_WEBHOOK_SECRET` |
| **Active Events** | `payment.captured`, `payment.failed`, `refund.created` |

### Test Webhook Locally

Use ngrok to expose local server:

```bash
ngrok http 8000

# Use the ngrok URL as webhook URL temporarily
# https://xxxx.ngrok.io/api/v1/payments/webhook
```

## Step 7: Frontend Integration

### Razorpay Checkout

```tsx
// Frontend checkout component
const handlePayment = async (invoiceId: string) => {
  // 1. Create order via backend
  const { data } = await api.post('/invoices/payments', {
    invoice_id: invoiceId,
    method: 'razorpay',
  });

  // 2. Open Razorpay checkout
  const options = {
    key: process.env.NEXT_PUBLIC_RAZORPAY_KEY_ID,
    amount: data.amount * 100, // paise
    currency: 'INR',
    name: 'Reprico',
    order_id: data.order_id,
    handler: async (response: any) => {
      // 3. Verify payment on backend
      await api.post('/invoices/payments/verify', {
        razorpay_order_id: response.razorpay_order_id,
        razorpay_payment_id: response.razorpay_payment_id,
        razorpay_signature: response.razorpay_signature,
      });
    },
  };

  const rzp = new window.Razorpay(options);
  rzp.open();
};
```

### Add Razorpay Script

```tsx
// app/layout.tsx or _document.tsx
import Script from 'next/script';

<Script
  src="https://checkout.razorpay.com/v1/checkout.js"
  strategy="lazyOnload"
/>
```

## Payment Flow

```
Customer clicks "Pay"
    │
    ▼
Frontend calls POST /invoices/payments
    │
    ▼
Backend creates Razorpay order
    │
    ▼
Razorpay checkout opens (frontend)
    │
    ▼
Customer completes payment
    │
    ▼
Razorpay sends webhook → POST /payments/webhook
    │
    ▼
Backend verifies signature, updates invoice status
    │
    ▼
WebSocket notification to customer portal
```

## Test Cards

| Card Number | Expiry | CVV | Result |
|-------------|--------|-----|--------|
| 4111 1111 1111 1111 | Any future | Any | Success |
| 4000 0000 0000 0002 | Any future | Any | Failure |
| 4000 0027 6000 3184 | Any future | Any | 3D Secure |

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Key ID invalid" | Check `RAZORPAY_KEY_ID` starts with `rzp_test_` or `rzp_live_` |
| Webhook not receiving | Verify URL, check ngrok is running |
| Signature mismatch | Ensure `RAZORPAY_WEBHOOK_SECRET` matches dashboard |
| Payment not captured | Check `payment_capture: 1` in order creation |
| Refund fails | Ensure payment was captured first |
