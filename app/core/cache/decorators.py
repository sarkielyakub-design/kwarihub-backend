import functools
import json

from app.core.cache.cache import cache


def cache_response(ttl: int = 300):
    """
    Cache the response of an async function.
    """

    def decorator(func):

        @functools.wraps(func)
        async def wrapper(*args, **kwargs):

            key = (
                f"{func.__module__}:"
                f"{func.__name__}:"
                f"{args}:{kwargs}"
            )

            cached = await cache.get(key)

            if cached:
                return json.loads(cached)

            result = await func(*args, **kwargs)

            await cache.set(
                key,
                json.dumps(
                    result,
                    default=str,
                ),
                ttl,
            )

            return result

        return wrapper

    return decorator