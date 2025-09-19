#!/usr/bin/env python3
"""Run SQL migrations"""
import asyncio
import asyncpg
from lib.settings import settings

async def run_migration():
    """Execute migration 001_clicks.sql"""

    # Connect to database
    conn = await asyncpg.connect(str(settings.database_url))

    print("[INFO] Running migration 001_clicks.sql...")

    try:
        # Read migration file
        with open('sql/migrations/001_clicks.sql', 'r') as f:
            migration_sql = f.read()

        # Execute migration
        await conn.execute(migration_sql)

        print("[OK] Migration completed successfully!")

        # Verify tables exist
        tables = await conn.fetch("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            AND table_name IN ('tracking_links', 'clicks')
        """)

        for table in tables:
            print(f"[OK] Table created: {table['table_name']}")

        # Check indexes
        indexes = await conn.fetch("""
            SELECT indexname
            FROM pg_indexes
            WHERE tablename IN ('tracking_links', 'clicks')
        """)

        print(f"[OK] Created {len(indexes)} indexes")

    except Exception as e:
        print(f"[ERROR] Migration failed: {e}")
        raise
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(run_migration())