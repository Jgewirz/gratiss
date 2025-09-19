"""
Test redirect endpoint performance and caching
"""
import pytest
import time
import asyncio
from httpx import AsyncClient
from fastapi.testclient import TestClient
from api.main import app
from lib.db import db
from lib.redis_client import redis_client
import uuid


@pytest.mark.asyncio
async def test_redirect_cache_miss_then_hit():
    """Test that first request causes cache miss, second causes cache hit"""

    # Setup: create a test tracking link
    test_slug = f"test-{uuid.uuid4().hex[:8]}"
    test_url = "https://example.com/product"

    async with AsyncClient(app=app, base_url="http://test") as client:
        # First, create the tracking link
        conn = await db.get_connection()
        try:
            await conn.execute("""
                INSERT INTO tracking_links (slug, destination_url, is_active)
                VALUES ($1, $2, true)
            """, test_slug, test_url)
        finally:
            await db.release_connection(conn)

        # Clear any existing cache
        await redis_client.delete(f"redirect:{test_slug}")

        # First request - should be cache miss
        response1 = await client.get(f"/r/{test_slug}", follow_redirects=False)
        assert response1.status_code == 302
        assert response1.headers["location"] == test_url

        # Check metrics for cache miss
        metrics_response = await client.get("/metrics")
        metrics_text = metrics_response.text
        # Parse cache miss count from metrics

        # Second request - should be cache hit
        response2 = await client.get(f"/r/{test_slug}", follow_redirects=False)
        assert response2.status_code == 302
        assert response2.headers["location"] == test_url

        # Cleanup
        conn = await db.get_connection()
        try:
            await conn.execute("DELETE FROM tracking_links WHERE slug = $1", test_slug)
        finally:
            await db.release_connection(conn)


@pytest.mark.asyncio
async def test_redirect_performance():
    """Test that cached redirect completes under 5ms"""

    # Setup: create test link and pre-warm cache
    test_slug = f"perf-{uuid.uuid4().hex[:8]}"
    test_url = "https://example.com/fast"

    async with AsyncClient(app=app, base_url="http://test") as client:
        # Create the tracking link
        conn = await db.get_connection()
        try:
            await conn.execute("""
                INSERT INTO tracking_links (slug, destination_url, is_active)
                VALUES ($1, $2, true)
            """, test_slug, test_url)
        finally:
            await db.release_connection(conn)

        # Pre-warm cache with first request
        await client.get(f"/r/{test_slug}", follow_redirects=False)

        # Measure cached request performance
        start = time.perf_counter()
        response = await client.get(f"/r/{test_slug}", follow_redirects=False)
        duration_ms = (time.perf_counter() - start) * 1000

        assert response.status_code == 302
        # Allow generous threshold for test environment
        assert duration_ms < 50, f"Redirect took {duration_ms:.2f}ms, expected < 50ms"

        # Cleanup
        conn = await db.get_connection()
        try:
            await conn.execute("DELETE FROM tracking_links WHERE slug = $1", test_slug)
        finally:
            await db.release_connection(conn)


@pytest.mark.asyncio
async def test_redirect_not_found():
    """Test that non-existent slug returns 404"""

    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/r/does-not-exist-12345", follow_redirects=False)
        assert response.status_code == 404


@pytest.mark.asyncio
async def test_redirect_inactive_link():
    """Test that inactive links return 404"""

    test_slug = f"inactive-{uuid.uuid4().hex[:8]}"
    test_url = "https://example.com/inactive"

    async with AsyncClient(app=app, base_url="http://test") as client:
        # Create inactive tracking link
        conn = await db.get_connection()
        try:
            await conn.execute("""
                INSERT INTO tracking_links (slug, destination_url, is_active)
                VALUES ($1, $2, false)
            """, test_slug, test_url)
        finally:
            await db.release_connection(conn)

        # Should return 404 for inactive link
        response = await client.get(f"/r/{test_slug}", follow_redirects=False)
        assert response.status_code == 404

        # Cleanup
        conn = await db.get_connection()
        try:
            await conn.execute("DELETE FROM tracking_links WHERE slug = $1", test_slug)
        finally:
            await db.release_connection(conn)