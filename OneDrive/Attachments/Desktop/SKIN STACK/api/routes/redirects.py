"""High-performance redirect handler with click tracking"""
from fastapi import APIRouter, Request, Response
from fastapi.responses import RedirectResponse
import hashlib
from datetime import datetime
import logging

from lib.db import db
from lib.websocket_manager import manager
from lib.redis_client import redis_client

router = APIRouter(tags=["redirects"])
logger = logging.getLogger(__name__)

def hash_ip(ip: str) -> str:
    """Hash IP address for privacy"""
    return hashlib.sha256(f"{ip}:skinstack".encode()).hexdigest()

def parse_user_agent(ua: str) -> dict:
    """Parse user agent string for device info"""
    device_type = "desktop"
    if any(x in ua.lower() for x in ['mobile', 'android', 'iphone']):
        device_type = "mobile"
    elif any(x in ua.lower() for x in ['tablet', 'ipad']):
        device_type = "tablet"

    browser = "unknown"
    if 'chrome' in ua.lower():
        browser = "chrome"
    elif 'firefox' in ua.lower():
        browser = "firefox"
    elif 'safari' in ua.lower():
        browser = "safari"
    elif 'edge' in ua.lower():
        browser = "edge"

    return {"device_type": device_type, "browser": browser}

@router.get("/l/{slug}")
async def handle_redirect(
    slug: str,
    request: Request,
    response: Response
):
    """
    Handle link redirect with sub-millisecond performance.
    Tracks click and redirects to destination URL.
    """
    start_time = datetime.now()
    cache_hit = False

    # Try Redis cache first
    cache_key = f"link:{slug}"
    cached_link = await redis_client.get(cache_key)

    if cached_link:
        link = cached_link
        cache_hit = True
    else:
        # Get database connection
        async with db.pool.acquire() as conn:
            # Fetch link in one query with program data
            row = await conn.fetchrow("""
                SELECT
                    tl.id,
                    tl.destination_url,
                    tl.influencer_id,
                    p.cookie_window_days as cookie_duration_days
                FROM tracking_links tl
                JOIN programs p ON p.id = tl.program_id
                WHERE tl.slug = $1 AND tl.is_active = true
            """, slug)

            if row:
                link = dict(row)
                # Cache for 1 hour
                await redis_client.set(cache_key, link, ttl=3600)
            else:
                link = None

    if not link:
        # Return 404 but still track for analytics
        logger.warning(f"Invalid slug attempted: {slug}")
        return RedirectResponse(url="/", status_code=302)

    # Extract request data from outside the with block since we may have cached data
    client_ip = request.client.host
    ip_hash = hash_ip(client_ip)
    user_agent = request.headers.get("user-agent", "")
    referer = request.headers.get("referer", "")
    device_info = parse_user_agent(user_agent)

    # Track click asynchronously (fire and forget)
    try:
        async with db.pool.acquire() as conn:
            click_id = await conn.fetchval("""
                INSERT INTO clicks (
                    tracking_link_id,
                    ip_hash,
                    user_agent,
                    referer,
                    device_type,
                    browser,
                    clicked_at
                ) VALUES ($1, $2, $3, $4, $5, $6, NOW())
                RETURNING id
            """,
                link['id'],
                ip_hash,
                user_agent[:500],  # Limit UA length
                referer[:500],     # Limit referer length
                device_info['device_type'],
                device_info['browser']
            )

            # Update link stats (non-blocking)
            await conn.execute("""
                UPDATE tracking_links
                SET total_clicks = total_clicks + 1
                WHERE id = $1
            """, link['id'])

        # Broadcast click event via WebSocket
        await manager.broadcast_click(
                tracking_link_id=link['id'],
                slug=slug,
                ip_hash=ip_hash,
                device_type=device_info['device_type']
            )

    except Exception as e:
        # Don't block redirect on tracking errors
        logger.error(f"Error tracking click: {e}")

    # Set attribution cookie
    response.set_cookie(
            key=f"skin_ref_{link['influencer_id']}",
            value=slug,
            max_age=link['cookie_duration_days'] * 24 * 60 * 60,
            httponly=True,
            samesite="lax"
        )

    # Calculate performance metrics
    processing_time = (datetime.now() - start_time).total_seconds() * 1000

    # Add performance headers
    response.headers["X-Processing-Time-Ms"] = str(processing_time)
    response.headers["X-Cache-Status"] = "HIT" if cache_hit else "MISS"

    # Log if slow
    if processing_time > 5:
        logger.warning(f"Slow redirect: {processing_time:.2f}ms for slug {slug}")

    # Redirect to destination
    return RedirectResponse(
            url=link['destination_url'],
            status_code=302,
            headers={
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "X-Redirect-By": "SkinStack"
            }
        )