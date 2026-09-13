import asyncio

from sqlalchemy import text

from app.database.session import AsyncSessionLocal
from app.core.security import hash_password


NEW_PASSWORD = "KwariHub@2026"
USER_ID = 4


async def main():
    password_hash = hash_password(NEW_PASSWORD)

    async with AsyncSessionLocal() as db:
        result = await db.execute(
            text("""
                UPDATE users
                SET password_hash = :password_hash
                WHERE id = :user_id
            """),
            {
                "password_hash": password_hash,
                "user_id": USER_ID,
            },
        )

        await db.commit()

        print("Password reset successfully.")
        print("Rows updated:", result.rowcount)
        print("User ID:", USER_ID)
        print("Email: ztechhub1@gmail.com")
        print("New password:", NEW_PASSWORD)


asyncio.run(main())
