# app/middleware/compression.py
import gzip
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, StreamingResponse


class CompressionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        response: Response = await call_next(request)

        accept_encoding = request.headers.get("accept-encoding", "")
        if "gzip" not in accept_encoding:
            return response

        content_encoding = response.headers.get("content-type", "")
        if "text/" in content_encoding or "json" in content_encoding or "javascript" in content_encoding or "xml" in content_encoding:
            pass
        else:
            return response

        body_parts: list[bytes] = []
        async for chunk in response.body_iterator:
            if isinstance(chunk, str):
                body_parts.append(chunk.encode("utf-8"))
            else:
                body_parts.append(chunk)

        body = b"".join(body_parts)

        if len(body) <= 1024:
            return Response(
                content=body,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.media_type,
            )

        compressed = gzip.compress(body, compresslevel=6)

        headers = dict(response.headers)
        headers["content-encoding"] = "gzip"
        headers["content-length"] = str(len(compressed))
        headers.pop("content-length", None)
        headers["content-length"] = str(len(compressed))

        return Response(
            content=compressed,
            status_code=response.status_code,
            headers=headers,
            media_type=response.media_type,
        )
