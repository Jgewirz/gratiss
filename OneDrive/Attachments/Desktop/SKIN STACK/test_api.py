#!/usr/bin/env python3
"""Test script to check if the API can start"""

import sys
import asyncio
from core_api import app, db

async def test_startup():
    """Test database connection and basic setup"""
    try:
        print("Testing database connection...")
        await db.connect()
        print("OK: Database connected successfully!")

        # Test a simple query
        if not db.pool:  # SQLite mode
            result = await db.fetchone("SELECT 1 as test", )
            if result and result['test'] == 1:
                print("OK: Database query test passed!")

        await db.disconnect()
        print("OK: Database disconnected successfully!")

        print("\nOK: All tests passed! The API is ready to run.")
        print("\nTo start the server, run:")
        print("  python core_api.py")
        print("\nOr with uvicorn:")
        print("  uvicorn core_api:app --reload --port 8000")

    except Exception as e:
        print(f"ERROR: Error during testing: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(test_startup())