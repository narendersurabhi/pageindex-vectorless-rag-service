from __future__ import annotations

import time
import uuid

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from structlog.contextvars import bind_contextvars, clear_contextvars

from vectorless_rag_service.observability.metrics import REQUEST_COUNT, REQUEST_LATENCY


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-Id") or str(uuid.uuid4())
        bind_contextvars(request_id=request_id)
        start = time.time()
        response: Response = await call_next(request)
        duration = time.time() - start
        REQUEST_LATENCY.labels(request.method, request.url.path).observe(duration)
        REQUEST_COUNT.labels(request.method, request.url.path, response.status_code).inc()
        response.headers["X-Request-Id"] = request_id
        clear_contextvars()
        return response
