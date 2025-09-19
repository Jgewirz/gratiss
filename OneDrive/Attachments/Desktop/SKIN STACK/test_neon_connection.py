#!/usr/bin/env python3
"""Test Neon PostgreSQL database connection"""

import os
import asyncio
import asyncpg
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_connection():
    """Test connection to Neon PostgreSQL"""

    # Get connection details from environment
    DATABASE_URL = os.getenv('DATABASE_URL')

    if not DATABASE_URL:
        print("[ERROR] DATABASE_URL not found in .env file")
        return False

    print(f"[INFO] Connecting to Neon database...")
    print(f"[INFO] URL: {DATABASE_URL[:30]}...")  # Show partial URL for security

    try:
        # Connect to the database
        conn = await asyncpg.connect(DATABASE_URL)

        print("[OK] Successfully connected to Neon PostgreSQL!")

        # Test a simple query
        version = await conn.fetchval('SELECT version()')
        print(f"[INFO] PostgreSQL version: {version[:50]}...")

        # Check if we can create tables
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS test_connection (
                id SERIAL PRIMARY KEY,
                message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        print("[OK] Can create tables")

        # Insert test data
        await conn.execute(
            'INSERT INTO test_connection (message) VALUES ($1)',
            'SkinStack connection test successful'
        )
        print("[OK] Can insert data")

        # Query test data
        row = await conn.fetchrow('SELECT * FROM test_connection ORDER BY id DESC LIMIT 1')
        print(f"[OK] Can query data: {row['message']}")

        # Clean up
        await conn.execute('DROP TABLE test_connection')
        print("[OK] Cleaned up test table")

        # Close connection
        await conn.close()
        print("[OK] Connection closed properly")

        return True

    except Exception as e:
        print(f"[ERROR] Failed to connect to Neon database: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_connection())
    if success:
        print("\n[SUCCESS] Neon PostgreSQL is ready for SkinStack!")
    else:
        print("\n[FAILED] Please check your database configuration")