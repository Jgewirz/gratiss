"""Link generation and management endpoints"""
from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel, Field
from typing import Optional
import secrets
import string
from datetime import datetime

from lib.db import db
from lib.redis_client import redis_client

router = APIRouter(prefix="/api/links", tags=["links"])

class CreateLinkRequest(BaseModel):
    """Request to create a tracking link"""
    destination_url: str
    influencer_id: str  # UUID as string
    program_id: str  # UUID as string
    campaign_name: Optional[str] = None
    tags: Optional[list[str]] = []
    utm_source: Optional[str] = None
    utm_medium: Optional[str] = None
    utm_campaign: Optional[str] = None

class LinkResponse(BaseModel):
    """Response with created link details"""
    id: str  # UUID as string
    slug: str
    short_url: str
    destination_url: str
    qr_code: Optional[str] = None

def generate_slug(length: int = 6) -> str:
    """Generate a random URL-safe slug"""
    characters = string.ascii_letters + string.digits
    return ''.join(secrets.choice(characters) for _ in range(length))

@router.post("/create", response_model=LinkResponse)
async def create_tracking_link(
    request: CreateLinkRequest,
    req: Request
):
    """Create a new tracking link with UTM parameters"""

    async with db.pool.acquire() as conn:
        # Generate unique slug
        max_attempts = 5
        slug = None
        for _ in range(max_attempts):
            candidate = generate_slug()
            exists = await conn.fetchval(
                "SELECT EXISTS(SELECT 1 FROM tracking_links WHERE slug = $1)",
                candidate
            )
            if not exists:
                slug = candidate
                break

        if not slug:
            raise HTTPException(status_code=500, detail="Could not generate unique slug")

        # Build destination URL with UTM parameters
        from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

        parsed = urlparse(request.destination_url)
        params = parse_qs(parsed.query)

        # Add UTM parameters
        if request.utm_source:
            params['utm_source'] = [request.utm_source]
        if request.utm_medium:
            params['utm_medium'] = [request.utm_medium]
        if request.utm_campaign:
            params['utm_campaign'] = [request.utm_campaign]

        # Add our tracking parameter
        params['ref'] = [slug]

        # Rebuild URL
        new_query = urlencode(params, doseq=True)
        destination_url = urlunparse((
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            parsed.params,
            new_query,
            parsed.fragment
        ))

        # Insert into database
        link_id = await conn.fetchval("""
            INSERT INTO tracking_links (
                slug, destination_url, influencer_id, program_id,
                utm_source, utm_medium, utm_campaign,
                created_at, is_active
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, NOW(), true)
            RETURNING id
        """,
            slug, destination_url, request.influencer_id, request.program_id,
            request.utm_source, request.utm_medium, request.utm_campaign
        )

        # Cache the link data in Redis for fast lookups
        link_data = {
            "id": str(link_id),  # Convert UUID to string for JSON serialization
            "destination_url": destination_url,
            "influencer_id": request.influencer_id,  # Already a string
            "cookie_duration_days": 7  # Default, should come from program
        }

        # Get program cookie duration
        cookie_days = await conn.fetchval(
            "SELECT cookie_window_days FROM programs WHERE id = $1",
            request.program_id
        )
        if cookie_days:
            link_data["cookie_duration_days"] = cookie_days

        # Cache for 1 hour
        cache_key = f"link:{slug}"
        await redis_client.set(cache_key, link_data, ttl=3600)

        # Build short URL
        base_url = req.app.state.settings.short_domain
        short_url = f"{base_url}/l/{slug}"

        return LinkResponse(
            id=str(link_id),  # Convert UUID to string
            slug=slug,
            short_url=short_url,
            destination_url=destination_url
        )

@router.get("/{slug}/stats")
async def get_link_stats(slug: str):
    """Get statistics for a specific tracking link"""

    async with db.pool.acquire() as conn:
        # Get link details with stats
        link = await conn.fetchrow("""
            SELECT
                tl.*,
                COUNT(DISTINCT c.id) as click_count,
                COUNT(DISTINCT c.ip_hash) as unique_visitors,
                COUNT(DISTINCT conv.id) as conversion_count,
                COALESCE(SUM(conv.order_amount), 0) as total_revenue,
                COALESCE(SUM(conv.commission_amount), 0) as total_commission
            FROM tracking_links tl
            LEFT JOIN clicks c ON c.tracking_link_id = tl.id
            LEFT JOIN conversions conv ON conv.tracking_link_id = tl.id
            WHERE tl.slug = $1
            GROUP BY tl.id
        """, slug)

        if not link:
            raise HTTPException(status_code=404, detail="Link not found")

        # Get click timeline
        clicks_timeline = await conn.fetch("""
            SELECT
                DATE(clicked_at) as date,
                COUNT(*) as clicks,
                COUNT(DISTINCT ip_hash) as unique_clicks
            FROM clicks
            WHERE tracking_link_id = $1
                AND clicked_at >= CURRENT_DATE - INTERVAL '30 days'
            GROUP BY DATE(clicked_at)
            ORDER BY date
        """, link['id'])

        # Get conversion details
        conversions = await conn.fetch("""
            SELECT
                order_id,
                order_amount,
                commission_amount,
                status,
                converted_at
            FROM conversions
            WHERE tracking_link_id = $1
            ORDER BY converted_at DESC
            LIMIT 10
        """, link['id'])

        return {
            "link": {
                "slug": link['slug'],
                "destination_url": link['destination_url'],
                "created_at": link['created_at'].isoformat() if link['created_at'] else None,
                "is_active": link['is_active']
            },
            "stats": {
                "total_clicks": link['click_count'],
                "unique_visitors": link['unique_visitors'],
                "conversions": link['conversion_count'],
                "total_revenue": float(link['total_revenue']),
                "total_commission": float(link['total_commission']),
                "conversion_rate": (link['conversion_count'] / link['click_count'] * 100)
                    if link['click_count'] > 0 else 0
            },
            "clicks_timeline": [
                {
                    "date": row['date'].isoformat(),
                    "clicks": row['clicks'],
                    "unique": row['unique_clicks']
                }
                for row in clicks_timeline
            ],
            "recent_conversions": [
                {
                    "order_id": row['order_id'],
                    "amount": float(row['order_amount']),
                    "commission": float(row['commission_amount']),
                    "status": row['status'],
                    "date": row['converted_at'].isoformat() if row['converted_at'] else None
                }
                for row in conversions
            ]
        }