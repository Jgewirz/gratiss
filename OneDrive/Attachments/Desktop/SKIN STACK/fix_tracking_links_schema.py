#!/usr/bin/env python3
"""
Fix tracking_links table schema to add missing UTM columns
"""
import asyncio
import asyncpg
from lib.settings import settings

async def fix_tracking_links_schema():
    """Add missing UTM columns to tracking_links table"""
    conn = await asyncpg.connect(str(settings.database_url))

    try:
        print("[INFO] Checking and fixing tracking_links table schema...")

        # Get current columns
        columns = await conn.fetch("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = 'tracking_links'
            AND table_schema = 'public'
        """)

        existing_columns = {row['column_name'] for row in columns}
        print(f"[INFO] Existing columns: {existing_columns}")

        # Define required columns with their types
        required_columns = {
            'utm_source': 'TEXT',
            'utm_medium': 'TEXT',
            'utm_campaign': 'TEXT'
        }

        # Check and add missing columns
        for column, dtype in required_columns.items():
            if column not in existing_columns:
                print(f"[ADD] Adding column '{column}' ({dtype})...")
                try:
                    await conn.execute(f"""
                        ALTER TABLE tracking_links
                        ADD COLUMN IF NOT EXISTS {column} {dtype}
                    """)
                    print(f"  [OK] Column '{column}' added successfully")
                except Exception as e:
                    print(f"  [ERROR] Failed to add column '{column}': {e}")
            else:
                print(f"[OK] Column '{column}' already exists")

        # Verify final schema
        print("\n[INFO] Verifying final schema...")
        final_columns = await conn.fetch("""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_name = 'tracking_links'
            AND table_schema = 'public'
            ORDER BY ordinal_position
        """)

        print("[OK] Final tracking_links table schema:")
        for col in final_columns:
            print(f"    - {col['column_name']}: {col['data_type']}")

        # Check if we have all required columns
        final_column_names = {row['column_name'] for row in final_columns}
        missing = set(required_columns.keys()) - final_column_names
        if missing:
            print(f"\n[WARNING] Still missing columns: {missing}")
            return False
        else:
            print("\n[SUCCESS] All required UTM columns are present!")
            return True

    except Exception as e:
        print(f"[ERROR] Failed to fix schema: {e}")
        return False
    finally:
        await conn.close()

if __name__ == "__main__":
    result = asyncio.run(fix_tracking_links_schema())
    exit(0 if result else 1)