import asyncio
from sqlalchemy import text
from app.database.session import engine

async def main():
    try:
        async with engine.connect() as connection:
            result = await connection.execute(
                text("SELECT current_database(), current_user")
            )
            print("Database connection successful:", result.one())
    except Exception as exc:
        print("Database connection failed:", type(exc).__name__)
        print(str(exc))
    finally:
        await engine.dispose()

asyncio.run(main())
