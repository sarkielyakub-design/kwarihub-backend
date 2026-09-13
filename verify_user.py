import asyncio

from sqlalchemy import text

from app.database.session import AsyncSessionLocal


USER_ID = 4


async def main():
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            text("""
                UPDATE users
                SET is_verified = TRUE
                WHERE id = :user_id
                RETURNING id, email, is_verified
            """),
            {"user_id": USER_ID},
        )

        user = result.mappings().first()

        await db.commit()

        if user:
            print("Email verification updated successfully.")
            print("ID:", user["id"])
            print("Email:", user["email"])
            print("Is verified:", user["is_verified"])
        else:
            print("User ID 4 not found.")


asyncio.run(main())
