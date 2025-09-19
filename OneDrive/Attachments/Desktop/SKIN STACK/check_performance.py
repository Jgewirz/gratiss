#!/usr/bin/env python3
"""Check performance of slug lookup query"""
import asyncio
import asyncpg
import time

DATABASE_URL = "postgresql://neondb_owner:npg_QlUFO3LdE5zn@ep-orange-night-admridz5-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require"

async def check_performance():
    conn = await asyncpg.connect(DATABASE_URL)

    try:
        # Get a slug to test with
        slug = await conn.fetchval("SELECT slug FROM tracking_links LIMIT 1")
        if not slug:
            print("[ERROR] No tracking links found")
            return

        print(f"[INFO] Testing with slug: {slug}")

        # Run EXPLAIN ANALYZE
        print("\n[EXPLAIN ANALYZE]")
        plan = await conn.fetch("""
            EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
            SELECT * FROM tracking_links
            WHERE slug = $1 AND is_active = true
        """, slug)

        for row in plan:
            print(row[0])

        # Measure query performance (10 runs)
        print("\n[PERFORMANCE TEST] Running 10 queries...")
        times = []
        for _ in range(10):
            start = time.perf_counter()
            result = await conn.fetchrow("""
                SELECT * FROM tracking_links
                WHERE slug = $1 AND is_active = true
            """, slug)
            elapsed_ms = (time.perf_counter() - start) * 1000
            times.append(elapsed_ms)

        times.sort()
        print(f"  Min: {times[0]:.2f}ms")
        print(f"  p50: {times[5]:.2f}ms")
        print(f"  p95: {times[9]:.2f}ms")
        print(f"  Max: {times[-1]:.2f}ms")

        # Test with prepared statement
        print("\n[PREPARED STATEMENT TEST]")
        stmt = await conn.prepare("""
            SELECT * FROM tracking_links
            WHERE slug = $1 AND is_active = true
        """)

        prep_times = []
        for _ in range(10):
            start = time.perf_counter()
            result = await stmt.fetchrow(slug)
            elapsed_ms = (time.perf_counter() - start) * 1000
            prep_times.append(elapsed_ms)

        prep_times.sort()
        print(f"  Min: {prep_times[0]:.2f}ms")
        print(f"  p50: {prep_times[5]:.2f}ms")
        print(f"  p95: {prep_times[9]:.2f}ms")
        print(f"  Max: {prep_times[-1]:.2f}ms")

    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(check_performance())