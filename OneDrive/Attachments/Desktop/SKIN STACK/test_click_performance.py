#!/usr/bin/env python3
"""Quick performance test for clicks table"""
import asyncio
import asyncpg
import time
from lib.settings import settings

async def test_performance():
    conn = await asyncpg.connect(str(settings.database_url))

    try:
        # Insert a test tracking link
        slug = f"test_{int(time.time())}"
        link_id = await conn.fetchval("""
            INSERT INTO tracking_links (slug, destination_url)
            VALUES ($1, $2)
            RETURNING id
        """, slug, "https://example.com/product")

        print(f"[OK] Created test link with slug: {slug}")

        # Test 1: Slug lookup performance
        print("\n[TEST] Slug lookup performance (100 queries)...")
        times = []
        for _ in range(100):
            start = time.perf_counter()
            result = await conn.fetchrow(
                "SELECT * FROM tracking_links WHERE slug = $1 AND is_active = true",
                slug
            )
            times.append((time.perf_counter() - start) * 1000)

        times.sort()
        p50 = times[50]
        p95 = times[95]
        print(f"  p50: {p50:.2f}ms (target <5ms) {'PASS' if p50 < 5 else 'FAIL'}")
        print(f"  p95: {p95:.2f}ms (target <10ms) {'PASS' if p95 < 10 else 'FAIL'}")

        # Test 2: Click insert performance
        print("\n[TEST] Click insert performance (100 inserts)...")
        times = []
        for i in range(100):
            start = time.perf_counter()
            await conn.execute("""
                INSERT INTO clicks (tracking_link_id, slug, ip, user_agent, device_id)
                VALUES ($1, $2, $3, $4, $5)
            """, link_id, slug, f"192.168.1.{i}", "Mozilla/5.0", f"device_{i}")
            times.append((time.perf_counter() - start) * 1000)

        times.sort()
        p50 = times[50]
        p95 = times[95]
        print(f"  p50: {p50:.2f}ms (target <2ms) {'PASS' if p50 < 2 else 'FAIL'}")
        print(f"  p95: {p95:.2f}ms (target <5ms) {'PASS' if p95 < 5 else 'FAIL'}")

        # Test 3: EXPLAIN ANALYZE
        print("\n[TEST] Query plan analysis...")
        plan = await conn.fetch("""
            EXPLAIN (ANALYZE, BUFFERS)
            SELECT * FROM tracking_links
            WHERE slug = $1 AND is_active = true
        """, slug)

        for row in plan:
            line = row[0]
            if 'Index Scan' in line:
                print(f"  [OK] Using index scan: {line[:60]}...")
            elif 'Seq Scan' in line:
                print(f"  [WARN] Sequential scan detected!")
            elif 'Execution Time' in line:
                print(f"  {line}")

    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(test_performance())