"""Redis client module for caching and rate limiting"""
import redis.asyncio as redis
from typing import Optional, Any
import json
import logging
from lib.settings import settings

logger = logging.getLogger(__name__)

class RedisClient:
    """Async Redis client with connection pooling"""

    def __init__(self):
        self.redis: Optional[redis.Redis] = None
        self.connected = False

    async def connect(self):
        """Initialize Redis connection"""
        try:
            self.redis = redis.from_url(
                settings.redis_url,
                encoding="utf-8",
                decode_responses=True,
                socket_keepalive=True,
                socket_keepalive_options={
                    1: 1,  # TCP_KEEPIDLE
                    2: 3,  # TCP_KEEPINTVL
                    3: 5,  # TCP_KEEPCNT
                }
            )
            # Test connection
            await self.redis.ping()
            self.connected = True
            logger.info("[OK] Connected to Redis successfully")
            return True
        except Exception as e:
            logger.warning(f"[WARNING] Redis not available: {e}")
            self.connected = False
            return False

    async def disconnect(self):
        """Close Redis connection"""
        if self.redis:
            await self.redis.close()
            self.connected = False
            logger.info("Redis connection closed")

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if not self.connected:
            return None
        try:
            value = await self.redis.get(key)
            if value:
                return json.loads(value) if value.startswith('{') else value
            return None
        except Exception as e:
            logger.error(f"Redis get error: {e}")
            return None

    async def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Set value in cache with TTL"""
        if not self.connected:
            return False
        try:
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            await self.redis.setex(key, ttl, value)
            return True
        except Exception as e:
            logger.error(f"Redis set error: {e}")
            return False

    async def incr(self, key: str, amount: int = 1) -> Optional[int]:
        """Increment counter"""
        if not self.connected:
            return None
        try:
            return await self.redis.incrby(key, amount)
        except Exception as e:
            logger.error(f"Redis incr error: {e}")
            return None

    async def expire(self, key: str, ttl: int) -> bool:
        """Set TTL on existing key"""
        if not self.connected:
            return False
        try:
            return await self.redis.expire(key, ttl)
        except Exception as e:
            logger.error(f"Redis expire error: {e}")
            return False

    async def ping(self) -> bool:
        """Check if Redis is responsive"""
        if not self.connected:
            return False
        try:
            await self.redis.ping()
            return True
        except Exception:
            return False

    async def delete(self, *keys: str) -> int:
        """Delete keys from cache"""
        if not self.connected:
            return 0
        try:
            return await self.redis.delete(*keys)
        except Exception as e:
            logger.error(f"Redis delete error: {e}")
            return 0

    async def exists(self, key: str) -> bool:
        """Check if key exists"""
        if not self.connected:
            return False
        try:
            return await self.redis.exists(key) > 0
        except Exception as e:
            logger.error(f"Redis exists error: {e}")
            return False

    # Rate limiting methods
    async def check_rate_limit(self, key: str, limit: int, window: int) -> tuple[bool, int]:
        """Check rate limit, returns (is_allowed, current_count)"""
        if not self.connected:
            return True, 0  # Allow if Redis is down

        try:
            pipe = self.redis.pipeline()
            pipe.incr(key)
            pipe.expire(key, window)
            results = await pipe.execute()

            current = results[0]
            return current <= limit, current
        except Exception as e:
            logger.error(f"Rate limit check error: {e}")
            return True, 0

# Global Redis client instance
redis_client = RedisClient()