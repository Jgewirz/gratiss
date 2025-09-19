#!/usr/bin/env python3
"""Test connection to new database"""
import asyncio
import asyncpg

async def test_connection():
    try:
        conn = await asyncpg.connect(
            'postgresql://neondb_owner:npg_QlUFO3LdE5zn@ep-orange-night-admridz5-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require'
        )
        print("[OK] Connected to new database successfully!")

        # Check if tables exist
        tables = await conn.fetch("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)

        if tables:
            print(f"[INFO] Found {len(tables)} tables:")
            for table in tables:
                print(f"  - {table['table_name']}")
        else:
            print("[INFO] No tables found - database is empty")

        await conn.close()

    except Exception as e:
        print(f"[ERROR] Failed to connect: {e}")

if __name__ == "__main__":
    asyncio.run(test_connection())