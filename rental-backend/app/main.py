# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

from app.config import settings
from app.api.v1.router import api_router
from app.websockets.handlers import ws_router
from app.webhooks.clerk import router as clerk_webhook_router
from app.middleware.request_id import RequestIDMiddleware
from app.middleware.rate_limiter import RateLimiterMiddleware
from app.middleware.audit import AuditMiddleware
from app.middleware.compression import CompressionMiddleware
from app.utils.database import primary_engine
from app.core.cache import cache


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await cache.connect()
    yield
    # Shutdown
    await cache.disconnect()
    await primary_engine.dispose()


# Sentry (if configured)
if settings.SENTRY_DSN:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        integrations=[FastApiIntegration()],
        traces_sample_rate=0.1,
        send_default_pii=True,
    )

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan,
)

# Middleware stack (order matters - last added = first executed)
app.add_middleware(CompressionMiddleware)
app.add_middleware(AuditMiddleware)
app.add_middleware(RateLimiterMiddleware)
app.add_middleware(RequestIDMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(api_router, prefix="/api/v1")
app.include_router(ws_router, prefix="/ws")
app.include_router(clerk_webhook_router, prefix="/api/v1/webhooks")


# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": settings.APP_VERSION}
