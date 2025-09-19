"""Rate limiting middleware for API protection"""
from fastapi import HTTPException, Request, Response
from fastapi.responses import JSONResponse
from typing import Dict, Tuple
import time
import asyncio
from collections import defaultdict
from datetime import datetime, timedelta


class RateLimiter:
    """
    Token bucket rate limiter with sliding window.
    Prevents API abuse and ensures fair usage.
    """

    def __init__(
        self,
        requests_per_minute: int = 60,
        requests_per_hour: int = 1000,
        burst_size: int = 10
    ):
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        self.burst_size = burst_size

        # Storage for rate limit data
        self.minute_buckets: Dict[str, list] = defaultdict(list)
        self.hour_buckets: Dict[str, list] = defaultdict(list)

        # Cleanup task
        self.cleanup_task = None

    async def start_cleanup(self):
        """Start background cleanup task"""
        if not self.cleanup_task:
            self.cleanup_task = asyncio.create_task(self._cleanup_old_entries())

    async def _cleanup_old_entries(self):
        """Remove old entries from buckets periodically"""
        while True:
            await asyncio.sleep(60)  # Run every minute

            current_time = time.time()
            minute_ago = current_time - 60
            hour_ago = current_time - 3600

            # Clean minute buckets
            for key in list(self.minute_buckets.keys()):
                self.minute_buckets[key] = [
                    t for t in self.minute_buckets[key] if t > minute_ago
                ]
                if not self.minute_buckets[key]:
                    del self.minute_buckets[key]

            # Clean hour buckets
            for key in list(self.hour_buckets.keys()):
                self.hour_buckets[key] = [
                    t for t in self.hour_buckets[key] if t > hour_ago
                ]
                if not self.hour_buckets[key]:
                    del self.hour_buckets[key]

    def _get_client_id(self, request: Request) -> str:
        """Get unique client identifier from request"""
        # Use IP address as primary identifier
        client_ip = request.client.host

        # Add API key if present (for authenticated requests)
        api_key = request.headers.get("X-API-Key", "")

        return f"{client_ip}:{api_key}" if api_key else client_ip

    def _check_rate_limit(
        self,
        client_id: str,
        current_time: float
    ) -> Tuple[bool, Dict]:
        """
        Check if request is within rate limits.
        Returns (allowed, headers_dict)
        """
        # Check minute limit
        minute_ago = current_time - 60
        self.minute_buckets[client_id] = [
            t for t in self.minute_buckets[client_id] if t > minute_ago
        ]

        minute_requests = len(self.minute_buckets[client_id])

        if minute_requests >= self.requests_per_minute:
            # Calculate retry after
            oldest_request = min(self.minute_buckets[client_id])
            retry_after = int(60 - (current_time - oldest_request))

            return False, {
                "X-RateLimit-Limit": str(self.requests_per_minute),
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": str(int(oldest_request + 60)),
                "Retry-After": str(retry_after)
            }

        # Check hour limit
        hour_ago = current_time - 3600
        self.hour_buckets[client_id] = [
            t for t in self.hour_buckets[client_id] if t > hour_ago
        ]

        hour_requests = len(self.hour_buckets[client_id])

        if hour_requests >= self.requests_per_hour:
            # Calculate retry after
            oldest_request = min(self.hour_buckets[client_id])
            retry_after = int(3600 - (current_time - oldest_request))

            return False, {
                "X-RateLimit-Limit-Hour": str(self.requests_per_hour),
                "X-RateLimit-Remaining-Hour": "0",
                "X-RateLimit-Reset-Hour": str(int(oldest_request + 3600)),
                "Retry-After": str(retry_after)
            }

        # Request allowed - add to buckets
        self.minute_buckets[client_id].append(current_time)
        self.hour_buckets[client_id].append(current_time)

        # Calculate remaining
        minute_remaining = self.requests_per_minute - minute_requests - 1
        hour_remaining = self.requests_per_hour - hour_requests - 1

        return True, {
            "X-RateLimit-Limit": str(self.requests_per_minute),
            "X-RateLimit-Remaining": str(minute_remaining),
            "X-RateLimit-Limit-Hour": str(self.requests_per_hour),
            "X-RateLimit-Remaining-Hour": str(hour_remaining)
        }

    async def __call__(self, request: Request, call_next):
        """Middleware to check rate limits"""

        # Skip rate limiting for health checks and WebSocket
        if request.url.path in ["/health", "/ws", "/ws/admin"]:
            return await call_next(request)

        # Get client identifier
        client_id = self._get_client_id(request)
        current_time = time.time()

        # Check rate limit
        allowed, headers = self._check_rate_limit(client_id, current_time)

        if not allowed:
            # Rate limit exceeded
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Rate limit exceeded",
                    "message": "Too many requests. Please slow down.",
                    "retry_after": headers.get("Retry-After", "60")
                },
                headers=headers
            )

        # Process request
        response = await call_next(request)

        # Add rate limit headers to response
        for key, value in headers.items():
            response.headers[key] = value

        return response


class EndpointRateLimiter:
    """
    Specific rate limits for individual endpoints.
    More restrictive limits for sensitive operations.
    """

    def __init__(self):
        self.endpoint_limits = {
            # Webhook endpoints - prevent spam
            "/webhooks/": {"per_minute": 10, "per_hour": 100},

            # Link generation - reasonable usage
            "/links/generate": {"per_minute": 20, "per_hour": 200},

            # Stats - expensive queries
            "/api/dashboard/": {"per_minute": 30, "per_hour": 500},
            "/stats/": {"per_minute": 30, "per_hour": 500},

            # Redirects - high volume allowed
            "/l/": {"per_minute": 1000, "per_hour": 50000},
        }

        self.buckets: Dict[str, Dict[str, list]] = defaultdict(
            lambda: defaultdict(list)
        )

    def get_endpoint_key(self, path: str) -> str:
        """Match path to endpoint pattern"""
        for pattern in self.endpoint_limits.keys():
            if path.startswith(pattern):
                return pattern
        return None

    def check_endpoint_limit(
        self,
        client_id: str,
        path: str,
        current_time: float
    ) -> Tuple[bool, Dict]:
        """Check endpoint-specific rate limits"""

        endpoint_key = self.get_endpoint_key(path)
        if not endpoint_key:
            # No specific limit for this endpoint
            return True, {}

        limits = self.endpoint_limits[endpoint_key]
        bucket_key = f"{client_id}:{endpoint_key}"

        # Check minute limit
        if "per_minute" in limits:
            minute_ago = current_time - 60
            minute_requests = [
                t for t in self.buckets[bucket_key]["minute"]
                if t > minute_ago
            ]
            self.buckets[bucket_key]["minute"] = minute_requests

            if len(minute_requests) >= limits["per_minute"]:
                retry_after = int(60 - (current_time - min(minute_requests)))
                return False, {
                    "X-RateLimit-Endpoint": endpoint_key,
                    "X-RateLimit-Endpoint-Limit": str(limits["per_minute"]),
                    "Retry-After": str(retry_after)
                }

        # Check hour limit
        if "per_hour" in limits:
            hour_ago = current_time - 3600
            hour_requests = [
                t for t in self.buckets[bucket_key]["hour"]
                if t > hour_ago
            ]
            self.buckets[bucket_key]["hour"] = hour_requests

            if len(hour_requests) >= limits["per_hour"]:
                retry_after = int(3600 - (current_time - min(hour_requests)))
                return False, {
                    "X-RateLimit-Endpoint": endpoint_key,
                    "X-RateLimit-Endpoint-Limit-Hour": str(limits["per_hour"]),
                    "Retry-After": str(retry_after)
                }

        # Add request to buckets
        self.buckets[bucket_key]["minute"].append(current_time)
        self.buckets[bucket_key]["hour"].append(current_time)

        return True, {
            "X-RateLimit-Endpoint": endpoint_key
        }


# Global instances
rate_limiter = RateLimiter(
    requests_per_minute=60,
    requests_per_hour=3600,
    burst_size=10
)

endpoint_limiter = EndpointRateLimiter()