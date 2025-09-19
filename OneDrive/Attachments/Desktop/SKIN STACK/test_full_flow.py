#!/usr/bin/env python3
"""
Test the full link creation → redirect → click tracking flow
"""
import asyncio
import httpx
import json
from datetime import datetime
import asyncpg
from lib.settings import settings
from lib.redis_client import redis_client

async def setup_test_data():
    """Create test merchant, program, and influencer"""
    conn = await asyncpg.connect(str(settings.database_url))

    try:
        # Try to get existing or create new user
        user_id = await conn.fetchval("""
            SELECT id FROM users WHERE email = 'merchant@skinglow.com'
        """)

        if not user_id:
            user_id = await conn.fetchval("""
                INSERT INTO users (email, password_hash, role, is_active, created_at)
                VALUES ('merchant@skinglow.com', 'hashed_password_here', 'merchant', true, NOW())
                RETURNING id
            """)

        # Try to get existing or create new merchant
        merchant_id = await conn.fetchval("""
            SELECT id FROM merchants WHERE user_id = $1
        """, user_id)

        if not merchant_id:
            merchant_id = await conn.fetchval("""
                INSERT INTO merchants (user_id, business_name, website_url, created_at)
                VALUES ($1, 'SkinGlow Co', 'https://skinglow.com', NOW())
                RETURNING id
            """, user_id)
        print(f"[OK] Merchant created: ID {merchant_id}")

        # Create test program
        program_id = await conn.fetchval("""
            INSERT INTO programs (
                merchant_id, name, commission_rate, cookie_window_days,
                is_active, created_at
            )
            VALUES ($1, 'Summer Sale 2025', 0.15, 30, true, NOW())
            ON CONFLICT DO NOTHING
            RETURNING id
        """, merchant_id)

        # If conflict, get existing program
        if not program_id:
            program_id = await conn.fetchval("""
                SELECT id FROM programs
                WHERE merchant_id = $1 AND name = 'Summer Sale 2025'
            """, merchant_id)
        print(f"[OK] Program created: ID {program_id}")

        # Try to get existing or create new influencer user
        influencer_user_id = await conn.fetchval("""
            SELECT id FROM users WHERE email = 'beauty@example.com'
        """)

        if not influencer_user_id:
            influencer_user_id = await conn.fetchval("""
                INSERT INTO users (email, password_hash, role, is_active, created_at)
                VALUES ('beauty@example.com', 'hashed_password_here', 'influencer', true, NOW())
                RETURNING id
            """)

        # Try to get existing or create new influencer
        influencer_id = await conn.fetchval("""
            SELECT id FROM influencers WHERE user_id = $1
        """, influencer_user_id)

        if not influencer_id:
            influencer_id = await conn.fetchval("""
                INSERT INTO influencers (
                    user_id, display_name, instagram_handle,
                    total_followers, created_at
                )
                VALUES ($1, 'Beauty Queen', '@beautyqueen', 50000, NOW())
                RETURNING id
            """, influencer_user_id)
        print(f"[OK] Influencer created: ID {influencer_id}")

    finally:
        await conn.close()

    return merchant_id, program_id, influencer_id


async def test_link_creation(program_id, influencer_id):
    """Test creating a tracking link via API"""
    print("\n[TEST] Creating tracking link...")

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8001/api/links/create",
            json={
                "destination_url": "https://skinglow.com/products/vitamin-c-serum",
                "influencer_id": str(influencer_id),  # Convert UUID to string
                "program_id": str(program_id),  # Convert UUID to string
                "campaign_name": "Summer Glow Campaign",
                "utm_source": "instagram",
                "utm_medium": "social",
                "utm_campaign": "summer2025"
            }
        )

        if response.status_code == 200:
            link_data = response.json()
            print(f"[OK] Link created!")
            print(f"  - ID: {link_data['id']}")
            print(f"  - Slug: {link_data['slug']}")
            print(f"  - Short URL: {link_data['short_url']}")
            print(f"  - Destination: {link_data['destination_url']}")
            return link_data
        else:
            print(f"[ERROR] Failed to create link: {response.status_code}")
            print(response.text)
            return None


async def test_redis_cache(slug):
    """Verify link is cached in Redis"""
    print(f"\n[TEST] Checking Redis cache for slug: {slug}")

    # Connect to Redis if not connected
    if not redis_client.connected:
        await redis_client.connect()

    cache_key = f"link:{slug}"
    cached_data = await redis_client.get(cache_key)

    if cached_data:
        print(f"[OK] Link found in Redis cache!")
        print(f"  - Cache data: {json.dumps(cached_data, indent=2)}")
        return True
    else:
        print(f"[WARNING] Link not found in cache")
        return False


