"""
High-performance redirect endpoint with Redis caching
"""
import time
from fastapi import APIRouter, Response, HTTPException
from fastapi.responses import RedirectResponse
from lib.db import db
from lib.redis_client import redis_client
from lib.metrics import metrics
from lib.logging import logger
import json

router = APIRouter(tags=["redirect"])

# Cache configuration
CACHE_TTL = 3600  # 1 hour TTL for slug->url mapping
CACHE_PREFIX = "redirect:"


@router.get("/r/{slug}")
async def redirect_slug(slug: str, response: Response):
    """
    High-performance redirect with Redis caching
    Target: <5ms p95 latency
    """
    start_time = time.time()

    # Try Redis cache first
    cache_key = f"{CACHE_PREFIX}{slug}"
    cached_url = None

    try:
        cached_data = await redis_client.get(cache_key)
        if cached_data:
            # Cache hit
            cached_url = json.loads(cached_data)
            metrics.increment_cache_hit()
        else:
            metrics.increment_cache_miss()
    except Exception as e:
        # Redis error - continue without cache
        print(f"Redis error: {e}")
        metrics.increment_cache_miss()

    if cached_url:
        # Cache hit - redirect immediately
        destination_url = cached_url.get("destination_url")
        tracking_link_id = cached_url.get("tracking_link_id")
    else:
        # Cache miss - fetch from database
        conn = await db.get_connection()
        try:
            row = await conn.fetchrow("""
                SELECT id, destination_url
                FROM tracking_links
                WHERE slug = $1 AND is_active = true
                LIMIT 1
            """, slug)

            if not row:
                raise HTTPException(status_code=404, detail="Link not found")

            tracking_link_id = row["id"]
            destination_url = row["destination_url"]

            # Cache the result
            cache_data = {
                "tracking_link_id": str(tracking_link_id),
                "destination_url": destination_url
            }
            try:
                await redis_client.set(
                    cache_key,
                    json.dumps(cache_data),
                    ttl=CACHE_TTL
                )
            except Exception as e:
                # Continue even if caching fails
                print(f"Failed to cache: {e}")

        finally:
            await db.release_connection(conn)

    # Record click asynchronously (fire and forget)
    # In production, this would go to a queue
    try:
        conn = await db.get_connection()
        await conn.execute("""
            INSERT INTO clicks (tracking_link_id, slug, clicked_at)
            VALUES ($1, $2, NOW())
        """, tracking_link_id, slug)
        await db.release_connection(conn)
    except Exception as e:
        # Don't fail the redirect if click recording fails
        print(f"Failed to record click: {e}")

    # Record metrics
    duration_ms = (time.time() - start_time) * 1000
    metrics.record_duration(duration_ms, metric_type="redirect")

    # Return 302 redirect
    return RedirectResponse(url=destination_url, status_code=302)


@router.on_event("startup")
async def prewarm_cache():
    """
    Pre-warm Redis cache with active tracking links
    """
    print("[INFO] Pre-warming redirect cache...")

    conn = await db.get_connection()
    try:
        rows = await conn.fetch("""
            SELECT id, slug, destination_url
            FROM tracking_links
            WHERE is_active = true
        """)

        count = 0
        for row in rows:
            cache_key = f"{CACHE_PREFIX}{row['slug']}"
            cache_data = {
                "tracking_link_id": str(row["id"]),
                "destination_url": row["destination_url"]
            }
            try:
                await redis_client.set(
                    cache_key,
                    json.dumps(cache_data),
                    ttl=CACHE_TTL
                )
                count += 1
            except Exception as e:
                print(f"Failed to cache {row['slug']}: {e}")

        print(f"[OK] Pre-warmed {count} slugs in cache")

    except Exception as e:
        print(f"[ERROR] Cache pre-warm failed: {e}")
    finally:
        await db.release_connection(conn)