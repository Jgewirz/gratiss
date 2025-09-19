#!/usr/bin/env python3
"""Run all SQL migrations in order (idempotent)"""
import asyncio
import asyncpg
import hashlib
from pathlib import Path
from lib.settings import settings

async def run_all_migrations():
    """Execute all migrations (idempotent with checksums)"""

    # Connect to database
    conn = await asyncpg.connect(str(settings.database_url))

    try:
        # Ensure schema_migrations table exists (from base migration)
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS schema_migrations (
                version INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                checksum TEXT,
                applied_at TIMESTAMPTZ DEFAULT NOW()
            )
        """)

        # Add checksum column if it doesn't exist (for existing tables)
        await conn.execute("""
            ALTER TABLE schema_migrations
            ADD COLUMN IF NOT EXISTS checksum TEXT
        """)

        # Get already applied migrations
        applied = await conn.fetch("""
            SELECT version,
                   COALESCE(checksum, '') as checksum
            FROM schema_migrations
        """)
        applied_versions = {row['version']: row['checksum'] for row in applied}

        # Get all migration files
        migrations_dir = Path('sql/migrations')
        migration_files = sorted(migrations_dir.glob('*.sql'))

        for migration_file in migration_files:
            # Extract version from filename (e.g., 001_clicks.sql -> 1)
            version = int(migration_file.name.split('_')[0])
            name = migration_file.stem

            # Calculate checksum
            with open(migration_file, 'rb') as f:
                content = f.read()
                checksum = hashlib.sha256(content).hexdigest()

            # Skip if already applied with same checksum
            if version in applied_versions:
                if applied_versions[version] == checksum:
                    print(f"[SKIP] Migration {name} already applied")
                    continue
                else:
                    print(f"[INFO] Migration {name} has changed, re-applying...")

            print(f"[INFO] Running migration {migration_file.name}...")

            # Execute migration in transaction
            async with conn.transaction():
                with open(migration_file, 'r') as f:
                    sql = f.read()
                    # Execute migration
                    await conn.execute(sql)

                # Record migration
                await conn.execute("""
                    INSERT INTO schema_migrations (version, name, checksum)
                    VALUES ($1, $2, $3)
                    ON CONFLICT (version)
                    DO UPDATE SET checksum = $3, applied_at = NOW()
                """, version, name, checksum)

            print(f"[OK] {name} migration completed")

        # Verify tables
        tables = await conn.fetch("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)

        print("\n[OK] Tables created:")
        for table in tables:
            print(f"  - {table['table_name']}")

        # Check indexes on clicks table
        indexes = await conn.fetch("""
            SELECT indexname
            FROM pg_indexes
            WHERE tablename = 'clicks'
        """)

        print(f"\n[OK] Indexes on clicks table:")
        for idx in indexes:
            print(f"  - {idx['indexname']}")

    except Exception as e:
        print(f"[ERROR] Migration failed: {e}")
        raise
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(run_all_migrations())