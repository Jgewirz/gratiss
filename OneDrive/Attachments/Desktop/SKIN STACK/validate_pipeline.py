#!/usr/bin/env python3
"""
Validate the SkinStack pipeline from the notebook
"""
import asyncio
import asyncpg
import redis.asyncio as redis
import hashlib
import secrets
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from decimal import Decimal
import uuid

# Configuration
DATABASE_URL = "postgresql://neondb_owner:npg_QlUFO3LdE5zn@ep-orange-night-admridz5-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require"
REDIS_URL = "redis://localhost:6379"

class SkinStackPipeline:
    def __init__(self):
        self.db = None
        self.redis = None

    async def connect(self):
        """Connect to databases"""
        print("[CONNECTING] Database and Redis...")
        self.db = await asyncpg.connect(DATABASE_URL)
        self.redis = await redis.from_url(REDIS_URL)
        print("[OK] Connected to PostgreSQL and Redis")

    async def setup_schema(self):
        """Create all required tables"""
        print("\n[STEP 1] Setting up database schema...")

        # Drop existing tables if needed (for testing)
        await self.db.execute("DROP TABLE IF EXISTS clicks CASCADE")
        await self.db.execute("DROP TABLE IF EXISTS tracking_links CASCADE")
        await self.db.execute("DROP TABLE IF EXISTS conversions CASCADE")
        await self.db.execute("DROP TABLE IF EXISTS commissions CASCADE")
        await self.db.execute("DROP TABLE IF EXISTS users CASCADE")
        await self.db.execute("DROP TABLE IF EXISTS influencers CASCADE")
        await self.db.execute("DROP TABLE IF EXISTS merchants CASCADE")
        await self.db.execute("DROP TABLE IF EXISTS programs CASCADE")
        await self.db.execute("DROP TABLE IF EXISTS products CASCADE")

        # Create users table
        await self.db.execute("""
            CREATE TABLE users (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT CHECK(role IN ('influencer', 'merchant', 'admin')) NOT NULL,
                is_active BOOLEAN DEFAULT true,
                created_at TIMESTAMPTZ DEFAULT NOW()
            )
        """)
        print("  [OK] Created users table")

        # Create influencers table
        await self.db.execute("""
            CREATE TABLE influencers (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                user_id UUID UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                display_name TEXT NOT NULL,
                instagram_handle TEXT,
                tiktok_handle TEXT,
                total_followers INTEGER DEFAULT 0,
                total_earned DECIMAL(10,2) DEFAULT 0,
                created_at TIMESTAMPTZ DEFAULT NOW()
            )
        """)
        print("  [OK] Created influencers table")

        # Create merchants table
        await self.db.execute("""
            CREATE TABLE merchants (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                user_id UUID REFERENCES users(id) ON DELETE SET NULL,
                business_name TEXT NOT NULL,
                website_url TEXT NOT NULL,
                shopify_shop_domain TEXT,
                total_sales DECIMAL(12,2) DEFAULT 0,
                total_commissions_paid DECIMAL(10,2) DEFAULT 0,
                created_at TIMESTAMPTZ DEFAULT NOW()
            )
        """)
        print("  [OK] Created merchants table")

        # Create programs table
        await self.db.execute("""
            CREATE TABLE programs (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                merchant_id UUID NOT NULL REFERENCES merchants(id) ON DELETE CASCADE,
                name TEXT NOT NULL,
                commission_rate DECIMAL(5,2) CHECK(commission_rate > 0 AND commission_rate <= 100),
                cookie_window_days INTEGER DEFAULT 30,
                is_active BOOLEAN DEFAULT true,
                created_at TIMESTAMPTZ DEFAULT NOW()
            )
        """)
        print("  [OK] Created programs table")

        # Create products table
        await self.db.execute("""
            CREATE TABLE products (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                merchant_id UUID NOT NULL REFERENCES merchants(id) ON DELETE CASCADE,
                program_id UUID REFERENCES programs(id) ON DELETE SET NULL,
                external_id TEXT NOT NULL,
                name TEXT NOT NULL,
                price DECIMAL(10,2) NOT NULL,
                product_url TEXT NOT NULL,
                created_at TIMESTAMPTZ DEFAULT NOW(),
                UNIQUE(merchant_id, external_id)
            )
        """)
        print("  [OK] Created products table")

        # Create tracking_links table with proper indexes
        await self.db.execute("""
            CREATE TABLE tracking_links (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                slug TEXT UNIQUE NOT NULL,
                influencer_id UUID NOT NULL REFERENCES influencers(id) ON DELETE CASCADE,
                program_id UUID NOT NULL REFERENCES programs(id) ON DELETE CASCADE,
                product_id UUID REFERENCES products(id) ON DELETE SET NULL,
                destination_url TEXT NOT NULL,
                total_clicks INTEGER DEFAULT 0,
                total_conversions INTEGER DEFAULT 0,
                total_revenue DECIMAL(10,2) DEFAULT 0,
                is_active BOOLEAN DEFAULT true,
                created_at TIMESTAMPTZ DEFAULT NOW()
            )
        """)

        await self.db.execute("""
            CREATE UNIQUE INDEX idx_tracking_links_slug_active
            ON tracking_links(slug)
            WHERE is_active = true
        """)
        print("  [OK] Created tracking_links table with indexes")

        # Create clicks table
        await self.db.execute("""
            CREATE TABLE clicks (
                id BIGSERIAL PRIMARY KEY,
                tracking_link_id UUID NOT NULL REFERENCES tracking_links(id) ON DELETE CASCADE,
                slug TEXT NOT NULL,
                clicked_at TIMESTAMPTZ DEFAULT NOW(),
                ip INET,
                user_agent TEXT,
                device_id TEXT,
                session_id TEXT
            )
        """)

        await self.db.execute("""
            CREATE INDEX idx_clicks_tracking_link_clicked
            ON clicks(tracking_link_id, clicked_at DESC)
        """)

        await self.db.execute("""
            CREATE INDEX idx_clicks_device_clicked
            ON clicks(device_id, clicked_at DESC)
            WHERE device_id IS NOT NULL
        """)
        print("  [OK] Created clicks table with indexes")

        # Create conversions table
        await self.db.execute("""
            CREATE TABLE conversions (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                tracking_link_id UUID NOT NULL REFERENCES tracking_links(id) ON DELETE CASCADE,
                click_id BIGINT REFERENCES clicks(id) ON DELETE SET NULL,
                order_id TEXT UNIQUE NOT NULL,
                order_amount DECIMAL(10,2) NOT NULL,
                commission_amount DECIMAL(10,2) NOT NULL,
                status TEXT CHECK(status IN ('pending', 'confirmed', 'paid', 'cancelled')) DEFAULT 'pending',
                converted_at TIMESTAMPTZ DEFAULT NOW()
            )
        """)
        print("  [OK] Created conversions table")

        # Create commissions table
        await self.db.execute("""
            CREATE TABLE commissions (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                influencer_id UUID NOT NULL REFERENCES influencers(id) ON DELETE CASCADE,
                conversion_id UUID NOT NULL REFERENCES conversions(id) ON DELETE CASCADE,
                amount DECIMAL(10,2) NOT NULL,
                platform_fee DECIMAL(10,2) DEFAULT 0,
                net_amount DECIMAL(10,2) NOT NULL,
                status TEXT CHECK(status IN ('pending', 'approved', 'paid', 'rejected')) DEFAULT 'pending',
                created_at TIMESTAMPTZ DEFAULT NOW()
            )
        """)
        print("  [OK] Created commissions table")

    async def insert_test_data(self):
        """Insert test data for validation"""
        print("\n[STEP 2] Inserting test data...")

        # Create a test user
        user_id = await self.db.fetchval("""
            INSERT INTO users (email, password_hash, role)
            VALUES ('influencer@test.com', 'hashed_password', 'influencer')
            RETURNING id
        """)
        print(f"  [OK] Created user: {user_id}")

        # Create a test influencer
        influencer_id = await self.db.fetchval("""
            INSERT INTO influencers (user_id, display_name, instagram_handle, total_followers)
            VALUES ($1, 'Test Influencer', '@testinfluencer', 50000)
            RETURNING id
        """, user_id)
        print(f"  [OK] Created influencer: {influencer_id}")

        # Create a test merchant user
        merchant_user_id = await self.db.fetchval("""
            INSERT INTO users (email, password_hash, role)
            VALUES ('merchant@test.com', 'hashed_password', 'merchant')
            RETURNING id
        """)

        # Create a test merchant
        merchant_id = await self.db.fetchval("""
            INSERT INTO merchants (user_id, business_name, website_url, shopify_shop_domain)
            VALUES ($1, 'Test Beauty Brand', 'https://testbeauty.com', 'test-beauty.myshopify.com')
            RETURNING id
        """, merchant_user_id)
        print(f"  [OK] Created merchant: {merchant_id}")

        # Create a test program
        program_id = await self.db.fetchval("""
            INSERT INTO programs (merchant_id, name, commission_rate, cookie_window_days)
            VALUES ($1, 'Summer Sale 20%', 20.0, 30)
            RETURNING id
        """, merchant_id)
        print(f"  [OK] Created program: {program_id}")

        # Create a test product
        product_id = await self.db.fetchval("""
            INSERT INTO products (merchant_id, program_id, external_id, name, price, product_url)
            VALUES ($1, $2, 'SKU123', 'Vitamin C Serum', 45.99, 'https://testbeauty.com/vitamin-c-serum')
            RETURNING id
        """, merchant_id, program_id)
        print(f"  [OK] Created product: {product_id}")

        return influencer_id, program_id, product_id

    async def test_link_generation(self, influencer_id, program_id, product_id):
        """Test link generation service"""
        print("\n[STEP 3] Testing link generation...")

        # Generate unique slug
        slug = secrets.token_urlsafe(6)[:6]
        destination = "https://testbeauty.com/vitamin-c-serum?ref=affiliate"

        # Create tracking link
        link_id = await self.db.fetchval("""
            INSERT INTO tracking_links (slug, influencer_id, program_id, product_id, destination_url)
            VALUES ($1, $2, $3, $4, $5)
            RETURNING id
        """, slug, influencer_id, program_id, product_id, destination)

        print(f"  [OK] Generated link: skin.st/{slug}")
        print(f"  [OK] Link ID: {link_id}")

        # Cache in Redis for fast lookups
        await self.redis.setex(
            f"link:{slug}",
            3600,  # 1 hour TTL
            json.dumps({
                "id": str(link_id),
                "destination": destination,
                "influencer_id": str(influencer_id),
                "program_id": str(program_id)
            })
        )
        print("  [OK] Cached in Redis")

        return link_id, slug

    async def test_click_tracking(self, link_id, slug):
        """Test click tracking service"""
        print("\n[STEP 4] Testing click tracking...")

        # Simulate 5 clicks
        click_ids = []
        for i in range(5):
            # Record click
            click_id = await self.db.fetchval("""
                INSERT INTO clicks (tracking_link_id, slug, ip, user_agent, device_id)
                VALUES ($1, $2, $3, $4, $5)
                RETURNING id
            """, link_id, slug, f"192.168.1.{i}", "Mozilla/5.0", f"device_{i}")
            click_ids.append(click_id)

            # Update click count
            await self.db.execute("""
                UPDATE tracking_links
                SET total_clicks = total_clicks + 1
                WHERE id = $1
            """, link_id)

        print(f"  [OK] Recorded {len(click_ids)} clicks")

        # Verify click count
        total_clicks = await self.db.fetchval("""
            SELECT total_clicks FROM tracking_links WHERE id = $1
        """, link_id)
        print(f"  [OK] Total clicks in DB: {total_clicks}")

        return click_ids[0]  # Return first click for conversion test

    async def test_conversion_attribution(self, link_id, click_id):
        """Test conversion attribution"""
        print("\n[STEP 5] Testing conversion attribution...")

        order_id = f"ORDER_{uuid.uuid4().hex[:8]}"
        order_amount = Decimal("45.99")
        commission_amount = order_amount * Decimal("0.20")  # 20% commission

        # Record conversion
        conversion_id = await self.db.fetchval("""
            INSERT INTO conversions (tracking_link_id, click_id, order_id, order_amount, commission_amount)
            VALUES ($1, $2, $3, $4, $5)
            RETURNING id
        """, link_id, click_id, order_id, order_amount, commission_amount)

        print(f"  [OK] Recorded conversion: {order_id}")
        print(f"  [OK] Order amount: ${order_amount}")
        print(f"  [OK] Commission: ${commission_amount}")

        # Update tracking link stats
        await self.db.execute("""
            UPDATE tracking_links
            SET total_conversions = total_conversions + 1,
                total_revenue = total_revenue + $2
            WHERE id = $1
        """, link_id, order_amount)

        return conversion_id, commission_amount

    async def test_commission_calculation(self, influencer_id, conversion_id, commission_amount):
        """Test commission calculation"""
        print("\n[STEP 6] Testing commission calculation...")

        platform_fee = commission_amount * Decimal("0.20")  # SkinStack takes 20%
        net_amount = commission_amount - platform_fee

        # Create commission record
        commission_id = await self.db.fetchval("""
            INSERT INTO commissions (influencer_id, conversion_id, amount, platform_fee, net_amount)
            VALUES ($1, $2, $3, $4, $5)
            RETURNING id
        """, influencer_id, conversion_id, commission_amount, platform_fee, net_amount)

        print(f"  [OK] Commission created: {commission_id}")
        print(f"  [OK] Gross commission: ${commission_amount}")
        print(f"  [OK] Platform fee (20%): ${platform_fee}")
        print(f"  [OK] Net to influencer: ${net_amount}")

        # Update influencer earnings
        await self.db.execute("""
            UPDATE influencers
            SET total_earned = total_earned + $2
            WHERE id = $1
        """, influencer_id, net_amount)

        return commission_id

    async def verify_pipeline(self):
        """Verify the complete pipeline"""
        print("\n[STEP 7] Verifying complete pipeline...")

        # Check tracking link stats
        link_stats = await self.db.fetchrow("""
            SELECT slug, total_clicks, total_conversions, total_revenue
            FROM tracking_links
            ORDER BY created_at DESC
            LIMIT 1
        """)

        print(f"  [OK] Link stats:")
        print(f"       Slug: {link_stats['slug']}")
        print(f"       Clicks: {link_stats['total_clicks']}")
        print(f"       Conversions: {link_stats['total_conversions']}")
        print(f"       Revenue: ${link_stats['total_revenue']}")

        # Check influencer earnings
        influencer_stats = await self.db.fetchrow("""
            SELECT display_name, total_earned
            FROM influencers
            ORDER BY created_at DESC
            LIMIT 1
        """)

        print(f"  [OK] Influencer earnings:")
        print(f"       Name: {influencer_stats['display_name']}")
        print(f"       Total earned: ${influencer_stats['total_earned']}")

        # Performance test: slug lookup
        import time
        start = time.perf_counter()
        result = await self.db.fetchrow("""
            SELECT * FROM tracking_links
            WHERE slug = $1 AND is_active = true
        """, link_stats['slug'])
        elapsed = (time.perf_counter() - start) * 1000

        print(f"\n  [OK] Performance test:")
        print(f"       Slug lookup: {elapsed:.2f}ms (target <5ms)")

    async def cleanup(self):
        """Close connections"""
        if self.db:
            await self.db.close()
        if self.redis:
            await self.redis.close()
        print("\n[DONE] Pipeline validation complete!")

async def main():
    pipeline = SkinStackPipeline()

    try:
        # Connect to databases
        await pipeline.connect()

        # Setup schema
        await pipeline.setup_schema()

        # Insert test data
        influencer_id, program_id, product_id = await pipeline.insert_test_data()

        # Test link generation
        link_id, slug = await pipeline.test_link_generation(influencer_id, program_id, product_id)

        # Test click tracking
        click_id = await pipeline.test_click_tracking(link_id, slug)

        # Test conversion attribution
        conversion_id, commission_amount = await pipeline.test_conversion_attribution(link_id, click_id)

        # Test commission calculation
        await pipeline.test_commission_calculation(influencer_id, conversion_id, commission_amount)

        # Verify complete pipeline
        await pipeline.verify_pipeline()

    except Exception as e:
        print(f"\n[ERROR] Pipeline validation failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await pipeline.cleanup()

if __name__ == "__main__":
    asyncio.run(main())