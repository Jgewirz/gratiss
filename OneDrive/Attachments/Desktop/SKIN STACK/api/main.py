"""
SkinStack API - Main entry point with security middleware
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager

from lib.db import db
from lib.settings import settings
from lib.rate_limiter import rate_limiter
from lib.redis_client import redis_client
from api.middleware.logging import RequestLoggingMiddleware
from api.routes.health import router as health_router
from api.routes.redirect import router as redirect_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage app lifecycle - connect/disconnect resources"""
    # Startup
    print("[INFO] Starting SkinStack API...")

    # Connect to database
    await db.connect()
    print("[OK] Connected to PostgreSQL database")

    # Connect to Redis
    redis_connected = await redis_client.connect()
    if redis_connected:
        print("[OK] Connected to Redis cache")
    else:
        print("[WARNING] Running without Redis cache (optional)")

    # Initialize rate limiter
    await rate_limiter.start_cleanup()
    print("[OK] Rate limiter initialized")

    # Store in app state
    app.state.settings = settings
    app.state.redis = redis_client

    print(f"[OK] SkinStack API ready at http://0.0.0.0:8000")
    print(f"[OK] Environment: {settings.environment}")
    print(f"[OK] Platform fee: {settings.platform_fee_rate * 100}%")
    yield
    # Shutdown
    await db.disconnect()
    await redis_client.disconnect()
    print(f"[OK] Disconnected from database and cache")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version="0.0.1",
    lifespan=lifespan
)

# Configure CORS middleware
# In production, replace with specific allowed origins
allowed_origins = [
    "http://localhost:3000",      # React dev server
    "http://localhost:8000",      # API dev server
    "http://localhost:8080",      # Alternative frontend
    "https://skin.st",            # Production domain
    "https://www.skin.st",        # Production www
    "https://app.skin.st",        # Production app subdomain
    "https://dashboard.skin.st",  # Production dashboard
]

# Add CORS middleware with security settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins if settings.environment == "production" else ["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-Total-Count", "X-Processing-Time-Ms"],
    max_age=3600,  # Cache preflight requests for 1 hour
)

# Add Trusted Host middleware for production
if settings.environment == "production":
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=[
            "skin.st",
            "*.skin.st",
            "localhost",
            "127.0.0.1"
        ]
    )

# Add logging middleware
app.add_middleware(RequestLoggingMiddleware)

# Add rate limiting middleware
app.middleware("http")(rate_limiter)

# Include routers
app.include_router(health_router)  # Health check endpoints
app.include_router(redirect_router)  # High-priority redirect handler
# app.include_router(links_router)  # TODO: implement
# app.include_router(redirects_router)  # TODO: implement
# app.include_router(stats_router)  # TODO: implement
# app.include_router(webhooks_router)  # TODO: implement
# app.include_router(websocket_router)  # TODO: implement
# app.include_router(dashboard_router)  # TODO: implement


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug
    )