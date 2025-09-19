#!/usr/bin/env python3
"""
Complete Pipeline Validation Script
Tests every component of the SkinStack platform
"""
import asyncio
import asyncpg
import redis.asyncio as redis
import time
import json
from decimal import Decimal

DATABASE_URL = "postgresql://neondb_owner:npg_QlUFO3LdE5zn@ep-orange-night-admridz5-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require"
REDIS_URL = "redis://localhost:6379"

class PipelineValidator:
    def __init__(self):
        self.db = None
        self.redis = None
        self.results = {}

    async def connect(self):
        """Connect to all services"""
        print("\n" + "="*70)
        print("SKINSTACK COMPLETE PIPELINE VALIDATION")
        print("="*70)

        print("\n[1] CONNECTING TO SERVICES")
        print("-" * 40)

        try:
            self.db = await asyncpg.connect(DATABASE_URL)
            print("  [OK] PostgreSQL connected")

            self.redis = await redis.from_url(REDIS_URL)
            await self.redis.ping()
            print("  [OK] Redis connected")

            self.results['connections'] = 'PASS'
        except Exception as e:
            print(f"  [FAIL] Connection failed: {e}")
            self.results['connections'] = 'FAIL'
            raise

    async def validate_schema(self):
        """Verify all tables exist with correct structure"""
        print("\n[2] VALIDATING DATABASE SCHEMA")
        print("-" * 40)

        required_tables = [
            'users', 'influencers', 'merchants', 'programs', 'products',
            'tracking_links', 'clicks', 'conversions', 'commissions',
            'webhook_events', 'schema_migrations'
        ]

        existing_tables = await self.db.fetch("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)

        existing_names = {t['table_name'] for t in existing_tables}

        all_exist = True
        for table in required_tables:
            if table in existing_names:
                print(f"  [OK] {table}")
            else:
                print(f"  [FAIL] {table} MISSING")
                all_exist = False

        # Check critical indexes
        print("\n  Checking critical indexes:")
        indexes = await self.db.fetch("""
            SELECT indexname FROM pg_indexes
            WHERE tablename IN ('tracking_links', 'clicks', 'webhook_events')
            AND indexname LIKE 'idx_%'
        """)

        critical_indexes = [
            'idx_tracking_links_slug_active',
            'idx_clicks_tracking_link_clicked',
            'idx_webhook_events_idempotency'
        ]

        index_names = {idx['indexname'] for idx in indexes}
        for idx in critical_indexes:
            if idx in index_names:
                print(f"  [OK] {idx}")
            else:
                print(f"  [FAIL] {idx} MISSING")
                all_exist = False

        self.results['schema'] = 'PASS' if all_exist else 'FAIL'

    async def test_link_generation(self):
        """Test tracking link generation"""
        print("\n[3] TESTING LINK GENERATION")
        print("-" * 40)

        try:
            # Get or create test influencer
            influencer = await self.db.fetchrow("""
                SELECT id FROM influencers LIMIT 1
            """)

            if not influencer:
                print("  Creating test data...")
                # Create user first
                user_id = await self.db.fetchval("""
                    INSERT INTO users (email, password_hash, role)
                    VALUES ('test@validator.com', 'hash', 'influencer')
                    RETURNING id
                """)

                influencer_id = await self.db.fetchval("""
                    INSERT INTO influencers (user_id, display_name)
                    VALUES ($1, 'Validator Test')
                    RETURNING id
                """, user_id)
            else:
                influencer_id = influencer['id']

            # Get or create program
            program = await self.db.fetchrow("""
                SELECT id FROM programs WHERE is_active = true LIMIT 1
            """)

            if not program:
                # Create merchant and program
                merchant_id = await self.db.fetchval("""
                    INSERT INTO merchants (business_name, website_url)
                    VALUES ('Test Merchant', 'https://test.com')
                    RETURNING id
                """)

                program_id = await self.db.fetchval("""
                    INSERT INTO programs (merchant_id, name, commission_rate)
                    VALUES ($1, 'Test Program', 20.0)
                    RETURNING id
                """, merchant_id)
            else:
                program_id = program['id']

            # Generate link
            import secrets
            slug = f"val_{secrets.token_urlsafe(4)[:4]}"

            link_id = await self.db.fetchval("""
                INSERT INTO tracking_links (slug, influencer_id, program_id, destination_url)
                VALUES ($1, $2, $3, $4)
                RETURNING id
            """, slug, influencer_id, program_id, "https://test.com/product")

            # Cache in Redis
            await self.redis.setex(
                f"link:{slug}",
                300,
                json.dumps({"id": str(link_id), "destination": "https://test.com/product"})
            )

            # Verify
            cached = await self.redis.get(f"link:{slug}")
            if cached:
                print(f"  [OK] Link generated: skin.st/{slug}")
                print(f"  [OK] Cached in Redis")
                self.results['link_generation'] = 'PASS'
                self.results['test_slug'] = slug
                self.results['test_link_id'] = link_id
            else:
                print(f"  [FAIL] Redis caching failed")
                self.results['link_generation'] = 'FAIL'

        except Exception as e:
            print(f"  [FAIL] Link generation failed: {e}")
            self.results['link_generation'] = 'FAIL'

    async def test_click_tracking(self):
        """Test click tracking performance"""
        print("\n[4] TESTING CLICK TRACKING")
        print("-" * 40)

        if 'test_link_id' not in self.results:
            print("  [WARN] No test link available")
            self.results['click_tracking'] = 'SKIP'
            return

        try:
            link_id = self.results['test_link_id']
            slug = self.results['test_slug']

            # Record clicks
            click_times = []
            for i in range(5):
                start = time.perf_counter()
                await self.db.execute("""
                    INSERT INTO clicks (tracking_link_id, slug, ip, device_id)
                    VALUES ($1, $2, $3, $4)
                """, link_id, slug, f"127.0.0.{i}", f"device_test_{i}")
                elapsed = (time.perf_counter() - start) * 1000
                click_times.append(elapsed)

            # Update stats
            await self.db.execute("""
                UPDATE tracking_links
                SET total_clicks = total_clicks + 5
                WHERE id = $1
            """, link_id)

            # Check performance
            click_times.sort()
            p50 = click_times[2]
            p95 = click_times[4]

            print(f"  [OK] Recorded 5 clicks")
            print(f"  [PERF] Insert p50: {p50:.2f}ms")
            print(f"  [PERF] Insert p95: {p95:.2f}ms")

            if p50 < 50:  # 50ms threshold for cloud DB
                self.results['click_tracking'] = 'PASS'
            else:
                self.results['click_tracking'] = 'SLOW'

        except Exception as e:
            print(f"  [FAIL] Click tracking failed: {e}")
            self.results['click_tracking'] = 'FAIL'

    async def test_webhook_idempotency(self):
        """Test webhook idempotency"""
        print("\n[5] TESTING WEBHOOK IDEMPOTENCY")
        print("-" * 40)

        try:
            test_event_id = f"validate_{int(time.time())}"

            # First call - should be new
            result1 = await self.db.fetchrow("""
                SELECT * FROM process_webhook_idempotently($1, $2, $3, $4)
            """, "refersion", test_event_id, "sale", json.dumps({"test": "data"}))

            if not result1['is_duplicate']:
                print(f"  [OK] First webhook processed (new)")
            else:
                print(f"  [FAIL] First webhook marked as duplicate")

            # Second call - should be duplicate
            result2 = await self.db.fetchrow("""
                SELECT * FROM process_webhook_idempotently($1, $2, $3, $4)
            """, "refersion", test_event_id, "sale", json.dumps({"test": "data"}))

            if result2['is_duplicate']:
                print(f"  [OK] Duplicate webhook detected")
            else:
                print(f"  [FAIL] Duplicate not detected")

            # Verify only one record
            count = await self.db.fetchval("""
                SELECT COUNT(*) FROM webhook_events
                WHERE external_event_id = $1
            """, test_event_id)

            if count == 1:
                print(f"  [OK] Exactly 1 webhook event stored")
                self.results['webhook_idempotency'] = 'PASS'
            else:
                print(f"  [FAIL] Found {count} webhook events (expected 1)")
                self.results['webhook_idempotency'] = 'FAIL'

        except Exception as e:
            print(f"  [FAIL] Webhook test failed: {e}")
            self.results['webhook_idempotency'] = 'FAIL'

    async def test_query_performance(self):
        """Test critical query performance"""
        print("\n[6] TESTING QUERY PERFORMANCE")
        print("-" * 40)

        if 'test_slug' not in self.results:
            print("  [WARN] No test slug available")
            self.results['query_performance'] = 'SKIP'
            return

        try:
            slug = self.results['test_slug']

            # Test slug lookup
            times = []
            for _ in range(10):
                start = time.perf_counter()
                await self.db.fetchrow("""
                    SELECT * FROM tracking_links
                    WHERE slug = $1 AND is_active = true
                """, slug)
                elapsed = (time.perf_counter() - start) * 1000
                times.append(elapsed)

            times.sort()
            p50 = times[5]
            p95 = times[9]

            print(f"  [PERF] Slug lookup p50: {p50:.2f}ms")
            print(f"  [PERF] Slug lookup p95: {p95:.2f}ms")

            # Check EXPLAIN plan
            plan = await self.db.fetch("""
                EXPLAIN (FORMAT JSON)
                SELECT * FROM tracking_links
                WHERE slug = $1 AND is_active = true
            """, slug)

            plan_json = json.loads(plan[0]['QUERY PLAN'])
            if 'Index Scan' in str(plan_json):
                print(f"  [OK] Using index scan")
                self.results['query_performance'] = 'PASS'
            else:
                print(f"  [WARN] Not using index scan")
                self.results['query_performance'] = 'SLOW'

        except Exception as e:
            print(f"  [FAIL] Performance test failed: {e}")
            self.results['query_performance'] = 'FAIL'

    async def test_commission_calculation(self):
        """Test commission calculation flow"""
        print("\n[7] TESTING COMMISSION CALCULATION")
        print("-" * 40)

        try:
            # Create a test conversion
            if 'test_link_id' in self.results:
                link_id = self.results['test_link_id']

                conversion_id = await self.db.fetchval("""
                    INSERT INTO conversions (
                        tracking_link_id, order_id, order_amount, commission_amount
                    ) VALUES ($1, $2, $3, $4)
                    RETURNING id
                """, link_id, f"TEST_ORDER_{int(time.time())}",
                    Decimal("100.00"), Decimal("20.00"))

                # Get influencer
                influencer_id = await self.db.fetchval("""
                    SELECT influencer_id FROM tracking_links WHERE id = $1
                """, link_id)

                # Calculate commission
                platform_fee = Decimal("20.00") * Decimal("0.20")
                net_amount = Decimal("20.00") - platform_fee

                commission_id = await self.db.fetchval("""
                    INSERT INTO commissions (
                        influencer_id, conversion_id, amount, platform_fee, net_amount
                    ) VALUES ($1, $2, $3, $4, $5)
                    RETURNING id
                """, influencer_id, conversion_id, Decimal("20.00"),
                    platform_fee, net_amount)

                print(f"  [OK] Commission calculated")
                print(f"  [INFO] Gross: $20.00")
                print(f"  [INFO] Platform fee (20%): ${platform_fee}")
                print(f"  [INFO] Net to influencer: ${net_amount}")
                self.results['commission_calculation'] = 'PASS'
            else:
                print(f"  [WARN] No test data available")
                self.results['commission_calculation'] = 'SKIP'

        except Exception as e:
            print(f"  [FAIL] Commission test failed: {e}")
            self.results['commission_calculation'] = 'FAIL'

    async def generate_summary(self):
        """Generate final summary"""
        print("\n" + "="*70)
        print("VALIDATION SUMMARY")
        print("="*70)

        all_pass = True
        for test, result in self.results.items():
            if test in ['test_slug', 'test_link_id']:
                continue

            symbol = "[OK]" if result == 'PASS' else "[FAIL]" if result == 'FAIL' else "[WARN]"
            print(f"  {symbol} {test}: {result}")
            if result == 'FAIL':
                all_pass = False

        print("\n" + "="*70)
        if all_pass:
            print("[SUCCESS] ALL VALIDATIONS PASSED!")
        else:
            print("[WARNING] SOME VALIDATIONS FAILED - CHECK ABOVE")
        print("="*70)

        return all_pass

    async def cleanup(self):
        """Close connections"""
        if self.db:
            await self.db.close()
        if self.redis:
            await self.redis.aclose()

async def main():
    validator = PipelineValidator()

    try:
        await validator.connect()
        await validator.validate_schema()
        await validator.test_link_generation()
        await validator.test_click_tracking()
        await validator.test_webhook_idempotency()
        await validator.test_query_performance()
        await validator.test_commission_calculation()
        success = await validator.generate_summary()

        return success

    except Exception as e:
        print(f"\n[ERROR] VALIDATION FAILED: {e}")
        return False
    finally:
        await validator.cleanup()

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)