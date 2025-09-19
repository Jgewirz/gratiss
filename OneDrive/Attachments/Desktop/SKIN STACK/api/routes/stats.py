"""Analytics and statistics endpoints"""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, date, timedelta
from decimal import Decimal

from lib.db import db

router = APIRouter(prefix="/api/stats", tags=["stats"])

class InfluencerStats(BaseModel):
    """Comprehensive influencer statistics"""
    total_clicks: int
    unique_visitors: int
    total_conversions: int
    conversion_rate: float
    total_revenue: float
    total_commission: float
    net_earnings: float
    pending_payout: float
    lifetime_earnings: float

class DashboardStats(BaseModel):
    """Platform dashboard statistics"""
    total_influencers: int
    active_campaigns: int
    total_clicks: int
    total_conversions: int
    total_revenue: float
    platform_earnings: float
    avg_conversion_rate: float
    top_performers: List[dict]

@router.get("/influencer/{influencer_id}", response_model=InfluencerStats)
async def get_influencer_stats(
    influencer_id: int,
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None)
):
    """Get comprehensive stats for an influencer"""

    # Default to last 30 days if no dates provided
    if not end_date:
        end_date = date.today()
    if not start_date:
        start_date = end_date - timedelta(days=30)

    async with db.pool.acquire() as conn:
        # Get click and conversion stats
        stats = await conn.fetchrow("""
            SELECT
                COUNT(DISTINCT c.id) as total_clicks,
                COUNT(DISTINCT c.ip_hash) as unique_visitors,
                COUNT(DISTINCT conv.id) as total_conversions,
                COALESCE(SUM(conv.order_amount), 0) as total_revenue,
                COALESCE(SUM(conv.commission_amount), 0) as total_commission
            FROM tracking_links tl
            LEFT JOIN clicks c ON c.tracking_link_id = tl.id
                AND c.clicked_at BETWEEN $2 AND $3 + INTERVAL '1 day'
            LEFT JOIN conversions conv ON conv.tracking_link_id = tl.id
                AND conv.converted_at BETWEEN $2 AND $3 + INTERVAL '1 day'
            WHERE tl.influencer_id = $1
        """, influencer_id, start_date, end_date)

        # Get commission details
        commission_stats = await conn.fetchrow("""
            SELECT
                COALESCE(SUM(net_amount), 0) as net_earnings,
                COALESCE(SUM(CASE WHEN status = 'pending' THEN net_amount ELSE 0 END), 0) as pending_payout,
                COALESCE(SUM(CASE WHEN status = 'paid' THEN net_amount ELSE 0 END), 0) as lifetime_earnings
            FROM commissions
            WHERE influencer_id = $1
        """, influencer_id)

        # Calculate conversion rate
        conversion_rate = 0
        if stats['total_clicks'] > 0:
            conversion_rate = (stats['total_conversions'] / stats['total_clicks']) * 100

        return InfluencerStats(
            total_clicks=stats['total_clicks'],
            unique_visitors=stats['unique_visitors'],
            total_conversions=stats['total_conversions'],
            conversion_rate=conversion_rate,
            total_revenue=float(stats['total_revenue']),
            total_commission=float(stats['total_commission']),
            net_earnings=float(commission_stats['net_earnings']),
            pending_payout=float(commission_stats['pending_payout']),
            lifetime_earnings=float(commission_stats['lifetime_earnings'])
        )

