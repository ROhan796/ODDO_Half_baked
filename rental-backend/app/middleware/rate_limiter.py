# app/middleware/rate_limiter.py
import time
import json
from collections import defaultdict
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse


class _TokenBucket:
    __slots__ = ("capacity", "tokens", "refill_rate", "last_refill")

    def __init__(self, capacity: int, refill_rate: float):
        self.capacity = capacity
        self.tokens = capacity
        self.refill_rate = refill_rate  # tokens per second
        self.last_refill = time.monotonic()

    def consume(self) -> bool:
        now = time.monotonic()
        elapsed = now - self.last_refill
        self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_rate)
        self.last_refill = now

        if self.tokens >= 1:
            self.tokens -= 1
            return True
        return False


GENERAL_LIMIT = 200  # per minute
AUTH_LIMIT = 5  # per minute


class RateLimiterMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self._buckets: dict[str, _TokenBucket] = defaultdict(
            lambda: _TokenBucket(GENERAL_LIMIT, GENERAL_LIMIT / 60)
        )
        self._auth_buckets: dict[str, _TokenBucket] = defaultdict(
            lambda: _TokenBucket(AUTH_LIMIT, AUTH_LIMIT / 60)
        )

    def _get_client_ip(self, request: Request) -> str:
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        if request.client:
            return request.client.host
        return "unknown"

    async def dispatch(self, request: Request, call_next) -> JSONResponse:
        client_ip = self._get_client_ip(request)
        path = request.url.path

        if path.startswith("/api/v1/auth"):
            bucket = self._auth_buckets[client_ip]
            limit = AUTH_LIMIT
        else:
            bucket = self._buckets[client_ip]
            limit = GENERAL_LIMIT

        if not bucket.consume():
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Rate limit exceeded",
                    "error": "too_many_requests",
                    "retry_after": 60,
                    "limit": limit,
                },
                headers={"Retry-After": "60"},
            )

        return await call_next(request)
