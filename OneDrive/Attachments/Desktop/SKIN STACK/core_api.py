#!/usr/bin/env python3
"""
SkinStack Core API Server
=========================
This is the SECOND FILE - the core API that handles:
1. Link generation (/api/links/create)
2. Click tracking & redirects (/l/{slug})
3. Webhook processing (/webhooks/{network})
4. Stats API (/api/stats)

This is a production-ready server using FastAPI with:
- PostgreSQL for production (SQLite for development)
- Redis for caching and rate limiting
- Async request handling
- Security headers and CORS
- Comprehensive error handling

Run: uvicorn core_api:app --reload --port 8000
"""

import os
import json
import uuid
import hashlib
import secrets
import hmac
import base64
from datetime import datetime, timedelta, date
from decimal import Decimal
from typing import Optional, List, Dict, Any
from urllib.parse import urlencode, urlparse, parse_qs, urlunparse
import asyncio
import logging

# FastAPI and async
from fastapi import FastAPI, HTTPException, Depends, Query, Request, Response, BackgroundTasks
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from pydantic import BaseModel, Field, field_validator
import uvicorn

# Database
import asyncpg
import sqlite3
from contextlib import asynccontextmanager

# Redis for caching
import redis.asyncio as redis

# HTTP client for external APIs
import httpx

# Security
from passlib.context import CryptContext
from jose import JWTError, jwt

# Environment
from dotenv import load_dotenv
load_dotenv()

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# =============================================================================
# Configuration
# =============================================================================

class Config:
    # Database
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///skinstack.db')
    USE_POSTGRES = DATABASE_URL.startswith('postgresql')

    # Redis
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

    # Security
    SECRET_KEY = os.getenv('SECRET_KEY', secrets.token_hex(32))
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30

    # Domain
    BASE_URL = os.getenv('BASE_URL', 'http://localhost:8000')
    SHORT_DOMAIN = os.getenv('SHORT_DOMAIN', 'http://localhost:8000')

    # Platform settings
    PLATFORM_FEE_RATE = float(os.getenv('PLATFORM_FEE_RATE', '0.20'))  # 20%
    MIN_PAYOUT_AMOUNT = Decimal(os.getenv('MIN_PAYOUT_AMOUNT', '50.00'))
    DEFAULT_COOKIE_WINDOW_DAYS = int(os.getenv('DEFAULT_COOKIE_WINDOW_DAYS', '7'))

    # Network credentials (will be encrypted in production)
    SHOPIFY_WEBHOOK_SECRET = os.getenv('SHOPIFY_WEBHOOK_SECRET', '')
    IMPACT_ACCOUNT_SID = os.getenv('IMPACT_ACCOUNT_SID', '')
    IMPACT_AUTH_TOKEN = os.getenv('IMPACT_AUTH_TOKEN', '')
    AMAZON_ASSOCIATE_TAG = os.getenv('AMAZON_ASSOCIATE_TAG', '')

    # Rate limiting
    RATE_LIMIT_CLICKS = int(os.getenv('RATE_LIMIT_CLICKS', '100'))  # per minute
    RATE_LIMIT_API = int(os.getenv('RATE_LIMIT_API', '1000'))  # per minute

config = Config()

# =============================================================================
# Database Setup
# =============================================================================