async def test_redirect_and_click(slug):
    """Test the redirect endpoint and click tracking"""
    print(f"\n[TEST] Testing redirect for slug: {slug}")

    async with httpx.AsyncClient(follow_redirects=False) as client:
        # Test redirect
        response = await client.get(
            f"http://localhost:8001/l/{slug}",
            headers={
                "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X)",
                "Referer": "https://instagram.com/beautyqueen"
            }
        )

        if response.status_code == 302:
            print(f"[OK] Redirect successful!")
            print(f"  - Status: {response.status_code}")
            print(f"  - Location: {response.headers.get('Location')}")
            print(f"  - Cache Status: {response.headers.get('X-Cache-Status')}")
            print(f"  - Processing Time: {response.headers.get('X-Processing-Time-Ms')}ms")

            # Check if cookie was set
            if 'Set-Cookie' in response.headers:
                print(f"  - Cookie set: Yes")

            return True
        else:
            print(f"[ERROR] Redirect failed: {response.status_code}")
            return False


async def verify_click_recorded(slug):
    """Verify click was recorded in database"""
    print(f"\n[TEST] Verifying click was recorded for slug: {slug}")

    conn = await asyncpg.connect(str(settings.database_url))

    try:
        # Get click count
        result = await conn.fetchrow("""
            SELECT
                tl.id,
                tl.total_clicks,
                COUNT(c.id) as actual_clicks
            FROM tracking_links tl
            LEFT JOIN clicks c ON c.tracking_link_id = tl.id
            WHERE tl.slug = $1
            GROUP BY tl.id
        """, slug)

        if result:
            print(f"[OK] Click tracking verified!")
            print(f"  - Link ID: {result['id']}")
            print(f"  - Total clicks counter: {result['total_clicks']}")
            print(f"  - Actual click records: {result['actual_clicks']}")
            return True
        else:
            print(f"[ERROR] Link not found in database")
            return False

    finally:
        await conn.close()


async def test_link_stats(slug):
    """Test the stats endpoint"""
    print(f"\n[TEST] Getting stats for slug: {slug}")

    async with httpx.AsyncClient() as client:
        response = await client.get(f"http://localhost:8001/api/links/{slug}/stats")

        if response.status_code == 200:
            stats = response.json()
            print(f"[OK] Stats retrieved!")
            print(f"  - Total clicks: {stats['stats']['total_clicks']}")
            print(f"  - Unique visitors: {stats['stats']['unique_visitors']}")
            print(f"  - Conversions: {stats['stats']['conversions']}")
            print(f"  - Conversion rate: {stats['stats']['conversion_rate']:.2f}%")
            return True
        else:
            print(f"[ERROR] Failed to get stats: {response.status_code}")
            return False


async def main():
    """Run the complete end-to-end test"""
    print("=" * 60)
    print("SKINSTACK END-TO-END TEST")
    print("=" * 60)

    # Setup test data
    merchant_id, program_id, influencer_id = await setup_test_data()

    # Test link creation
    link_data = await test_link_creation(program_id, influencer_id)
    if not link_data:
        print("[FAIL] Could not create link. Exiting.")
        return

    slug = link_data['slug']

    # Wait a moment for async operations
    await asyncio.sleep(0.5)

    # Test Redis cache
    cache_ok = await test_redis_cache(slug)

    # Test redirect and click tracking
    redirect_ok = await test_redirect_and_click(slug)

    # Wait for async click recording
    await asyncio.sleep(0.5)

    # Verify click was recorded
    click_ok = await verify_click_recorded(slug)

    # Test stats endpoint
    stats_ok = await test_link_stats(slug)

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"  Link Creation: {'PASS' if link_data else 'FAIL'}")
    print(f"  Redis Cache: {'PASS' if cache_ok else 'FAIL'}")
    print(f"  Redirect: {'PASS' if redirect_ok else 'FAIL'}")
    print(f"  Click Tracking: {'PASS' if click_ok else 'FAIL'}")
    print(f"  Stats API: {'PASS' if stats_ok else 'FAIL'}")

    all_passed = all([link_data, cache_ok, redirect_ok, click_ok, stats_ok])

    print("\n" + "=" * 60)
    if all_passed:
        print("[SUCCESS] ALL TESTS PASSED!")
    else:
        print("[PARTIAL] Some tests failed. Check output above.")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())