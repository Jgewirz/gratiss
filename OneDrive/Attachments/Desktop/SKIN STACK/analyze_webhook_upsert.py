#!/usr/bin/env python3
"""EXPLAIN ANALYZE for webhook upsert path"""
import asyncio
import asyncpg
import json

DATABASE_URL = "postgresql://neondb_owner:npg_QlUFO3LdE5zn@ep-orange-night-admridz5-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require"

async def analyze_upsert_performance():
    conn = await asyncpg.connect(DATABASE_URL)

    try:
        print("="*70)
        print("EXPLAIN ANALYZE: Webhook Idempotency Upsert Path")
        print("="*70)

        # Test event ID
        test_event_id = "analyze_test_001"

        # 1. ANALYZE INSERT (new event)
        print("\n[1] INSERT PATH (New Event)")
        print("-" * 40)

        # First, ensure the event doesn't exist
        await conn.execute("""
            DELETE FROM webhook_events
            WHERE source = 'refersion' AND external_event_id = $1
        """, test_event_id)

        insert_plan = await conn.fetch("""
            EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
            INSERT INTO webhook_events (source, external_event_id, event_type, payload)
            VALUES ('refersion', $1, 'sale', $2::jsonb)
            ON CONFLICT (source, external_event_id) DO NOTHING
            RETURNING id
        """, test_event_id, json.dumps({"test": "data"}))

        for row in insert_plan:
            print(row[0])

        # 2. ANALYZE DUPLICATE CHECK (event exists)
        print("\n[2] DUPLICATE CHECK PATH (Event Exists)")
        print("-" * 40)

        duplicate_plan = await conn.fetch("""
            EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
            INSERT INTO webhook_events (source, external_event_id, event_type, payload)
            VALUES ('refersion', $1, 'sale', $2::jsonb)
            ON CONFLICT (source, external_event_id) DO NOTHING
            RETURNING id
        """, test_event_id, json.dumps({"test": "duplicate"}))

        for row in duplicate_plan:
            print(row[0])

        # 3. ANALYZE SELECT AFTER CONFLICT
        print("\n[3] SELECT PATH (Retrieve Existing on Conflict)")
        print("-" * 40)

        select_plan = await conn.fetch("""
            EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
            SELECT id, conversion_id
            FROM webhook_events
            WHERE source = 'refersion'
            AND external_event_id = $1
        """, test_event_id)

        for row in select_plan:
            print(row[0])

        # 4. ANALYZE FUNCTION CALL
        print("\n[4] FUNCTION CALL (Complete Idempotent Process)")
        print("-" * 40)

        function_plan = await conn.fetch("""
            EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
            SELECT * FROM process_webhook_idempotently(
                'refersion', $1, 'sale', $2::jsonb
            )
        """, f"{test_event_id}_function", json.dumps({"test": "function"}))

        for row in function_plan:
            print(row[0])

        # 5. Show index details
        print("\n[5] INDEX INFORMATION")
        print("-" * 40)

        indexes = await conn.fetch("""
            SELECT
                indexname,
                indexdef,
                pg_size_pretty(pg_relation_size(indexname::regclass)) as size
            FROM pg_indexes
            WHERE tablename = 'webhook_events'
            ORDER BY indexname
        """)

        for idx in indexes:
            print(f"\n{idx['indexname']}:")
            print(f"  Definition: {idx['indexdef']}")
            print(f"  Size: {idx['size']}")

        # 6. Table statistics
        print("\n[6] TABLE STATISTICS")
        print("-" * 40)

        stats = await conn.fetchrow("""
            SELECT
                n_tup_ins as total_inserts,
                n_tup_upd as total_updates,
                n_tup_del as total_deletes,
                n_live_tup as live_tuples,
                n_dead_tup as dead_tuples,
                last_vacuum,
                last_autovacuum
            FROM pg_stat_user_tables
            WHERE relname = 'webhook_events'
        """)

        if stats:
            print(f"  Total Inserts: {stats['total_inserts']}")
            print(f"  Live Tuples: {stats['live_tuples']}")
            print(f"  Dead Tuples: {stats['dead_tuples']}")

        print("\n" + "="*70)

    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(analyze_upsert_performance())