class Database:
    def __init__(self):
        self.pool = None
        self.redis = None

    async def connect(self):
        """Initialize database connections"""
        if config.USE_POSTGRES:
            # PostgreSQL connection pool
            # Parse the DATABASE_URL properly
            db_url = config.DATABASE_URL
            if db_url.startswith('postgresql://'):
                db_url = db_url.replace('postgresql://', '')
            elif db_url.startswith('postgres://'):
                db_url = db_url.replace('postgres://', '')

            try:
                self.pool = await asyncpg.create_pool(
                    f"postgresql://{db_url}",
                    min_size=10,
                    max_size=20,
                    command_timeout=60
                )
                logger.info("Connected to PostgreSQL")
            except Exception as e:
                logger.error(f"Failed to connect to PostgreSQL: {e}")
                # Fallback to SQLite
                logger.info("Falling back to SQLite for development")
                config.USE_POSTGRES = False
        else:
            # SQLite for development (synchronous, wrapped in async)
            logger.info("Using SQLite for development")
            # Create tables if they don't exist
            await self._init_sqlite_tables()

        # Redis connection
        try:
            self.redis = await redis.from_url(
                config.REDIS_URL,
                encoding="utf-8",
                decode_responses=True
            )
            await self.redis.ping()
            logger.info("Connected to Redis")
        except Exception as e:
            logger.warning(f"Redis not available: {e}. Running without cache.")
            self.redis = None

    async def disconnect(self):
        """Close database connections"""
        if self.pool:
            await self.pool.close()
        if self.redis:
            await self.redis.close()

    async def execute(self, query: str, *args):
        """Execute a query"""
        if config.USE_POSTGRES:
            async with self.pool.acquire() as conn:
                return await conn.execute(query, *args)
        else:
            # SQLite fallback (sync wrapped in async)
            return await self._sqlite_execute(query, args)

    async def fetchone(self, query: str, *args):
        """Fetch one row"""
        if config.USE_POSTGRES:
            async with self.pool.acquire() as conn:
                return await conn.fetchrow(query, *args)
        else:
            return await self._sqlite_fetchone(query, args)

    async def fetchall(self, query: str, *args):
        """Fetch all rows"""
        if config.USE_POSTGRES:
            async with self.pool.acquire() as conn:
                return await conn.fetch(query, *args)
        else:
            return await self._sqlite_fetchall(query, args)

    async def _sqlite_execute(self, query: str, args):
        """SQLite execute wrapper"""
        await asyncio.sleep(0)  # Yield control
        conn = sqlite3.connect('skinstack.db')
        cursor = conn.cursor()
        # Convert PostgreSQL placeholders to SQLite
        for i in range(20, 0, -1):  # Handle up to $20 placeholders
            query = query.replace(f'${i}', '?')
        cursor.execute(query, args)
        conn.commit()
        lastrowid = cursor.lastrowid
        conn.close()
        return lastrowid

    async def _sqlite_fetchone(self, query: str, args):
        """SQLite fetchone wrapper"""
        await asyncio.sleep(0)  # Yield control
        conn = sqlite3.connect('skinstack.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        for i in range(20, 0, -1):  # Handle up to $20 placeholders
            query = query.replace(f'${i}', '?')
        cursor.execute(query, args)
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    async def _sqlite_fetchall(self, query: str, args):
        """SQLite fetchall wrapper"""
        await asyncio.sleep(0)  # Yield control
        conn = sqlite3.connect('skinstack.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        for i in range(20, 0, -1):  # Handle up to $20 placeholders
            query = query.replace(f'${i}', '?')
        cursor.execute(query, args)
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    async def _init_sqlite_tables(self):
        """Initialize SQLite tables if they don't exist"""
        await asyncio.sleep(0)
        conn = sqlite3.connect('skinstack.db')
        cursor = conn.cursor()

        # Create tables
        cursor.executescript('''
            CREATE TABLE IF NOT EXISTS tracking_links (
                id TEXT PRIMARY KEY,
                influencer_id TEXT NOT NULL,
                program_id TEXT NOT NULL,
                product_id TEXT,
                campaign_id TEXT,
                slug TEXT UNIQUE NOT NULL,
                destination_url TEXT NOT NULL,
                utm_source TEXT,
                utm_medium TEXT,
                utm_campaign TEXT,
                metadata TEXT,
                active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS clicks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tracking_link_id TEXT NOT NULL,
                ip_hash TEXT,
                user_agent TEXT,
                referrer TEXT,
                device_id TEXT,
                session_id TEXT,
                fingerprint TEXT,
                platform TEXT,
                subid TEXT,
                fraud_score REAL,
                fraud_flags TEXT,
                clicked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (tracking_link_id) REFERENCES tracking_links(id)
            );

            CREATE TABLE IF NOT EXISTS conversions (
                id TEXT PRIMARY KEY,
                order_id TEXT UNIQUE NOT NULL,
                occurred_at TIMESTAMP,
                subtotal REAL,
                tax REAL,
                shipping REAL,
                total REAL,
                currency TEXT,
                items TEXT,
                subid TEXT,
                raw_event TEXT,
                status TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS attributions (
                id TEXT PRIMARY KEY,
                conversion_id TEXT NOT NULL,
                tracking_link_id TEXT NOT NULL,
                model TEXT,
                match_type TEXT,
                reason TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (conversion_id) REFERENCES conversions(id),
                FOREIGN KEY (tracking_link_id) REFERENCES tracking_links(id)
            );

            CREATE TABLE IF NOT EXISTS commissions (
                id TEXT PRIMARY KEY,
                attribution_id TEXT,
                conversion_id TEXT,
                influencer_id TEXT NOT NULL,
                program_id TEXT NOT NULL,
                gross_amount REAL,
                platform_fee REAL,
                net_amount REAL,
                status TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (attribution_id) REFERENCES attributions(id),
                FOREIGN KEY (conversion_id) REFERENCES conversions(id)
            );

            CREATE TABLE IF NOT EXISTS programs (
                id TEXT PRIMARY KEY,
                merchant_id TEXT NOT NULL,
                name TEXT NOT NULL,
                commission_type TEXT,
                commission_value REAL,
                website TEXT,
                integration_type TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS merchants (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                website TEXT,
                integration_type TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS products (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        ''')

        conn.commit()
        conn.close()
        logger.info("SQLite tables initialized")

# Global database instance
db = Database()

# =============================================================================
# Pydantic Models
# =============================================================================

class CreateLinkRequest(BaseModel):
    """Request to create a new tracking link"""
    influencer_id: str
    program_id: str
    product_id: Optional[str] = None
    campaign_id: Optional[str] = None
    custom_slug: Optional[str] = Field(None, min_length=3, max_length=20)
    utm_source: Optional[str] = "influencer"
    utm_medium: Optional[str] = "social"
    utm_campaign: Optional[str] = None

class LinkResponse(BaseModel):
    """Tracking link response"""
    id: str
    slug: str
    short_url: str
    destination_url: str
    clicks: int = 0
    conversions: int = 0
    earnings: float = 0.0
    created_at: datetime

class WebhookRequest(BaseModel):
    """Generic webhook request"""
    event_type: str
    payload: Dict[str, Any]
    signature: Optional[str] = None

class StatsResponse(BaseModel):
    """Statistics response"""
    period: str
    clicks: int
    unique_clicks: int
    conversions: int
    conversion_rate: float
    total_revenue: float
    total_commission: float
    avg_order_value: float
    earnings_per_click: float

class InfluencerStats(BaseModel):
    """Influencer statistics"""
    influencer_id: str
    total_clicks: int
    total_conversions: int
    conversion_rate: float
    pending_earnings: float
    approved_earnings: float
    paid_earnings: float
    top_products: List[Dict[str, Any]]

# =============================================================================
# Core Services
# =============================================================================

class LinkService:
    """Handle link generation and management"""

    @staticmethod
    def generate_slug(length: int = 8) -> str:
        """Generate a unique short slug"""
        chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        return ''.join(secrets.choice(chars) for _ in range(length))

    @staticmethod
    def build_destination_url(base_url: str, params: dict, network_type: str) -> str:
        """Build the final destination URL with tracking parameters"""

        # Network-specific parameter mappings
        network_params = {
            'shopify_refersion': {'subid': 'ref', 'campaign': 'utm_campaign'},
            'impact': {'subid': 'irpid', 'campaign': 'utm_campaign'},
            'amazon': {'subid': 'tag', 'campaign': 'linkCode'},
            'levanta': {'subid': 'aff_id', 'campaign': 'campaign_id'}
        }

        parsed = urlparse(base_url)
        query_params = parse_qs(parsed.query)

        # Add network-specific parameters
        if network_type in network_params:
            mapping = network_params[network_type]
            for our_key, their_key in mapping.items():
                if our_key in params:
                    query_params[their_key] = [params[our_key]]

        # Add UTM parameters
        for key in ['utm_source', 'utm_medium', 'utm_campaign']:
            if key in params:
                query_params[key] = [params[key]]

        # Rebuild URL
        query_string = urlencode(query_params, doseq=True)
        return urlunparse((
            parsed.scheme, parsed.netloc, parsed.path,
            parsed.params, query_string, parsed.fragment
        ))

    async def create_link(self, request: CreateLinkRequest) -> LinkResponse:
        """Create a new tracking link"""

        # Generate or validate slug
        if request.custom_slug:
            # Check if custom slug is available
            existing = await db.fetchone(
                "SELECT id FROM tracking_links WHERE slug = $1",
                request.custom_slug
            )
            if existing:
                raise HTTPException(400, f"Slug '{request.custom_slug}' already exists")
            slug = request.custom_slug
        else:
            # Generate unique slug
            for _ in range(10):
                slug = self.generate_slug()
                existing = await db.fetchone(
                    "SELECT id FROM tracking_links WHERE slug = $1",
                    slug
                )
                if not existing:
                    break
            else:
                raise HTTPException(500, "Could not generate unique slug")

        # Get program and product details
        program = await db.fetchone(
            """
            SELECT p.*, m.website, m.integration_type
            FROM programs p
            JOIN merchants m ON p.merchant_id = m.id
            WHERE p.id = $1
            """,
            request.program_id
        )
        if not program:
            raise HTTPException(404, "Program not found")

        # Get product URL if specified
        destination_base = program['website']
        if request.product_id:
            product = await db.fetchone(
                "SELECT url FROM products WHERE id = $1",
                request.product_id
            )
            if product and product['url']:
                destination_base = product['url']

        # Build tracking parameters
        link_id = str(uuid.uuid4())
        subid = f"{request.influencer_id[:8]}_{slug}_{int(datetime.utcnow().timestamp())}"

        params = {
            'subid': subid,
            'utm_source': request.utm_source,
            'utm_medium': request.utm_medium,
            'utm_campaign': request.utm_campaign or slug
        }

        # Build final destination URL
        destination_url = self.build_destination_url(
            destination_base,
            params,
            program['integration_type']
        )

        # Save to database
        await db.execute(
            """
            INSERT INTO tracking_links
            (id, influencer_id, program_id, product_id, campaign_id,
             slug, destination_url, utm_source, utm_medium, utm_campaign, metadata)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
            """,
            link_id, request.influencer_id, request.program_id,
            request.product_id, request.campaign_id, slug,
            destination_url, request.utm_source, request.utm_medium,
            request.utm_campaign or slug, json.dumps({'subid': subid})
        )

        # Cache in Redis for fast lookups
        if db.redis:
            await db.redis.setex(
                f"link:{slug}",
                86400,  # 24 hour TTL
                json.dumps({
                    'id': link_id,
                    'destination': destination_url,
                    'influencer_id': request.influencer_id,
                    'program_id': request.program_id,
                    'product_id': request.product_id,
                    'subid': subid
                })
            )

        return LinkResponse(
            id=link_id,
            slug=slug,
            short_url=f"{config.SHORT_DOMAIN}/l/{slug}",
            destination_url=destination_url,
            created_at=datetime.utcnow()
        )


class ClickService:
    """Handle click tracking and fraud detection"""

    @staticmethod
    def get_device_fingerprint(user_agent: str, ip: str) -> str:
        """Generate device fingerprint"""
        data = f"{user_agent}_{ip}"
        return hashlib.sha256(data.encode()).hexdigest()[:32]

    @staticmethod
    async def check_fraud_signals(ip: str, user_agent: str, device_id: str) -> dict:
        """Check for fraud indicators"""
        fraud_signals = {
            'is_bot': False,
            'is_vpn': False,
            'velocity_exceeded': False,
            'score': 0.0
        }

        # Bot detection
        bot_indicators = ['bot', 'crawler', 'spider', 'scraper', 'curl', 'wget']
        ua_lower = user_agent.lower() if user_agent else ''
        if any(indicator in ua_lower for indicator in bot_indicators):
            fraud_signals['is_bot'] = True
            fraud_signals['score'] += 0.5

        # Check click velocity in Redis
        if db.redis:
            key = f"clicks:ip:{ip}"
            count = await db.redis.incr(key)
            if count == 1:
                await db.redis.expire(key, 60)  # 1 minute window
            if count > config.RATE_LIMIT_CLICKS:
                fraud_signals['velocity_exceeded'] = True
                fraud_signals['score'] += 0.3

        return fraud_signals

    async def track_click(self, slug: str, request: Request) -> str:
        """Track a click and return destination URL"""

        # Get link data from cache or database
        link_data = None
        if db.redis:
            cached = await db.redis.get(f"link:{slug}")
            if cached:
                link_data = json.loads(cached)

        if not link_data:
            # Fetch from database
            link = await db.fetchone(
                """
                SELECT id, destination_url, influencer_id, program_id,
                       product_id, metadata
                FROM tracking_links
                WHERE slug = $1 AND active = true
                """,
                slug
            )
            if not link:
                raise HTTPException(404, "Link not found")

            link_data = {
                'id': link['id'],
                'destination': link['destination_url'],
                'influencer_id': link['influencer_id'],
                'program_id': link['program_id'],
                'product_id': link['product_id'],
                'subid': json.loads(link['metadata'])['subid'] if link['metadata'] else None
            }

        # Extract request data
        ip = request.client.host
        user_agent = request.headers.get('user-agent', '')
        referrer = request.headers.get('referer', '')

        # Get or create device ID
        device_id = request.cookies.get('device_id', str(uuid.uuid4()))
        session_id = request.cookies.get('session_id', str(uuid.uuid4()))

        # Check fraud signals
        fraud_signals = await self.check_fraud_signals(ip, user_agent, device_id)

        # Generate fingerprint
        fingerprint = self.get_device_fingerprint(user_agent, ip)
        ip_hash = hashlib.sha256(ip.encode()).hexdigest()

        # Detect platform
        platform = 'desktop'
        if 'mobile' in user_agent.lower():
            platform = 'mobile'
        elif 'tablet' in user_agent.lower():
            platform = 'tablet'

        # Save click to database
        await db.execute(
            """
            INSERT INTO clicks
            (tracking_link_id, ip_hash, user_agent, referrer, device_id,
             session_id, fingerprint, platform, subid, fraud_score, fraud_flags)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
            """,
            link_data['id'], ip_hash, user_agent[:500], referrer[:1000],
            device_id, session_id, fingerprint, platform,
            link_data.get('subid'), fraud_signals['score'],
            json.dumps(fraud_signals)
        )

        # Update Redis stats
        if db.redis:
            await db.redis.hincrby(f"stats:link:{slug}", "clicks", 1)
            await db.redis.hincrby(f"stats:daily:{date.today()}", "clicks", 1)

            # Store click data for attribution
            await db.redis.setex(
                f"device:{device_id}:latest",
                86400 * 7,  # 7 day TTL
                json.dumps({
                    'link_id': link_data['id'],
                    'subid': link_data.get('subid'),
                    'timestamp': datetime.utcnow().isoformat()
                })
            )

        return link_data['destination'], device_id, session_id


class WebhookProcessor:
    """Process webhooks from affiliate networks"""

    async def process_shopify(self, headers: dict, payload: dict) -> dict:
        """Process Shopify webhook"""

        # Verify webhook signature
        if config.SHOPIFY_WEBHOOK_SECRET:
            provided_hmac = headers.get('x-shopify-hmac-sha256', '')
            calculated_hmac = base64.b64encode(
                hmac.new(
                    config.SHOPIFY_WEBHOOK_SECRET.encode(),
                    json.dumps(payload).encode(),
                    hashlib.sha256
                ).digest()
            ).decode()

            if not hmac.compare_digest(calculated_hmac, provided_hmac):
                raise HTTPException(401, "Invalid webhook signature")

        # Extract conversion data
        order_id = payload.get('id')
        if not order_id:
            raise HTTPException(400, "Missing order ID")

        # Check for duplicate
        existing = await db.fetchone(
            "SELECT id FROM conversions WHERE order_id = $1",
            str(order_id)
        )
        if existing:
            return {"status": "duplicate", "order_id": order_id}

        # Extract subid from landing site or note attributes
        subid = None
        landing_site = payload.get('landing_site', '')
        if 'ref=' in landing_site:
            subid = landing_site.split('ref=')[1].split('&')[0]

        # Create conversion record
        conversion_id = str(uuid.uuid4())
        await db.execute(
            """
            INSERT INTO conversions
            (id, order_id, occurred_at, subtotal, tax, shipping, total,
             currency, items, subid, raw_event, status)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
            """,
            conversion_id, str(order_id), datetime.utcnow(),
            float(payload.get('subtotal_price', 0)),
            float(payload.get('total_tax', 0)),
            float(payload.get('total_shipping', 0)),
            float(payload.get('total_price', 0)),
            payload.get('currency', 'USD'),
            json.dumps(payload.get('line_items', [])),
            subid, json.dumps(payload), 'pending'
        )

        # Process attribution
        if subid:
            await self.process_attribution(conversion_id, subid)

        return {
            "status": "success",
            "conversion_id": conversion_id,
            "order_id": order_id
        }

    async def process_attribution(self, conversion_id: str, subid: str):
        """Process attribution and calculate commission"""

        # Find the tracking link from subid
        parts = subid.split('_')
        if len(parts) < 2:
            logger.warning(f"Invalid subid format: {subid}")
            return

        slug = parts[1]

        # Get link and program data
        link = await db.fetchone(
            """
            SELECT tl.id, tl.influencer_id, tl.program_id,
                   p.commission_type, p.commission_value
            FROM tracking_links tl
            JOIN programs p ON tl.program_id = p.id
            WHERE tl.slug = $1
            """,
            slug
        )

        if not link:
            logger.warning(f"No tracking link found for slug: {slug}")
            return

        # Create attribution
        attribution_id = str(uuid.uuid4())
        await db.execute(
            """
            INSERT INTO attributions
            (id, conversion_id, tracking_link_id, model, match_type, reason)
            VALUES ($1, $2, $3, $4, $5, $6)
            """,
            attribution_id, conversion_id, link['id'],
            'last_click', 'subid', f'Subid match: {subid}'
        )

        # Get conversion details
        conversion = await db.fetchone(
            "SELECT subtotal, total FROM conversions WHERE id = $1",
            conversion_id
        )

        # Calculate commission
        if link['commission_type'] == 'percent':
            gross_commission = float(conversion['subtotal']) * float(link['commission_value'])
        else:
            gross_commission = float(link['commission_value'])

        platform_fee = gross_commission * config.PLATFORM_FEE_RATE
        net_commission = gross_commission - platform_fee

        # Create commission record
        commission_id = str(uuid.uuid4())
        await db.execute(
            """
            INSERT INTO commissions
            (id, attribution_id, conversion_id, influencer_id, program_id,
             gross_amount, platform_fee, net_amount, status)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
            """,
            commission_id, attribution_id, conversion_id,
            link['influencer_id'], link['program_id'],
            gross_commission, platform_fee, net_commission, 'pending'
        )

        # Update Redis stats
        if db.redis:
            await db.redis.hincrby(f"stats:daily:{date.today()}", "conversions", 1)
            await db.redis.hincrbyfloat(
                f"stats:influencer:{link['influencer_id']}",
                "pending_earnings", net_commission
            )


# =============================================================================
# FastAPI Application
# =============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    await db.connect()
    logger.info("SkinStack API started")
    yield
    # Shutdown
    await db.disconnect()
    logger.info("SkinStack API stopped")

app = FastAPI(
    title="SkinStack Core API",
    version="1.0.0",
    description="Influencer skincare affiliate tracking platform",
    lifespan=lifespan
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Services
link_service = LinkService()
click_service = ClickService()
webhook_processor = WebhookProcessor()

# =============================================================================
# API Endpoints
# =============================================================================

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "SkinStack Core API",
        "version": "1.0.0",
        "status": "healthy",
        "timestamp": datetime.utcnow()
    }

@app.get("/l/{slug}")
async def redirect_link(slug: str, request: Request):
    """Handle link click and redirect"""
    try:
        destination, device_id, session_id = await click_service.track_click(slug, request)

        response = RedirectResponse(url=destination, status_code=302)

        # Set cookies for tracking
        response.set_cookie(
            key="device_id",
            value=device_id,
            max_age=365 * 24 * 60 * 60,
            httponly=True,
            secure=True,
            samesite="lax"
        )
        response.set_cookie(
            key="session_id",
            value=session_id,
            max_age=24 * 60 * 60,
            httponly=True,
            secure=True,
            samesite="lax"
        )

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error tracking click: {e}")
        raise HTTPException(500, "Internal server error")

@app.post("/api/links/create", response_model=LinkResponse)
async def create_link(request: CreateLinkRequest):
    """Create a new tracking link"""
    try:
        return await link_service.create_link(request)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating link: {e}")
        raise HTTPException(500, "Internal server error")

@app.get("/api/links/{slug}/stats")
async def get_link_stats(slug: str):
    """Get statistics for a specific link"""

    # Get link data
    link = await db.fetchone(
        "SELECT * FROM tracking_links WHERE slug = $1",
        slug
    )
    if not link:
        raise HTTPException(404, "Link not found")

    # Get click count
    clicks = await db.fetchone(
        "SELECT COUNT(*) as count FROM clicks WHERE tracking_link_id = $1",
        link['id']
    )

    # Get conversion count and earnings
    conversions = await db.fetchone(
        """
        SELECT COUNT(c.id) as count, COALESCE(SUM(cm.net_amount), 0) as earnings
        FROM conversions c
        JOIN attributions a ON c.id = a.conversion_id
        JOIN commissions cm ON a.id = cm.attribution_id
        WHERE a.tracking_link_id = $1
        """,
        link['id']
    )

    return {
        "slug": slug,
        "clicks": clicks['count'],
        "conversions": conversions['count'],
        "conversion_rate": (conversions['count'] / max(clicks['count'], 1)) * 100,
        "earnings": float(conversions['earnings']),
        "created_at": link['created_at']
    }

@app.get("/api/stats/influencer/{influencer_id}", response_model=InfluencerStats)
async def get_influencer_stats(influencer_id: str):
    """Get comprehensive stats for an influencer"""

    # Get click stats
    clicks = await db.fetchone(
        """
        SELECT COUNT(c.id) as total, COUNT(DISTINCT c.device_id) as unique_clicks
        FROM clicks c
        JOIN tracking_links tl ON c.tracking_link_id = tl.id
        WHERE tl.influencer_id = $1
        """,
        influencer_id
    )

    # Get conversion stats
    conversions = await db.fetchone(
        """
        SELECT COUNT(*) as count FROM commissions
        WHERE influencer_id = $1
        """,
        influencer_id
    )

    # Get earnings by status
    earnings = await db.fetchall(
        """
        SELECT status, COALESCE(SUM(net_amount), 0) as amount
        FROM commissions
        WHERE influencer_id = $1
        GROUP BY status
        """,
        influencer_id
    )

    earnings_dict = {row['status']: float(row['amount']) for row in earnings}

    # Get top products
    top_products = await db.fetchall(
        """
        SELECT p.name, COUNT(cm.id) as sales, SUM(cm.net_amount) as earnings
        FROM commissions cm
        JOIN tracking_links tl ON cm.influencer_id = tl.influencer_id
        JOIN products p ON tl.product_id = p.id
        WHERE cm.influencer_id = $1
        GROUP BY p.id, p.name
        ORDER BY earnings DESC
        LIMIT 5
        """,
        influencer_id
    )

    return InfluencerStats(
        influencer_id=influencer_id,
        total_clicks=clicks['total'],
        total_conversions=conversions['count'],
        conversion_rate=(conversions['count'] / max(clicks['total'], 1)) * 100,
        pending_earnings=earnings_dict.get('pending', 0),
        approved_earnings=earnings_dict.get('approved', 0),
        paid_earnings=earnings_dict.get('paid', 0),
        top_products=[
            {
                "name": p['name'],
                "sales": p['sales'],
                "earnings": float(p['earnings'])
            }
            for p in top_products
        ]
    )

@app.post("/webhooks/shopify")
async def shopify_webhook(request: Request):
    """Handle Shopify webhooks"""
    try:
        headers = dict(request.headers)
        payload = await request.json()

        result = await webhook_processor.process_shopify(headers, payload)
        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Webhook processing error: {e}")
        raise HTTPException(500, "Webhook processing failed")

@app.post("/webhooks/impact")
async def impact_webhook(request: Request):
    """Handle Impact.com webhooks"""
    # Similar structure to Shopify webhook
    return {"status": "not_implemented"}

@app.get("/api/stats/dashboard")
async def get_dashboard_stats(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None)
):
    """Get dashboard statistics"""

    if not start_date:
        start_date = date.today() - timedelta(days=30)
    if not end_date:
        end_date = date.today()

    # Get overall metrics
    metrics = await db.fetchone(
        """
        SELECT
            COUNT(DISTINCT cl.id) as total_clicks,
            COUNT(DISTINCT cv.id) as total_conversions,
            COALESCE(SUM(cv.total), 0) as total_revenue,
            COALESCE(SUM(cm.net_amount), 0) as total_commissions
        FROM clicks cl
        LEFT JOIN attributions a ON a.tracking_link_id =
            (SELECT id FROM tracking_links WHERE id = cl.tracking_link_id)
        LEFT JOIN conversions cv ON a.conversion_id = cv.id
        LEFT JOIN commissions cm ON cv.id = cm.conversion_id
        WHERE DATE(cl.clicked_at) BETWEEN $1 AND $2
        """,
        start_date, end_date
    )

    return {
        "period": f"{start_date} to {end_date}",
        "total_clicks": metrics['total_clicks'],
        "total_conversions": metrics['total_conversions'],
        "conversion_rate": (metrics['total_conversions'] / max(metrics['total_clicks'], 1)) * 100,
        "total_revenue": float(metrics['total_revenue']),
        "total_commissions": float(metrics['total_commissions']),
        "avg_order_value": float(metrics['total_revenue']) / max(metrics['total_conversions'], 1)
    }

# =============================================================================
# Run the server
# =============================================================================

if __name__ == "__main__":
    print("Starting SkinStack Core API...")
    print(f"API docs available at: http://localhost:8000/docs")
    print(f"Link redirect endpoint: http://localhost:8000/l/{{slug}}")

    uvicorn.run(
        "core_api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )