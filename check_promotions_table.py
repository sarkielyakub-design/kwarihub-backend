import asyncio
from sqlalchemy import inspect
from app.database.session import engine

async def main():
    async with engine.connect() as connection:
        tables = await connection.run_sync(
            lambda conn: inspect(conn).get_table_names()
        )
        print("promotions exists:", "promotions" in tables)
    await engine.dispose()

asyncio.run(main())
