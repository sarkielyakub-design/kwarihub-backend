import asyncio

from app.core.cache.cache import cache


async def main():
    await cache.set(
        "hello",
        {
            "message": "KWARIHUB Redis Working"
        },
    )

    value = await cache.get("hello")

    print(value)


if __name__ == "__main__":
    asyncio.run(main())