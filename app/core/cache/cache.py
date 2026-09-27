from datetime import timedelta
from typing import Any, Awaitable, Callable

from redis.exceptions import RedisError

from app.core.cache.redis import redis_client
from app.core.cache.serializer import CacheSerializer


class CacheService:

    # ============================================================
    # GET
    # ============================================================

    async def get(
        self,
        key: str,
    ):
        try:
            value = await redis_client.get(key)

            if value is None:
                return None

            return CacheSerializer.loads(value)

        except RedisError:
            # Redis must never break the application.
            return None

        except Exception:
            # Protect application from invalid/corrupt cache data.
            return None

    # ============================================================
    # SET
    # ============================================================

    async def set(
        self,
        key: str,
        value: Any,
        ttl: int = 300,
    ):
        try:
            await redis_client.set(
                key,
                CacheSerializer.dumps(value),
                ex=timedelta(
                    seconds=ttl
                ),
            )

        except RedisError:
            # Cache failure should not fail the request.
            return None

        except Exception:
            return None

    # ============================================================
    # DELETE
    # ============================================================

    async def delete(
        self,
        key: str,
    ):
        try:
            await redis_client.delete(key)

        except RedisError:
            return None

        except Exception:
            return None

    # ============================================================
    # EXISTS
    # ============================================================

    async def exists(
        self,
        key: str,
    ) -> bool:

        try:
            return bool(
                await redis_client.exists(key)
            )

        except RedisError:
            return False

        except Exception:
            return False

    # ============================================================
    # CLEAR
    # ============================================================

    async def clear(self):

        try:
            await redis_client.flushdb()

        except RedisError:
            return None

        except Exception:
            return None

    # ============================================================
    # DELETE PATTERN
    # ============================================================

    async def delete_pattern(
        self,
        pattern: str,
    ):

        try:
            keys = await redis_client.keys(
                pattern
            )

            if keys:
                await redis_client.delete(
                    *keys
                )

        except RedisError:
            return None

        except Exception:
            return None

    # ============================================================
    # REMEMBER
    # ============================================================

    async def remember(
        self,
        key: str,
        callback: Callable[
            [],
            Awaitable[Any],
        ],
        ttl: int = 300,
    ):

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