#!/usr/bin/env python3
"""
Check data types of primary keys in tables
"""
import asyncio
import asyncpg
from lib.settings import settings

async def check_types():
    conn = await asyncpg.connect(str(settings.database_url))

    try:
        # Check tracking_links id type
        result = await conn.fetchrow("""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_name = 'tracking_links'
            AND column_name = 'id'
        """)

        print(f"tracking_links.id type: {result['data_type']}")

    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(check_types())