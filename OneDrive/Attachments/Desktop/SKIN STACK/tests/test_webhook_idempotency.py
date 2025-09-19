"""Test webhook idempotency for Refersion webhooks"""
import pytest
import asyncio
import asyncpg
from decimal import Decimal
import json
import time

DATABASE_URL = "postgresql://neondb_owner:npg_QlUFO3LdE5zn@ep-orange-night-admridz5-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require"

@pytest.fixture
async def db_conn():
    """Database connection fixture"""
    conn = await asyncpg.connect(DATABASE_URL)
    yield conn
    await conn.close()

@pytest.mark.asyncio
async def test_webhook_idempotency(db_conn):
    """Test that duplicate webhooks don't create duplicate conversions"""

    # Create test data
    external_event_id = f"test_evt_{int(time.time())}"

    # First webhook call - should create conversion
    result1 = await db_conn.fetchrow("""
        SELECT * FROM process_webhook_idempotently(
            $1, $2, $3, $4
        )
    """,
        "refersion",
        external_event_id,
        "sale",
        json.dumps({
            "order_id": "TEST_ORDER_001",
            "commission_amount": "15.00",
            "sale_amount": "75.00"
        })
    )

    assert result1['is_duplicate'] == False
    assert result1['webhook_event_id'] is not None
    webhook_id_1 = result1['webhook_event_id']

    # Second webhook call with SAME event_id - should be duplicate
    result2 = await db_conn.fetchrow("""
        SELECT * FROM process_webhook_idempotently(
            $1, $2, $3, $4
        )
    """,
        "refersion",
        external_event_id,  # Same event ID
        "sale",
        json.dumps({
            "order_id": "TEST_ORDER_001",
            "commission_amount": "15.00",
            "sale_amount": "75.00"
        })
    )

    assert result2['is_duplicate'] == True
    assert result2['webhook_event_id'] == webhook_id_1  # Same webhook event

    # Verify only ONE webhook_event exists
    count = await db_conn.fetchval("""
        SELECT COUNT(*)
        FROM webhook_events
        WHERE external_event_id = $1
    """, external_event_id)

    assert count == 1, f"Expected 1 webhook event, got {count}"

    print(f"[PASS] Idempotency test passed: duplicate event rejected")

@pytest.mark.asyncio
async def test_different_event_ids_create_separate_records(db_conn):
    """Test that different event IDs create separate records"""

    # Two different event IDs
    event_id_1 = f"test_evt_A_{int(time.time())}"
    event_id_2 = f"test_evt_B_{int(time.time())}"

    # First webhook
    result1 = await db_conn.fetchrow("""
        SELECT * FROM process_webhook_idempotently($1, $2, $3, $4)
    """, "refersion", event_id_1, "sale", json.dumps({"order_id": "ORDER_A"}))

    # Second webhook with different event_id
    result2 = await db_conn.fetchrow("""
        SELECT * FROM process_webhook_idempotently($1, $2, $3, $4)
    """, "refersion", event_id_2, "sale", json.dumps({"order_id": "ORDER_B"}))

    assert result1['is_duplicate'] == False
    assert result2['is_duplicate'] == False
    assert result1['webhook_event_id'] != result2['webhook_event_id']

    # Verify two separate records exist
    count = await db_conn.fetchval("""
        SELECT COUNT(*)
        FROM webhook_events
        WHERE external_event_id IN ($1, $2)
    """, event_id_1, event_id_2)

    assert count == 2, f"Expected 2 webhook events, got {count}"

    print(f"[PASS] Different event IDs create separate records")

@pytest.mark.asyncio
async def test_idempotency_across_sources(db_conn):
    """Test that same event_id can exist for different sources"""

    event_id = f"shared_evt_{int(time.time())}"

    # Same event_id for refersion
    result1 = await db_conn.fetchrow("""
        SELECT * FROM process_webhook_idempotently($1, $2, $3, $4)
    """, "refersion", event_id, "sale", json.dumps({"source": "refersion"}))

    # Same event_id for shopify (different source)
    result2 = await db_conn.fetchrow("""
        SELECT * FROM process_webhook_idempotently($1, $2, $3, $4)
    """, "shopify", event_id, "order", json.dumps({"source": "shopify"}))

    assert result1['is_duplicate'] == False
    assert result2['is_duplicate'] == False
    assert result1['webhook_event_id'] != result2['webhook_event_id']

    # Verify both records exist
    count = await db_conn.fetchval("""
        SELECT COUNT(*)
        FROM webhook_events
        WHERE external_event_id = $1
    """, event_id)

    assert count == 2, f"Expected 2 webhook events (different sources), got {count}"

    print(f"[PASS] Same event_id allowed for different sources")

async def main():
    """Run all tests and display results"""
    conn = await asyncpg.connect(DATABASE_URL)

    try:
        print("\n" + "="*60)
        print("WEBHOOK IDEMPOTENCY TESTS")
        print("="*60)

        # Run migration first
        print("\n[INFO] Running migration...")
        with open('sql/migrations/002_webhook_idempotency.sql', 'r') as f:
            migration_sql = f.read()

        # Check if migration already ran
        try:
            await conn.execute(migration_sql)
            print("[OK] Migration completed")
        except asyncpg.UniqueViolationError:
            print("[OK] Migration already exists")
        except asyncpg.DuplicateTableError:
            print("[OK] Tables already exist")

        # Test 1: Basic idempotency
        print("\n[TEST 1] Basic Idempotency")
        await test_webhook_idempotency(conn)

        # Test 2: Different event IDs
        print("\n[TEST 2] Different Event IDs")
        await test_different_event_ids_create_separate_records(conn)

        # Test 3: Cross-source idempotency
        print("\n[TEST 3] Cross-Source Idempotency")
        await test_idempotency_across_sources(conn)

        # Performance test
        print("\n[PERFORMANCE] Testing upsert performance...")
        event_id = f"perf_test_{int(time.time())}"

        times = []
        for i in range(10):
            start = time.perf_counter()
            await conn.fetchrow("""
                SELECT * FROM process_webhook_idempotently($1, $2, $3, $4)
            """, "refersion", f"{event_id}_{i}", "sale", json.dumps({"test": i}))
            elapsed = (time.perf_counter() - start) * 1000
            times.append(elapsed)

        times.sort()
        print(f"  Insert p50: {times[5]:.2f}ms")
        print(f"  Insert p95: {times[9]:.2f}ms")

        # Test duplicate performance
        dup_times = []
        for _ in range(10):
            start = time.perf_counter()
            await conn.fetchrow("""
                SELECT * FROM process_webhook_idempotently($1, $2, $3, $4)
            """, "refersion", event_id, "sale", json.dumps({"duplicate": True}))
            elapsed = (time.perf_counter() - start) * 1000
            dup_times.append(elapsed)

        dup_times.sort()
        print(f"  Duplicate check p50: {dup_times[5]:.2f}ms")
        print(f"  Duplicate check p95: {dup_times[9]:.2f}ms")

        print("\n" + "="*60)
        print("ALL TESTS PASSED!")
        print("="*60)

    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(main())