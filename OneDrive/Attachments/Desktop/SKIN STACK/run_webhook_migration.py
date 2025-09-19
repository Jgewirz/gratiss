#!/usr/bin/env python3
"""Run webhook idempotency migration"""
import asyncio
import asyncpg

DATABASE_URL = "postgresql://neondb_owner:npg_QlUFO3LdE5zn@ep-orange-night-admridz5-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require"

async def run_migration():
    conn = await asyncpg.connect(DATABASE_URL)

    try:
        # Create schema_migrations table if it doesn't exist
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS schema_migrations (
                version INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                applied_at TIMESTAMPTZ DEFAULT NOW()
            )
        """)
        print("[OK] Schema migrations table ready")

        # Run webhook idempotency migration
        with open('sql/migrations/002_webhook_idempotency.sql', 'r') as f:
            migration = f.read()

        await conn.execute(migration)
        print("[OK] Webhook idempotency migration completed")

        # Verify tables
        tables = await conn.fetch("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            AND table_name IN ('webhook_events', 'schema_migrations')
        """)

        for table in tables:
            print(f"[OK] Table exists: {table['table_name']}")

        # Verify indexes
        indexes = await conn.fetch("""
            SELECT indexname
            FROM pg_indexes
            WHERE tablename = 'webhook_events'
        """)

        print(f"[OK] Created {len(indexes)} indexes on webhook_events")

    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(run_migration())