@router.get("/dashboard")
async def get_dashboard_stats(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None)
):
    """Get platform-wide dashboard statistics"""

    # Default to last 30 days
    if not end_date:
        end_date = date.today()
    if not start_date:
        start_date = end_date - timedelta(days=30)

    async with db.pool.acquire() as conn:
        # Platform overview
        overview = await conn.fetchrow("""
            SELECT
                COUNT(DISTINCT i.id) as total_influencers,
                COUNT(DISTINCT p.id) as active_campaigns,
                COUNT(DISTINCT c.id) as total_clicks,
                COUNT(DISTINCT conv.id) as total_conversions,
                COALESCE(SUM(conv.order_amount), 0) as total_revenue,
                COALESCE(SUM(comm.platform_fee), 0) as platform_earnings
            FROM influencers i
            LEFT JOIN tracking_links tl ON tl.influencer_id = i.id
            LEFT JOIN programs p ON p.id = tl.program_id AND p.is_active = true
            LEFT JOIN clicks c ON c.tracking_link_id = tl.id
                AND c.clicked_at BETWEEN $1 AND $2 + INTERVAL '1 day'
            LEFT JOIN conversions conv ON conv.tracking_link_id = tl.id
                AND conv.converted_at BETWEEN $1 AND $2 + INTERVAL '1 day'
            LEFT JOIN commissions comm ON comm.conversion_id = conv.id
        """, start_date, end_date)

        # Top performers
        top_performers = await conn.fetch("""
            SELECT
                i.id,
                i.name,
                i.email,
                COUNT(DISTINCT conv.id) as conversions,
                COALESCE(SUM(conv.order_amount), 0) as revenue,
                COALESCE(SUM(comm.net_amount), 0) as earnings
            FROM influencers i
            JOIN tracking_links tl ON tl.influencer_id = i.id
            JOIN conversions conv ON conv.tracking_link_id = tl.id
                AND conv.converted_at BETWEEN $1 AND $2 + INTERVAL '1 day'
            LEFT JOIN commissions comm ON comm.conversion_id = conv.id
            GROUP BY i.id, i.name, i.email
            ORDER BY revenue DESC
            LIMIT 10
        """, start_date, end_date)

        # Calculate average conversion rate
        avg_conversion_rate = 0
        if overview['total_clicks'] > 0:
            avg_conversion_rate = (overview['total_conversions'] / overview['total_clicks']) * 100

        return {
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "overview": {
                "total_influencers": overview['total_influencers'],
                "active_campaigns": overview['active_campaigns'],
                "total_clicks": overview['total_clicks'],
                "total_conversions": overview['total_conversions'],
                "total_revenue": float(overview['total_revenue']),
                "platform_earnings": float(overview['platform_earnings']),
                "avg_conversion_rate": avg_conversion_rate
            },
            "top_performers": [
                {
                    "influencer_id": p['id'],
                    "name": p['name'],
                    "email": p['email'],
                    "conversions": p['conversions'],
                    "revenue": float(p['revenue']),
                    "earnings": float(p['earnings'])
                }
                for p in top_performers
            ]
        }

@router.get("/performance/hourly")
async def get_hourly_performance(
    date: Optional[date] = Query(None)
):
    """Get hourly performance metrics for a specific date"""

    if not date:
        date = date.today()

    async with db.pool.acquire() as conn:
        hourly_stats = await conn.fetch("""
            SELECT
                EXTRACT(HOUR FROM clicked_at) as hour,
                COUNT(*) as clicks,
                COUNT(DISTINCT ip_hash) as unique_clicks
            FROM clicks
            WHERE DATE(clicked_at) = $1
            GROUP BY EXTRACT(HOUR FROM clicked_at)
            ORDER BY hour
        """, date)

        return {
            "date": date.isoformat(),
            "hourly_performance": [
                {
                    "hour": int(row['hour']),
                    "clicks": row['clicks'],
                    "unique": row['unique_clicks']
                }
                for row in hourly_stats
            ]
        }

@router.get("/conversions/recent")
async def get_recent_conversions(
    limit: int = Query(20, le=100)
):
    """Get recent conversions across the platform"""

    async with db.pool.acquire() as conn:
        conversions = await conn.fetch("""
            SELECT
                conv.id,
                conv.order_id,
                conv.order_amount,
                conv.commission_amount,
                conv.status,
                conv.converted_at,
                i.name as influencer_name,
                p.name as program_name,
                tl.slug as tracking_slug
            FROM conversions conv
            JOIN tracking_links tl ON tl.id = conv.tracking_link_id
            JOIN influencers i ON i.id = tl.influencer_id
            JOIN programs p ON p.id = tl.program_id
            ORDER BY conv.converted_at DESC
            LIMIT $1
        """, limit)

        return {
            "conversions": [
                {
                    "id": row['id'],
                    "order_id": row['order_id'],
                    "amount": float(row['order_amount']),
                    "commission": float(row['commission_amount']),
                    "status": row['status'],
                    "date": row['converted_at'].isoformat() if row['converted_at'] else None,
                    "influencer": row['influencer_name'],
                    "program": row['program_name'],
                    "tracking_slug": row['tracking_slug']
                }
                for row in conversions
            ]
        }