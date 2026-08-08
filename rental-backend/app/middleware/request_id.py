# app/middleware/request_id.py
import uuid
from contextvars import ContextVar
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

request_id_var: ContextVar[str] = ContextVar("request_id", default="")

GENERATED_REQUEST_ID_HEADER = "X-Request-ID"


class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = request.headers.get(GENERATED_REQUEST_ID_HEADER) or str(uuid.uuid4())
        request_id_var.set(request_id)

        response: Response = await call_next(request)
        response.headers[GENERATED_REQUEST_ID_HEADER] = request_id
        return response
