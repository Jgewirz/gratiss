#!/usr/bin/env python3
"""
Fix clicks table schema to match the application code expectations
This script adds the missing columns to align with api/routes/redirects.py
"""
import asyncio
import asyncpg
from lib.settings import settings

async def fix_clicks_schema():
    """Add missing columns to clicks table"""
    conn = await asyncpg.connect(str(settings.database_url))

    try:
        print("[INFO] Checking and fixing clicks table schema...")

        # Get current columns
        columns = await conn.fetch("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = 'clicks'
            AND table_schema = 'public'
        """)

        existing_columns = {row['column_name'] for row in columns}
        print(f"[INFO] Existing columns: {existing_columns}")

        # Define required columns with their types
        required_columns = {
            'ip_hash': 'TEXT',
            'referer': 'TEXT',
            'device_type': 'TEXT',
            'browser': 'TEXT'
        }

        # Check and add missing columns
        for column, dtype in required_columns.items():
            if column not in existing_columns:
                print(f"[ADD] Adding column '{column}' ({dtype})...")
                try:
                    await conn.execute(f"""
                        ALTER TABLE clicks
                        ADD COLUMN IF NOT EXISTS {column} {dtype}
                    """)
                    print(f"  [OK] Column '{column}' added successfully")
                except Exception as e:
                    print(f"  [ERROR] Failed to add column '{column}': {e}")
            else:
                print(f"[OK] Column '{column}' already exists")

        # If 'referrer' exists but 'referer' doesn't, we might want to rename
        if 'referrer' in existing_columns and 'referer' not in existing_columns:
            print("[INFO] Column 'referrer' exists but 'referer' is expected")
            print("      Code expects 'referer' (single 'r'), migration has 'referrer'")
            # We'll handle this by adding 'referer' column since we can't rename in read-only
            try:
                await conn.execute("""
                    ALTER TABLE clicks
                    ADD COLUMN IF NOT EXISTS referer TEXT
                """)
                print("  [OK] Added 'referer' column")
            except Exception as e:
                print(f"  [ERROR] Failed to add 'referer' column: {e}")

        # If 'ip' exists but 'ip_hash' doesn't, add ip_hash
        if 'ip' in existing_columns and 'ip_hash' not in existing_columns:
            print("[INFO] Column 'ip' exists but 'ip_hash' is expected")
            try:
                await conn.execute("""
                    ALTER TABLE clicks
                    ADD COLUMN IF NOT EXISTS ip_hash TEXT
                """)
                print("  [OK] Added 'ip_hash' column")
            except Exception as e:
                print(f"  [ERROR] Failed to add 'ip_hash' column: {e}")

        # Verify final schema
        print("\n[INFO] Verifying final schema...")
        final_columns = await conn.fetch("""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_name = 'clicks'
            AND table_schema = 'public'
            ORDER BY ordinal_position
        """)

        print("[OK] Final clicks table schema:")
        for col in final_columns:
            print(f"    - {col['column_name']}: {col['data_type']}")

        # Check if we have all required columns
        final_column_names = {row['column_name'] for row in final_columns}
        missing = set(required_columns.keys()) - final_column_names
        if missing:
            print(f"\n[WARNING] Still missing columns: {missing}")
            return False
        else:
            print("\n[SUCCESS] All required columns are present!")
            return True

    except Exception as e:
        print(f"[ERROR] Failed to fix schema: {e}")
        return False
    finally:
        await conn.close()

if __name__ == "__main__":
    result = asyncio.run(fix_clicks_schema())
    exit(0 if result else 1)