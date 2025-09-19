"""
Database module - PostgreSQL connection pooling
Following STEP 0 rules: minimal, < 50 LOC
"""
import asyncpg
from contextlib import asynccontextmanager
from lib.settings import settings


class Database:
    """Database connection pool manager"""

    def __init__(self):
        self.pool = None

    async def connect(self):
        """Create connection pool"""
        self.pool = await asyncpg.create_pool(
            str(settings.database_url),
            min_size=5,
            max_size=20,
            command_timeout=60
        )

    async def disconnect(self):
        """Close connection pool"""
        if self.pool:
            await self.pool.close()

    @asynccontextmanager
    async def acquire(self):
        """Acquire connection from pool"""
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                yield conn

    async def health_check(self) -> bool:
        """Test database connectivity"""
        try:
            async with self.pool.acquire() as conn:
                result = await conn.fetchval("SELECT 1")
                return result == 1
        except Exception:
            return False

    async def get_connection(self):
        """Get a connection from the pool (with short timeout for reads)"""
        return await self.pool.acquire(timeout=5.0)

    async def release_connection(self, conn):
        """Release connection back to pool"""
        await self.pool.release(conn)


db = Database()