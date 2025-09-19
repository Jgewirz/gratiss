"""
Request logging middleware with correlation ID
"""
import time
import json
import uuid
from fastapi import Request, Response, FastAPI
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Generate or extract request ID
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))

        # Store in request state for downstream use
        request.state.request_id = request_id

        # Start timer
        start_time = time.time()

        # Process request
        response = await call_next(request)

        # Calculate duration
        duration_ms = (time.time() - start_time) * 1000

        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id

        # Log request (JSON format for structured logging)
        log_data = {
            "method": request.method,
            "path": request.url.path,
            "status": response.status_code,
            "dur_ms": round(duration_ms, 2),
            "request_id": request_id
        }

        # Print as JSON line (can be picked up by log aggregators)
        print(json.dumps(log_data))

        return response


def install_logging(app: FastAPI):
    """Install the request logging middleware on the app"""
    app.add_middleware(RequestLoggingMiddleware)