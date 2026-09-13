import asyncio

from sqlalchemy import text
from app.database.session import AsyncSessionLocal


async def main():
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            text("""
                SELECT id, uuid, email, phone
                FROM users
                WHERE id = 4
            """)
        )

        user = result.mappings().first()

        if user:
            print("ID:", user["id"])
            print("UUID:", user["uuid"])
            print("Email:", user["email"])
            print("Phone:", user["phone"])
        else:
            print("User ID 4 not found")


asyncio.run(main())
