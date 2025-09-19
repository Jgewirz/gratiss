"""
Health check endpoints
Following STEP 0 rules: minimal, < 100 LOC
"""
from fastapi import APIRouter, Response
from lib.db import db
from lib.logging import logger
from lib.redis_client import redis_client
import os
from pathlib import Path
import asyncpg

router = APIRouter(tags=["ops"])


@router.get("/healthz")
async def health_check(response: Response):
    """
    Health check endpoint
    Returns: {"ok": true} with 200 if healthy
    """
    # Log request
    request_id = logger.log_request("GET", "/healthz")

    # Check database
    db_healthy = await db.health_check()

    # Prepare response
    if db_healthy:
        status_code = 200
        result = {"ok": True, "database": "connected"}
    else:
        status_code = 503
        result = {"ok": False, "database": "disconnected"}

    # Log response
    latency = logger.log_response(status_code, "health-check")
    result["latency_ms"] = latency
    result["request_id"] = request_id

    response.status_code = status_code
    return result


@router.get("/readyz")
async def readiness_check(response: Response):
    """
    Readiness check endpoint
    Returns 200 when all migrations are applied and services are ready
    Returns 503 if migrations pending or services unavailable
    """
    request_id = logger.log_request("GET", "/readyz")

    # Check database
    db_healthy = await db.health_check()

    # Check Redis
    redis_healthy = await redis_client.ping()

    # Check migrations
    migrations_ready = True
    migration_status = []

    try:
        # Get list of migration files
        migrations_dir = Path(__file__).parent.parent.parent / "sql" / "migrations"
        migration_files = sorted([f.name for f in migrations_dir.glob("*.sql")])

        # Check applied migrations in database
        conn = await db.get_connection()
        try:
            applied = await conn.fetch(
                "SELECT version, name FROM schema_migrations ORDER BY version"
            )
            applied_versions = {row['version'] for row in applied}

            # Check each migration file
            for file in migration_files:
                # Extract version from filename (e.g., 001_clicks.sql -> 1)
                version = int(file.split('_')[0])
                is_applied = version in applied_versions
                migration_status.append({
                    "file": file,
                    "version": version,
                    "applied": is_applied
                })
                if not is_applied:
                    migrations_ready = False
        finally:
            await db.release_connection(conn)
    except Exception as e:
        migrations_ready = False
        migration_status = [{"error": str(e)}]

    # Determine overall readiness
    is_ready = db_healthy and redis_healthy and migrations_ready

    if is_ready:
        status_code = 200
        result = {
            "ready": True,
            "database": "ok",
            "redis": "ok" if redis_healthy else "unavailable",
            "migrations": "applied"
        }
    else:
        status_code = 503
        result = {
            "ready": False,
            "database": "ok" if db_healthy else "unavailable",
            "redis": "ok" if redis_healthy else "unavailable",
            "migrations": "pending" if not migrations_ready else "applied",
            "migration_details": migration_status if not migrations_ready else None
        }

    latency = logger.log_response(status_code, "readiness-check")
    result["latency_ms"] = latency
    result["request_id"] = request_id

    response.status_code = status_code
    return result


@router.get("/version")
async def version_info():
    """Return API version information"""
    import subprocess
    from datetime import datetime

    # Get git SHA
    try:
        git_sha = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()[:8]
    except:
        git_sha = "unknown"

    return {
        "version": "1.0.0",
        "name": "SkinStack API",
        "environment": os.getenv("ENVIRONMENT", "development"),
        "git_sha": git_sha,
        "build_time": datetime.utcnow().isoformat() + "Z",
        "env": os.getenv("ENVIRONMENT", "development")
    }


@router.get("/metrics", response_class=Response)
async def metrics():
    """Prometheus-compatible metrics endpoint"""
    from lib.metrics import metrics as global_metrics

    # Export metrics in Prometheus format
    prometheus_output = global_metrics.export_prometheus()

    # Also add database metrics
    try:
        conn = await db.get_connection()
        try:
            link_count = await conn.fetchval("SELECT COUNT(*) FROM tracking_links")
            click_count = await conn.fetchval("SELECT COUNT(*) FROM clicks")
            conversion_count = await conn.fetchval("SELECT COUNT(*) FROM conversions WHERE id IS NOT NULL")

            prometheus_output += f"\n# HELP tracking_links_total Total tracking links\n"
            prometheus_output += f"# TYPE tracking_links_total gauge\n"
            prometheus_output += f"tracking_links_total {link_count}\n"

            prometheus_output += f"# HELP clicks_total Total clicks\n"
            prometheus_output += f"# TYPE clicks_total gauge\n"
            prometheus_output += f"clicks_total {click_count}\n"

            prometheus_output += f"# HELP conversions_total Total conversions\n"
            prometheus_output += f"# TYPE conversions_total gauge\n"
            prometheus_output += f"conversions_total {conversion_count}\n"
        finally:
            await db.release_connection(conn)
    except Exception as e:
        # Include error as comment
        prometheus_output += f"\n# ERROR: {str(e)}\n"

    return Response(content=prometheus_output, media_type="text/plain")