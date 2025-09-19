"""Dashboard API endpoints for metrics and analytics"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta, date
from decimal import Decimal
import logging

from lib.db import db

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])
logger = logging.getLogger(__name__)


@router.get("/overview")
async def get_dashboard_overview():
    """Get high-level dashboard metrics"""

    async with db.pool.acquire() as conn:
        # Get today's metrics
        today_metrics = await conn.fetchrow("""
            SELECT
                COUNT(DISTINCT c.id) as clicks_today,
                COUNT(DISTINCT conv.id) as conversions_today,
                COALESCE(SUM(conv.order_amount), 0) as revenue_today,
                COUNT(DISTINCT c.tracking_link_id) as active_links_today
            FROM clicks c
            LEFT JOIN conversions conv ON conv.tracking_link_id = c.tracking_link_id
                AND DATE(conv.converted_at) = CURRENT_DATE
            WHERE DATE(c.clicked_at) = CURRENT_DATE
        """)

        # Get total metrics
        total_metrics = await conn.fetchrow("""
            SELECT
                COUNT(DISTINCT tl.id) as total_links,
                COUNT(DISTINCT i.id) as total_influencers,
                COUNT(DISTINCT c.id) as total_clicks,
                COUNT(DISTINCT conv.id) as total_conversions,
                COALESCE(SUM(conv.order_amount), 0) as total_revenue
            FROM tracking_links tl
            LEFT JOIN influencers i ON i.id = tl.influencer_id
            LEFT JOIN clicks c ON c.tracking_link_id = tl.id
            LEFT JOIN conversions conv ON conv.tracking_link_id = tl.id
        """)

        # Calculate conversion rate
        conversion_rate = 0
        if total_metrics['total_clicks'] > 0:
            conversion_rate = (total_metrics['total_conversions'] / total_metrics['total_clicks']) * 100

        return {
            "today": {
                "clicks": today_metrics['clicks_today'],
                "conversions": today_metrics['conversions_today'],
                "revenue": float(today_metrics['revenue_today']),
                "active_links": today_metrics['active_links_today']
            },
            "total": {
                "links": total_metrics['total_links'],
                "influencers": total_metrics['total_influencers'],
                "clicks": total_metrics['total_clicks'],
                "conversions": total_metrics['total_conversions'],
                "revenue": float(total_metrics['total_revenue']),
                "conversion_rate": round(conversion_rate, 2)
            }
        }


@router.get("/time-series")
async def get_time_series_data(
    metric: str = Query(..., description="Metric to retrieve: clicks, conversions, revenue"),
    days: int = Query(7, description="Number of days to retrieve"),
    group_by: str = Query("day", description="Grouping: hour, day, week")
):
    """Get time series data for charts"""

    if metric not in ["clicks", "conversions", "revenue"]:
        raise HTTPException(status_code=400, detail="Invalid metric")

    if group_by not in ["hour", "day", "week"]:
        raise HTTPException(status_code=400, detail="Invalid grouping")

    async with db.pool.acquire() as conn:
        # Determine date truncation based on grouping
        date_trunc = {
            "hour": "hour",
            "day": "day",
            "week": "week"
        }[group_by]

        if metric == "clicks":
            query = f"""
                SELECT
                    DATE_TRUNC('{date_trunc}', clicked_at) as period,
                    COUNT(*) as value
                FROM clicks
                WHERE clicked_at >= CURRENT_TIMESTAMP - INTERVAL '{days} days'
                GROUP BY period
                ORDER BY period ASC
            """
        elif metric == "conversions":
            query = f"""
                SELECT
                    DATE_TRUNC('{date_trunc}', converted_at) as period,
                    COUNT(*) as value
                FROM conversions
                WHERE converted_at >= CURRENT_TIMESTAMP - INTERVAL '{days} days'
                GROUP BY period
                ORDER BY period ASC
            """
        else:  # revenue
            query = f"""
                SELECT
                    DATE_TRUNC('{date_trunc}', converted_at) as period,
                    COALESCE(SUM(order_amount), 0) as value
                FROM conversions
                WHERE converted_at >= CURRENT_TIMESTAMP - INTERVAL '{days} days'
                GROUP BY period
                ORDER BY period ASC
            """

        rows = await conn.fetch(query)

        return {
            "metric": metric,
            "group_by": group_by,
            "data": [
                {
                    "period": row['period'].isoformat(),
                    "value": float(row['value']) if metric == "revenue" else row['value']
                }
                for row in rows
            ]
        }


@router.get("/top-performers")
async def get_top_performers(
    limit: int = Query(10, description="Number of results"),
    period_days: int = Query(30, description="Period in days"),
    order_by: str = Query("revenue", description="Order by: clicks, conversions, revenue")
):
    """Get top performing influencers"""

    if order_by not in ["clicks", "conversions", "revenue"]:
        raise HTTPException(status_code=400, detail="Invalid order_by parameter")

    async with db.pool.acquire() as conn:
        order_column = {
            "clicks": "total_clicks",
            "conversions": "total_conversions",
            "revenue": "total_revenue"
        }[order_by]

        query = f"""
            SELECT
                i.id,
                i.name,
                i.email,
                COUNT(DISTINCT c.id) as total_clicks,
                COUNT(DISTINCT conv.id) as total_conversions,
                COALESCE(SUM(conv.order_amount), 0) as total_revenue,
                CASE
                    WHEN COUNT(DISTINCT c.id) > 0
                    THEN (COUNT(DISTINCT conv.id)::float / COUNT(DISTINCT c.id) * 100)
                    ELSE 0
                END as conversion_rate
            FROM influencers i
            LEFT JOIN tracking_links tl ON tl.influencer_id = i.id
            LEFT JOIN clicks c ON c.tracking_link_id = tl.id
                AND c.clicked_at >= CURRENT_TIMESTAMP - INTERVAL '{period_days} days'
            LEFT JOIN conversions conv ON conv.tracking_link_id = tl.id
                AND conv.converted_at >= CURRENT_TIMESTAMP - INTERVAL '{period_days} days'
            GROUP BY i.id, i.name, i.email
            ORDER BY {order_column} DESC
            LIMIT $1
        """

        rows = await conn.fetch(query, limit)

        return {
            "period_days": period_days,
            "order_by": order_by,
            "influencers": [
                {
                    "id": str(row['id']),
                    "name": row['name'],
                    "email": row['email'],
                    "total_clicks": row['total_clicks'],
                    "total_conversions": row['total_conversions'],
                    "total_revenue": float(row['total_revenue']),
                    "conversion_rate": round(row['conversion_rate'], 2)
                }
                for row in rows
            ]
        }


@router.get("/recent-activity")
async def get_recent_activity(
    limit: int = Query(20, description="Number of events"),
    event_types: Optional[str] = Query(None, description="Comma-separated event types")
):
    """Get recent activity feed"""

    allowed_types = ["click", "conversion", "webhook"]
    if event_types:
        requested_types = event_types.split(",")
        invalid_types = [t for t in requested_types if t not in allowed_types]
        if invalid_types:
            raise HTTPException(status_code=400, detail=f"Invalid event types: {invalid_types}")
    else:
        requested_types = allowed_types

    async with db.pool.acquire() as conn:
        events = []

        # Get recent clicks
        if "click" in requested_types:
            clicks = await conn.fetch("""
                SELECT
                    'click' as event_type,
                    c.clicked_at as timestamp,
                    c.device_type,
                    c.browser,
                    tl.slug,
                    i.name as influencer_name
                FROM clicks c
                JOIN tracking_links tl ON tl.id = c.tracking_link_id
                LEFT JOIN influencers i ON i.id = tl.influencer_id
                ORDER BY c.clicked_at DESC
                LIMIT $1
            """, limit)

            for click in clicks:
                events.append({
                    "type": "click",
                    "timestamp": click['timestamp'].isoformat(),
                    "details": {
                        "slug": click['slug'],
                        "influencer": click['influencer_name'],
                        "device": click['device_type'],
                        "browser": click['browser']
                    }
                })

        # Get recent conversions
        if "conversion" in requested_types:
            conversions = await conn.fetch("""
                SELECT
                    'conversion' as event_type,
                    conv.converted_at as timestamp,
                    conv.order_id,
                    conv.order_amount,
                    conv.commission_amount,
                    i.name as influencer_name
                FROM conversions conv
                JOIN tracking_links tl ON tl.id = conv.tracking_link_id
                LEFT JOIN influencers i ON i.id = tl.influencer_id
                ORDER BY conv.converted_at DESC
                LIMIT $1
            """, limit)

            for conv in conversions:
                events.append({
                    "type": "conversion",
                    "timestamp": conv['timestamp'].isoformat(),
                    "details": {
                        "order_id": conv['order_id'],
                        "amount": float(conv['order_amount']),
                        "commission": float(conv['commission_amount']),
                        "influencer": conv['influencer_name']
                    }
                })

        # Get recent webhooks
        if "webhook" in requested_types:
            webhooks = await conn.fetch("""
                SELECT
                    'webhook' as event_type,
                    created_at as timestamp,
                    source,
                    event_type as webhook_type,
                    status_code,
                    is_duplicate
                FROM webhook_events
                ORDER BY created_at DESC
                LIMIT $1
            """, limit)

            for webhook in webhooks:
                events.append({
                    "type": "webhook",
                    "timestamp": webhook['timestamp'].isoformat(),
                    "details": {
                        "source": webhook['source'],
                        "webhook_type": webhook['webhook_type'],
                        "status": webhook['status_code'],
                        "duplicate": webhook['is_duplicate']
                    }
                })

        # Sort all events by timestamp
        events.sort(key=lambda x: x['timestamp'], reverse=True)

        return {
            "count": len(events[:limit]),
            "events": events[:limit]
        }


@router.get("/device-stats")
async def get_device_statistics(
    period_days: int = Query(30, description="Period in days")
):
    """Get device and browser statistics"""

    async with db.pool.acquire() as conn:
        # Device type breakdown
        device_stats = await conn.fetch("""
            SELECT
                device_type,
                COUNT(*) as count,
                COUNT(DISTINCT tracking_link_id) as unique_links
            FROM clicks
            WHERE clicked_at >= CURRENT_TIMESTAMP - INTERVAL '$1 days'
            GROUP BY device_type
            ORDER BY count DESC
        """, period_days)

        # Browser breakdown
        browser_stats = await conn.fetch("""
            SELECT
                browser,
                COUNT(*) as count,
                COUNT(DISTINCT tracking_link_id) as unique_links
            FROM clicks
            WHERE clicked_at >= CURRENT_TIMESTAMP - INTERVAL '$1 days'
            GROUP BY browser
            ORDER BY count DESC
        """, period_days)

        # Calculate percentages
        total_clicks = sum(row['count'] for row in device_stats)

        return {
            "period_days": period_days,
            "total_clicks": total_clicks,
            "devices": [
                {
                    "type": row['device_type'],
                    "count": row['count'],
                    "percentage": round((row['count'] / total_clicks * 100) if total_clicks > 0 else 0, 2),
                    "unique_links": row['unique_links']
                }
                for row in device_stats
            ],
            "browsers": [
                {
                    "type": row['browser'],
                    "count": row['count'],
                    "percentage": round((row['count'] / total_clicks * 100) if total_clicks > 0 else 0, 2),
                    "unique_links": row['unique_links']
                }
                for row in browser_stats
            ]
        }


@router.get("/commission-summary")
async def get_commission_summary():
    """Get commission payout summary"""

    async with db.pool.acquire() as conn:
        # Get pending commissions
        pending = await conn.fetchrow("""
            SELECT
                COUNT(*) as count,
                COALESCE(SUM(net_amount), 0) as total_amount,
                COUNT(DISTINCT influencer_id) as influencer_count
            FROM commissions
            WHERE status = 'pending'
        """)

        # Get paid commissions
        paid = await conn.fetchrow("""
            SELECT
                COUNT(*) as count,
                COALESCE(SUM(net_amount), 0) as total_amount,
                COUNT(DISTINCT influencer_id) as influencer_count
            FROM commissions
            WHERE status = 'paid'
        """)

        # Get platform fees collected
        fees = await conn.fetchrow("""
            SELECT
                COALESCE(SUM(platform_fee), 0) as total_fees
            FROM commissions
        """)

        # Get influencers ready for payout (>$50)
        ready_for_payout = await conn.fetch("""
            SELECT
                i.id,
                i.name,
                i.email,
                SUM(c.net_amount) as pending_amount
            FROM influencers i
            JOIN commissions c ON c.influencer_id = i.id
            WHERE c.status = 'pending'
            GROUP BY i.id, i.name, i.email
            HAVING SUM(c.net_amount) >= 50
            ORDER BY pending_amount DESC
        """)

        return {
            "pending": {
                "count": pending['count'],
                "total_amount": float(pending['total_amount']),
                "influencer_count": pending['influencer_count']
            },
            "paid": {
                "count": paid['count'],
                "total_amount": float(paid['total_amount']),
                "influencer_count": paid['influencer_count']
            },
            "platform_fees": float(fees['total_fees']),
            "ready_for_payout": [
                {
                    "id": str(row['id']),
                    "name": row['name'],
                    "email": row['email'],
                    "amount": float(row['pending_amount'])
                }
                for row in ready_for_payout
            ]
        }