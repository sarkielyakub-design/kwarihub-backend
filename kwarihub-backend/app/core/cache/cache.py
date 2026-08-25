from datetime import timedelta
from typing import Any, Awaitable, Callable

from app.core.cache.redis import redis_client
from app.core.cache.serializer import CacheSerializer


class CacheService:

    async def get(
        self,
        key: str,
    ):
        value = await redis_client.get(key)

        if value:
            return CacheSerializer.loads(value)

        return None

    async def set(
        self,
        key: str,
        value: Any,
        ttl: int = 300,
    ):
        await redis_client.set(
            key,
            CacheSerializer.dumps(value),
            ex=timedelta(seconds=ttl),
        )

    async def delete(
        self,
        key: str,
    ):
        await redis_client.delete(key)

    async def exists(
        self,
        key: str,
    ):
        return await redis_client.exists(key)

    async def clear(self):
        await redis_client.flushdb()

    async def delete_pattern(
        self,
        pattern: str,
    ):
        keys = await redis_client.keys(pattern)

        if keys:
            await redis_client.delete(*keys)

    async def remember(
        self,
        key: str,
        callback: Callable[[], Awaitable[Any]],
        ttl: int = 300,
    ):
        """
        Get from cache or execute callback and cache result.
        """

        cached = await self.get(key)

        if cached is not None:
            return cached

        data = await callback()

        await self.set(
            key,
            data,
            ttl,
        )

        return data


cache = CacheService()