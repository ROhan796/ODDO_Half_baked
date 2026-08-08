# app/middleware/audit.py
import time
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

try:
    import structlog
    _structlog_available = True
except ImportError:
    _structlog_available = False

try:
    from app.middleware.request_id import request_id_var
except ImportError:
    request_id_var = None

logger = logging.getLogger("audit")


class AuditMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        start = time.monotonic()
        method = request.method
        path = request.url.path
        client_ip = "unknown"
        if request.client:
            client_ip = request.client.host

        response: Response = await call_next(request)

        duration_ms = round((time.monotonic() - start) * 1000, 2)
        status_code = response.status_code
        request_id = request_id_var.get() if request_id_var else ""

        log_data = {
            "method": method,
            "path": path,
            "status": status_code,
            "duration_ms": duration_ms,
            "client_ip": client_ip,
            "request_id": request_id,
        }

        if _structlog_available:
            structlog.get_logger("audit").info("request", **log_data)
        else:
            if status_code >= 500:
                logger.error("%s %s %s %sms", method, path, status_code, duration_ms)
            elif status_code >= 400:
                logger.warning("%s %s %s %sms", method, path, status_code, duration_ms)
            else:
                logger.info("%s %s %s %sms", method, path, status_code, duration_ms)

        return response
